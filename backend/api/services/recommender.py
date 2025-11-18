from typing import List, Optional, Dict, Any
from ..config import settings
from ..utils.logger import logger
import sys
from pathlib import Path

# Add backend directory to path to import scripts
backend_dir = Path(__file__).parent.parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

# Import GraphHybridRecommender from recommend_graph.py
try:
    from scripts.recommend_graph import GraphHybridRecommender
    _recommender_class = GraphHybridRecommender
except Exception as e:
    logger.warning(f"Could not import GraphHybridRecommender: {e}")
    _recommender_class = None


def recommend(
    user_id: Optional[str],
    ingredient_ids: Optional[List[str]],
    limit: int = 10,
    max_cook_time: Optional[int] = None,
    recipe_category: Optional[str] = None,
    preferred_cuisines: Optional[List[str]] = None,
    ingredient_names: Optional[List[str]] = None,
    min_match_ratio: float = 0.6,
) -> List[Dict[str, Any]]:
    """
    Facade that calls GraphHybridRecommender from recommend_graph.py.
    
    Args match the signature in recommend_graph.py:
    - user_id: User ID (optional)
    - ingredient_ids: List of ingredient IDs (optional)
    - ingredient_names: List of ingredient names/text (optional, will be mapped to IDs)
    - limit: Maximum number of results
    - min_match_ratio: Minimum Jaccard match ratio
    - max_cook_time: Maximum cooking time in minutes
    - recipe_category: Filter by recipe category/meal type
    - preferred_cuisines: List of preferred cuisines for priority ranking
    """
    if _recommender_class:
        try:
            print(f"🔧 Creating GraphHybridRecommender with:", file=sys.stderr)
            print(f"  - URI: {settings.NEO4J_URI}", file=sys.stderr)
            print(f"  - Database: {settings.NEO4J_DATABASE}", file=sys.stderr)
            print(f"  - User: {settings.NEO4J_USER}", file=sys.stderr)
            
            recommender = _recommender_class(
                uri=settings.NEO4J_URI,
                username=settings.NEO4J_USER,
                password=settings.NEO4J_PASSWORD,
                database=settings.NEO4J_DATABASE
            )
            
            print(f"✅ GraphHybridRecommender created successfully", file=sys.stderr)
            print(f"🔍 Calling recommend with:", file=sys.stderr)
            print(f"  - user_id: {user_id}", file=sys.stderr)
            print(f"  - ingredient_ids: {ingredient_ids}", file=sys.stderr)
            print(f"  - ingredient_names: {ingredient_names}", file=sys.stderr)
            print(f"  - limit: {limit}", file=sys.stderr)
            print(f"  - min_match_ratio: {min_match_ratio}", file=sys.stderr)
            print(f"  - max_cook_time: {max_cook_time}", file=sys.stderr)
            
            results = recommender.recommend(
                user_id=user_id,
                ingredient_ids=ingredient_ids,
                ingredient_names=ingredient_names,
                limit=limit,
                min_match_ratio=min_match_ratio,
                max_cook_time=max_cook_time,
                recipe_category=recipe_category,
                preferred_cuisines=preferred_cuisines
            )
            
            print(f"✅ recommend() returned {len(results)} results", file=sys.stderr)
            recommender.close()
            return results
        except Exception as e:
            import traceback
            error_msg = f"Error in GraphHybridRecommender: {e}"
            print(f"❌ {error_msg}", file=sys.stderr)
            print(f"❌ Traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            logger.error(error_msg, exc_info=True)
            # Fall through to fallback

    # --- Minimal fallback (very simple) ---
    logger.warning("Using fallback recommendation query")
    from ..db import get_session
    q = """
    MATCH (r:Recipe)
    WHERE ($max_cook_time IS NULL OR 
           coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
    AND ($recipe_category IS NULL OR 
         r.recipe_category = $recipe_category OR
         toLower(r.recipe_category) = toLower($recipe_category) OR
         toLower(r.recipe_category) CONTAINS toLower($recipe_category))
    WITH r
    OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
    WITH r, collect(i.ingredient_id) AS all_ing
    WITH r, all_ing,
         CASE WHEN $ingredient_ids IS NULL OR size($ingredient_ids)=0 THEN 0.0
              ELSE toFloat(size([x IN all_ing WHERE x IN $ingredient_ids])) /
                   toFloat(size(all_ing) + size($ingredient_ids) - size([x IN all_ing WHERE x IN $ingredient_ids]))
         END AS jaccard,
         [x IN all_ing WHERE x IN $ingredient_ids] AS matched_ing,
         [x IN all_ing WHERE NOT x IN $ingredient_ids] AS missing_ing,
         size(all_ing) AS ing_count
    WHERE 
        // Absolute minimum: must match at least 1 ingredient (or 2 if user provided 4+ ingredients)
        size(matched_ing) >= CASE WHEN size($ingredient_ids) >= 4 THEN 2 ELSE 1 END
        AND (
            // Relative minimum: match ratio threshold that adapts to recipe size
            CASE
                WHEN ing_count < 5 THEN jaccard >= $min_match * 0.6
                WHEN ing_count >= 5 AND ing_count < 10 THEN jaccard >= $min_match * 0.4
                WHEN ing_count >= 10 AND ing_count < 15 THEN jaccard >= $min_match * 0.3
                ELSE jaccard >= $min_match * 0.2
            END
        )
    // Collect full recipe ingredients with details
    OPTIONAL MATCH (r)-[rel:HAS_INGREDIENT]->(ing:Ingredient)
    WITH r, matched_ing, missing_ing, jaccard,
         collect({
            ingredient_id: ing.ingredient_id,
            ingredient_name: coalesce(ing.name, ing.canonical_name),
            base: coalesce(ing.base, ing.canonical_name),
            category: ing.category
        }) AS ingredients
    RETURN r.recipe_id AS recipe_id, 
           r.title AS title, 
           coalesce(r.cuisine, []) AS cuisine,
           coalesce(r.tags, []) AS tags,
           r.recipe_category AS recipe_category,
           round(jaccard * 100, 1) AS match_percent,
           r.cook_time_min AS cook_time_min,
           r.prep_time_min AS prep_time_min,
           r.total_time_min AS total_time_min,
           r.servings AS servings,
           r.yield AS yield,
           head(coalesce(r.image_urls, [])) AS image,
           matched_ing,
           missing_ing,
           ingredients,
           [] AS reasoning
    ORDER BY jaccard DESC, r.popularity_views DESC
    LIMIT $limit
    """
    with get_session() as s:
        recs = [dict(r) for r in s.run(
            q, 
            limit=limit, 
            ingredient_ids=ingredient_ids or [], 
            max_cook_time=max_cook_time,
            recipe_category=recipe_category,
            min_match=min_match_ratio
        )]
        return recs