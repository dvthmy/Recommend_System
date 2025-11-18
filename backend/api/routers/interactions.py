from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from ..db import get_session

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
async def record_interaction(user_id: str, body: InteractionRequest):
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
            q = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            WITH u, r, rel, coalesce(rel.last_view, datetime("1900-01-01T00:00:00")) AS last_view
            // Nếu chưa từng xem hoặc lần xem trước cách đây hơn 5 giây
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
                return {
                    "message": "View recorded 👁️",
                    "user_view_count": result["total_views"],
                    "recipe_total_views": result["recipe_views"]
                }
            else:
                return {"message": "View recently counted ⏱️"}



        # ===================
        # ❤️ Like Event
        # ===================
        elif body.event_type == "like":
            q_check = """
            MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe {recipe_id:$rid})
            RETURN rel.liked AS liked
            """
            liked_status = s.run(q_check, uid=user_id, rid=body.recipe_id).single()

            # Already liked → skip
            if liked_status and liked_status["liked"]:
                return {"message": "Already liked ❤️", "liked": True}

            # Not yet liked → set liked=true and increment
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
            WITH r, collect(rel.rating) AS all_ratings
            SET r.rating_count = size(all_ratings),
                r.rating_value = round(reduce(total=0, x IN all_ratings | total + x) / size(all_ratings), 2)
            RETURN rel.rating AS rating, r.rating_value AS avg_rating, r.rating_count AS count
            """
            result = s.run(q, uid=user_id, rid=body.recipe_id, rating=body.rating).single()
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
async def get_user_interactions(user_id: str):
    q = """
    MATCH (u:User {user_id:$uid})-[rel:INTERACTED_WITH]->(r:Recipe)
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
    """
    with get_session() as s:
        records = [dict(r) for r in s.run(q, uid=user_id)]
    if not records:
        raise HTTPException(status_code=404, detail="No interactions found")

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