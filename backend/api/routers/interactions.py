from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from ..db import get_session
from ..services.user_profile import update_user_profile_incremental

router = APIRouter(prefix="/users", tags=["Interactions"])

# ========================
# 🧩 MODEL
# ========================
class InteractionRequest(BaseModel):
    recipe_id: str
    event_type: str = Field(..., pattern="^(view|like|rating)$")
    rating: Optional[int] = Field(None, ge=1, le=5)


# ========================
# 🧩 POST — Record user actions (view / like / rating)
# ========================
@router.post("/{user_id}/interactions", summary="Record or update an interaction (view/like/rating)")
async def record_interaction(
    user_id: str, 
    body: InteractionRequest, 
    background_tasks: BackgroundTasks
):
    with get_session() as s:
        # Check user & recipe
        if not s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single():
            raise HTTPException(status_code=404, detail="User not found")
        if not s.run("MATCH (r:Recipe {recipe_id:$rid}) RETURN r", rid=body.recipe_id).single():
            raise HTTPException(status_code=404, detail="Recipe not found")

        # Ensure relationship exists
        s.run("""
            MATCH (u:User {user_id:$uid})
            MATCH (r:Recipe {recipe_id:$rid})
            MERGE (u)-[rel:INTERACTED_WITH]->(r)
            ON CREATE SET rel.created_at = datetime()
            SET rel.updated_at = datetime()
        """, uid=user_id, rid=body.recipe_id)

        # ===================
        # 👁️ View Event
        # ===================
        if body.event_type == "view":
            # Record view interaction with rate limiting (5 seconds between views)
            # This prevents spam and ensures accurate view counts
            q = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            WITH u, r, rel, coalesce(rel.last_view, datetime("1900-01-01T00:00:00")) AS last_view
            // Only count view if never viewed before or last view was more than 5 seconds ago
            WHERE rel.last_view IS NULL OR duration.inSeconds(last_view, datetime()).seconds > 5
            SET rel.event_type = 'view',
                rel.last_view = datetime(),
                rel.view_count = coalesce(rel.view_count, 0) + 1,
                rel.timestamp = datetime(),
                r.popularity_views = coalesce(r.popularity_views, 0) + 1
            RETURN rel.view_count AS total_views, r.popularity_views AS recipe_views
            """
            result = s.run(q, uid=user_id, rid=body.recipe_id).single()
            if result:
                # ✅ Trigger incremental profile update
                background_tasks.add_task(update_user_profile_incremental, user_id)
                
                return {
                    "message": "View recorded 👁️",
                    "user_view_count": result["total_views"],
                    "recipe_total_views": result["recipe_views"]
                }
            else:
                # View was recorded recently (within 5 seconds), skip counting
                # Get current view count without incrementing
                q_current = """
                MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
                RETURN rel.view_count AS total_views, r.popularity_views AS recipe_views
                """
                current_result = s.run(q_current, uid=user_id, rid=body.recipe_id).single()
                if current_result:
                    return {
                        "message": "View recently counted ⏱️",
                        "user_view_count": current_result.get("total_views", 0),
                        "recipe_total_views": current_result.get("recipe_views", 0)
                    }
                return {"message": "View recently counted ⏱️"}



        # ===================
        # ❤️ Like Event (Toggle)
        # ===================
        elif body.event_type == "like":
            q_check = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            RETURN rel.liked AS liked
            """
            liked_status = s.run(q_check, uid=user_id, rid=body.recipe_id).single()
            current_liked = liked_status and liked_status.get("liked", False)

            # Toggle: If liked → unlike, if not liked → like
            # Note: Unlike only sets liked=false, does NOT delete the recipe node
            if current_liked:
                # Unlike: set liked=false and decrement popularity
                # Recipe node remains intact, only the like status is removed
                q_unlike = """
                MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
                SET rel.liked = false,
                    rel.timestamp = datetime()
                WITH r
                SET r.popularity_likes = CASE 
                    WHEN r.popularity_likes > 0 THEN r.popularity_likes - 1 
                    ELSE 0 
                END
                RETURN r.popularity_likes AS recipe_likes
                """
                result = s.run(q_unlike, uid=user_id, rid=body.recipe_id).single()
                
                # ✅ Trigger incremental profile update
                background_tasks.add_task(update_user_profile_incremental, user_id)
                
                return {"message": "Unliked 💔", "liked": False, "recipe_likes": result["recipe_likes"]}
            else:
                # Like: set liked=true and increment
                q_like = """
                MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
                SET rel.event_type = 'like',
                rel.liked = true,
                rel.like_time = datetime(),
                rel.timestamp = datetime()
                WITH r
                SET r.popularity_likes = coalesce(r.popularity_likes, 0) + 1
                RETURN r.popularity_likes AS recipe_likes
                """
                result = s.run(q_like, uid=user_id, rid=body.recipe_id).single()
                
                # ✅ Trigger incremental profile update
                background_tasks.add_task(update_user_profile_incremental, user_id)
                
                return {"message": "Liked ❤️", "liked": True, "recipe_likes": result["recipe_likes"]}

        # ===================
        # ⭐ Rating Event
        # ===================
        elif body.event_type == "rating":
            if body.rating is None:
                raise HTTPException(status_code=400, detail="Rating required for 'rating' event")

            q = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            SET rel.event_type = 'rating',
                rel.rating = $rating,
                rel.rating_time = datetime(),
                rel.timestamp = datetime()
            
            // Re-calculate average rating for the recipe
            WITH r, rel
            MATCH (r)<-[all_rels:INTERACTED_WITH]-(:User)
            WHERE all_rels.rating IS NOT NULL
            WITH r, rel, avg(all_rels.rating) AS new_avg, count(all_rels) AS new_count
            SET r.rating_value = round(new_avg, 2),
                r.rating_count = new_count
            
            RETURN rel.rating AS rating, r.rating_value AS avg_rating, r.rating_count AS count
            """
            result = s.run(q, uid=user_id, rid=body.recipe_id, rating=body.rating).single()
            
            # ✅ Trigger incremental profile update
            background_tasks.add_task(update_user_profile_incremental, user_id)
            
            return {
                "message": "Rating updated ⭐",
                "user_rating": result["rating"],
                "recipe_avg_rating": result["avg_rating"],
                "rating_count": result["count"]
            }


# ========================
# 🧩 GET — Retrieve all user interactions
# ========================
@router.get("/{user_id}/interactions", summary="Get all user interactions (likes, ratings, views)")
async def get_user_interactions(
    user_id: str,
    event_type: Optional[str] = Query(None, pattern="^(view|like|rating)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0)
):
    # Build query with optional filter
    where_clause = ""
    if event_type == "like":
        where_clause = "WHERE rel.liked = true"
    elif event_type == "view":
        where_clause = "WHERE rel.view_count > 0"
    elif event_type == "rating":
        where_clause = "WHERE rel.rating IS NOT NULL"
    
    q = f"""
    MATCH (u:User {{user_id:$uid}})-[rel:INTERACTED_WITH]->(r:Recipe)
    {where_clause}
    RETURN 
        r.recipe_id AS recipe_id,
        r.title AS title,
        coalesce(r.image, head(r.image_urls)) AS image,
        rel.view_count AS view_count,
        rel.liked AS liked,
        rel.rating AS rating,
        rel.last_view AS last_view,
        rel.like_time AS like_time,
        rel.rating_time AS rating_time
    ORDER BY coalesce(rel.updated_at, rel.created_at) DESC
    SKIP $offset
    LIMIT $limit
    """
    with get_session() as s:
        records = [dict(r) for r in s.run(q, uid=user_id, offset=offset, limit=limit)]
    
    # Convert Neo4j DateTime objects to ISO strings
    def convert_datetime_to_iso(value):
        if value is None:
            return None
        # Check if it's a Neo4j DateTime object
        if hasattr(value, 'to_native'):
            # Neo4j DateTime object - convert to Python datetime then ISO string
            dt = value.to_native()
            return dt.isoformat() if isinstance(dt, datetime) else str(dt)
        elif isinstance(value, datetime):
            # Already a Python datetime
            return value.isoformat()
        elif isinstance(value, str):
            # Already a string
            return value
        return str(value)
    
    if event_type == "like":
        # Return only liked recipes for 'like' event_type
        likes = [r for r in records if r.get("liked")]
        return {
            "user_id": user_id,
            "interactions": [{
                "recipe_id": r["recipe_id"],
                "like_time": convert_datetime_to_iso(r.get("like_time"))
            } for r in likes]
        }
    
    elif event_type == "view":
        # Return only viewed recipes for 'view' event_type
        views = [r for r in records if r.get("view_count", 0) > 0]
        return {
            "user_id": user_id,
            "interactions": [{
                "recipe_id": r["recipe_id"], 
                "view_count": r.get("view_count", 0),
                "last_view": convert_datetime_to_iso(r.get("last_view"))
            } for r in views]
        }
    
    elif event_type == "rating":
        # Return only rated recipes for 'rating' event_type
        ratings = [r for r in records if r.get("rating")]
        return {
            "user_id": user_id,
            "interactions": [{
                "recipe_id": r["recipe_id"], 
                "rating": r.get("rating"),
                "rating_time": convert_datetime_to_iso(r.get("rating_time"))
            } for r in ratings]
        }
    
    # Return all interactions if no filter
    if not records:
        return {
            "user_id": user_id,
            "summary": {
                "total_likes": 0,
                "total_views": 0,
                "total_ratings": 0
            },
            "likes": [],
            "views": [],
            "ratings": []
        }

    likes = [r for r in records if r.get("liked")]
    views = [r for r in records if r.get("view_count")]
    ratings = [r for r in records if r.get("rating")]

    return {
        "user_id": user_id,
        "summary": {
            "total_likes": len(likes),
            "total_views": len(views),
            "total_ratings": len(ratings)
        },
        "likes": likes,
        "views": views,
        "ratings": ratings
    }


# ========================
# 📊 GET — Get user interaction statistics
# ========================
@router.get("/{user_id}/interactions/stats", summary="Get user interaction statistics")
async def get_user_interaction_stats(user_id: str):
    """Get aggregated statistics for user interactions"""
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Get all interactions
        q = """
        MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe)
        RETURN 
            count(CASE WHEN rel.liked = true THEN 1 END) AS like_count,
            count(CASE WHEN rel.view_count > 0 THEN 1 END) AS view_count,
            count(CASE WHEN rel.rating IS NOT NULL AND rel.rating > 0 THEN 1 END) AS rating_count,
            count(CASE WHEN EXISTS((u)-[:INTERACTED_WITH {saved: true}]->(r)) THEN 1 END) AS save_count
        """
        result = s.run(q, uid=user_id).single()
        
        if not result:
            # Return zero stats if no interactions
            return {
                "user_id": user_id,
                "stats": {
                    "like_count": 0,
                    "view_count": 0,
                    "rating_count": 0,
                    "save_count": 0,
                    "total_interactions": 0
                }
            }
        
        like_count = result.get("like_count", 0) or 0
        view_count = result.get("view_count", 0) or 0
        rating_count = result.get("rating_count", 0) or 0
        save_count = result.get("save_count", 0) or 0
        
        # Also check for saved recipes (if saved property exists)
        saved_q = """
        MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe)
        WHERE rel.saved = true
        RETURN count(rel) AS save_count
        """
        saved_result = s.run(saved_q, uid=user_id).single()
        if saved_result:
            save_count = saved_result.get("save_count", 0) or 0
        
        total = like_count + view_count + rating_count
        
        return {
            "user_id": user_id,
            "stats": {
                "like_count": like_count,
                "view_count": view_count,
                "rating_count": rating_count,
                "save_count": save_count,
                "total_interactions": total
            }
        }


# ========================
# 🗑️ DELETE — Delete user interaction
# ========================
@router.delete("/{user_id}/interactions/{recipe_id}", summary="Delete a user interaction (like/unlike)")
async def delete_interaction(
    user_id: str,
    recipe_id: str,
    event_type: Optional[str] = Query(None, pattern="^(view|like|rating)$")
):
    """Delete a specific interaction (like, rating, or all interactions) for a recipe"""
    with get_session() as s:
        # Check user & recipe
        if not s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single():
            raise HTTPException(status_code=404, detail="User not found")
        if not s.run("MATCH (r:Recipe {recipe_id:$rid}) RETURN r", rid=recipe_id).single():
            raise HTTPException(status_code=404, detail="Recipe not found")
        
        # Check if interaction exists
        q_check = """
        MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
        RETURN rel.liked AS liked, rel.rating AS rating, rel.view_count AS view_count
        """
        interaction = s.run(q_check, uid=user_id, rid=recipe_id).single()
        
        if not interaction:
            raise HTTPException(status_code=404, detail="Interaction not found")
        
        # Delete specific interaction type
        if event_type == "like":
            # Unlike: set liked=false and decrement popularity
            # Note: This only removes the like status, does NOT delete the recipe node
            if not interaction.get("liked"):
                return {"message": "Recipe not liked", "liked": False}
            
            q_delete_like = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            SET rel.liked = false,
                rel.timestamp = datetime()
            WITH r
            SET r.popularity_likes = CASE 
                WHEN r.popularity_likes > 0 THEN r.popularity_likes - 1 
                ELSE 0 
            END
            RETURN r.popularity_likes AS recipe_likes
            """
            result = s.run(q_delete_like, uid=user_id, rid=recipe_id).single()
            return {
                "message": "Like removed 💔",
                "liked": False,
                "recipe_likes": result["recipe_likes"]
            }
        
        elif event_type == "view":
            # Reset view count for this user-recipe interaction
            # Note: This only resets the user's view count, not the recipe's total popularity_views
            # To decrement popularity_views, we would need to check if this was a unique view
            # For simplicity, we only reset the user's view_count
            current_view_count = interaction.get("view_count", 0) or 0
            
            if current_view_count == 0:
                return {"message": "No views to remove", "view_count": 0}
            
            q_delete_view = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            SET rel.view_count = 0,
                rel.last_view = NULL,
                rel.timestamp = datetime()
            RETURN rel.view_count AS view_count
            """
            result = s.run(q_delete_view, uid=user_id, rid=recipe_id).single()
            return {
                "message": "View count reset",
                "view_count": result.get("view_count", 0) if result else 0
            }
        
        elif event_type == "rating":
            # Remove rating
            if not interaction.get("rating"):
                return {"message": "No rating found", "rating": None}
            
            # First, remove the rating
            q_delete_rating = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            SET rel.rating = NULL,
                rel.rating_time = NULL,
                rel.timestamp = datetime()
            RETURN r.recipe_id AS recipe_id
            """
            s.run(q_delete_rating, uid=user_id, rid=recipe_id)
            
            # Then, recalculate rating stats for the recipe
            q_recalculate = """
            MATCH (u:User)-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            WHERE rel.rating IS NOT NULL AND rel.rating > 0
            WITH r, collect(rel.rating) AS all_ratings
            SET r.rating_count = size(all_ratings),
                r.rating_value = CASE 
                    WHEN size(all_ratings) > 0 
                    THEN round(reduce(total=0, x IN all_ratings | total + x) / size(all_ratings), 2)
                    ELSE NULL
                END
            RETURN r.rating_value AS avg_rating, r.rating_count AS count
            """
            result = s.run(q_recalculate, rid=recipe_id).single()
            return {
                "message": "Rating removed",
                "rating": None,
                "recipe_avg_rating": result.get("avg_rating") if result else None,
                "recipe_rating_count": result.get("count") if result else 0
            }
        
        else:
            # Delete entire interaction relationship (all types)
            q_delete_all = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            WITH u, r, rel
            DELETE rel
            RETURN r.recipe_id AS recipe_id
            """
            result = s.run(q_delete_all, uid=user_id, rid=recipe_id).single()
            
            if result:
                return {
                    "message": "Interaction deleted",
                    "recipe_id": recipe_id
                }
            else:
                raise HTTPException(status_code=404, detail="Interaction not found")