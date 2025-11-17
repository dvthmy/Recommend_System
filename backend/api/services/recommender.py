from typing import List, Optional, Dict, Any
from ..config import settings
from ..utils.logger import logger

# We try to import your existing scripts.recommend.recommend
try:
    from scripts.recommend_graph import recommend as _recommend_impl  # type: ignore
except Exception as e:
    _recommend_impl = None


def recommend(
    user_id: Optional[str],
    ingredient_ids: Optional[List[str]],
    limit: int = 10,
    max_cook_time: Optional[int] = None,
) -> List[Dict[str, Any]]:
    """Facade that calls your recommend() in scripts or a minimal Cypher fallback."""
    if _recommend_impl:
        logger.info("Calling scripts.recommend.recommend(...)")
        return _recommend_impl(
            uri=settings.NEO4J_URI,
            user=settings.NEO4J_USER,
            password=settings.NEO4J_PASSWORD,
            database=settings.NEO4J_DATABASE,
            user_id=user_id,
            ingredient_ids=ingredient_ids,
            cuisine=None,
            max_cook_time=max_cook_time,
            limit_candidates=limit * 5,
            limit_results=limit,
            w_ing=1.0, w_text=1.0, w_pop=1.0, w_cf=1.0,
            norm="rank", pop_half_life=60.0,
            diversify=False, mmr_lambda=0.7,
        )

    # --- Minimal fallback (very simple) ---
    from ..db import get_session
    q = """
    MATCH (r:Recipe)
    WHERE ($max_cook_time IS NULL OR r.cook_time_min <= $max_cook_time)
    WITH r
    OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
    WITH r, collect(i.ingredient_id) AS all_ing
    WITH r,
         CASE WHEN $ingredient_ids IS NULL OR size($ingredient_ids)=0 THEN 0.0
              ELSE toFloat(size([x IN all_ing WHERE x IN $ingredient_ids])) /
                   toFloat(size(all_ing) + size($ingredient_ids) - size([x IN all_ing WHERE x IN $ingredient_ids]))
         END AS jaccard
    RETURN r.recipe_id AS recipe_id, r.title AS title, r.cuisine AS cuisine,
           r.cook_time_min AS cook_time_min, jaccard AS score,
           {jaccard: jaccard} AS scores, r.image_urls AS image_urls
    ORDER BY score DESC, r.popularity_views DESC
    LIMIT $limit
    """
    with get_session() as s:
        recs = [dict(r) for r in s.run(q, limit=limit, ingredient_ids=ingredient_ids, max_cook_time=max_cook_time)]
        return recs