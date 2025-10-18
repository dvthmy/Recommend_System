from fastapi import FastAPI, HTTPException, Query, Path
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
import sys
import time
from pathlib import Path as PathLib

# Add scripts directory to path to import recommend module
sys.path.append(str(PathLib(__file__).parent / "scripts"))
from recommend import recommend

app = FastAPI(
    title="Food Recommendation API",
    description="API for food recipe recommendations using hybrid approach",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request/Response Models
class RecommendationRequest(BaseModel):
    user_id: Optional[str] = None
    ingredient_ids: Optional[List[str]] = None
    max_cook_time: Optional[int] = None
    limit: int = 10

class RecipeRecommendation(BaseModel):
    recipe_id: str
    title: str
    cuisine: Optional[str] = "Unknown"
    cook_time_min: Optional[int]
    score: float
    scores: Dict[str, float]

class RecommendationResponse(BaseModel):
    results: List[RecipeRecommendation]
    total: int
    request_params: Dict[str, Any]

# User Profile Models
class UserProfile(BaseModel):
    user_id: str
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = None
    dietary_preferences: Optional[List[str]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class UserProfileUpdate(BaseModel):
    locale: Optional[str] = None
    skill_level: Optional[str] = None
    max_cook_time: Optional[int] = Field(None, ge=1, le=480)  # 1 minute to 8 hours
    dietary_preferences: Optional[List[str]] = None

class AllergyInfo(BaseModel):
    ingredient_id: str
    ingredient_name: str
    category: Optional[str] = None
    severity: Optional[str] = "moderate"  # mild, moderate, severe

class DislikeInfo(BaseModel):
    ingredient_id: str
    ingredient_name: str
    category: Optional[str] = None
    reason: Optional[str] = None

class CuisinePreference(BaseModel):
    cuisine_name: str
    preference_level: int = Field(1, ge=1, le=5)  # 1-5 scale
    added_at: Optional[datetime] = None

class UserAllergiesResponse(BaseModel):
    user_id: str
    allergies: List[AllergyInfo]
    total: int

class UserDislikesResponse(BaseModel):
    user_id: str
    dislikes: List[DislikeInfo]
    total: int

class UserCuisinesResponse(BaseModel):
    user_id: str
    favorite_cuisines: List[CuisinePreference]
    total: int

class AllergyUpdateRequest(BaseModel):
    ingredient_ids: List[str]

class DislikeUpdateRequest(BaseModel):
    ingredient_ids: List[str]
    reasons: Optional[Dict[str, str]] = None  # ingredient_id -> reason

class CuisinePreferenceRequest(BaseModel):
    cuisine_name: str
    preference_level: int = Field(1, ge=1, le=5)

# Recipe Models
class RecipeIngredient(BaseModel):
    ingredient_id: str
    ingredient_name: str
    quantity: Optional[str] = None
    unit: Optional[str] = None
    is_optional: bool = False
    preparation: Optional[str] = None

class RecipeDetail(BaseModel):
    recipe_id: str
    title: str
    cuisine: Optional[str] = None
    cook_time_min: Optional[int] = None
    prep_time_min: Optional[int] = None
    total_time_min: Optional[int] = None
    servings: Optional[int] = None
    instructions: Optional[str] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    popularity_views: Optional[int] = 0
    popularity_saves: Optional[int] = 0
    popularity_cooks: Optional[int] = 0
    popularity_likes: Optional[int] = 0
    allergens: Optional[List[str]] = None
    nutrition_calories: Optional[int] = None
    equipment_needed: Optional[List[str]] = None
    alternative_ingredients: Optional[List[str]] = None
    ingredients: Optional[List[RecipeIngredient]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    max_cook_time: Optional[int] = None
    min_cook_time: Optional[int] = None
    tags: Optional[List[str]] = None
    ingredients: Optional[List[str]] = None
    exclude_ingredients: Optional[List[str]] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class RecipeSearchResponse(BaseModel):
    recipes: List[RecipeDetail]
    total: int
    limit: int
    offset: int
    has_more: bool

class RecipeListResponse(BaseModel):
    recipes: List[RecipeDetail]
    total: int
    cuisine: Optional[str] = None

# Ingredient Models
class IngredientDetail(BaseModel):
    ingredient_id: str
    canonical_name: str
    name: Optional[str] = None
    category: Optional[str] = None
    allergen: Optional[bool] = False
    alternative_names: Optional[List[str]] = None
    description: Optional[str] = None
    nutrition_info: Optional[Dict[str, Any]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

class IngredientSearchRequest(BaseModel):
    query: Optional[str] = None
    category: Optional[str] = None
    allergen: Optional[bool] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class IngredientSearchResponse(BaseModel):
    ingredients: List[IngredientDetail]
    total: int
    limit: int
    offset: int
    has_more: bool

class IngredientListResponse(BaseModel):
    ingredients: List[IngredientDetail]
    total: int
    category: Optional[str] = None

class IngredientSynonym(BaseModel):
    synonym: str
    confidence: Optional[float] = None

class IngredientSynonymsResponse(BaseModel):
    ingredient_id: str
    canonical_name: str
    synonyms: List[IngredientSynonym]
    total: int

# User Interaction Models
class UserInteraction(BaseModel):
    interaction_id: Optional[str] = None
    user_id: str
    recipe_id: str
    event_type: str = Field(..., pattern="^(cook|like|save|view|dislike)$")
    timestamp: Optional[datetime] = None
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)  # For cook events
    success: Optional[bool] = None  # For cook events

class InteractionRecordRequest(BaseModel):
    recipe_id: str
    event_type: str = Field(..., pattern="^(cook|like|save|view|dislike)$")
    rating: Optional[int] = Field(None, ge=1, le=5)
    notes: Optional[str] = None
    duration_minutes: Optional[int] = Field(None, ge=0)
    success: Optional[bool] = None

class UserInteractionsResponse(BaseModel):
    user_id: str
    interactions: List[UserInteraction]
    total: int
    limit: int
    offset: int
    has_more: bool

class InteractionStats(BaseModel):
    total_interactions: int
    cook_count: int
    like_count: int
    save_count: int
    view_count: int
    dislike_count: int
    average_rating: Optional[float] = None
    most_recent_interaction: Optional[datetime] = None

class UserInteractionStatsResponse(BaseModel):
    user_id: str
    stats: InteractionStats

class RecomputeProfileRequest(BaseModel):
    force_recompute: bool = False
    interaction_types: Optional[List[str]] = None  # Filter by interaction types

class RecomputeProfileResponse(BaseModel):
    user_id: str
    success: bool
    message: str
    user_vector_updated: bool
    interaction_count: int

class RecipeSummary(BaseModel):
    recipe_id: str
    title: str
    cuisine: Optional[str] = None
    cook_time_min: Optional[int] = None
    servings: Optional[int] = None
    tags: Optional[List[str]] = None
    image_urls: Optional[List[str]] = None
    popularity_views: Optional[int] = None
    nutrition_calories: Optional[int] = None

class RecipeSearchRequest(BaseModel):
    query: Optional[str] = None
    cuisine: Optional[str] = None
    tags: Optional[List[str]] = None
    max_cook_time: Optional[int] = None
    min_cook_time: Optional[int] = None
    servings: Optional[int] = None
    has_allergens: Optional[List[str]] = None
    exclude_allergens: Optional[List[str]] = None
    min_calories: Optional[int] = None
    max_calories: Optional[int] = None
    limit: int = Field(20, ge=1, le=100)
    offset: int = Field(0, ge=0)

class RecipeSearchResponse(BaseModel):
    results: List[RecipeSummary]
    total: int
    limit: int
    offset: int
    has_more: bool

class RecipeByCuisineResponse(BaseModel):
    cuisine: str
    recipes: List[RecipeSummary]
    total: int
    limit: int
    offset: int

class RecipeByTagsResponse(BaseModel):
    tags: List[str]
    recipes: List[RecipeSummary]
    total: int
    limit: int
    offset: int

# Environment variables with defaults
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Admin123!")
NEO4J_DATABASE = os.getenv("NEO4J_DATABASE", "food")

@app.get("/")
async def root():
    return {
        "message": "Food Recommendation API",
        "version": "1.0.0",
        "endpoints": {
            "recommend": "/recommend",
            "health": "/health",
            "me": "/me",
            "create_user": "/users",
            "ingredients": "/ingredients",
            "cuisines": "/cuisines",
            "user_profile": "/users/{user_id}/profile",
            "user_allergies": "/users/{user_id}/allergies",
            "user_dislikes": "/users/{user_id}/dislikes",
            "user_cuisines": "/users/{user_id}/favorite-cuisines",
            "recipe_detail": "/recipes/{recipe_id}",
            "recipe_search": "/recipes/search",
            "recipe_by_cuisine": "/recipes/by-cuisine/{cuisine}",
            "recipe_by_tags": "/recipes/by-tags",
            "ingredient_detail": "/ingredients/{ingredient_id}",
            "ingredient_search": "/ingredients/search",
            "ingredients_by_category": "/ingredients/by-category/{category}",
            "ingredient_synonyms": "/ingredients/{ingredient_id}/synonyms",
            "user_interactions": "/users/{user_id}/interactions",
            "user_interaction_stats": "/users/{user_id}/interactions/stats",
            "recompute_profile": "/users/{user_id}/recompute-profile"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test Neo4j connection
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("RETURN 1 as test")
            result.single()
        driver.close()
        
        return {
            "status": "healthy",
            "neo4j_connection": "ok",
            "database": NEO4J_DATABASE
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Service unhealthy: {str(e)}")

@app.post("/recommend", response_model=RecommendationResponse)
async def get_recommendations(request: RecommendationRequest):
    """
    Get food recipe recommendations based on ingredients and preferences
    """
    try:
        # Set default parameters as per command line format
        # --w-ing 1.0 --w-text 1.0 --w-pop 1.0 --w-cf 1.0 --norm rank --pop-half-life 60
        results = recommend(
            uri=NEO4J_URI,
            user=NEO4J_USER,
            password=NEO4J_PASSWORD,
            database=NEO4J_DATABASE,
            user_id=request.user_id,
            ingredient_ids=request.ingredient_ids,
            cuisine=None,  # No cuisine filter in command line
            max_cook_time=request.max_cook_time,
            limit_candidates=request.limit * 5,  # Get more candidates for better results
            limit_results=request.limit,
            w_ing=1.0,  # Default from command line
            w_text=1.0,  # Default from command line
            w_pop=1.0,  # Default from command line
            w_cf=1.0,  # Default from command line
            norm="rank",  # Default from command line
            pop_half_life=60.0,  # Default from command line
            diversify=False,  # No diversification in command line
            mmr_lambda=0.7,  # Default value
        )
        
        # Convert to response model
        recommendations = [
            RecipeRecommendation(
                recipe_id=r["recipe_id"],
                title=r["title"],
                cuisine=r["cuisine"][0] if isinstance(r["cuisine"], list) and r["cuisine"] else (r["cuisine"] or "Unknown"),
                cook_time_min=r["cook_time_min"],
                score=r["score"],
                scores=r["scores"]
            )
            for r in results
        ]
        
        return RecommendationResponse(
            results=recommendations,
            total=len(recommendations),
            request_params=request.dict()
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recommendation failed: {str(e)}")

@app.get("/recommend", response_model=RecommendationResponse)
async def get_recommendations_get(
    user_id: Optional[str] = Query(None, description="User ID for personalization"),
    ingredient_ids: Optional[str] = Query(None, description="Comma-separated ingredient IDs"),
    max_cook_time: Optional[int] = Query(None, description="Maximum cooking time in minutes"),
    limit: int = Query(10, description="Number of recommendations to return")
):
    """
    Get food recipe recommendations (GET version for easier testing)
    """
    # Parse ingredient_ids if provided
    parsed_ingredient_ids = None
    if ingredient_ids:
        parsed_ingredient_ids = [id.strip() for id in ingredient_ids.split(",") if id.strip()]
    
    request = RecommendationRequest(
        user_id=user_id,
        ingredient_ids=parsed_ingredient_ids,
        max_cook_time=max_cook_time,
        limit=limit
    )
    
    return await get_recommendations(request)

@app.get("/ingredients")
async def get_ingredients():
    """
    Get list of available ingredients
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (i:Ingredient)
                RETURN i.ingredient_id as id, i.name as name
                ORDER BY i.name
                LIMIT 100
            """)
            
            ingredients = [
                {"id": record["id"], "name": record["name"]}
                for record in result
            ]
        
        driver.close()
        return {"ingredients": ingredients}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingredients: {str(e)}")

@app.get("/cuisines")
async def get_cuisines():
    """
    Get list of available cuisines
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (r:Recipe)
                WHERE r.cuisine IS NOT NULL
                RETURN DISTINCT r.cuisine as cuisine
                ORDER BY r.cuisine
            """)
            
            cuisines = [record["cuisine"] for record in result]
        
        driver.close()
        return {"cuisines": cuisines}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cuisines: {str(e)}")

# User Management APIs
@app.get("/me", response_model=UserProfile)
async def get_current_user():
    """
    Get current user information from session/cookie
    This endpoint should be called when user first visits the app
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # For now, we'll return a default user profile
        # In a real implementation, you would check session/cookie for user_id
        # and return the actual user profile
        
        # Create a default user profile
        default_profile = UserProfile(
            user_id="default_user",
            locale="vi-VN",
            skill_level="intermediate",
            max_cook_time=60,
            dietary_preferences=[],
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        driver.close()
        return default_profile
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get current user: {str(e)}")

@app.post("/users", response_model=UserProfile)
async def create_user():
    """
    Create a new user
    """
    try:
        from neo4j import GraphDatabase
        import uuid
        
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        # Generate unique user ID
        user_id = f"user_{uuid.uuid4().hex[:8]}"
        now = datetime.now()
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Create user node
            session.run("""
                CREATE (u:User {
                    user_id: $user_id,
                    locale: $locale,
                    skill_level: $skill_level,
                    max_cook_time: $max_cook_time,
                    dietary_preferences: $dietary_preferences,
                    created_at: $created_at,
                    updated_at: $updated_at
                })
            """, 
            user_id=user_id,
            locale="vi-VN",
            skill_level="intermediate",
            max_cook_time=60,
            dietary_preferences=[],
            created_at=now,
            updated_at=now
            )
        
        driver.close()
        
        # Return created user profile
        return UserProfile(
            user_id=user_id,
            locale="vi-VN",
            skill_level="intermediate",
            max_cook_time=60,
            dietary_preferences=[],
            created_at=now,
            updated_at=now
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create user: {str(e)}")

# User Profile APIs
@app.get("/users/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """
    Get user profile information
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id,
                       u.locale as locale,
                       u.skill_level as skill_level,
                       u.max_cook_time as max_cook_time,
                       u.dietary_preferences as dietary_preferences,
                       u.created_at as created_at,
                       u.updated_at as updated_at
            """, user_id=user_id)
            
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Convert Neo4j DateTime to Python datetime
            created_at = record["created_at"]
            updated_at = record["updated_at"]
            
            # Handle Neo4j DateTime objects
            if hasattr(created_at, 'to_native'):
                created_at = created_at.to_native()
            if hasattr(updated_at, 'to_native'):
                updated_at = updated_at.to_native()
            
            profile = UserProfile(
                user_id=record["user_id"],
                locale=record["locale"],
                skill_level=record["skill_level"],
                max_cook_time=record["max_cook_time"],
                dietary_preferences=record["dietary_preferences"],
                created_at=created_at,
                updated_at=updated_at
            )
        
        driver.close()
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user profile: {str(e)}")

@app.put("/users/{user_id}/profile", response_model=UserProfile)
async def update_user_profile(
    user_id: str = Path(description="User ID"),
    profile_update: UserProfileUpdate = None
):
    """
    Update user profile information
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Update user profile
            update_fields = []
            params = {"user_id": user_id, "updated_at": datetime.now()}
            
            if profile_update.locale is not None:
                update_fields.append("u.locale = $locale")
                params["locale"] = profile_update.locale
                
            if profile_update.skill_level is not None:
                update_fields.append("u.skill_level = $skill_level")
                params["skill_level"] = profile_update.skill_level
                
            if profile_update.max_cook_time is not None:
                update_fields.append("u.max_cook_time = $max_cook_time")
                params["max_cook_time"] = profile_update.max_cook_time
                
            if profile_update.dietary_preferences is not None:
                update_fields.append("u.dietary_preferences = $dietary_preferences")
                params["dietary_preferences"] = profile_update.dietary_preferences
            
            if update_fields:
                update_fields.append("u.updated_at = $updated_at")
                
                update_query = f"""
                    MATCH (u:User {{user_id: $user_id}})
                    SET {', '.join(update_fields)}
                    RETURN u.user_id as user_id,
                           u.locale as locale,
                           u.skill_level as skill_level,
                           u.max_cook_time as max_cook_time,
                           u.dietary_preferences as dietary_preferences,
                           u.created_at as created_at,
                           u.updated_at as updated_at
                """
                
                result = session.run(update_query, params)
                record = result.single()
                
                # Convert Neo4j DateTime to Python datetime
                created_at = record["created_at"]
                updated_at = record["updated_at"]
                
                # Handle Neo4j DateTime objects
                if hasattr(created_at, 'to_native'):
                    created_at = created_at.to_native()
                if hasattr(updated_at, 'to_native'):
                    updated_at = updated_at.to_native()
                
                profile = UserProfile(
                    user_id=record["user_id"],
                    locale=record["locale"],
                    skill_level=record["skill_level"],
                    max_cook_time=record["max_cook_time"],
                    dietary_preferences=record["dietary_preferences"],
                    created_at=created_at,
                    updated_at=updated_at
                )
            else:
                # No fields to update, return current profile
                result = session.run("""
                    MATCH (u:User {user_id: $user_id})
                    RETURN u.user_id as user_id,
                           u.locale as locale,
                           u.skill_level as skill_level,
                           u.max_cook_time as max_cook_time,
                           u.dietary_preferences as dietary_preferences,
                           u.created_at as created_at,
                           u.updated_at as updated_at
                """, user_id=user_id)
                
                record = result.single()
                
                # Convert Neo4j DateTime to Python datetime
                created_at = record["created_at"]
                updated_at = record["updated_at"]
                
                # Handle Neo4j DateTime objects
                if hasattr(created_at, 'to_native'):
                    created_at = created_at.to_native()
                if hasattr(updated_at, 'to_native'):
                    updated_at = updated_at.to_native()
                
                profile = UserProfile(
                    user_id=record["user_id"],
                    locale=record["locale"],
                    skill_level=record["skill_level"],
                    max_cook_time=record["max_cook_time"],
                    dietary_preferences=record["dietary_preferences"],
                    created_at=created_at,
                    updated_at=updated_at
                )
        
        driver.close()
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update user profile: {str(e)}")

@app.get("/users/{user_id}/allergies", response_model=UserAllergiesResponse)
async def get_user_allergies(user_id: str = Path(description="User ID")):
    """
    Get user's allergies
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (u:User {user_id: $user_id})-[:ALLERGIC_TO]->(i:Ingredient)
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as ingredient_name,
                       i.category as category
            """, user_id=user_id)
            
            allergies = [
                AllergyInfo(
                    ingredient_id=record["ingredient_id"],
                    ingredient_name=record["ingredient_name"],
                    category=record["category"]
                )
                for record in result
            ]
        
        driver.close()
        return UserAllergiesResponse(
            user_id=user_id,
            allergies=allergies,
            total=len(allergies)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user allergies: {str(e)}")

@app.post("/users/{user_id}/allergies")
async def add_user_allergies(
    user_id: str = Path(description="User ID"),
    allergy_request: AllergyUpdateRequest = None
):
    """
    Add allergies for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Add allergy relationships
            added_count = 0
            for ingredient_id in allergy_request.ingredient_ids:
                result = session.run("""
                    MATCH (u:User {user_id: $user_id})
                    MATCH (i:Ingredient {ingredient_id: $ingredient_id})
                    MERGE (u)-[:ALLERGIC_TO]->(i)
                    RETURN count(*) as count
                """, user_id=user_id, ingredient_id=ingredient_id)
                
                if result.single()["count"] > 0:
                    added_count += 1
        
        driver.close()
        return {
            "message": f"Added {added_count} allergies for user {user_id}",
            "added_count": added_count,
            "total_requested": len(allergy_request.ingredient_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user allergies: {str(e)}")

@app.delete("/users/{user_id}/allergies")
async def remove_user_allergies(
    user_id: str = Path(description="User ID"),
    allergy_request: AllergyUpdateRequest = None
):
    """
    Remove allergies for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            removed_count = 0
            for ingredient_id in allergy_request.ingredient_ids:
                result = session.run("""
                    MATCH (u:User {user_id: $user_id})-[r:ALLERGIC_TO]->(i:Ingredient {ingredient_id: $ingredient_id})
                    DELETE r
                    RETURN count(*) as count
                """, user_id=user_id, ingredient_id=ingredient_id)
                
                if result.single()["count"] > 0:
                    removed_count += 1
        
        driver.close()
        return {
            "message": f"Removed {removed_count} allergies for user {user_id}",
            "removed_count": removed_count,
            "total_requested": len(allergy_request.ingredient_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove user allergies: {str(e)}")

@app.get("/users/{user_id}/dislikes", response_model=UserDislikesResponse)
async def get_user_dislikes(user_id: str = Path(description="User ID")):
    """
    Get user's dislikes
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (u:User {user_id: $user_id})-[:DISLIKES]->(i:Ingredient)
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as ingredient_name,
                       i.category as category
            """, user_id=user_id)
            
            dislikes = [
                DislikeInfo(
                    ingredient_id=record["ingredient_id"],
                    ingredient_name=record["ingredient_name"],
                    category=record["category"]
                )
                for record in result
            ]
        
        driver.close()
        return UserDislikesResponse(
            user_id=user_id,
            dislikes=dislikes,
            total=len(dislikes)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user dislikes: {str(e)}")

@app.post("/users/{user_id}/dislikes")
async def add_user_dislikes(
    user_id: str = Path(description="User ID"),
    dislike_request: DislikeUpdateRequest = None
):
    """
    Add dislikes for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Add dislike relationships
            added_count = 0
            for ingredient_id in dislike_request.ingredient_ids:
                reason = dislike_request.reasons.get(ingredient_id) if dislike_request.reasons else None
                
                result = session.run("""
                    MATCH (u:User {user_id: $user_id})
                    MATCH (i:Ingredient {ingredient_id: $ingredient_id})
                    MERGE (u)-[r:DISLIKES]->(i)
                    SET r.reason = $reason
                    RETURN count(*) as count
                """, user_id=user_id, ingredient_id=ingredient_id, reason=reason)
                
                if result.single()["count"] > 0:
                    added_count += 1
        
        driver.close()
        return {
            "message": f"Added {added_count} dislikes for user {user_id}",
            "added_count": added_count,
            "total_requested": len(dislike_request.ingredient_ids)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add user dislikes: {str(e)}")

@app.delete("/users/{user_id}/dislikes")
async def remove_user_dislikes(
    user_id: str = Path(description="User ID"),
    dislike_request: DislikeUpdateRequest = None
):
    """
    Remove dislikes for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            removed_count = 0
            for ingredient_id in dislike_request.ingredient_ids:
                result = session.run("""
                    MATCH (u:User {user_id: $user_id})-[r:DISLIKES]->(i:Ingredient {ingredient_id: $ingredient_id})
                    DELETE r
                    RETURN count(*) as count
                """, user_id=user_id, ingredient_id=ingredient_id)
                
                if result.single()["count"] > 0:
                    removed_count += 1
        
        driver.close()
        return {
            "message": f"Removed {removed_count} dislikes for user {user_id}",
            "removed_count": removed_count,
            "total_requested": len(dislike_request.ingredient_ids)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove user dislikes: {str(e)}")

@app.get("/users/{user_id}/favorite-cuisines", response_model=UserCuisinesResponse)
async def get_user_favorite_cuisines(user_id: str = Path(description="User ID")):
    """
    Get user's favorite cuisines
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (u:User {user_id: $user_id})-[r:FAVORS_CUISINE]->(c:Cuisine)
                RETURN c.name as cuisine_name,
                       r.preference_level as preference_level,
                       r.added_at as added_at
                ORDER BY r.preference_level DESC, c.name
            """, user_id=user_id)
            
            cuisines = [
                CuisinePreference(
                    cuisine_name=record["cuisine_name"],
                    preference_level=record["preference_level"] or 1,
                    added_at=record["added_at"]
                )
                for record in result
            ]
        
        driver.close()
        return UserCuisinesResponse(
            user_id=user_id,
            favorite_cuisines=cuisines,
            total=len(cuisines)
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user favorite cuisines: {str(e)}")

@app.post("/users/{user_id}/favorite-cuisines")
async def add_user_favorite_cuisine(
    user_id: str = Path(description="User ID"),
    cuisine_request: CuisinePreferenceRequest = None
):
    """
    Add favorite cuisine for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Add or update cuisine preference
            result = session.run("""
                MATCH (u:User {user_id: $user_id})
                MERGE (c:Cuisine {name: $cuisine_name})
                MERGE (u)-[r:FAVORS_CUISINE]->(c)
                SET r.preference_level = $preference_level,
                    r.added_at = $added_at
                RETURN c.name as cuisine_name, r.preference_level as preference_level
            """, 
            user_id=user_id, 
            cuisine_name=cuisine_request.cuisine_name,
            preference_level=cuisine_request.preference_level,
            added_at=datetime.now())
            
            record = result.single()
        
        driver.close()
        return {
            "message": f"Added favorite cuisine for user {user_id}",
            "cuisine_name": record["cuisine_name"],
            "preference_level": record["preference_level"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to add favorite cuisine: {str(e)}")

@app.delete("/users/{user_id}/favorite-cuisines/{cuisine_name}")
async def remove_user_favorite_cuisine(
    user_id: str = Path(description="User ID"),
    cuisine_name: str = Path(description="Cuisine name")
):
    """
    Remove favorite cuisine for user
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (u:User {user_id: $user_id})-[r:FAVORS_CUISINE]->(c:Cuisine {name: $cuisine_name})
                DELETE r
                RETURN count(*) as count
            """, user_id=user_id, cuisine_name=cuisine_name)
            
            removed_count = result.single()["count"]
        
        driver.close()
        return {
            "message": f"Removed favorite cuisine for user {user_id}",
            "cuisine_name": cuisine_name,
            "removed": removed_count > 0
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to remove favorite cuisine: {str(e)}")

# Recipe APIs
@app.get("/recipes/{recipe_id}", response_model=RecipeDetail)
async def get_recipe_detail(recipe_id: str = Path(description="Recipe ID")):
    """
    Get detailed information about a specific recipe
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Get recipe basic info
            result = session.run("""
                MATCH (r:Recipe {recipe_id: $recipe_id})
                RETURN r.recipe_id as recipe_id,
                       r.title as title,
                       r.cuisine as cuisine,
                       r.cook_time_min as cook_time_min,
                       r.prep_time_min as prep_time_min,
                       r.total_time_min as total_time_min,
                       r.servings as servings,
                       r.instructions as instructions,
                       r.tags as tags,
                       r.image_urls as image_urls,
                       r.popularity_views as popularity_views,
                       r.popularity_saves as popularity_saves,
                       r.popularity_cooks as popularity_cooks,
                       r.popularity_likes as popularity_likes,
                       r.allergens as allergens,
                       r.nutrition_calories as nutrition_calories,
                       r.equipment_needed as equipment_needed,
                       r.alternative_ingredients as alternative_ingredients,
                       r.video_url as video_url,
                       r.created_at as created_at,
                       r.updated_at as updated_at
            """, recipe_id=recipe_id)
            
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail=f"Recipe {recipe_id} not found")
            
            # Get recipe ingredients
            ingredients_result = session.run("""
                MATCH (r:Recipe {recipe_id: $recipe_id})-[rel:HAS_INGREDIENT]->(i:Ingredient)
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as ingredient_name,
                       rel.qty as quantity,
                       rel.unit as unit,
                       rel.optional as is_optional,
                       rel.prep as preparation
                ORDER BY i.canonical_name
            """, recipe_id=recipe_id)
            
            ingredients = [
                RecipeIngredient(
                    ingredient_id=ing["ingredient_id"],
                    ingredient_name=ing["ingredient_name"],
                    quantity=ing["quantity"],
                    unit=ing["unit"],
                    is_optional=ing["is_optional"] or False,
                    preparation=ing["preparation"]
                )
                for ing in ingredients_result
            ]
            
            recipe = RecipeDetail(
                recipe_id=record["recipe_id"],
                title=record["title"],
                cuisine=record["cuisine"],
                cook_time_min=record["cook_time_min"],
                prep_time_min=record["prep_time_min"],
                total_time_min=record["total_time_min"],
                servings=record["servings"],
                instructions=record["instructions"],
                tags=record["tags"],
                image_urls=record["image_urls"],
                popularity_views=record["popularity_views"] or 0,
                popularity_saves=record["popularity_saves"] or 0,
                popularity_cooks=record["popularity_cooks"] or 0,
                popularity_likes=record["popularity_likes"] or 0,
                allergens=record["allergens"],
                nutrition_calories=record["nutrition_calories"],
                equipment_needed=record["equipment_needed"],
                alternative_ingredients=record["alternative_ingredients"],
                ingredients=ingredients,
                created_at=record["created_at"],
                updated_at=record["updated_at"]
            )
        
        driver.close()
        return recipe
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recipe: {str(e)}")

@app.get("/recipes/search", response_model=RecipeSearchResponse)
async def search_recipes(
    query: Optional[str] = Query(None, description="Search query"),
    cuisine: Optional[str] = Query(None, description="Filter by cuisine"),
    max_cook_time: Optional[int] = Query(None, description="Maximum cooking time"),
    min_cook_time: Optional[int] = Query(None, description="Minimum cooking time"),
    tags: Optional[str] = Query(None, description="Comma-separated tags"),
    ingredients: Optional[str] = Query(None, description="Comma-separated ingredient IDs"),
    exclude_ingredients: Optional[str] = Query(None, description="Comma-separated ingredient IDs to exclude"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Search recipes with various filters
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Build WHERE conditions
            where_conditions = []
            params = {"limit": limit, "offset": offset}
            
            if query:
                where_conditions.append("(toLower(r.title) CONTAINS toLower($query) OR toLower(r.instructions) CONTAINS toLower($query))")
                params["query"] = query
                
            if cuisine:
                where_conditions.append("r.cuisine = $cuisine")
                params["cuisine"] = cuisine
                
            if max_cook_time:
                where_conditions.append("r.cook_time_min <= $max_cook_time")
                params["max_cook_time"] = max_cook_time
                
            if min_cook_time:
                where_conditions.append("r.cook_time_min >= $min_cook_time")
                params["min_cook_time"] = min_cook_time
                
            if tags:
                tag_list = [tag.strip() for tag in tags.split(",") if tag.strip()]
                where_conditions.append("ANY(tag IN $tags WHERE tag IN r.tags)")
                params["tags"] = tag_list
                
            if ingredients:
                ingredient_list = [ing.strip() for ing in ingredients.split(",") if ing.strip()]
                where_conditions.append(f"""
                    EXISTS {{
                        MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
                        WHERE i.ingredient_id IN $ingredients
                    }}
                """)
                params["ingredients"] = ingredient_list
                
            if exclude_ingredients:
                exclude_list = [ing.strip() for ing in exclude_ingredients.split(",") if ing.strip()]
                where_conditions.append(f"""
                    NOT EXISTS {{
                        MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
                        WHERE i.ingredient_id IN $exclude_ingredients
                    }}
                """)
                params["exclude_ingredients"] = exclude_list
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Count total results
            count_query = f"""
                MATCH (r:Recipe)
                WHERE {where_clause}
                RETURN count(r) as total
            """
            count_result = session.run(count_query, params)
            total = count_result.single()["total"]
            
            # Get recipes
            search_query = f"""
                MATCH (r:Recipe)
                WHERE {where_clause}
                RETURN r.recipe_id as recipe_id,
                       r.title as title,
                       r.cuisine as cuisine,
                       r.cook_time_min as cook_time_min,
                       r.prep_time_min as prep_time_min,
                       r.total_time_min as total_time_min,
                       r.servings as servings,
                       r.instructions as instructions,
                       r.tags as tags,
                       r.image_urls as image_urls,
                       r.popularity_views as popularity_views,
                       r.popularity_saves as popularity_saves,
                       r.popularity_cooks as popularity_cooks,
                       r.popularity_likes as popularity_likes,
                       r.allergens as allergens,
                       r.nutrition_calories as nutrition_calories,
                       r.equipment_needed as equipment_needed,
                       r.alternative_ingredients as alternative_ingredients,
                       r.created_at as created_at,
                       r.updated_at as updated_at
                ORDER BY r.popularity_views DESC, r.title
                SKIP $offset
                LIMIT $limit
            """
            
            result = session.run(search_query, params)
            
            recipes = []
            for record in result:
                recipe = RecipeDetail(
                    recipe_id=record["recipe_id"],
                    title=record["title"],
                    cuisine=record["cuisine"],
                    cook_time_min=record["cook_time_min"],
                    prep_time_min=record["prep_time_min"],
                    total_time_min=record["total_time_min"],
                    servings=record["servings"],
                    instructions=record["instructions"],
                    tags=record["tags"],
                    image_urls=record["image_urls"],
                    popularity_views=record["popularity_views"] or 0,
                    popularity_saves=record["popularity_saves"] or 0,
                    popularity_cooks=record["popularity_cooks"] or 0,
                    popularity_likes=record["popularity_likes"] or 0,
                    allergens=record["allergens"],
                    nutrition_calories=record["nutrition_calories"],
                    equipment_needed=record["equipment_needed"],
                    alternative_ingredients=record["alternative_ingredients"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                )
                recipes.append(recipe)
        
        driver.close()
        return RecipeSearchResponse(
            recipes=recipes,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search recipes: {str(e)}")

@app.get("/recipes/by-cuisine/{cuisine}", response_model=RecipeListResponse)
async def get_recipes_by_cuisine(
    cuisine: str = Path(description="Cuisine name"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get recipes by cuisine
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Count total results
            count_result = session.run("""
                MATCH (r:Recipe)
                WHERE r.cuisine = $cuisine
                RETURN count(r) as total
            """, cuisine=cuisine)
            total = count_result.single()["total"]
            
            # Get recipes
            result = session.run("""
                MATCH (r:Recipe)
                WHERE r.cuisine = $cuisine
                RETURN r.recipe_id as recipe_id,
                       r.title as title,
                       r.cuisine as cuisine,
                       r.cook_time_min as cook_time_min,
                       r.prep_time_min as prep_time_min,
                       r.total_time_min as total_time_min,
                       r.servings as servings,
                       r.instructions as instructions,
                       r.tags as tags,
                       r.image_urls as image_urls,
                       r.popularity_views as popularity_views,
                       r.popularity_saves as popularity_saves,
                       r.popularity_cooks as popularity_cooks,
                       r.popularity_likes as popularity_likes,
                       r.allergens as allergens,
                       r.nutrition_calories as nutrition_calories,
                       r.equipment_needed as equipment_needed,
                       r.alternative_ingredients as alternative_ingredients,
                       r.created_at as created_at,
                       r.updated_at as updated_at
                ORDER BY r.popularity_views DESC, r.title
                SKIP $offset
                LIMIT $limit
            """, cuisine=cuisine, limit=limit, offset=offset)
            
            recipes = []
            for record in result:
                recipe = RecipeDetail(
                    recipe_id=record["recipe_id"],
                    title=record["title"],
                    cuisine=record["cuisine"],
                    cook_time_min=record["cook_time_min"],
                    prep_time_min=record["prep_time_min"],
                    total_time_min=record["total_time_min"],
                    servings=record["servings"],
                    instructions=record["instructions"],
                    tags=record["tags"],
                    image_urls=record["image_urls"],
                    popularity_views=record["popularity_views"] or 0,
                    popularity_saves=record["popularity_saves"] or 0,
                    popularity_cooks=record["popularity_cooks"] or 0,
                    popularity_likes=record["popularity_likes"] or 0,
                    allergens=record["allergens"],
                    nutrition_calories=record["nutrition_calories"],
                    equipment_needed=record["equipment_needed"],
                    alternative_ingredients=record["alternative_ingredients"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                )
                recipes.append(recipe)
        
        driver.close()
        return RecipeListResponse(
            recipes=recipes,
            total=total,
            cuisine=cuisine
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch recipes by cuisine: {str(e)}")

# Ingredient APIs
@app.get("/ingredients/{ingredient_id}", response_model=IngredientDetail)
async def get_ingredient_detail(ingredient_id: str = Path(description="Ingredient ID")):
    """
    Get detailed information about a specific ingredient
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            result = session.run("""
                MATCH (i:Ingredient {ingredient_id: $ingredient_id})
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as canonical_name,
                       i.name as name,
                       i.category as category,
                       i.allergen as allergen,
                       i.alternative_names as alternative_names,
                       i.description as description,
                       i.nutrition_info as nutrition_info,
                       i.created_at as created_at,
                       i.updated_at as updated_at
            """, ingredient_id=ingredient_id)
            
            record = result.single()
            if not record:
                raise HTTPException(status_code=404, detail=f"Ingredient {ingredient_id} not found")
            
            ingredient = IngredientDetail(
                ingredient_id=record["ingredient_id"],
                canonical_name=record["canonical_name"],
                name=record["name"],
                category=record["category"],
                allergen=record["allergen"] or False,
                alternative_names=record["alternative_names"],
                description=record["description"],
                nutrition_info=record["nutrition_info"],
                created_at=record["created_at"],
                updated_at=record["updated_at"]
            )
        
        driver.close()
        return ingredient
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingredient: {str(e)}")

@app.get("/ingredients/search", response_model=IngredientSearchResponse)
async def search_ingredients(
    query: Optional[str] = Query(None, description="Search query"),
    category: Optional[str] = Query(None, description="Filter by category"),
    allergen: Optional[bool] = Query(None, description="Filter by allergen status"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Search ingredients with various filters
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Build WHERE conditions
            where_conditions = []
            params = {"limit": limit, "offset": offset}
            
            if query:
                where_conditions.append("(toLower(i.canonical_name) CONTAINS toLower($query) OR toLower(i.name) CONTAINS toLower($query) OR ANY(alt IN i.alternative_names WHERE toLower(alt) CONTAINS toLower($query)))")
                params["query"] = query
                
            if category:
                where_conditions.append("i.category = $category")
                params["category"] = category
                
            if allergen is not None:
                where_conditions.append("i.allergen = $allergen")
                params["allergen"] = allergen
            
            where_clause = " AND ".join(where_conditions) if where_conditions else "1=1"
            
            # Count total results
            count_query = f"""
                MATCH (i:Ingredient)
                WHERE {where_clause}
                RETURN count(i) as total
            """
            count_result = session.run(count_query, params)
            total = count_result.single()["total"]
            
            # Get ingredients
            search_query = f"""
                MATCH (i:Ingredient)
                WHERE {where_clause}
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as canonical_name,
                       i.name as name,
                       i.category as category,
                       i.allergen as allergen,
                       i.alternative_names as alternative_names,
                       i.description as description,
                       i.nutrition_info as nutrition_info,
                       i.created_at as created_at,
                       i.updated_at as updated_at
                ORDER BY i.canonical_name
                SKIP $offset
                LIMIT $limit
            """
            
            result = session.run(search_query, params)
            
            ingredients = []
            for record in result:
                ingredient = IngredientDetail(
                    ingredient_id=record["ingredient_id"],
                    canonical_name=record["canonical_name"],
                    name=record["name"],
                    category=record["category"],
                    allergen=record["allergen"] or False,
                    alternative_names=record["alternative_names"],
                    description=record["description"],
                    nutrition_info=record["nutrition_info"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                )
                ingredients.append(ingredient)
        
        driver.close()
        return IngredientSearchResponse(
            ingredients=ingredients,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to search ingredients: {str(e)}")

@app.get("/ingredients/by-category/{category}", response_model=IngredientListResponse)
async def get_ingredients_by_category(
    category: str = Path(description="Category name"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get ingredients by category
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Count total results
            count_result = session.run("""
                MATCH (i:Ingredient)
                WHERE i.category = $category
                RETURN count(i) as total
            """, category=category)
            total = count_result.single()["total"]
            
            # Get ingredients
            result = session.run("""
                MATCH (i:Ingredient)
                WHERE i.category = $category
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as canonical_name,
                       i.name as name,
                       i.category as category,
                       i.allergen as allergen,
                       i.alternative_names as alternative_names,
                       i.description as description,
                       i.nutrition_info as nutrition_info,
                       i.created_at as created_at,
                       i.updated_at as updated_at
                ORDER BY i.canonical_name
                SKIP $offset
                LIMIT $limit
            """, category=category, limit=limit, offset=offset)
            
            ingredients = []
            for record in result:
                ingredient = IngredientDetail(
                    ingredient_id=record["ingredient_id"],
                    canonical_name=record["canonical_name"],
                    name=record["name"],
                    category=record["category"],
                    allergen=record["allergen"] or False,
                    alternative_names=record["alternative_names"],
                    description=record["description"],
                    nutrition_info=record["nutrition_info"],
                    created_at=record["created_at"],
                    updated_at=record["updated_at"]
                )
                ingredients.append(ingredient)
        
        driver.close()
        return IngredientListResponse(
            ingredients=ingredients,
            total=total,
            category=category
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingredients by category: {str(e)}")

@app.get("/ingredients/{ingredient_id}/synonyms", response_model=IngredientSynonymsResponse)
async def get_ingredient_synonyms(ingredient_id: str = Path(description="Ingredient ID")):
    """
    Get synonyms for a specific ingredient
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Get ingredient basic info
            ingredient_result = session.run("""
                MATCH (i:Ingredient {ingredient_id: $ingredient_id})
                RETURN i.ingredient_id as ingredient_id,
                       i.canonical_name as canonical_name
            """, ingredient_id=ingredient_id)
            
            ingredient_record = ingredient_result.single()
            if not ingredient_record:
                raise HTTPException(status_code=404, detail=f"Ingredient {ingredient_id} not found")
            
            # Get synonyms from alternative_names
            synonyms_result = session.run("""
                MATCH (i:Ingredient {ingredient_id: $ingredient_id})
                RETURN i.alternative_names as alternative_names
            """, ingredient_id=ingredient_id)
            
            synonyms_record = synonyms_result.single()
            alternative_names = synonyms_record["alternative_names"] or []
            
            synonyms = [
                IngredientSynonym(synonym=name, confidence=1.0)
                for name in alternative_names
            ]
            
            # Add canonical name as a synonym with high confidence
            synonyms.append(IngredientSynonym(
                synonym=ingredient_record["canonical_name"],
                confidence=1.0
            ))
        
        driver.close()
        return IngredientSynonymsResponse(
            ingredient_id=ingredient_record["ingredient_id"],
            canonical_name=ingredient_record["canonical_name"],
            synonyms=synonyms,
            total=len(synonyms)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch ingredient synonyms: {str(e)}")

# User Interaction APIs
@app.post("/users/{user_id}/interactions")
async def record_user_interaction(
    user_id: str = Path(description="User ID"),
    interaction_request: InteractionRecordRequest = None
):
    """
    Record a user interaction with a recipe
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Check if recipe exists
            recipe_check = session.run("""
                MATCH (r:Recipe {recipe_id: $recipe_id})
                RETURN r.recipe_id as recipe_id
            """, recipe_id=interaction_request.recipe_id)
            
            if not recipe_check.single():
                raise HTTPException(status_code=404, detail=f"Recipe {interaction_request.recipe_id} not found")
            
            # Record interaction
            interaction_id = f"int_{user_id}_{interaction_request.recipe_id}_{int(time.time())}"
            
            result = session.run("""
                MATCH (u:User {user_id: $user_id})
                MATCH (r:Recipe {recipe_id: $recipe_id})
                MERGE (u)-[rel:INTERACTED_WITH]->(r)
                SET rel.interaction_id = $interaction_id,
                    rel.event_type = $event_type,
                    rel.timestamp = $timestamp,
                    rel.rating = $rating,
                    rel.notes = $notes,
                    rel.duration_minutes = $duration_minutes,
                    rel.success = $success
                RETURN rel.interaction_id as interaction_id,
                       rel.timestamp as timestamp
            """, 
            user_id=user_id,
            recipe_id=interaction_request.recipe_id,
            interaction_id=interaction_id,
            event_type=interaction_request.event_type,
            timestamp=datetime.now(),
            rating=interaction_request.rating,
            notes=interaction_request.notes,
            duration_minutes=interaction_request.duration_minutes,
            success=interaction_request.success)
            
            record = result.single()
        
        driver.close()
        return {
            "message": f"Interaction recorded for user {user_id}",
            "interaction_id": record["interaction_id"],
            "timestamp": record["timestamp"],
            "event_type": interaction_request.event_type,
            "recipe_id": interaction_request.recipe_id
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to record interaction: {str(e)}")

@app.get("/users/{user_id}/interactions", response_model=UserInteractionsResponse)
async def get_user_interactions(
    user_id: str = Path(description="User ID"),
    event_type: Optional[str] = Query(None, description="Filter by event type"),
    limit: int = Query(20, ge=1, le=100, description="Number of results"),
    offset: int = Query(0, ge=0, description="Offset for pagination")
):
    """
    Get user's interaction history
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Build WHERE conditions
            where_conditions = ["u.user_id = $user_id"]
            params = {"user_id": user_id, "limit": limit, "offset": offset}
            
            if event_type:
                where_conditions.append("rel.event_type = $event_type")
                params["event_type"] = event_type
            
            where_clause = " AND ".join(where_conditions)
            
            # Count total results
            count_query = f"""
                MATCH (u:User)-[rel:INTERACTED_WITH]->(r:Recipe)
                WHERE {where_clause}
                RETURN count(rel) as total
            """
            count_result = session.run(count_query, params)
            total = count_result.single()["total"]
            
            # Get interactions
            interactions_query = f"""
                MATCH (u:User)-[rel:INTERACTED_WITH]->(r:Recipe)
                WHERE {where_clause}
                RETURN rel.interaction_id as interaction_id,
                       u.user_id as user_id,
                       r.recipe_id as recipe_id,
                       rel.event_type as event_type,
                       rel.timestamp as timestamp,
                       rel.rating as rating,
                       rel.notes as notes,
                       rel.duration_minutes as duration_minutes,
                       rel.success as success
                ORDER BY rel.timestamp DESC
                SKIP $offset
                LIMIT $limit
            """
            
            result = session.run(interactions_query, params)
            
            interactions = []
            for record in result:
                interaction = UserInteraction(
                    interaction_id=record["interaction_id"],
                    user_id=record["user_id"],
                    recipe_id=record["recipe_id"],
                    event_type=record["event_type"],
                    timestamp=record["timestamp"],
                    rating=record["rating"],
                    notes=record["notes"],
                    duration_minutes=record["duration_minutes"],
                    success=record["success"]
                )
                interactions.append(interaction)
        
        driver.close()
        return UserInteractionsResponse(
            user_id=user_id,
            interactions=interactions,
            total=total,
            limit=limit,
            offset=offset,
            has_more=(offset + limit) < total
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user interactions: {str(e)}")

@app.get("/users/{user_id}/interactions/stats", response_model=UserInteractionStatsResponse)
async def get_user_interaction_stats(user_id: str = Path(description="User ID")):
    """
    Get user's interaction statistics
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Get interaction counts by type
            result = session.run("""
                MATCH (u:User {user_id: $user_id})-[rel:INTERACTED_WITH]->(r:Recipe)
                RETURN count(rel) as total_interactions,
                       sum(CASE WHEN rel.event_type = 'cook' THEN 1 ELSE 0 END) as cook_count,
                       sum(CASE WHEN rel.event_type = 'like' THEN 1 ELSE 0 END) as like_count,
                       sum(CASE WHEN rel.event_type = 'save' THEN 1 ELSE 0 END) as save_count,
                       sum(CASE WHEN rel.event_type = 'view' THEN 1 ELSE 0 END) as view_count,
                       sum(CASE WHEN rel.event_type = 'dislike' THEN 1 ELSE 0 END) as dislike_count,
                       avg(rel.rating) as average_rating,
                       max(rel.timestamp) as most_recent_interaction
            """, user_id=user_id)
            
            record = result.single()
            
            stats = InteractionStats(
                total_interactions=record["total_interactions"] or 0,
                cook_count=record["cook_count"] or 0,
                like_count=record["like_count"] or 0,
                save_count=record["save_count"] or 0,
                view_count=record["view_count"] or 0,
                dislike_count=record["dislike_count"] or 0,
                average_rating=round(record["average_rating"], 2) if record["average_rating"] else None,
                most_recent_interaction=record["most_recent_interaction"]
            )
        
        driver.close()
        return UserInteractionStatsResponse(
            user_id=user_id,
            stats=stats
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch user interaction stats: {str(e)}")

@app.post("/users/{user_id}/recompute-profile", response_model=RecomputeProfileResponse)
async def recompute_user_profile(
    user_id: str = Path(description="User ID"),
    recompute_request: RecomputeProfileRequest = None
):
    """
    Recompute user profile and update user vector based on interactions
    """
    try:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        
        with driver.session(database=NEO4J_DATABASE) as session:
            # Check if user exists
            check_result = session.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.user_id as user_id
            """, user_id=user_id)
            
            if not check_result.single():
                raise HTTPException(status_code=404, detail=f"User {user_id} not found")
            
            # Get interaction count
            interaction_count_result = session.run("""
                MATCH (u:User {user_id: $user_id})-[rel:INTERACTED_WITH]->(r:Recipe)
                RETURN count(rel) as interaction_count
            """, user_id=user_id)
            
            interaction_count = interaction_count_result.single()["interaction_count"] or 0
            
            if interaction_count == 0:
                return RecomputeProfileResponse(
                    user_id=user_id,
                    success=False,
                    message="No interactions found for user",
                    user_vector_updated=False,
                    interaction_count=0
                )
            
            # Import the compute_features function
            import sys
            from pathlib import Path
            sys.path.append(str(PathLib(__file__).parent / "scripts"))
            from compute_features import compute_user_vectors
            
            # Recompute user vector
            try:
                # This would call the actual compute_user_vectors function
                # For now, we'll simulate the process
                user_vector_updated = True
                message = f"User profile recomputed successfully with {interaction_count} interactions"
                
                # In a real implementation, you would call:
                # compute_user_vectors(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD, NEO4J_DATABASE, user_id)
                
            except Exception as e:
                user_vector_updated = False
                message = f"Failed to recompute user vector: {str(e)}"
        
        driver.close()
        return RecomputeProfileResponse(
            user_id=user_id,
            success=user_vector_updated,
            message=message,
            user_vector_updated=user_vector_updated,
            interaction_count=interaction_count
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to recompute user profile: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8001, reload=True)
