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
           r.popularity_views AS popularity_views, r.servings AS servings,
           r.rating_value AS rating_value, r.rating_count AS rating_count
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
           r.source_url AS url,
           r.description AS description,
           r.image_urls AS image_urls,
           r.cuisine AS cuisine,
           r.tags AS tags,
           r.instructions AS instructions,
           r.ingredient AS ingredient,
           r.prep_time_min AS prep_time_min,
           r.cook_time_min AS cook_time_min,
           r.total_time_min AS total_time_min,
           r.servings AS servings,
           r.yield AS yield,
           r.rating_value AS rating_value,
           r.rating_count AS rating_count,
           r.review_count AS review_count,
           r.nutrition_calories AS nutrition_calories,
           r.nutrition_protein AS nutrition_protein,
           r.nutrition_total_fat AS nutrition_total_fat,
           r.nutrition_saturated_fat AS nutrition_saturated_fat,
           r.nutrition_total_carbohydrate AS nutrition_total_carbohydrate,
           r.nutrition_dietary_fiber AS nutrition_dietary_fiber,
           r.nutrition_total_sugars AS nutrition_total_sugars,
           r.nutrition_sodium AS nutrition_sodium,
           r.nutrition_cholesterol AS nutrition_cholesterol,
           r.nutrition_vitamin_c AS nutrition_vitamin_c,
           r.nutrition_calcium AS nutrition_calcium,
           r.nutrition_iron AS nutrition_iron,
           r.nutrition_potassium AS nutrition_potassium
    """

    with get_session() as s:
        recipe = s.run(q_recipe, id=recipe_id).single()
        if not recipe:
            raise HTTPException(status_code=404, detail="Recipe not found")

        item = dict(recipe)
        
        # Parse ingredient field (JSON array or Python-style list string from CSV)
        # Formats: 
        # - JSON: ["59.1ml Lemoncello", "29.6ml Prosecco"]
        # - Python: ['5 c filtered water', '1/2 head cabbage']
        raw_ingredient = item.get("ingredient")
        
        if raw_ingredient:
            if isinstance(raw_ingredient, list):
                # Already parsed as list by Neo4j driver
                item["ingredients_list"] = raw_ingredient
                print(f"✅ Recipe {recipe_id}: Already list with {len(raw_ingredient)} items")
            elif isinstance(raw_ingredient, str):
                import json
                import ast
                
                # Try JSON parsing first
                try:
                    parsed = json.loads(raw_ingredient)
                    if isinstance(parsed, list):
                        item["ingredients_list"] = parsed
                        print(f"✅ Recipe {recipe_id}: JSON parsed {len(parsed)} ingredients")
                    else:
                        item["ingredients_list"] = [str(parsed)]
                except json.JSONDecodeError:
                    # Try Python literal_eval for Python-style lists: ['item1', 'item2']
                    try:
                        parsed = ast.literal_eval(raw_ingredient)
                        if isinstance(parsed, list):
                            item["ingredients_list"] = [str(i) for i in parsed]
                            print(f"✅ Recipe {recipe_id}: Python-style parsed {len(parsed)} ingredients")
                        else:
                            item["ingredients_list"] = [str(parsed)]
                    except (ValueError, SyntaxError) as e:
                        # If all parsing fails, treat as single item
                        print(f"⚠️ Recipe {recipe_id}: Failed to parse, using raw string")
                        print(f"   Raw: {raw_ingredient[:100]}")
                        item["ingredients_list"] = [raw_ingredient]
            else:
                item["ingredients_list"] = []
        else:
            item["ingredients_list"] = []
        
        # Remove the raw 'ingredient' field from response
        item.pop("ingredient", None)
        
        return item

