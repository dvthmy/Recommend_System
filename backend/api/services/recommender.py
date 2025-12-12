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
_recommender_class = None
_import_error = None
try:
    print(f"🔍 [recommender.py] Attempting to import GraphHybridRecommender from scripts.recommend_graph", file=sys.stderr)
    print(f"   Backend dir: {backend_dir}", file=sys.stderr)
    print(f"   Scripts path: {backend_dir / 'scripts'}", file=sys.stderr)
    print(f"   recommend_graph.py exists: {(backend_dir / 'scripts' / 'recommend_graph.py').exists()}", file=sys.stderr)
    
    from scripts.recommend_graph import GraphHybridRecommender
    _recommender_class = GraphHybridRecommender
    print(f"✅ [recommender.py] Successfully imported GraphHybridRecommender", file=sys.stderr)
except ImportError as e:
    _import_error = str(e)
    logger.warning(f"[recommender.py] Could not import GraphHybridRecommender (ImportError): {e}")
    print(f"❌ [recommender.py] ImportError: Failed to import GraphHybridRecommender: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    _recommender_class = None
except Exception as e:
    _import_error = str(e)
    logger.warning(f"[recommender.py] Could not import GraphHybridRecommender (Exception): {e}")
    print(f"❌ [recommender.py] Exception: Failed to import GraphHybridRecommender: {e}", file=sys.stderr)
    import traceback
    traceback.print_exc(file=sys.stderr)
    _recommender_class = None


def _filter_allergic_recipes(user_id: Optional[str], recs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Post-filter recommendations to remove recipes that contain ingredients
    the user is allergic to.

    This is a safety net on top of any filtering done inside the recommender
    graph logic. It only runs when user_id is provided.
    """
    if not user_id or not recs:
        return recs

    try:
        from ..db import get_session

        recipe_ids = [r.get("recipe_id") for r in recs if r.get("recipe_id")]
        if not recipe_ids:
            return recs

        with get_session() as s:
            # Get all allergic ingredient_ids for this user
            allergic_ids = [
                row["ingredient_id"]
                for row in s.run(
                    """
                    MATCH (u:User {user_id:$uid})-[:ALLERGIC_TO]->(i:Ingredient)
                    RETURN i.ingredient_id AS ingredient_id
                    """,
                    uid=user_id,
                )
                if row.get("ingredient_id")
            ]

            if not allergic_ids:
                return recs

            # Find recipes that contain any allergic ingredient
            rows = s.run(
                """
                MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
                WHERE r.recipe_id IN $recipe_ids AND i.ingredient_id IN $allergic_ids
                RETURN DISTINCT r.recipe_id AS recipe_id
                """,
                recipe_ids=recipe_ids,
                allergic_ids=allergic_ids,
            )
            banned_ids = {row["recipe_id"] for row in rows if row.get("recipe_id")}

        if not banned_ids:
            return recs

        filtered = [r for r in recs if r.get("recipe_id") not in banned_ids]
        logger.info(
            "Allergy filter: removed %d recipes (remaining %d) for user %s",
            len(recs) - len(filtered),
            len(filtered),
            user_id,
        )
        return filtered
    except Exception as e:
        logger.error("Allergy post-filter failed: %s", e, exc_info=True)
        # Fail-open: if filtering fails, return original recs rather than crashing
        return recs


def recommend(
    user_id: Optional[str],
    ingredient_ids: Optional[List[str]],
    limit: int = 20,
    max_cook_time: Optional[int] = None,
    recipe_category: Optional[str] = None,
    preferred_cuisines: Optional[List[str]] = None,
    ingredient_names: Optional[List[str]] = None,
    min_match_ratio: float = 0.3,
    max_cuisine_priority_1_ratio: float = 0.6,  # Maximum ratio of recipes with cuisine_priority=1 (default: 60%)
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
    logger.info(f"🔍 recommend() called with: user_id={user_id}, ingredient_ids_count={len(ingredient_ids) if ingredient_ids else 0}, ingredient_names_count={len(ingredient_names) if ingredient_names else 0}, limit={limit}, preferred_cuisines={preferred_cuisines}")
    print(f"🔍 recommend() called with:", file=sys.stderr)
    print(f"  - user_id: {user_id}", file=sys.stderr)
    print(f"  - ingredient_ids: {ingredient_ids} (count: {len(ingredient_ids) if ingredient_ids else 0})", file=sys.stderr)
    print(f"  - ingredient_names: {ingredient_names} (count: {len(ingredient_names) if ingredient_names else 0})", file=sys.stderr)
    print(f"  - limit: {limit}", file=sys.stderr)
    print(f"  - preferred_cuisines: {preferred_cuisines}", file=sys.stderr)
    print(f"  - _recommender_class available: {_recommender_class is not None}", file=sys.stderr)
    
    if _recommender_class:
        logger.info("✅ GraphHybridRecommender is available, using it")
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
            print(f"  - recipe_category: {recipe_category}", file=sys.stderr)
            print(f"  - preferred_cuisines: {preferred_cuisines}", file=sys.stderr)
            
            results = recommender.recommend(
                user_id=user_id,
                ingredient_ids=ingredient_ids,
                ingredient_names=ingredient_names,
                limit=limit,
                min_match_ratio=min_match_ratio,
                max_cook_time=max_cook_time,
                recipe_category=recipe_category,
                max_cuisine_priority_1_ratio=max_cuisine_priority_1_ratio,
                preferred_cuisines=preferred_cuisines,
            )

            print(f"✅ recommend() returned {len(results)} results", file=sys.stderr)
            if results and len(results) > 0:
                first_few = results[:3]
                titles = [r.get('title', 'N/A') for r in first_few]
                cuisines = [r.get('cuisine', []) for r in first_few]
                match_percents = [r.get('match_percent', 'N/A') for r in first_few]
                print(f"📋 First {len(titles)} recipes from GraphHybridRecommender:", file=sys.stderr)
                for i, (title, cuisine, match) in enumerate(zip(titles, cuisines, match_percents), 1):
                    print(f"  {i}. {title} (cuisine: {cuisine}, match: {match}%)", file=sys.stderr)
            
            recommender.close()
            # Safety allergy filter in case graph logic didn't exclude them
            filtered_results = _filter_allergic_recipes(user_id, results)
            if not filtered_results:
                print(f"⚠️ All recipes filtered out by allergy check or empty results", file=sys.stderr)
            return filtered_results or []
        except Exception as e:
            import traceback
            error_msg = f"Error in GraphHybridRecommender: {e}"
            print(f"❌ {error_msg}", file=sys.stderr)
            print(f"❌ Traceback:", file=sys.stderr)
            traceback.print_exc(file=sys.stderr)
            logger.error(error_msg, exc_info=True)
            # Fall through to fallback

    # --- Minimal fallback (very simple, runs when GraphHybridRecommender fails) ---
    logger.error("⚠️ WARNING: Using fallback recommendation query instead of GraphHybridRecommender")
    logger.error(f"   This means GraphHybridRecommender failed or is not available")
    logger.error(f"   Request params: user_id={user_id}, ingredient_ids={ingredient_ids}, ingredient_names={ingredient_names}")
    print("⚠️ WARNING: Using fallback recommendation query instead of GraphHybridRecommender", file=sys.stderr)
    print(f"   This means GraphHybridRecommender failed or is not available", file=sys.stderr)
    print(f"   Fallback query may not use all user preferences correctly", file=sys.stderr)
    print(f"   Request params: user_id={user_id}, ingredient_ids={ingredient_ids}, ingredient_names={ingredient_names}", file=sys.stderr)
    from ..db import get_session

    # If we don't have ingredient_ids but have ingredient_names,
    # try to map names -> IDs with simple exact / canonical_name matching.
    if (not ingredient_ids or len(ingredient_ids) == 0) and ingredient_names:
        mapped_ids: List[str] = []
        with get_session() as s:
            for name in ingredient_names:
                if not name:
                    continue
                row = s.run(
                    """
                    MATCH (i:Ingredient)
                    WHERE toLower(i.canonical_name) = toLower($name)
                       OR toLower(i.name) = toLower($name)
                    RETURN i.ingredient_id AS id
                    LIMIT 1
                    """,
                    name=name.strip(),
                ).single()
                if row and row.get("id"):
                    mapped_ids.append(row["id"])
        if mapped_ids:
            ingredient_ids = mapped_ids
    # Check if we have ingredients or user_id
    has_ingredients = ingredient_ids and len(ingredient_ids) > 0
    has_user = user_id is not None
    
    if not has_ingredients and not has_user:
        # No ingredients and no user_id: return popular recipes only
        q = """
        MATCH (r:Recipe)
        WHERE ($max_cook_time IS NULL OR 
               coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
        AND ($recipe_category IS NULL OR 
             r.recipe_category = $recipe_category OR
             toLower(r.recipe_category) = toLower($recipe_category) OR
             toLower(r.recipe_category) CONTAINS toLower($recipe_category))
        
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             sum(CASE WHEN iv.event_type = 'like' THEN 1 ELSE 0 END) AS like_count
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, avg_rating, like_count,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             collect(ing.ingredient_id) AS all_ing
        RETURN r.recipe_id AS recipe_id, 
               r.title AS title, 
               coalesce(r.cuisine, []) AS cuisine,
               coalesce(r.tags, []) AS tags,
               r.recipe_category AS recipe_category,
               CASE 
                   WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                   WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                   WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                   WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                   ELSE 'Dinner'
               END AS meal,
               0.0 AS match_percent,
               r.cook_time_min AS cook_time_min,
               r.prep_time_min AS prep_time_min,
               r.total_time_min AS total_time_min,
               r.servings AS servings,
               r.yield AS yield,
               head(coalesce(r.image_urls, [])) AS image,
               [] AS matched_ing,
               all_ing AS missing_ing,
               ingredients,
               [] AS reasoning
        ORDER BY avg_rating DESC, like_count DESC
        LIMIT $limit
        """
    elif not has_ingredients and has_user:
        # No ingredients but has user_id: use user profile and popularity
        # IMPORTANT: Use preferred_cuisines from request if provided, otherwise use user's FAVORS_CUISINE relationships
        q = """
        MATCH (r:Recipe)
        OPTIONAL MATCH (u:User {user_id:$user_id})-[:ALLERGIC_TO]->(a:Ingredient)
        WITH r, collect(DISTINCT a.ingredient_id) AS allergic_ids
        WHERE ($max_cook_time IS NULL OR 
               coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
        AND ($recipe_category IS NULL OR 
             r.recipe_category = $recipe_category OR
             toLower(r.recipe_category) = toLower($recipe_category) OR
             toLower(r.recipe_category) CONTAINS toLower($recipe_category))
        
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH r, allergic_ids, collect(i.ingredient_id) AS all_ing
        WHERE (allergic_ids IS NULL OR size(allergic_ids) = 0 OR size([ing IN all_ing WHERE ing IN allergic_ids]) = 0)
        
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        // Get user's favorite cuisines from FAVORS_CUISINE relationships
        // IMPORTANT: Use preferred_cuisines from request FIRST (more reliable for new users)
        // Only fallback to FAVORS_CUISINE if preferred_cuisines is not provided
        OPTIONAL MATCH (u:User {user_id:$user_id})-[:FAVORS_CUISINE]->(c:Cuisine)
        WITH r, all_ing,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             sum(CASE WHEN iv.event_type = 'like' THEN 1 ELSE 0 END) AS like_count,
             collect(DISTINCT c.name) AS user_fav_cuisines_from_db
        // IMPORTANT: Always prioritize preferred_cuisines from request over FAVORS_CUISINE
        // This is critical for new users who just completed onboarding
        // because FAVORS_CUISINE relationships might not be immediately queryable
        WITH r, all_ing, avg_rating, like_count, user_fav_cuisines_from_db,
             CASE 
                 WHEN $preferred_cuisines IS NOT NULL AND size($preferred_cuisines) > 0 
                 THEN $preferred_cuisines
                 WHEN user_fav_cuisines_from_db IS NOT NULL AND size(user_fav_cuisines_from_db) > 0
                 THEN user_fav_cuisines_from_db
                 ELSE []
             END AS target_cuisines
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, all_ing, avg_rating, like_count, target_cuisines,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             CASE 
                 WHEN size(target_cuisines) = 0 THEN 0.0
                 ELSE toFloat(size([c IN coalesce(r.cuisine, []) WHERE c IS NOT NULL AND 
                     any(tc IN target_cuisines WHERE toLower(toString(c)) = toLower(toString(tc)))])) / 
                      toFloat(size(target_cuisines))
             END AS cuisine_match
        // IMPORTANT: Don't filter by cuisine_match - return all recipes
        // min_match_ratio = 0 means we should return recipes even with 0% cuisine match
        // Just prioritize recipes that match preferred cuisines in ORDER BY
        RETURN r.recipe_id AS recipe_id, 
               r.title AS title, 
               coalesce(r.cuisine, []) AS cuisine,
               coalesce(r.tags, []) AS tags,
               r.recipe_category AS recipe_category,
               CASE 
                   WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                   WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                   WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                   WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                   ELSE 'Dinner'
               END AS meal,
               round(cuisine_match * 100, 1) AS match_percent,
               r.cook_time_min AS cook_time_min,
               r.prep_time_min AS prep_time_min,
               r.total_time_min AS total_time_min,
               r.servings AS servings,
               r.yield AS yield,
               head(coalesce(r.image_urls, [])) AS image,
               [] AS matched_ing,
               all_ing AS missing_ing,
               ingredients,
               [] AS reasoning
        ORDER BY 
            // Prioritize recipes that match preferred cuisines, but still return others if no match
            CASE WHEN cuisine_match > 0 THEN 0 ELSE 1 END,
            cuisine_match DESC, 
            avg_rating DESC, 
            like_count DESC
        LIMIT $limit
        """
    else:
        # Has ingredients: original query
        q = """
        // Base recipe match
        MATCH (r:Recipe)
        // Optional: load user allergies (if user_id provided)
        OPTIONAL MATCH (u:User {user_id:$user_id})-[:ALLERGIC_TO]->(a:Ingredient)
        WITH r, collect(DISTINCT a.ingredient_id) AS allergic_ids
        WHERE ($max_cook_time IS NULL OR 
               coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
        AND ($recipe_category IS NULL OR 
             r.recipe_category = $recipe_category OR
             toLower(r.recipe_category) = toLower($recipe_category) OR
             toLower(r.recipe_category) CONTAINS toLower($recipe_category))
        // Collect recipe ingredients
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH r, allergic_ids, collect(i.ingredient_id) AS all_ing
        WITH r, all_ing,
             CASE WHEN $ingredient_ids IS NULL OR size($ingredient_ids)=0 THEN 0.0
                  ELSE toFloat(size([x IN all_ing WHERE x IN $ingredient_ids])) /
                       toFloat(size(all_ing) + size($ingredient_ids) - size([x IN all_ing WHERE x IN $ingredient_ids]))
             END AS jaccard,
             [x IN all_ing WHERE x IN $ingredient_ids] AS matched_ing,
             [x IN all_ing WHERE NOT x IN $ingredient_ids] AS missing_ing,
             size(all_ing) AS ing_count
        WHERE 
            // ❌ Exclude recipes that contain allergic ingredients for this user (if any)
            (
              allergic_ids IS NULL OR 
              size(allergic_ids) = 0 OR 
              size([ing IN all_ing WHERE ing IN allergic_ids]) = 0
            )
            AND
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
               // Normalize meal type to 4 standard categories: Breakfast, Lunch, Dinner, Snack
               CASE 
                   WHEN r.recipe_category IS NULL OR r.recipe_category = '' THEN 'Dinner'  // Default
                   WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR 
                        toLower(r.recipe_category) CONTAINS 'brunch' OR 
                        toLower(r.recipe_category) CONTAINS 'tea time' THEN 'Breakfast'
                   WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                   WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                   WHEN toLower(r.recipe_category) CONTAINS 'snack' OR 
                        toLower(r.recipe_category) CONTAINS 'appetizer' OR 
                        toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                   ELSE 'Dinner'  // Default fallback
               END AS meal,
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
        # Prepare parameters for query
        params = {
            "limit": limit,
            "ingredient_ids": ingredient_ids or [],
            "max_cook_time": max_cook_time,
            "recipe_category": recipe_category,
            "min_match": min_match_ratio,
            "user_id": user_id,
            "preferred_cuisines": preferred_cuisines or []
        }
        # Log query parameters for debugging
        print(f"🔍 Fallback query parameters:", file=sys.stderr)
        print(f"  - user_id: {user_id}", file=sys.stderr)
        print(f"  - preferred_cuisines: {preferred_cuisines}", file=sys.stderr)
        print(f"  - recipe_category: {recipe_category}", file=sys.stderr)
        print(f"  - max_cook_time: {max_cook_time}", file=sys.stderr)
        print(f"  - limit: {limit}", file=sys.stderr)
        
        # Test query first to see if it returns any results at all
        test_query = """
        MATCH (r:Recipe)
        WHERE ($max_cook_time IS NULL OR 
               coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
        RETURN count(r) AS total_recipes
        LIMIT 1
        """
        test_result = s.run(test_query, max_cook_time=max_cook_time).single()
        total_available = test_result.get("total_recipes", 0) if test_result else 0
        print(f"🔍 Total recipes available (with max_cook_time filter): {total_available}", file=sys.stderr)
        
        # Test if preferred_cuisines can match any recipes
        if preferred_cuisines and len(preferred_cuisines) > 0:
            test_cuisine_query = """
            MATCH (r:Recipe)
            WHERE ($max_cook_time IS NULL OR 
                   coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
            AND any(tc IN $preferred_cuisines WHERE 
                any(c IN coalesce(r.cuisine, []) WHERE c IS NOT NULL AND toLower(toString(c)) = toLower(toString(tc))))
            RETURN count(r) AS matching_recipes
            LIMIT 1
            """
            test_cuisine_result = s.run(test_cuisine_query, max_cook_time=max_cook_time, preferred_cuisines=preferred_cuisines).single()
            matching_count = test_cuisine_result.get("matching_recipes", 0) if test_cuisine_result else 0
            print(f"🔍 Recipes matching preferred_cuisines {preferred_cuisines}: {matching_count}", file=sys.stderr)
        
        recs = [
            dict(r)
            for r in s.run(q, **params)
        ]
        print(f"📊 Fallback query returned {len(recs)} results before allergy filter", file=sys.stderr)
        if len(recs) > 0:
            first_few = recs[:3]
            titles = [r.get('title', 'N/A') for r in first_few]
            cuisines = [r.get('cuisine', []) for r in first_few]
            match_percents = [r.get('match_percent', 'N/A') for r in first_few]
            print(f"📋 First {len(titles)} recipes from fallback query:", file=sys.stderr)
            for i, (title, cuisine, match) in enumerate(zip(titles, cuisines, match_percents), 1):
                print(f"  {i}. {title} (cuisine: {cuisine}, match: {match}%)", file=sys.stderr)
        
        # Allergy safety filter applied here as well
        filtered_recs = _filter_allergic_recipes(user_id, recs)
        print(f"📊 After allergy filter: {len(filtered_recs)} results", file=sys.stderr)
        
        # IMPORTANT: If no results and recipe_category was provided, try again without recipe_category filter
        # This is critical for guest users who might have "Main Dishes" that doesn't match database
        if not filtered_recs and recipe_category and not has_ingredients and has_user:
            print(f"⚠️ Fallback query returned no results with recipe_category='{recipe_category}', trying without recipe_category filter", file=sys.stderr)
            # Create a modified query without recipe_category filter
            q_no_category = q.replace(
                """AND ($recipe_category IS NULL OR 
             r.recipe_category = $recipe_category OR
             toLower(r.recipe_category) = toLower($recipe_category) OR
             toLower(r.recipe_category) CONTAINS toLower($recipe_category))""",
                "// recipe_category filter removed for fallback"
            )
            params_no_category = params.copy()
            params_no_category["recipe_category"] = None
            recs_no_category = [
                dict(r)
                for r in s.run(q_no_category, **params_no_category)
            ]
            filtered_recs = _filter_allergic_recipes(user_id, recs_no_category)
            if filtered_recs:
                print(f"✅ Fallback query returned {len(filtered_recs)} results without recipe_category filter", file=sys.stderr)
        
        if not filtered_recs:
            print(f"⚠️ Fallback query returned no results", file=sys.stderr)
        return filtered_recs or []