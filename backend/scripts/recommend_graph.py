#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Graph-based Knowledge-Based Recipe Recommendation System 🧠
------------------------------------------------------------
- No scoring; reasoning relies on knowledge rules (IF–THEN logic)
- Uses the Jaccard formula to measure ingredient similarity
- Filters out interacted recipes, allergy matches, and those exceeding cook time
- Provides explainable recommendations
"""

from neo4j import GraphDatabase
import argparse
import json
import sys
from typing import Dict, List, Optional


# =========================================================
# 🌍 Cuisine Hierarchy Mapping
# =========================================================
# Define cuisine groups for priority-based matching
# Priority: 1 = exact match, 2 = same group, 3 = all others
CUISINE_GROUPS = {
    "Asian": ["Vietnamese", "Chinese", "Japanese", "Korean", "Thai", "Asian"],
    "European": ["Italian", "French", "British", "European"],
    "Latin": ["Mexican", "Caribbean"],
    "All": ["American", "World", "Indian"]
}

def get_cuisine_priority(recipe_cuisine: str, target_cuisine: Optional[str]) -> int:
    """
    Calculate cuisine priority for ranking.
    Returns: 1 (exact match), 2 (same group), 3 (all others)
    """
    if not target_cuisine or not recipe_cuisine:
        return 3  # No preference or no cuisine = lowest priority
    
    target_lower = target_cuisine.lower().strip()
    recipe_lower = str(recipe_cuisine).lower()
    
    # Extract individual cuisines from combined string (e.g., "Vietnamese, Chinese")
    recipe_cuisines = [c.strip() for c in recipe_lower.split(",")]
    
    # Check exact match (highest priority)
    if target_lower in recipe_cuisines or recipe_lower == target_lower:
        return 1
    
    # Check group match
    target_group = None
    for group, cuisines in CUISINE_GROUPS.items():
        if target_lower in [c.lower() for c in cuisines]:
            target_group = group
            break
    
    if target_group:
        # Check if recipe cuisine belongs to same group
        for recipe_c in recipe_cuisines:
            for group, cuisines in CUISINE_GROUPS.items():
                if group == target_group and recipe_c in [c.lower() for c in cuisines]:
                    return 2
    
    # Default: all others
    return 3


# =========================================================
# 🧩 Core Recommender Class
# =========================================================
class GraphHybridRecommender:
    def __init__(self, uri="bolt://localhost:7687", username="neo4j",
                 password="Admin123!", database="test"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()

    # ---------------------------------------------------
    # 🔍 Map ingredient names to ingredient_ids
    # ---------------------------------------------------
    def map_ingredient_names_to_ids(self, session, ingredient_names: List[str]) -> List[str]:
        """
        Map ingredient names (text) to ingredient_ids using fulltext search and fuzzy matching.
        Returns list of ingredient_ids that match the input names.
        """
        if not ingredient_names:
            return []
        
        ingredient_ids = []
        for name in ingredient_names:
            name = name.strip()
            if not name:
                continue
            
            # Try exact match first (by canonical_name or ingredient_id)
            q_exact = """
            MATCH (i:Ingredient)
            WHERE i.ingredient_id = $name 
               OR toLower(i.canonical_name) = toLower($name)
               OR $name IN i.alt_names
            RETURN i.ingredient_id AS id
            LIMIT 1
            """
            result = session.run(q_exact, name=name).single()
            if result:
                ingredient_ids.append(result["id"])
                continue
            
            # Try fulltext search
            q_fts = """
            CALL db.index.fulltext.queryNodes('ingredient_name_fts', $name)
            YIELD node, score
            WHERE node:Ingredient
            RETURN node.ingredient_id AS id, score
            ORDER BY score DESC
            LIMIT 1
            """
            result = session.run(q_fts, name=name).single()
            if result:
                ingredient_ids.append(result["id"])
                continue
            
            # Try fuzzy match (contains)
            q_fuzzy = """
            MATCH (i:Ingredient)
            WHERE toLower(i.canonical_name) CONTAINS toLower($name)
               OR any(alt IN i.alt_names WHERE toLower(alt) CONTAINS toLower($name))
            RETURN i.ingredient_id AS id
            LIMIT 1
            """
            result = session.run(q_fuzzy, name=name).single()
            if result:
                ingredient_ids.append(result["id"])
        
        return list(set(ingredient_ids))  # Remove duplicates

    def build_ingredient_match_context(self, session, ingredient_ids: List[str]) -> Dict[str, List[str]]:
        """
        Build helper sets for ingredient matching (bases, synonyms).
        """
        if not ingredient_ids:
            return {"bases": [], "synonyms": []}
        q = """
        MATCH (i:Ingredient)
        WHERE i.ingredient_id IN $ids
        RETURN 
            toLower(i.base) AS base,
            toLower(i.canonical_name) AS canonical,
            [name IN coalesce(i.alt_names, []) | toLower(name)] AS alt_names
        """
        bases = set()
        synonyms = set()
        result = session.run(q, ids=ingredient_ids)
        for row in result:
            base = row.get("base")
            canonical = row.get("canonical")
            alt_names = row.get("alt_names") or []
            if base:
                bases.add(base)
            if canonical:
                synonyms.add(canonical)
            for alt in alt_names:
                if alt:
                    synonyms.add(alt)
        return {
            "bases": list(bases),
            "synonyms": list(synonyms)
        }

    # ---------------------------------------------------
    # 🧠 Load user profile
    # ---------------------------------------------------
    def get_user_profile(self, session, user_id: str) -> Dict:
        q = """
        MATCH (u:User {user_id: $uid})
        OPTIONAL MATCH (u)-[:ALLERGIC_TO]->(a:Ingredient)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        RETURN 
            u.user_id AS uid,
            coalesce(u.gender, 'unknown') AS gender,
            collect(DISTINCT a.ingredient_id) AS allergies,
            collect(DISTINCT c.name) AS fav_cuisines,
            u.max_cook_time AS maxCook
        """
        row = session.run(q, uid=user_id).single()
        if not row:
            return {"allergies": [], "fav_cuisines": None, "maxCook": None,
                    "gender": "unknown", "cuisine_interaction_counts": {}}
        try:
            maxCook = int(row.get("maxCook")) if row.get("maxCook") else None
        except:
            maxCook = None
        # Normalize fav_cuisines: return None if empty, otherwise normalize to lowercase
        fav_cuisines_raw = row.get("fav_cuisines") or []
        if not fav_cuisines_raw or len(fav_cuisines_raw) == 0:
            fav_cuisines_normalized = None  # None means no preference
        else:
            fav_cuisines_normalized = [c.lower().strip() for c in fav_cuisines_raw if c]
            # If after filtering all are empty, set to None
            if not fav_cuisines_normalized:
                fav_cuisines_normalized = None
        
        return {
            "allergies": row.get("allergies") or [],
            "fav_cuisines": fav_cuisines_normalized,  # Can be None, [], or list
            "maxCook": maxCook,
            "gender": row.get("gender") or "unknown",
            "cuisine_interaction_counts": {}
        }

    # ---------------------------------------------------
    # 📊 Get cuisine interaction counts for user
    # ---------------------------------------------------
    def get_cuisine_interaction_counts(self, session, user_id: str) -> Dict[str, int]:
        """
        Count how many times user has interacted with each cuisine.
        Returns dict: {cuisine_name: count}
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r:Recipe)
        UNWIND r.cuisine AS cuisine_name
        WITH toLower(cuisine_name) AS cuisine, count(iv) AS interaction_count
        RETURN cuisine, interaction_count
        ORDER BY interaction_count DESC
        """
        result = session.run(q, uid=user_id)
        return {row["cuisine"]: row["interaction_count"] for row in result}

    # ---------------------------------------------------
    # 🔍 Knowledge-Based Reasoning (no score, Jaccard)
    # ---------------------------------------------------
    def recommend_knowledge_based(self, session, user_id, ingredient_ids,
                                  user_profile, limit=30, min_match_ratio=0.4,
                                  max_cook_time=None, recipe_category=None, preferred_cuisines=None,
                                  cuisine_diversity_threshold=5, ingredient_match_context=None):
        """
        Recommend recipes with cuisine diversity balance.
        
        Args:
            cuisine_diversity_threshold: If user has interacted with a cuisine >= this many times,
                                        reduce its priority to encourage exploration
        """
        fav_cuisines = user_profile.get("fav_cuisines")  # Can be None, [], or list
        allergies = user_profile.get("allergies", [])
        max_cook = max_cook_time or user_profile.get("maxCook", None)
        match_bases = []
        match_synonyms = []
        if ingredient_match_context:
            match_bases = [b for b in ingredient_match_context.get("bases", []) if b]
            match_synonyms = [s for s in ingredient_match_context.get("synonyms", []) if s]
        
        # Get cuisine interaction counts for explore/exploit balance
        cuisine_counts = self.get_cuisine_interaction_counts(session, user_id)
        
        # Use preferred_cuisines if provided, otherwise use fav_cuisines from profile
        # If fav_cuisines is None (no preference), use empty list to not filter by cuisine
        if preferred_cuisines:
            target_cuisines = preferred_cuisines
        elif fav_cuisines is None:
            # None means no preference - don't filter by cuisine
            target_cuisines = []
        elif fav_cuisines:
            # Has cuisines - use them
            target_cuisines = fav_cuisines
        else:
            # Empty list - also means no preference
            target_cuisines = []
        
        # Normalize to list
        if isinstance(target_cuisines, str):
            target_cuisines = [c.strip() for c in target_cuisines.split(",")]
        target_cuisines = [c.lower() for c in target_cuisines if c]
        
        # Identify overused cuisines (high usage frequency)
        overused_cuisines = {c: count for c, count in cuisine_counts.items() 
                            if count >= cuisine_diversity_threshold}

        q = """
        MATCH (u:User {user_id:$uid})

        // --- Step 1️⃣: Load user context ---
        OPTIONAL MATCH (u)-[:ALLERGIC_TO]->(a:Ingredient)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        OPTIONAL MATCH (u)-[:INTERACTED_WITH {event_type:'like'}]->(prev:Recipe)
        OPTIONAL MATCH (u)-[:INTERACTED_WITH]->(x:Recipe)
        WITH u,
            collect(DISTINCT a.ingredient_id) AS allergies,
            // Normalize cuisine names to lowercase for consistent comparison
            [cuisine IN collect(DISTINCT c.name) WHERE cuisine IS NOT NULL | toLower(cuisine)] AS fav_cuisines,
            collect(DISTINCT x.recipe_id) AS interacted_ids,
            collect(DISTINCT prev) AS liked_recipes,
            coalesce(u.max_cook_time, NULL) AS max_cook

        // --- Step 2️⃣: Candidate recipes ---
        // Try to find recipes (prefer non-interacted, but allow interacted if needed)
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH u, allergies, fav_cuisines, liked_recipes, r, i,
            CASE
                WHEN i.ingredient_id IN $input_ing THEN 'exact'
                WHEN i.base IS NOT NULL AND toLower(i.base) IN $input_bases THEN 'base'
                WHEN toLower(i.canonical_name) IN $input_synonyms
                     OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) IN $input_synonyms)
                THEN 'synonym'
                ELSE NULL
            END AS match_type
        WHERE match_type IS NOT NULL
        AND ($max_cook IS NULL OR
            coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook)
        AND ($recipe_category IS NULL OR 
            r.recipe_category = $recipe_category OR
            toLower(r.recipe_category) = toLower($recipe_category) OR
            toLower(r.recipe_category) CONTAINS toLower($recipe_category))
        WITH u, allergies, fav_cuisines, liked_recipes, r,
            collect(DISTINCT i.ingredient_id) AS matched_ing,
            collect(match_type) AS match_types,
            // Get categories of matched ingredients (from user input)
            collect(DISTINCT i.category) AS matched_categories,
            // Get recipe cuisines (normalized to lowercase)
            [c IN r.cuisine | toLower(c)] AS recipe_cuisines,
            // Check if recipe matches user's direct choices (meal & time)
            CASE 
                WHEN $recipe_category IS NOT NULL AND 
                     (r.recipe_category = $recipe_category OR
                      toLower(r.recipe_category) = toLower($recipe_category) OR
                      toLower(r.recipe_category) CONTAINS toLower($recipe_category))
                THEN 1
                ELSE 0
            END AS matches_user_meal_choice,
            // Check if recipe matches user's time preference (closer to max_cook = better)
            CASE 
                WHEN $max_cook IS NOT NULL THEN
                    CASE 
                        WHEN coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook THEN
                            // Prefer recipes closer to max_cook (but not exceeding)
                            1.0 - (toFloat(coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 0)) / toFloat($max_cook)) * 0.5
                        ELSE 0.0
                    END
                ELSE 1.0  // No time preference = all recipes equal
            END AS time_preference_score
            
        // Count interactions for each cuisine in this recipe
        OPTIONAL MATCH (u)-[:INTERACTED_WITH]->(prev_r:Recipe)
        WHERE any(rc IN recipe_cuisines WHERE rc IN [c IN prev_r.cuisine | toLower(c)])
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, matched_categories,
            recipe_cuisines, matches_user_meal_choice, time_preference_score,
            match_types,
            count(DISTINCT prev_r) AS cuisine_interaction_count,
            // Check if recipe has new/unexplored cuisines (not in cuisine_counts dict)
            any(rc IN recipe_cuisines WHERE NOT rc IN keys($cuisine_counts)) AS has_new_cuisine
            
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, matched_categories,
            recipe_cuisines, cuisine_interaction_count, has_new_cuisine,
            matches_user_meal_choice, time_preference_score,
            size([type IN match_types WHERE type='exact']) AS exact_match_count,
            size([type IN match_types WHERE type='base']) AS base_match_count,
            size([type IN match_types WHERE type='synonym']) AS synonym_match_count
            
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, matched_categories,
            recipe_cuisines, cuisine_interaction_count, has_new_cuisine,
            matches_user_meal_choice, time_preference_score, exact_match_count,
            base_match_count, synonym_match_count,
            // Check if any recipe cuisine is overused (>= threshold)
            cuisine_interaction_count >= $diversity_threshold AS has_overused_cuisine,
            // Calculate base cuisine priority: 1=exact match any, 2=same group match any, 3=all others
            CASE 
                WHEN size($target_cuisines) = 0 THEN 3
                // Priority 1: Exact match with ANY cuisine in the list
                WHEN any(tc IN $target_cuisines WHERE tc IN recipe_cuisines)
                THEN 1
                // Priority 2: Match the group of ANY cuisine in the list
                WHEN any(tc IN $target_cuisines WHERE 
                    (tc = 'vietnamese' AND 'asian' IN recipe_cuisines) OR
                    (tc IN ['chinese', 'japanese', 'korean', 'thai'] AND 'asian' IN recipe_cuisines) OR
                    (tc IN ['italian', 'french', 'british'] AND 'european' IN recipe_cuisines) OR
                    (tc IN ['mexican', 'caribbean'] AND any(c IN recipe_cuisines WHERE c IN ['mexican', 'caribbean']))
                )
                THEN 2
                ELSE 3
            END AS base_priority
            
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, matched_categories,
            recipe_cuisines, has_overused_cuisine, has_new_cuisine, base_priority,
            matches_user_meal_choice, time_preference_score,
            exact_match_count, base_match_count, synonym_match_count,
            // Adjust priority based on exploration:
            // - If target_cuisines is empty -> keep priority = 3, no cuisine adjustment
            // - If target_cuisines exist -> adjust according to overused/new cuisines
            CASE 
                WHEN size($target_cuisines) = 0 THEN base_priority  // No cuisine preference -> keep original priority
                WHEN base_priority = 1 AND has_overused_cuisine THEN 2  // Exact match but overused -> downgrade priority
                WHEN base_priority = 2 AND has_overused_cuisine THEN 3  // Group match but overused -> downgrade priority
                WHEN base_priority = 3 AND has_new_cuisine THEN 2       // New cuisine -> upgrade priority to encourage exploration
                ELSE base_priority
            END AS cuisine_priority

        // --- Step 3️⃣: Collect all recipe ingredients with categories ---
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH u, allergies, fav_cuisines, liked_recipes, r,
            matched_ing, matched_categories,
            matches_user_meal_choice, time_preference_score,
            collect(DISTINCT ai.ingredient_id) AS all_ing,
            // Get categories of all recipe ingredients
            collect(DISTINCT ai.category) AS all_categories,
            cuisine_priority,
            exact_match_count, base_match_count, synonym_match_count

        // --- Step 4️⃣: Compute weighted Jaccard match ratio with ingredient importance ---
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, all_ing, 
            matched_categories, all_categories, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            // Pre-compute size of all_ing for use in CASE statement
            size(all_ing) AS ing_count,
            exact_match_count, base_match_count, synonym_match_count
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, all_ing, 
            matched_categories, all_categories, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            ing_count,
            exact_match_count, base_match_count, synonym_match_count,
            // Count ingredients by importance level
            size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) AS protein_match_count,
            size([cat IN matched_categories WHERE cat IN ['grain']]) AS carbo_match_count,
            size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) AS vegetable_match_count,
            size([cat IN matched_categories WHERE cat IN ['herb', 'seasoning']]) AS herb_spice_match_count,
            // Calculate ingredient importance bonus
            // Protein (meat, plant_protein, seafood): +0.3 per match
            // Carbo (grain): +0.2 per match
            // Vegetable: +0.1 per match
            // Herbs/spices (herb, seasoning): 0.0 (lowest weight)
            (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) * 0.3 +
             size([cat IN matched_categories WHERE cat IN ['grain']]) * 0.2 +
             size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) * 0.1) AS importance_bonus,
            // Base Jaccard match ratio
            CASE 
                WHEN ing_count = 0 THEN 0.0
                ELSE toFloat(size(matched_ing)) /
                    toFloat(ing_count + size($input_ing) - size(matched_ing))
            END AS base_match_ratio
        WHERE 
            // Improved matching logic: combine absolute minimum (at least 1-2 ingredients) 
            // with relative minimum (match ratio) that scales with recipe complexity
            (
                // Absolute minimum: must match at least 1 ingredient (or 2 if user provided 4+ ingredients)
                size(matched_ing) >= CASE WHEN size($input_ing) >= 4 THEN 2 ELSE 1 END
            )
            AND (
                // Relative minimum: match ratio threshold that adapts to recipe size
                // Smaller recipes (< 5 ingredients): require higher match ratio (easier to match)
                // Larger recipes (>= 10 ingredients): require lower match ratio (harder to match)
                CASE
                    WHEN ing_count < 5 THEN base_match_ratio >= $min_match * 0.6
                    WHEN ing_count >= 5 AND ing_count < 10 THEN base_match_ratio >= $min_match * 0.4
                    WHEN ing_count >= 10 AND ing_count < 15 THEN base_match_ratio >= $min_match * 0.3
                    ELSE base_match_ratio >= $min_match * 0.2
                END
            )
        // Filter allergies: only filter if recipe contains ALL user's allergies (very strict)
        // This allows recipes with some allergens if they don't have all of them
        AND NOT (size([ing IN all_ing WHERE ing IN allergies]) = size($allergies) AND size($allergies) > 0)
        // Filter out recipes that only match herbs/spices (avoid recommending based solely on herbs/spices)
        // Apply this filter only when match ratio is very low (< 0.2) and matches are herbs/spices only
        AND NOT (base_match_ratio < 0.2 AND protein_match_count = 0 AND carbo_match_count = 0 AND vegetable_match_count = 0 AND herb_spice_match_count > 0)
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, all_ing, 
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            matches_user_meal_choice, time_preference_score,
            exact_match_count, base_match_count, synonym_match_count,
            // Calculate weighted match ratio: base + importance bonus (capped at 1.0)
            CASE 
                WHEN base_match_ratio + importance_bonus > 1.0 THEN 1.0
                ELSE base_match_ratio + importance_bonus
            END AS match_ratio,
            cuisine_priority,
            [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing

        // --- Step 5️⃣: Interaction history scoring (for long-term users) ---
        // Calculate similarity with user's interaction history
        OPTIONAL MATCH (u)-[iv_inter:INTERACTED_WITH]->(interacted_recipe:Recipe)
        WHERE interacted_recipe IS NOT NULL
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            all_ing, interacted_recipe, iv_inter,
            exact_match_count, base_match_count, synonym_match_count,
            // Interaction weight (like > cook > view)
            CASE 
                WHEN iv_inter.event_type = 'like' THEN 3.0
                WHEN iv_inter.event_type = 'cook' THEN 2.0
                WHEN iv_inter.event_type = 'view' THEN 1.0
                ELSE 0.5
            END AS interaction_weight,
            // Recency score (more recent = higher score)
            CASE 
                WHEN iv_inter.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv_inter.timestamp, datetime()).days / 30.0)
            END AS interaction_recency,
            // Ingredient overlap with interacted recipes
            size([ing IN all_ing WHERE ing IN [(interacted_recipe)-[:HAS_INGREDIENT]->(ri:Ingredient) | ri.ingredient_id]]) AS shared_ing_count,
            // Cuisine overlap
            CASE 
                WHEN any(c IN r.cuisine WHERE c IN interacted_recipe.cuisine) THEN 1.0
                ELSE 0.0
            END AS shared_cuisine
        
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            all_ing,
            // Calculate weighted interaction history score
            coalesce(sum(interaction_weight * interaction_recency * 
                (toFloat(shared_ing_count) / toFloat(size(all_ing) + 1.0)) * 0.5 + 
                shared_cuisine * 0.5
            ), 0.0) AS history_score,
            // Count distinct interacted recipes that are similar
            coalesce(count(DISTINCT CASE WHEN shared_ing_count > 0 OR shared_cuisine > 0 THEN interacted_recipe ELSE NULL END), 0) AS similar_interacted_count,
            exact_match_count, base_match_count, synonym_match_count
            
        // --- Step 6️⃣: Reasoning flags ---
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            history_score, similar_interacted_count,
            // Match quality flags (based on weighted match_ratio)
            (match_ratio >= 0.75) AS good_match,
            (match_ratio >= 0.5 AND match_ratio < 0.75) AS partial_match,
            (match_ratio >= 0.3 AND match_ratio < 0.5) AS slight_match,
            // Ingredient importance flags
            (protein_match_count > 0) AS has_protein_match,
            (carbo_match_count > 0) AS has_carbo_match,
            (protein_match_count > 0 AND carbo_match_count > 0) AS has_protein_and_carbo,
            // Matches cuisine: cuisine_priority = 1 (exact match) or 2 (group match)
            // No longer rely on exact matches with favorite cuisines; use cuisine_priority instead
            (cuisine_priority = 1 OR cuisine_priority = 2) AS matches_cuisine,
            // Check if recipe is similar to user's interaction history
            history_score > 0.5 AS similar_to_history,
            exact_match_count, base_match_count, synonym_match_count

        // --- Step 7️⃣: Social & demographic signals ---
        OPTIONAL MATCH (u)-[:SIMILAR_USER]->(u2:User)-[:INTERACTED_WITH]->(r)
        WITH u, liked_recipes, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            exact_match_count, base_match_count, synonym_match_count,
            count(DISTINCT u2) AS similar_users

        OPTIONAL MATCH (u)-[:BELONGS_TO]->(g:Group)-[:POPULAR_IN]->(r)
        WITH u, liked_recipes, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, count(g) AS demo_signal,
            exact_match_count, base_match_count, synonym_match_count

                // --- Step 8️⃣: Semantic similarity (TF-IDF cosine) ---
        // Only compute semantic similarity if user has liked recipes
        // If liked_recipes is empty, set max_text_sim to 0 and continue
        // Use conditional UNWIND: only process if liked_recipes is not empty
        WITH u, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal,
            exact_match_count, base_match_count, synonym_match_count,
            liked_recipes,  // Include liked_recipes in WITH clause
            // If no liked recipes, skip UNWIND and set max_text_sim to 0
            CASE WHEN size(liked_recipes) = 0 THEN 0.0 ELSE NULL END AS max_text_sim_if_empty
        // UNWIND liked_recipes - if empty, this will produce no rows, but we handle that with max_text_sim_if_empty
        UNWIND CASE WHEN size(liked_recipes) > 0 THEN liked_recipes ELSE [null] END AS lr
        WITH u, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal, lr,
            exact_match_count, base_match_count, synonym_match_count,
            max_text_sim_if_empty
        WHERE lr IS NULL OR (lr.text_weights IS NOT NULL AND r.text_weights IS NOT NULL)
        WITH u, r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal,
            exact_match_count, base_match_count, synonym_match_count,
            max_text_sim_if_empty,
            CASE 
                WHEN lr IS NULL THEN NULL
                WHEN lr.text_weights IS NULL OR r.text_weights IS NULL THEN NULL
                WHEN size(lr.text_weights) = 0 OR size(r.text_weights) = 0 THEN NULL
                WHEN size(lr.text_weights) <> size(r.text_weights) THEN NULL
                ELSE gds.similarity.cosine(lr.text_weights, r.text_weights)
            END AS sim
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal,
            exact_match_count, base_match_count, synonym_match_count,
            max_text_sim_if_empty,
            max(sim) AS max_sim
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal,
            exact_match_count, base_match_count, synonym_match_count,
            coalesce(max_text_sim_if_empty, coalesce(max_sim, 0.0)) AS max_text_sim
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal,
            (max_text_sim >= 0.6) AS text_similar,
            exact_match_count, base_match_count, synonym_match_count
        // --- Step 9️⃣: Rating & popularity ---
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal, text_similar,
            coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
            coalesce(toInteger(r.rating_count), 0) AS rating_count,
            sum(CASE WHEN iv.event_type='like' THEN 1 ELSE 0 END) AS like_count,
            sum(CASE WHEN iv.event_type='view' THEN 1 ELSE 0 END) AS view_count,
            exact_match_count, base_match_count, synonym_match_count

        // --- Step 🔟: Build reasoning explanations ---
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal, text_similar,
            avg_rating, like_count, view_count,
            exact_match_count, base_match_count, synonym_match_count,
            [reason IN [
                CASE 
                WHEN good_match THEN '✅ Shares most of your given ingredients'
                WHEN partial_match THEN '🧂 Partially matches your given ingredients'
                WHEN slight_match THEN '🥄 Slightly matches your given ingredients'
                ELSE NULL END,
                CASE WHEN matches_user_meal_choice = 1 THEN '🍽️ Matches your meal preference' ELSE NULL END,
                CASE WHEN similar_to_history THEN '📚 Similar to recipes you interacted with before' ELSE NULL END,
                CASE WHEN similar_interacted_count > 3 THEN '🎯 Matches your cooking patterns' ELSE NULL END,
                CASE WHEN matches_cuisine THEN '🍜 Matches your favorite cuisine' ELSE NULL END,
                CASE WHEN text_similar THEN '🧠 Similar to recipes you liked before' ELSE NULL END,
                CASE WHEN similar_users > 0 THEN '👥 Liked by users similar to you' ELSE NULL END,
                CASE WHEN demo_signal > 0 THEN '🏷️ Popular among your demographic group' ELSE NULL END,
                CASE WHEN avg_rating >= 4.5 THEN '⭐ Top-rated recipe' ELSE NULL END,
                CASE WHEN avg_rating >= 4.0 AND avg_rating < 4.5 THEN '👍 Well-rated by users' ELSE NULL END,
                CASE WHEN like_count > 10 THEN '❤️ Liked by many users' ELSE NULL END,
                CASE WHEN view_count > 30 THEN '👀 Frequently viewed by users' ELSE NULL END
            ] WHERE reason IS NOT NULL] AS reasoning

        // --- Step 1️⃣1️⃣: Collect full recipe ingredients with details ---
        OPTIONAL MATCH (r)-[rel:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, matched_ing, missing_ing, match_ratio, cuisine_priority,
            matches_user_meal_choice, time_preference_score,
            base_match_ratio, importance_bonus,
            protein_match_count, carbo_match_count, vegetable_match_count,
            good_match, partial_match, slight_match,
            has_protein_match, has_carbo_match, has_protein_and_carbo,
            matches_cuisine,
            history_score, similar_interacted_count, similar_to_history,
            similar_users, demo_signal, text_similar,
            avg_rating, like_count, view_count,
            reasoning,
            exact_match_count, base_match_count, synonym_match_count,
            collect({
                ingredient_id: ing.ingredient_id,
                ingredient_name: coalesce(ing.name, ing.canonical_name),
                base: coalesce(ing.base, ing.canonical_name),
                category: ing.category
            }) AS ingredients

        // --- Step 1️⃣2️⃣: Return final explainable results ---
        RETURN
            r.recipe_id AS recipe_id,
            r.title AS title,
            coalesce(r.cuisine, []) AS cuisine,
            coalesce(r.tags, []) AS tags,
            r.recipe_category AS recipe_category,
            round(match_ratio * 100, 1) AS match_percent,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            matched_ing,
            missing_ing,
            ingredients,
            reasoning
        ORDER BY 
            match_ratio DESC,                    // ✅ Highest priority: ingredient match ratio
            exact_match_count DESC,              // Prioritize exact ingredient matches
            cuisine_priority ASC,                // ✅ Second priority: cuisine preference
            matches_user_meal_choice DESC,       // ✅ Third priority: matches user's meal choice (if provided)
            time_preference_score DESC,           // ✅ Fourth priority: matches user's time preference (if provided)
            history_score DESC,                  // ✅ Fifth priority: similar to interaction history (long-term users)
            similar_interacted_count DESC,       // ✅ Sixth priority: aligns with many interacted recipes
            size(reasoning) DESC                 // Fallback: more reasoning signals first
        LIMIT $lim

        """

        try:
            result = session.run(
                q,
                uid=user_id,
                input_ing=ingredient_ids,
                allergies=allergies,
                fav_cuisines=fav_cuisines,
                max_cook=max_cook,
                recipe_category=recipe_category,
                target_cuisines=target_cuisines,
                cuisine_counts=cuisine_counts,
                diversity_threshold=cuisine_diversity_threshold,
                min_match=min_match_ratio,
                lim=limit,
                input_bases=match_bases,
                input_synonyms=match_synonyms
            )
            results = [dict(r) for r in result]
            return results
        except Exception as e:
            error_msg = str(e)
            # Only print error message, not the full query
            if "SyntaxError" in error_msg or "Syntax" in error_msg:
                # Extract line number and column if available
                import re
                line_match = re.search(r'line (\d+)', error_msg)
                col_match = re.search(r'column (\d+)', error_msg)
                if line_match:
                    print(f"❌ Cypher syntax error at line {line_match.group(1)}", file=sys.stderr)
                else:
                    print(f"❌ Cypher syntax error: {error_msg[:200]}", file=sys.stderr)
            else:
                print(f"❌ Error: {error_msg[:200]}", file=sys.stderr)
            raise

    # ---------------------------------------------------
    # 🌿 Ingredient-only fallback (Explainable)
    # ---------------------------------------------------
    def recommend_ingredient_only(self, session, ingredient_ids, limit=30, min_match_ratio=0.6,
                                  max_cook_time=None, recipe_category=None, preferred_cuisines=None,
                                  ingredient_match_context=None):
        # Normalize to list
        target_cuisines = preferred_cuisines if preferred_cuisines else []
        if isinstance(target_cuisines, str):
            target_cuisines = [c.strip() for c in target_cuisines.split(",")]
        target_cuisines = [c.lower() for c in target_cuisines if c]
        match_bases = []
        match_synonyms = []
        if ingredient_match_context:
            match_bases = [b for b in ingredient_match_context.get("bases", []) if b]
            match_synonyms = [s for s in ingredient_match_context.get("synonyms", []) if s]
        q = """
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH r, i,
            CASE
                WHEN i.ingredient_id IN $input_ing THEN 'exact'
                WHEN i.base IS NOT NULL AND toLower(i.base) IN $input_bases THEN 'base'
                WHEN toLower(i.canonical_name) IN $input_synonyms
                     OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) IN $input_synonyms)
                THEN 'synonym'
                ELSE NULL
            END AS match_type
        WHERE match_type IS NOT NULL
        AND ($max_cook_time IS NULL OR
            coalesce(r.total_time_min, r.cook_time_min, r.prep_time_min, 999999) <= $max_cook_time)
        AND ($recipe_category IS NULL OR 
            r.recipe_category = $recipe_category OR
            toLower(r.recipe_category) = toLower($recipe_category) OR
            toLower(r.recipe_category) CONTAINS toLower($recipe_category))
        WITH r, 
            collect(DISTINCT i.ingredient_id) AS matched_ing,
            collect(match_type) AS match_types,
            // Calculate cuisine priority: 1=exact match any, 2=same group match any, 3=all others
            CASE 
                WHEN size($target_cuisines) = 0 THEN 3
                // Priority 1: Exact match với BẤT KỲ cuisine nào trong list
                WHEN any(tc IN $target_cuisines WHERE any(c IN r.cuisine WHERE toLower(c) = tc))
                THEN 1
                // Priority 2: Match với group của BẤT KỲ cuisine nào trong list
                WHEN any(tc IN $target_cuisines WHERE 
                    (tc = 'vietnamese' AND any(c IN r.cuisine WHERE toLower(c) = 'asian')) OR
                    (tc IN ['chinese', 'japanese', 'korean', 'thai'] AND any(c IN r.cuisine WHERE toLower(c) = 'asian')) OR
                    (tc IN ['italian', 'french', 'british'] AND any(c IN r.cuisine WHERE toLower(c) = 'european')) OR
                    (tc IN ['mexican', 'caribbean'] AND any(c IN r.cuisine WHERE toLower(c) IN ['mexican', 'caribbean']))
                )
                THEN 2
                ELSE 3
            END AS cuisine_priority
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, cuisine_priority,
             collect(DISTINCT ai.ingredient_id) AS all_ing,
             size([type IN match_types WHERE type='exact']) AS exact_match_count
        WITH r, matched_ing, cuisine_priority, all_ing, size(all_ing) AS all_ing_count, exact_match_count
        WITH r, matched_ing, cuisine_priority, all_ing, all_ing_count,
             CASE 
                WHEN all_ing_count = 0 THEN 0.0
                ELSE toFloat(size(matched_ing)) / 
                     toFloat(all_ing_count + size($input_ing) - size(matched_ing))
             END AS match_ratio,
             exact_match_count
        WHERE match_ratio >= $min_match
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, cuisine_priority, all_ing, match_ratio,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             sum(CASE WHEN iv.event_type='like' THEN 1 ELSE 0 END) AS like_count,
             exact_match_count
        WITH r, matched_ing, cuisine_priority, missing_ing, match_ratio, avg_rating, like_count, exact_match_count,
             [reason IN [
                CASE WHEN match_ratio >= 0.75 THEN '✅ Shares most of your given ingredients'
                     WHEN match_ratio >= 0.5 THEN '🧂 Partially matches your given ingredients'
                     ELSE NULL END,
                CASE WHEN avg_rating >= 4.5 THEN '⭐ Top-rated recipe' ELSE NULL END,
                CASE WHEN like_count > 10 THEN '❤️ Liked by many users' ELSE NULL END
             ] WHERE reason IS NOT NULL] AS reasoning
        // Collect full recipe ingredients with details
        OPTIONAL MATCH (r)-[rel:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, matched_ing, cuisine_priority, missing_ing, match_ratio, avg_rating, like_count, reasoning,
             collect({
                ingredient_id: ing.ingredient_id,
                base: coalesce(ing.base, ing.canonical_name),
                category: ing.category
            }) AS ingredients
        RETURN r.recipe_id AS recipe_id, r.title AS title,
               coalesce(r.cuisine, []) AS cuisine,
               coalesce(r.tags, []) AS tags,
               r.recipe_category AS recipe_category,
               round(match_ratio*100,1) AS match_percent,
               r.cook_time_min AS cook_time_min,
               r.prep_time_min AS prep_time_min,
               r.total_time_min AS total_time_min,
               r.servings AS servings,
               r.yield AS yield,
               head(coalesce(r.image_urls, [])) AS image,
               matched_ing, missing_ing, ingredients, reasoning
        ORDER BY cuisine_priority ASC, exact_match_count DESC, match_ratio DESC, size(reasoning) DESC
        LIMIT $lim
        """
        result = session.run(q, input_ing=ingredient_ids, min_match=min_match_ratio, 
                            max_cook_time=max_cook_time, recipe_category=recipe_category,
                            target_cuisines=target_cuisines, lim=limit,
                            input_bases=match_bases, input_synonyms=match_synonyms)
        return [dict(r) for r in result]


    # ---------------------------------------------------
    # 🧩 Main entrypoint
    # ---------------------------------------------------
    def recommend(self, user_id=None, ingredient_ids=None, ingredient_names=None, 
                 limit=30, min_match_ratio=0.6, max_cook_time=None, recipe_category=None,
                 preferred_cuisines=None):
        """
        Main recommendation entrypoint.
        
        Args:
            user_id: User ID (optional)
            ingredient_ids: List of ingredient IDs (optional)
            ingredient_names: List of ingredient names/text (optional, will be mapped to IDs)
            limit: Maximum number of results
            min_match_ratio: Minimum Jaccard match ratio
            max_cook_time: Maximum cooking time in minutes
            recipe_category: Filter by recipe category/meal type (None/"no preference"/"none"/"all" = no filter)
            preferred_cuisines: List of preferred cuisines for priority ranking (e.g., ["Korean", "Vietnamese", "American"])
                                Can be string (comma-separated) or list
        """
        with self.driver.session(database=self.database) as session:
            # Normalize recipe_category: treat "no preference", "none", "all" as None (no filter)
            if recipe_category:
                normalized = recipe_category.strip().lower()
                if normalized in ["no preference", "none", "all", "all categories", ""]:
                    recipe_category = None
            
            # Map ingredient names to IDs if provided
            mapped_ids = []
            if ingredient_names:
                print(f"🔍 Mapping ingredient names to IDs: {ingredient_names}", file=sys.stderr)
                mapped_ids = self.map_ingredient_names_to_ids(session, ingredient_names)
                if mapped_ids:
                    print(f"✅ Mapped ingredients: {ingredient_names} -> {mapped_ids}", file=sys.stderr)
                else:
                    print(f"⚠️ Warning: No ingredients found for names: {ingredient_names}", file=sys.stderr)
            
            # Combine ingredient_ids and mapped_ids (remove duplicates)
            original_ingredient_ids = ingredient_ids
            if ingredient_ids:
                print(f"📋 Original ingredient_ids: {ingredient_ids}", file=sys.stderr)
                if mapped_ids:
                    # Merge both lists, removing duplicates
                    ingredient_ids = list(set(ingredient_ids + mapped_ids))
                    print(f"✅ Merged ingredient_ids: {ingredient_ids} (original: {original_ingredient_ids}, mapped: {mapped_ids})", file=sys.stderr)
                # else: keep ingredient_ids as is
            else:
                # Only mapped_ids available
                if mapped_ids:
                    ingredient_ids = mapped_ids
                    print(f"✅ Using mapped ingredient_ids: {ingredient_ids}", file=sys.stderr)
                else:
                    # No ingredients at all
                    print(f"⚠️ Warning: No ingredient_ids or mapped ingredient_names provided", file=sys.stderr)
                    return []  # No matching ingredients found
            
            if not ingredient_ids:
                print(f"⚠️ Warning: No valid ingredients found after mapping", file=sys.stderr)
                return []  # No matching ingredients found
            
            print(f"🎯 Final ingredient_ids for recommendation: {ingredient_ids} (count: {len(ingredient_ids)})", file=sys.stderr)
            
            ingredient_match_context = self.build_ingredient_match_context(session, ingredient_ids)
            
            if user_id and ingredient_ids:
                return self.recommend_knowledge_based(
                    session,
                    user_id,
                    ingredient_ids,
                    self.get_user_profile(session, user_id),
                    limit,
                    min_match_ratio,
                    max_cook_time,
                    recipe_category,
                    preferred_cuisines=preferred_cuisines,
                    ingredient_match_context=ingredient_match_context)
            elif ingredient_ids:
                return self.recommend_ingredient_only(
                    session,
                    ingredient_ids,
                    limit,
                    min_match_ratio,
                    max_cook_time,
                    recipe_category,
                    preferred_cuisines,
                    ingredient_match_context=ingredient_match_context)
            else:
                # Default: return globally popular recipes
                q = """
                MATCH (r:Recipe)<-[iv:INTERACTED_WITH]-()
                WITH r, count(iv) AS pop
                RETURN r.recipe_id AS recipe_id, r.title AS title,
                       head(r.image_urls) AS image,
                       r.cook_time_min AS cook_time_min, pop
                ORDER BY pop DESC LIMIT $lim
                """
                result = session.run(q, lim=limit)
                return [dict(r) for r in result]


# =========================================================
# 🖥️ CLI Interface
# =========================================================
def main():
    parser = argparse.ArgumentParser(description="Knowledge-Based Recipe Recommender (Explainable)")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--db", dest="database", default="test")
    parser.add_argument("--user-id", dest="user_id")
    parser.add_argument("--ingredients", dest="ingredients", help="Comma-separated ingredient IDs")
    parser.add_argument("--ingredient-names", dest="ingredient_names", help="Comma-separated ingredient names (will be mapped to IDs)")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--min-match", type=float, default=0.4)
    parser.add_argument("--max-cook-time", type=int, dest="max_cook_time", help="Maximum cooking time in minutes")
    parser.add_argument("--recipe-category", dest="recipe_category", 
                       help="Filter by recipe category/meal type (use 'no preference'/'none'/'all' for no filter)")
    parser.add_argument("--preferred-cuisines", dest="preferred_cuisines",
                       help="Preferred cuisines for priority ranking (comma-separated, e.g., 'Korean,Vietnamese,American')")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ingredient_ids = [x.strip() for x in args.ingredients.split(",")] if args.ingredients else None
    ingredient_names = [x.strip() for x in args.ingredient_names.split(",")] if args.ingredient_names else None
    
    rec = GraphHybridRecommender(args.uri, args.user, args.password, args.database)
    results = rec.recommend(
        user_id=args.user_id, 
        ingredient_ids=ingredient_ids,
        ingredient_names=ingredient_names,
        limit=args.limit, 
        min_match_ratio=args.min_match,
        max_cook_time=args.max_cook_time,
        recipe_category=args.recipe_category,
        preferred_cuisines=args.preferred_cuisines
    )

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(results, 1):
            print(f"#{i}. {r.get('title')} ({r.get('recipe_id')})")
            print(f"   🍳 Match: {r.get('match_percent')}%")
            if r.get("reasoning"):
                for reason in r["reasoning"]:
                    print(f"   • {reason}")
            print(f"   ✅ Matched: {', '.join(r.get('matched_ing', []))}")
            print(f"   📝 Missing: {', '.join(r.get('missing_ing', []))}")
            if r.get('cook_time_min'):
                print(f"   ⏱️  Cook time: {r.get('cook_time_min')} min")
            if r.get('recipe_category'):
                print(f"   🍽️  Category: {r.get('recipe_category')}")
            print()

    rec.close()


if __name__ == "__main__":
    main()
