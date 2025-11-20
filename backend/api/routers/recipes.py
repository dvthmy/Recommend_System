from fastapi import APIRouter, HTTPException, Query
from typing import Optional
from ..db import get_session

router = APIRouter(prefix="/recipes", tags=["Recipes"])

# ========================================
# 🔍 SEARCH RECIPE LIST
# ========================================
@router.get("/search")
async def search_recipes(
    query: Optional[str] = Query(None),
    cuisine: Optional[str] = Query(None),
    max_cook_time: Optional[int] = Query(None),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    where = ["1=1"]
    params = {"limit": limit, "offset": offset}
    if query:
        where.append("(toLower(r.title) CONTAINS toLower($q) OR toLower(r.instructions) CONTAINS toLower($q))")
        params["q"] = query
    if cuisine:
        # Handle cuisine as array (case-insensitive matching)
        # Check if cuisine matches any element in the cuisine array
        where.append("r.cuisine IS NOT NULL AND any(c IN r.cuisine WHERE c IS NOT NULL AND toLower(toString(c)) = toLower($c))")
        params["c"] = cuisine
    if max_cook_time is not None:
        where.append("r.cook_time_min <= $m"); params["m"] = max_cook_time
    wc = " AND ".join(where)

    count_q = f"MATCH (r:Recipe) WHERE {wc} RETURN count(r) AS total"
    list_q = f"""
    MATCH (r:Recipe) WHERE {wc}
    RETURN r.recipe_id AS recipe_id, r.title AS title, r.cuisine AS cuisine,
           r.cook_time_min AS cook_time_min, r.tags AS tags, r.image_urls AS image_urls,
           r.popularity_views AS popularity_views
    ORDER BY r.popularity_views DESC, r.title
    SKIP $offset LIMIT $limit
    """
    with get_session() as s:
        total = s.run(count_q, **params).single()["total"]
        items = [dict(r) for r in s.run(list_q, **params)]
        return {"recipes": items, "total": total, "limit": limit, "offset": offset, "has_more": offset+limit < total}


# ========================================
# 🍲 GET RECIPE DETAIL
# ========================================
@router.get("/{recipe_id}")
async def get_recipe(recipe_id: str):
    q_recipe = """
    MATCH (r:Recipe {recipe_id:$id})
    RETURN r.recipe_id AS recipe_id,
           r.title AS title,
           r.description AS description,
           
           r.image_urls AS image_urls,
           r.cuisine AS cuisine,
           r.tags AS tags,
           r.instructions AS instructions,
           r.total_time_min AS total_time_min,
           r.cook_time_min AS cook_time_min,
           r.servings AS servings
    """
    
    q_ingredients = """
    MATCH (r:Recipe {recipe_id:$id})-[rel:HAS_INGREDIENT]->(i:Ingredient)
    RETURN 
        i.ingredient_id AS ingredient_id,
        coalesce(i.name, i.canonical_name) AS ingredient_name,
        coalesce(rel.qty, '') AS quantity,
        coalesce(rel.unit, '') AS unit,
        coalesce(rel.optional, false) AS is_optional,
        coalesce(rel.prep, '') AS preparation
    ORDER BY ingredient_name
    """

    with get_session() as s:
        recipe = s.run(q_recipe, id=recipe_id).single()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        ingredients = [dict(x) for x in s.run(q_ingredients, id=recipe_id)]
        item = dict(recipe)
        item["ingredients"] = ingredients
        return item

