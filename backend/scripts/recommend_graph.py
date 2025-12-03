#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Refactored Graph-based Knowledge-Based Recipe Recommendation System 🧠
-----------------------------------------------------------------------
- Modular design với các classes riêng biệt
- Dựa trên knowledge-based approach từ knowledge_based_recommender.py
- Tách Cypher queries lớn thành smaller, maintainable queries
- Dễ test, dễ extend, dễ maintain
"""

from neo4j import GraphDatabase
import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from math import log

# Import knowledge-based components
try:
    import sys
    from pathlib import Path
    # Add scripts directory to path
    scripts_dir = Path(__file__).parent
    if str(scripts_dir) not in sys.path:
        sys.path.insert(0, str(scripts_dir))
    
    from knowledge_based_recommender import (
        KnowledgeBasedRecommender,
        UserKnowledge,
        RecipeKnowledge,
        GroupKnowledge,
        RecommendationReason
    )
except ImportError as e:
    # Fallback if not available
    print(f"⚠️ Warning: Could not import knowledge_based_recommender: {e}", file=sys.stderr)
    print("   Continuing without knowledge-based components...", file=sys.stderr)
    KnowledgeBasedRecommender = None
    UserKnowledge = None
    RecipeKnowledge = None
    GroupKnowledge = None
    RecommendationReason = None

# Import classify_recipe from compute_features_improve (for fallback if flags not in DB)
try:
    from compute_features_improve import classify_recipe as classify_recipe_from_features
except ImportError:
    classify_recipe_from_features = None


# =========================================================
# 🥗 Nutrition Classification & Dietary Plan Helpers
# =========================================================

def classify_recipe(n: Dict) -> Dict[str, bool]:
    """
    Phân loại recipe vào các dietary categories dựa trên nutrition values.
    
    Args:
        n: Nutrition dict cho 1 recipe (values đã là per serving)
            - total_fat (g)
            - total_carbohydrate (g)
            - protein (g)
            - saturated_fat (g)
            - total_sugars (g)
            - dietary_fiber (g)
            - sodium (mg)
            - cholesterol (mg)
    
    Returns:
        Dict với các boolean flags:
        {
            "low_carb": bool,
            "high_protein": bool,
            "keto": bool,
            "low_fat": bool
        }
    """
    # Lấy các giá trị (gram / mg)
    fat = n.get("total_fat", 0) or 0
    carb = n.get("total_carbohydrate", 0) or 0
    protein = n.get("protein", 0) or 0
    sat_fat = n.get("saturated_fat", 0) or 0
    sugar = n.get("total_sugars", 0) or 0
    fiber = n.get("dietary_fiber", 0) or 0
    sodium = n.get("sodium", 0) or 0
    cholesterol = n.get("cholesterol", 0) or 0
    
    # B1 – Tính calories_est và % năng lượng
    calories_est = 9 * fat + 4 * carb + 4 * protein
    if calories_est <= 0:
        return {
            "low_carb": False,
            "high_protein": False,
            "keto": False,
            "low_fat": False
        }
    
    carb_pct = (4 * carb) / calories_est
    protein_pct = (4 * protein) / calories_est
    fat_pct = (9 * fat) / calories_est
    sat_fat_pct = (9 * sat_fat) / calories_est
    
    result = {
        "low_carb": False,
        "high_protein": False,
        "keto": False,
        "low_fat": False
    }
    
    # ---- LOW CARB ----
    if carb_pct <= 0.26 and carb <= 30:
        result["low_carb"] = True
    
    # ---- HIGH PROTEIN ----
    if protein_pct >= 0.25 and protein >= 20:
        result["high_protein"] = True
    
    # ---- KETO ----
    if (
        carb_pct <= 0.10 and
        carb <= 15 and
        fat_pct >= 0.60 and
        0.15 <= protein_pct <= 0.30 and
        sugar <= 5
    ):
        result["keto"] = True
    
    # ---- LOW FAT ----
    if fat_pct <= 0.30:
        result["low_fat"] = True
    
    return result


def calculate_bmi(weight_kg: float, height_cm: float) -> float:
    """Calculate BMI from weight (kg) and height (cm)"""
    height_m = height_cm / 100.0
    return weight_kg / (height_m ** 2)


def get_dietary_plan_from_bmi(bmi: float) -> Optional[str]:
    """
    Xác định dietary plan dựa trên BMI.
    
    Args:
        bmi: Body Mass Index
    
    Returns:
        - "weight_gain": BMI < 18.5 → High-protein + High-calorie
        - None: BMI 18.5-24.9 → Balanced (không filter)
        - "weight_loss": BMI > 24.9 → Low-carb + High-protein + Low-fat
    """
    if bmi < 18.5:
        return "weight_gain"  # High-protein + High-calorie
    elif bmi > 24.9:
        return "weight_loss"  # Low-carb + High-protein + Low-fat
    else:
        return None  # Balanced diet, không filter theo nutrition


def filter_recipe_by_dietary_plan(
    recipe: Dict,
    dietary_plan: str
) -> bool:
    """
    Filter recipe based on dietary plan constraints.
    Sử dụng pre-computed classification flags từ classify_recipe().
    
    Args:
        recipe: Recipe dict với classification flags
            - is_low_carb: bool
            - is_high_protein: bool
            - is_keto: bool
            - is_low_fat: bool
        dietary_plan: "low_carb", "high_protein", "low_fat", "keto", 
                     "weight_gain", "weight_loss"
    
    Returns:
        True nếu recipe phù hợp với dietary plan, False nếu không
    """
    if not dietary_plan:
        return True  # Không filter nếu không có plan
    
    # Single plan filters
    if dietary_plan == "low_carb":
        return recipe.get("is_low_carb", False)
    elif dietary_plan == "high_protein":
        return recipe.get("is_high_protein", False)
    elif dietary_plan == "low_fat":
        return recipe.get("is_low_fat", False)
    elif dietary_plan == "keto":
        return recipe.get("is_keto", False)
    
    # Combined plans
    elif dietary_plan == "weight_gain":
        # High-protein + High-calorie
        # High-protein là bắt buộc, calories sẽ được boost trong scoring
        return recipe.get("is_high_protein", False)
    
    elif dietary_plan == "weight_loss":
        # Low-carb + High-protein + Low-fat
        # Phải thỏa TẤT CẢ 3 điều kiện
        return (
            recipe.get("is_low_carb", False) and
            recipe.get("is_high_protein", False) and
            recipe.get("is_low_fat", False)
        )
    
    return True  # Default: không filter


# =========================================================
# 📊 Data Structures
# =========================================================

@dataclass
class IngredientMatchContext:
    """Context for ingredient matching"""
    bases: List[str]
    synonyms: List[str]
    ingredient_ids: List[str]


@dataclass
class RecipeScore:
    """Score components for a recipe"""
    match_ratio: float
    cuisine_priority: int
    demo_signal: float
    history_score: float
    serendipity_score: float
    popular_unexplored_boost: float
    # Removed: text_similarity - TF-IDF not needed (redundant with History Score)
    final_score: float
    reasoning: List[str]


# =========================================================
# 🔍 Ingredient Matcher Component
# =========================================================

class IngredientMatcher:
    """Handles ingredient name to ID mapping and matching context"""
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def map_names_to_ids(self, session, ingredient_names: List[str]) -> List[str]:
        """Map ingredient names to IDs using fulltext search and fuzzy matching"""
        if not ingredient_names:
            return []
        
        ingredient_ids = []
        for name in ingredient_names:
            name = name.strip()
            if not name:
                continue
            
            # Try exact match first
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
            
            # Try fuzzy match
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
        
        return list(set(ingredient_ids))
    
    def build_match_context(self, session, ingredient_ids: List[str]) -> IngredientMatchContext:
        """Build helper sets for ingredient matching"""
        if not ingredient_ids:
            return IngredientMatchContext(bases=[], synonyms=[], ingredient_ids=[])
        
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
        
        return IngredientMatchContext(
            bases=list(bases),
            synonyms=list(synonyms),
            ingredient_ids=ingredient_ids
        )


# =========================================================
# 🍜 Cuisine Prioritizer Component
# =========================================================

class CuisinePrioritizer:
    """Handles cuisine priority calculation and hierarchy"""
    
    CUISINE_GROUPS = {
        "Asian": ["vietnamese", "chinese", "japanese", "korean", "thai", "asian"],
        "European": ["italian", "french", "british", "european"],
        "Latin": ["mexican", "caribbean"]
    }
    
    def calculate_priority(self, recipe_cuisines: List[str], target_cuisines: List[str]) -> int:
        """
        Calculate cuisine priority: 1=exact, 2=group, 3=others
        """
        if not target_cuisines:
            return 3
        
        recipe_lower = [c.lower() if isinstance(c, str) else str(c).lower() for c in recipe_cuisines]
        target_lower = [c.lower() for c in target_cuisines]
        
        # Check exact match
        if any(tc in recipe_lower for tc in target_lower):
            return 1
        
        # Check group match
        for target_cuisine in target_lower:
            target_group = self._get_cuisine_group(target_cuisine)
            if target_group:
                for recipe_cuisine in recipe_lower:
                    if self._is_in_group(recipe_cuisine, target_group):
                        return 2
        
        return 3
    
    def _get_cuisine_group(self, cuisine: str) -> Optional[str]:
        """Get which group a cuisine belongs to"""
        for group_name, group_cuisines in self.CUISINE_GROUPS.items():
            if cuisine in [c.lower() for c in group_cuisines]:
                return group_name
        return None
    
    def _is_in_group(self, cuisine: str, group_name: str) -> bool:
        """Check if cuisine is in a specific group"""
        group_cuisines = self.CUISINE_GROUPS.get(group_name, [])
        return cuisine in [c.lower() for c in group_cuisines]
    
    def _get_cuisine_group_name_from_recipe(self, recipe_cuisines: List[str]) -> Optional[str]:
        """
        Determine which cuisine group the recipe belongs to.
        Returns group name (e.g., "Asian", "European", "Latin") or None.
        """
        if not recipe_cuisines:
            return None
        
        recipe_lower = [c.lower() if isinstance(c, str) else str(c).lower() for c in recipe_cuisines]
        
        # Check against cuisine groups
        for group_name, group_cuisines in self.CUISINE_GROUPS.items():
            group_lower = [c.lower() for c in group_cuisines]
            if any(rc in group_lower for rc in recipe_lower):
                return group_name
        
        return None


# =========================================================
# 👥 Group Preferences Extractor Component
# =========================================================

class GroupPreferencesExtractor:
    """Extracts group preferences including POPULAR_IN relationships"""
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def get_group_preferences(self, session, gender: str, age_group: str) -> Dict:
        """
        Get demographic group preferences using knowledge-based rules.
        Returns popular cuisines, recipes, and categories for user's demographic group.
        Uses POPULAR_IN relationship for group-based recommendations.
        
        Updated: Supports users with only gender OR only age_group (uses 'unknown' for missing).
        """
        # Use 'unknown' as placeholder if gender or age_group is missing
        gender_value = gender if gender and gender != "unknown" else 'unknown'
        age_group_value = age_group if age_group and age_group != "unknown" else 'unknown'
        
        # If both are unknown, return empty
        if gender_value == 'unknown' and age_group_value == 'unknown':
            return {
                "popular_cuisines": [],
                "popular_categories": [],
                "popular_recipes": [],
                "group_size": 0
            }
        
        # Query to get group preferences (including POPULAR_IN)
        # Match Group with exact values (including 'unknown' if one is missing)
        q = """
        MATCH (g:Group {gender: $gender, age_group: $age_group})
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u:User)
        WITH g, count(DISTINCT u) AS group_size
        
        // Get popular cuisines in this group
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u1:User)-[:INTERACTED_WITH]->(r1:Recipe)
        WHERE r1.cuisine IS NOT NULL
        UNWIND r1.cuisine AS cuisine_name
        WITH g, group_size, toLower(cuisine_name) AS cuisine, count(*) AS cuisine_freq
        ORDER BY cuisine_freq DESC
        WITH g, group_size, collect({cuisine: cuisine, freq: cuisine_freq})[..5] AS top_cuisines
        
        // Get popular recipe categories in this group
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u2:User)-[:INTERACTED_WITH]->(r2:Recipe)
        WHERE r2.recipe_category IS NOT NULL
        WITH g, group_size, top_cuisines, r2.recipe_category AS category, count(*) AS cat_freq
        ORDER BY cat_freq DESC
        WITH g, group_size, top_cuisines, collect({category: category, freq: cat_freq})[..3] AS top_categories
        
        // Get most popular recipes in this group (via POPULAR_IN relationship)
        OPTIONAL MATCH (g)-[pop:POPULAR_IN]->(r3:Recipe)
        WITH g, group_size, top_cuisines, top_categories, r3, pop.score AS pop_score
        ORDER BY pop_score DESC
        WITH g, group_size, top_cuisines, top_categories, 
             collect({recipe_id: r3.recipe_id, title: r3.title, score: pop_score})[..10] AS top_recipes
        
        RETURN 
            group_size,
            top_cuisines AS popular_cuisines,
            top_categories AS popular_categories,
            top_recipes AS popular_recipes
        """
        
        result = session.run(q, gender=gender_value, age_group=age_group_value).single()
        
        if not result:
            return {
                "popular_cuisines": [],
                "popular_categories": [],
                "popular_recipes": [],
                "group_size": 0
            }
        
        return {
            "popular_cuisines": result.get("popular_cuisines") or [],
            "popular_categories": result.get("popular_categories") or [],
            "popular_recipes": result.get("popular_recipes") or [],
            "group_size": result.get("group_size") or 0
        }
    
    def is_popular_in_group(self, session, recipe_id: str, gender: str, age_group: str) -> Tuple[bool, float]:
        """
        Check if recipe is popular in user's group via POPULAR_IN relationship.
        Returns: (is_popular, popularity_score)
        
        Updated: Supports users with only gender OR only age_group (uses 'unknown' for missing).
        """
        # Use 'unknown' as placeholder if gender or age_group is missing
        gender_value = gender if gender and gender != "unknown" else 'unknown'
        age_group_value = age_group if age_group and age_group != "unknown" else 'unknown'
        
        # If both are unknown, cannot check popularity
        if gender_value == 'unknown' and age_group_value == 'unknown':
            return False, 0.0
        
        q = """
        MATCH (g:Group {gender: $gender, age_group: $age_group})-[pop:POPULAR_IN]->(r:Recipe {recipe_id: $rid})
        RETURN pop.score AS score
        """
        
        result = session.run(q, gender=gender_value, age_group=age_group_value, rid=recipe_id).single()
        
        if result and result.get("score"):
            return True, result.get("score") or 0.0
        return False, 0.0


# =========================================================
# 📊 Scoring Engine Component
# =========================================================

class ScoringEngine:
    """Calculates various scores for recipes"""
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def calculate_jaccard_match(
        self, 
        matched_ing: List[str], 
        all_ing: List[str], 
        input_ing: List[str],
        matched_categories: List[str]
    ) -> Tuple[float, float]:
        """
        Calculate weighted Jaccard match ratio with ingredient importance.
        Returns: (base_match_ratio, importance_bonus)
        """
        if not all_ing:
            return 0.0, 0.0
        
        # Base Jaccard
        intersection = len(matched_ing)
        union = len(set(all_ing) | set(input_ing))
        base_match_ratio = intersection / union if union > 0 else 0.0
        
        # Importance bonus
        protein_count = sum(1 for cat in matched_categories if cat in ['meat', 'plant_protein', 'seafood'])
        carbo_count = sum(1 for cat in matched_categories if cat == 'grain')
        vegetable_count = sum(1 for cat in matched_categories if cat in ['vegetable', 'fruit'])
        
        importance_bonus = (
            protein_count * 0.3 +
            carbo_count * 0.2 +
            vegetable_count * 0.1
        )
        
        return base_match_ratio, importance_bonus
    
    def calculate_serendipity_score(self, match_ratio: float) -> float:
        """Calculate serendipity score (sweet spot: 0.3-0.7)"""
        if 0.3 <= match_ratio <= 0.7:
            return 1.0  # Perfect serendipity
        elif 0.7 < match_ratio <= 0.8:
            return 0.5  # Slightly too similar
        elif 0.2 < match_ratio < 0.3:
            return 0.3  # Slightly too different
        else:
            return 0.0  # Too similar or too different
    
    def calculate_history_score(
        self, 
        session, 
        user_id: str, 
        recipe_id: str,
        recipe_ingredients: List[str],
        recipe_cuisines: List[str]
    ) -> Tuple[float, int]:
        """
        Calculate interaction history score.
        Returns: (history_score, similar_interacted_count)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(interacted:Recipe)
        WHERE interacted IS NOT NULL
        WITH iv, interacted,
            CASE 
                WHEN iv.event_type = 'like' THEN 3.0
                WHEN iv.event_type = 'rating' THEN 2.0
                WHEN iv.event_type = 'view' THEN 1.0
                ELSE 0.5
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv.timestamp, datetime()).days / 30.0)
            END AS recency
        OPTIONAL MATCH (interacted)-[:HAS_INGREDIENT]->(ri:Ingredient)
        WITH iv, interacted, interaction_weight, recency,
            collect(DISTINCT ri.ingredient_id) AS interacted_ingredients,
            interacted.cuisine AS interacted_cuisines
        WITH interaction_weight, recency, interacted, interacted_ingredients, interacted_cuisines,
            size([ing IN $recipe_ingredients WHERE ing IN interacted_ingredients]) AS shared_ing_count,
            CASE 
                WHEN any(c IN $recipe_cuisines WHERE c IN coalesce(interacted_cuisines, [])) THEN 1.0
                ELSE 0.0
            END AS shared_cuisine
        WITH interaction_weight, recency, interacted, shared_ing_count, shared_cuisine,
            toFloat(shared_ing_count) / toFloat(size($recipe_ingredients) + 1.0) * 0.5 + 
            shared_cuisine * 0.5 AS similarity
        WHERE shared_ing_count > 0 OR shared_cuisine > 0
        RETURN 
            sum(interaction_weight * recency * similarity) AS history_score,
            count(DISTINCT interacted) AS similar_count
        """
        
        result = session.run(
            q,
            uid=user_id,
            recipe_ingredients=recipe_ingredients,
            recipe_cuisines=recipe_cuisines
        ).single()
        
        if result:
            return (
                result.get("history_score", 0.0) or 0.0,
                result.get("similar_count", 0) or 0
            )
        return 0.0, 0
    
    def calculate_demographic_signal(
        self,
        session,
        user_id: str,
        recipe_id: str,
        group_cuisines: List[str],
        group_categories: List[str],
        group_extractor: Optional['GroupPreferencesExtractor'] = None,
        user_gender: Optional[str] = None,
        user_age_group: Optional[str] = None
    ) -> float:
        """
        Calculate demographic group signal using POPULAR_IN relationship.
        Enhanced with group preferences extractor for better accuracy.
        
        Updated: Supports users with only gender OR only age_group.
        """
        # First check POPULAR_IN relationship (most direct signal)
        pop_score = 0.0
        is_popular = False
        
        if group_extractor and (user_gender or user_age_group):
            is_popular, pop_score = group_extractor.is_popular_in_group(
                session, recipe_id, user_gender or 'unknown', user_age_group or 'unknown'
            )
        
        # Also check via user's group relationship
        q = """
        MATCH (u:User {user_id: $uid})-[:BELONGS_TO]->(g:Group)
        OPTIONAL MATCH (g)-[pop:POPULAR_IN]->(r:Recipe {recipe_id: $rid})
        WITH g, pop, r,
            coalesce(pop.score, 0) AS pop_score_from_query,
            CASE WHEN pop IS NOT NULL THEN 1 ELSE 0 END AS is_popular_from_query
        WITH is_popular_from_query, pop_score_from_query,
            CASE 
                WHEN size($group_cuisines) > 0 AND any(rc IN [c IN r.cuisine | toLower(c)] WHERE rc IN $group_cuisines)
                THEN 1 ELSE 0 
            END AS matches_cuisine,
            CASE 
                WHEN size($group_categories) > 0 AND r.recipe_category IN $group_categories
                THEN 1 ELSE 0 
            END AS matches_category
        RETURN 
            is_popular_from_query,
            pop_score_from_query,
            matches_cuisine,
            matches_category
        """
        
        result = session.run(
            q,
            uid=user_id,
            rid=recipe_id,
            group_cuisines=group_cuisines,
            group_categories=group_categories
        ).single()
        
        # Use result from query if available, otherwise use extractor result
        if result:
            is_popular = result.get("is_popular_from_query", 0) == 1 or is_popular
            pop_score = result.get("pop_score_from_query", 0.0) or pop_score
            matches_cuisine = result.get("matches_cuisine", 0) or 0
            matches_category = result.get("matches_category", 0) or 0
        else:
            matches_cuisine = 0
            matches_category = 0
        
        # Calculate composite demographic signal
        demo_signal = (
            (1.0 if is_popular else 0.0) * 2.0 +  # POPULAR_IN relationship (weight: 2.0)
            matches_cuisine * 1.5 +                # Cuisine matches group preference (weight: 1.5)
            matches_category * 1.0 +               # Category matches group preference (weight: 1.0)
            (log(1.0 + float(pop_score)) * 0.5 if pop_score > 0 else 0.0)  # Log-scaled popularity score
        )
        
        return demo_signal
    
    # Removed: calculate_text_similarity() - TF-IDF not needed
    # Reason: Not used in sorting, redundant with History Score, performance overhead
    # History Score already covers similarity with past interactions (ingredients + cuisines)
    # def calculate_text_similarity(...):
    #     """Calculate TF-IDF cosine similarity - REMOVED"""
    
    def calculate_similar_user_score(
        self,
        session,
        user_id: str,
        recipe_id: str
    ) -> Tuple[float, int]:
        """
        Calculate score from similar users who interacted with this recipe.
        Uses SIMILAR_USER relationship.
        Returns: (similar_user_score, similar_user_count)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[sim:SIMILAR_USER]->(u2:User)-[iv:INTERACTED_WITH]->(r:Recipe {recipe_id: $rid})
        WITH sim, iv, u2,
            CASE 
                WHEN iv.event_type = 'like' THEN 3.0
                WHEN iv.event_type = 'rating' THEN 2.0
                WHEN iv.event_type = 'view' THEN 1.0
                ELSE 0.5
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv.timestamp, datetime()).days / 30.0)
            END AS recency,
            coalesce(sim.score, 0.0) AS similarity_score
        RETURN 
            sum(interaction_weight * recency * similarity_score) AS similar_user_score,
            count(DISTINCT u2) AS similar_user_count
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id).single()
        if result:
            return (
                result.get("similar_user_score", 0.0) or 0.0,
                result.get("similar_user_count", 0) or 0
            )
        return 0.0, 0
    
    def calculate_similar_recipe_score(
        self,
        session,
        user_id: str,
        recipe_id: str
    ) -> Tuple[float, int]:
        """
        Calculate score from recipes similar to user's liked recipes.
        Uses SIMILAR_NUTRITION relationship (replaced SIMILAR_RECIPE).
        Returns: (similar_recipe_score, similar_recipe_count)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(liked:Recipe)
        WHERE iv.liked = true OR iv.rating >= 4.0
        MATCH (liked)-[sim:SIMILAR_NUTRITION]->(r:Recipe {recipe_id: $rid})
        WITH sim, iv, liked,
            CASE 
                WHEN iv.event_type = 'like' THEN 3.0
                WHEN iv.event_type = 'rating' THEN 2.0
                WHEN iv.event_type = 'view' THEN 1.0
                ELSE 0.5
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv.timestamp, datetime()).days / 30.0)
            END AS recency,
            coalesce(sim.similarity, 0.0) AS similarity_score
        RETURN 
            sum(interaction_weight * recency * similarity_score) AS similar_recipe_score,
            count(DISTINCT liked) AS similar_recipe_count
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id).single()
        if result:
            return (
                result.get("similar_recipe_score", 0.0) or 0.0,
                result.get("similar_recipe_count", 0) or 0
            )
        return 0.0, 0
    
    def calculate_nutrition_match_score(
        self,
        session,
        user_id: str,
        recipe_id: str
    ) -> Tuple[float, bool]:
        """
        Calculate nutrition match score between user preferences and recipe nutrition.
        Uses user nutrition preferences (7 core nutrients) and recipe HAS_NUTRITION relationships.
        Returns: (nutrition_match_score, has_nutrition_data)
        
        Based on NRKG approach: cosine similarity on normalized 7-dimensional nutrition vectors.
        """
        q = """
        MATCH (u:User {user_id: $uid})
        MATCH (r:Recipe {recipe_id: $rid})-[rel:HAS_NUTRITION]->(n:Nutrition)
        WHERE n.nutrition_id IN ['calories', 'total_fat', 'saturated_fat', 'sodium', 'protein', 'total_sugars', 'total_carbohydrate']
          AND u.nutrition_pref_calories_norm IS NOT NULL
          AND rel.normalized_value IS NOT NULL
        WITH n.nutrition_id AS nut_id,
             CASE n.nutrition_id
                 WHEN 'calories' THEN u.nutrition_pref_calories_norm
                 WHEN 'total_fat' THEN u.nutrition_pref_total_fat_norm
                 WHEN 'saturated_fat' THEN u.nutrition_pref_saturated_fat_norm
                 WHEN 'sodium' THEN u.nutrition_pref_sodium_norm
                 WHEN 'protein' THEN u.nutrition_pref_protein_norm
                 WHEN 'total_sugars' THEN u.nutrition_pref_total_sugars_norm
                 WHEN 'total_carbohydrate' THEN u.nutrition_pref_total_carbohydrate_norm
                 ELSE NULL
             END AS user_pref,
             rel.normalized_value AS recipe_nut
        ORDER BY nut_id
        WITH collect(user_pref) AS user_vec, collect(recipe_nut) AS recipe_vec
        WHERE size(user_vec) = 7 AND size(recipe_vec) = 7
          AND all(v IN user_vec WHERE v IS NOT NULL) AND all(v IN recipe_vec WHERE v IS NOT NULL)
        WITH user_vec, recipe_vec,
             reduce(dot=0.0, i IN range(0, 6) | dot + user_vec[i] * recipe_vec[i]) AS dot,
             sqrt(reduce(sum=0.0, v IN user_vec | sum + v*v)) AS norm1,
             sqrt(reduce(sum=0.0, v IN recipe_vec | sum + v*v)) AS norm2
        WITH CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS nutrition_match
        RETURN nutrition_match, true AS has_data
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id).single()
        if result and result.get("has_data"):
            return (
                float(result.get("nutrition_match", 0.0)) or 0.0,
                True
            )
        return 0.0, False
    
    def _get_cuisine_group_name(self, recipe_cuisines: List[str]) -> Optional[str]:
        """
        Determine which cuisine group the recipe belongs to.
        Returns group name (e.g., "Asian", "European", "Latin") or None.
        """
        if not recipe_cuisines:
            return None
        
        recipe_lower = [c.lower() if isinstance(c, str) else str(c).lower() for c in recipe_cuisines]
        
        # Check against cuisine groups
        for group_name, group_cuisines in self.CUISINE_GROUPS.items():
            group_lower = [c.lower() for c in group_cuisines]
            if any(rc in group_lower for rc in recipe_lower):
                return group_name
        
        return None


# =========================================================
# 🧠 Knowledge-Based Recommender (Enhanced)
# =========================================================

class EnhancedKnowledgeRecommender:
    """
    Enhanced knowledge-based recommender that uses knowledge_based_recommender.py
    as base and adds additional scoring capabilities.
    """
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
        
        # Use knowledge-based recommender as base if available
        if KnowledgeBasedRecommender:
            try:
                # Get connection info from driver
                uri = getattr(driver, '_uri', None) or "bolt://localhost:7687"
                username = getattr(driver, '_auth', (None, None))[0] or "neo4j"
                password = getattr(driver, '_auth', (None, None))[1] or "Admin123!"
                
                self.kb_recommender = KnowledgeBasedRecommender(
                    uri=uri,
                    username=username,
                    password=password,
                    database=database
                )
            except Exception as e:
                print(f"⚠️ Warning: Could not initialize KB recommender: {e}", file=sys.stderr)
                self.kb_recommender = None
        else:
            self.kb_recommender = None
        
        # Initialize components
        self.ingredient_matcher = IngredientMatcher(driver, database)
        self.cuisine_prioritizer = CuisinePrioritizer()
        self.scoring_engine = ScoringEngine(driver, database)
    
    def extract_user_knowledge(self, session, user_id: str) -> Optional[UserKnowledge]:
        """Extract user knowledge using KB recommender if available"""
        if self.kb_recommender:
            return self.kb_recommender.extract_user_knowledge(session, user_id)
        return None
    
    def extract_group_knowledge(self, session, gender: str, age_group: str) -> Optional[GroupKnowledge]:
        """Extract group knowledge using KB recommender if available"""
        if self.kb_recommender:
            return self.kb_recommender.extract_group_knowledge(session, gender, age_group)
        return None
    
    def apply_knowledge_rules(
        self,
        user_knowledge: Optional[UserKnowledge],
        recipe_knowledge: Optional[RecipeKnowledge],
        group_knowledge: Optional[GroupKnowledge]
    ) -> Tuple[bool, List[str], float]:
        """
        Apply knowledge-based rules.
        Returns: (should_include, reasons, rule_score)
        """
        if not self.kb_recommender or not user_knowledge or not recipe_knowledge:
            return True, [], 0.0
        
        reasons = []
        rule_score = 0.0
        
        # Rule 1: Allergen safety (HARD CONSTRAINT)
        is_safe, safety_reason = self.kb_recommender.rule_allergen_safety(
            user_knowledge, recipe_knowledge
        )
        if not is_safe:
            return False, ["❌ Contains allergens"], 0.0
        if safety_reason:
            reasons.append(str(safety_reason))
        
        # Rule 2: Time constraint (HARD CONSTRAINT)
        fits_time, time_reason = self.kb_recommender.rule_time_constraint(
            user_knowledge, recipe_knowledge
        )
        if not fits_time:
            return False, ["❌ Takes too long to cook"], 0.0
        if time_reason:
            reasons.append(str(time_reason))
            rule_score += 0.1
        
        # Rule 3: Cuisine preference (SOFT CONSTRAINT)
        cuisine_reason = self.kb_recommender.rule_cuisine_preference(
            user_knowledge, recipe_knowledge
        )
        if cuisine_reason:
            reasons.append(str(cuisine_reason))
            rule_score += 0.2
        
        # Rule 4: Group popularity (SOFT CONSTRAINT)
        group_reason = self.kb_recommender.rule_group_popularity(
            group_knowledge, recipe_knowledge
        )
        if group_reason:
            reasons.append(str(group_reason))
            rule_score += 0.15
        
        # Rule 5: Category match (SOFT CONSTRAINT)
        category_reason = self.kb_recommender.rule_category_match(
            user_knowledge, recipe_knowledge
        )
        if category_reason:
            reasons.append(str(category_reason))
            rule_score += 0.1
        
        return True, reasons, rule_score


# =========================================================
# 🎯 Main Refactored Recommender
# =========================================================

class GraphHybridRecommender:
    """
    Refactored graph-based hybrid recommender with modular design.
    Uses knowledge-based approach as foundation.
    """
    
    def __init__(self, uri="bolt://localhost:7687", username="neo4j",
                 password="Admin123!", database="test"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        
        # Initialize components
        self.kb_recommender = EnhancedKnowledgeRecommender(self.driver, database)
        self.ingredient_matcher = IngredientMatcher(self.driver, database)
        self.cuisine_prioritizer = CuisinePrioritizer()
        self.scoring_engine = ScoringEngine(self.driver, database)
        self.group_extractor = GroupPreferencesExtractor(self.driver, database)
    
    def close(self):
        self.driver.close()
    
    def recommend(
        self,
        user_id: Optional[str] = None,
        ingredient_ids: Optional[List[str]] = None,
        ingredient_names: Optional[List[str]] = None,
        limit: int = 30,
        min_match_ratio: float = 0.3,
        max_cook_time: Optional[int] = None,
        recipe_category: Optional[str] = None,
        preferred_cuisines: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Main recommendation entrypoint (refactored).
        Uses knowledge-based approach as foundation with additional scoring.
        """
        with self.driver.session(database=self.database) as session:
            # Step 1: Map ingredient names to IDs
            mapped_ids = []
            if ingredient_names:
                mapped_ids = self.ingredient_matcher.map_names_to_ids(session, ingredient_names)
            
            # Combine ingredient IDs
            all_ingredient_ids = list(set((ingredient_ids or []) + mapped_ids))
            if not all_ingredient_ids:
                return []
            
            # Step 2: Build ingredient match context
            match_context = self.ingredient_matcher.build_match_context(session, all_ingredient_ids)
            
            # Step 3: Extract knowledge (if user_id provided)
            user_knowledge = None
            group_knowledge = None
            group_prefs = None
            user_gender = None
            user_age_group = None
            
            # Step 3a: Determine dietary plan (if user_id provided)
            user_dietary_plan = None
            if user_id:
                # Get user profile to check dietary plan
                q_user_profile = """
                MATCH (u:User {user_id: $uid})
                RETURN u.dietary_plan AS dietary_plan,
                       u.auto_dietary_plan AS auto_dietary_plan,
                       u.weight_kg AS weight_kg,
                       u.height_cm AS height_cm,
                       u.bmi AS bmi
                """
                user_profile_result = session.run(q_user_profile, uid=user_id).single()
                if user_profile_result:
                    user_dietary_plan = user_profile_result.get("dietary_plan")
                    auto_dietary_plan = user_profile_result.get("auto_dietary_plan", False)
                    weight_kg = user_profile_result.get("weight_kg")
                    height_cm = user_profile_result.get("height_cm")
                    bmi = user_profile_result.get("bmi")
                    
                    # If auto_dietary_plan is True, calculate from BMI
                    if not user_dietary_plan and auto_dietary_plan:
                        if bmi:
                            user_dietary_plan = get_dietary_plan_from_bmi(bmi)
                        elif weight_kg and height_cm:
                            calculated_bmi = calculate_bmi(weight_kg, height_cm)
                            user_dietary_plan = get_dietary_plan_from_bmi(calculated_bmi)
                    
                    if user_dietary_plan:
                        print(f"🥗 User dietary plan: {user_dietary_plan}", file=sys.stderr)
            
            if user_id:
                user_knowledge = self.kb_recommender.extract_user_knowledge(session, user_id)
                if user_knowledge:
                    user_gender = user_knowledge.gender
                    user_age_group = user_knowledge.age_group
                    
                    # Extract group knowledge (from KB recommender)
                    group_knowledge = self.kb_recommender.extract_group_knowledge(
                        session, user_gender, user_age_group
                    )
                    
                    # Extract group preferences (including POPULAR_IN)
                    group_prefs = self.group_extractor.get_group_preferences(
                        session, user_gender, user_age_group
                    )
                    
                    # Log group preferences for debugging
                    if group_prefs and group_prefs.get('group_size', 0) > 0:
                        print(f"👥 Group Preferences (gender={user_gender}, age_group={user_age_group}):", file=sys.stderr)
                        print(f"  - Group size: {group_prefs.get('group_size', 0)} users", file=sys.stderr)
                        group_cuisines = [c.get('cuisine', '') for c in group_prefs.get('popular_cuisines', [])[:3]]
                        group_categories = [c.get('category', '') for c in group_prefs.get('popular_categories', [])]
                        print(f"  - Popular cuisines: {group_cuisines}", file=sys.stderr)
                        print(f"  - Popular categories: {group_categories}", file=sys.stderr)
                        popular_recipes_count = len(group_prefs.get('popular_recipes', []))
                        print(f"  - Popular recipes (via POPULAR_IN): {popular_recipes_count}", file=sys.stderr)
            
            # Step 4: Determine max_cook_time (use user_knowledge.maxTime if available)
            effective_max_cook_time = max_cook_time
            if user_knowledge and user_knowledge.max_cook_time and not effective_max_cook_time:
                effective_max_cook_time = user_knowledge.max_cook_time
            
            # Step 5: Get user allergies for filtering
            user_allergies = []
            if user_knowledge and user_knowledge.allergies:
                user_allergies = user_knowledge.allergies
            
            # Step 6: Combine preferred_cuisines with user profile fav_cuisines
            effective_preferred_cuisines = list(set((preferred_cuisines or []) + (user_knowledge.favorite_cuisines if user_knowledge and user_knowledge.favorite_cuisines else [])))
            
            # Step 7: Find candidate recipes (smaller, focused query)
            candidates = self._find_candidate_recipes(
                session,
                all_ingredient_ids,
                match_context,
                effective_max_cook_time,
                min_match_ratio,
                user_allergies,  # Add allergen filter
                limit * 3  # Get more candidates
            )
            
            # Log recipe_category for debugging
            if recipe_category:
                print(f"🍽️ User preferred meal type: {recipe_category}", file=sys.stderr)
            
            # Step 7a: Filter by dietary plan (if exists)
            if user_dietary_plan:
                filtered_candidates = []
                for candidate in candidates:
                    recipe_id = candidate.get('recipe_id')
                    
                    # Try to read classification flags from Recipe node (pre-computed in compute_features_improve.py)
                    q_flags = """
                    MATCH (r:Recipe {recipe_id: $rid})
                    RETURN r.is_low_carb AS is_low_carb,
                           r.is_high_protein AS is_high_protein,
                           r.is_keto AS is_keto,
                           r.is_low_fat AS is_low_fat
                    """
                    flags_result = session.run(q_flags, rid=recipe_id).single()
                    
                    if flags_result and flags_result.get("is_low_carb") is not None:
                        # Flags already computed and stored in DB
                        candidate.update({
                            "is_low_carb": flags_result.get("is_low_carb", False),
                            "is_high_protein": flags_result.get("is_high_protein", False),
                            "is_keto": flags_result.get("is_keto", False),
                            "is_low_fat": flags_result.get("is_low_fat", False)
                        })
                    else:
                        # Fallback: Compute classification on-the-fly if flags not in DB
                        # Get recipe nutrition to classify
                        q_nutrition = """
                        MATCH (r:Recipe {recipe_id: $rid})-[rel:HAS_NUTRITION]->(n:Nutrition)
                        WHERE n.nutrition_id IN ['calories', 'total_fat', 'total_carbohydrate', 'protein', 
                                                 'saturated_fat', 'total_sugars', 'dietary_fiber', 'sodium', 'cholesterol']
                        RETURN n.nutrition_id AS nut_id, rel.original_value AS value
                        ORDER BY nut_id
                        """
                        nutrition_result = session.run(q_nutrition, rid=recipe_id)
                        nutrition_dict = {}
                        for record in nutrition_result:
                            nut_id = record.get("nut_id")
                            value = record.get("value")
                            if nut_id and value is not None:
                                # Map nutrition_id to classify_recipe keys
                                if nut_id == "total_fat":
                                    nutrition_dict["total_fat"] = float(value)
                                elif nut_id == "total_carbohydrate":
                                    nutrition_dict["total_carbohydrate"] = float(value)
                                elif nut_id == "protein":
                                    nutrition_dict["protein"] = float(value)
                                elif nut_id == "saturated_fat":
                                    nutrition_dict["saturated_fat"] = float(value)
                                elif nut_id == "total_sugars":
                                    nutrition_dict["total_sugars"] = float(value)
                                elif nut_id == "dietary_fiber":
                                    nutrition_dict["dietary_fiber"] = float(value)
                                elif nut_id == "sodium":
                                    nutrition_dict["sodium"] = float(value)
                                elif nut_id == "cholesterol":
                                    nutrition_dict["cholesterol"] = float(value)
                        
                        # Classify recipe if we have nutrition data
                        if nutrition_dict and classify_recipe_from_features:
                            classification = classify_recipe_from_features(nutrition_dict)
                            candidate.update({
                                "is_low_carb": classification.get("low_carb", False),
                                "is_high_protein": classification.get("high_protein", False),
                                "is_keto": classification.get("keto", False),
                                "is_low_fat": classification.get("low_fat", False)
                            })
                        else:
                            # No nutrition data or classify_recipe not available, set all to False
                            candidate.update({
                                "is_low_carb": False,
                                "is_high_protein": False,
                                "is_keto": False,
                                "is_low_fat": False
                            })
                    
                    # Filter by dietary plan
                    if filter_recipe_by_dietary_plan(candidate, user_dietary_plan):
                        filtered_candidates.append(candidate)
                
                candidates = filtered_candidates
                print(f"🥗 Filtered {len(candidates)} recipes for dietary plan: {user_dietary_plan}", file=sys.stderr)
            
            # Step 5: Score and rank candidates
            recommendations = []
            for candidate in candidates:
                recipe_id = candidate['recipe_id']
                
                # Extract recipe knowledge
                recipe_knowledge = None
                if self.kb_recommender.kb_recommender:
                    recipe_knowledge = self.kb_recommender.kb_recommender.extract_recipe_knowledge(
                        session, recipe_id
                    )
                
                # Apply knowledge rules
                if user_knowledge and recipe_knowledge:
                    should_include, kb_reasons, kb_score = self.kb_recommender.apply_knowledge_rules(
                        user_knowledge, recipe_knowledge, group_knowledge
                    )
                    if not should_include:
                        continue
                    
                    # Filter out cuisine-related reasons from kb_reasons to avoid duplicates
                    # (cuisine reasoning is handled by _build_additional_reasoning based on cuisine_priority)
                    kb_reasons = [
                        str(reason) for reason in kb_reasons 
                        if not (isinstance(reason, str) and (
                            'cuisine' in reason.lower() or 
                            'Matches your favorite' in reason or
                            'Similar to your preferred' in reason
                        ))
                    ]
                else:
                    kb_reasons = []
                    kb_score = 0.0
                
                # Calculate additional scores
                match_ratio = candidate.get('match_ratio', 0.0)
                cuisine_priority = self.cuisine_prioritizer.calculate_priority(
                    candidate.get('cuisine', []),
                    effective_preferred_cuisines  # Use combined cuisines
                )
                
                # Calculate other scores (if user_id provided)
                history_score = 0.0
                demo_signal = 0.0
                is_popular_in_group = False
                group_popularity_score = 0.0
                similar_user_score = 0.0
                similar_user_count = 0
                similar_recipe_score = 0.0
                similar_recipe_count = 0
                nutrition_match_score = 0.0
                has_nutrition_data = False
                
                if user_id:
                    history_score, _ = self.scoring_engine.calculate_history_score(
                        session, user_id, recipe_id,
                        candidate.get('all_ingredients', []),
                        candidate.get('cuisine', [])
                    )
                    
                    # Calculate similar user score (SIMILAR_USER relationship)
                    similar_user_score, similar_user_count = self.scoring_engine.calculate_similar_user_score(
                        session, user_id, recipe_id
                    )
                    
                    # Calculate similar recipe score (SIMILAR_NUTRITION relationship)
                    similar_recipe_score, similar_recipe_count = self.scoring_engine.calculate_similar_recipe_score(
                        session, user_id, recipe_id
                    )
                    
                    # Calculate nutrition match score (user preferences vs recipe nutrition)
                    # Only use if user does NOT have dietary plan
                    if user_dietary_plan:
                        # Dietary plan mode: no nutrition preference scoring
                        # Recipes already filtered, just use other scores
                        nutrition_match_score = 0.0
                        has_nutrition_data = True
                    else:
                        # Normal mode: use nutrition preferences
                        nutrition_match_score, has_nutrition_data = self.scoring_engine.calculate_nutrition_match_score(
                            session, user_id, recipe_id
                        )
                    
                    # Get group preferences (from group_prefs or group_knowledge)
                    if group_prefs:
                        group_cuisines = [c.get('cuisine', '') for c in group_prefs.get('popular_cuisines', [])]
                        group_categories = [c.get('category', '') for c in group_prefs.get('popular_categories', [])]
                    elif group_knowledge:
                        group_cuisines = [c[0] for c in (group_knowledge.popular_cuisines or [])]
                        group_categories = [c[0] for c in (group_knowledge.popular_categories or [])]
                    else:
                        group_cuisines = []
                        group_categories = []
                    
                    # Calculate demographic signal (with POPULAR_IN support)
                    demo_signal = self.scoring_engine.calculate_demographic_signal(
                        session, user_id, recipe_id, 
                        group_cuisines, group_categories,
                        group_extractor=self.group_extractor,
                        user_gender=user_gender,
                        user_age_group=user_age_group
                    )
                    
                    # Check POPULAR_IN relationship directly
                    if user_gender and user_age_group:
                        is_popular_in_group, group_popularity_score = self.group_extractor.is_popular_in_group(
                            session, recipe_id, user_gender, user_age_group
                        )
                        # Boost demo_signal if recipe is popular in group
                        if is_popular_in_group:
                            demo_signal += log(1.0 + float(group_popularity_score)) * 0.3
                
                serendipity_score = self.scoring_engine.calculate_serendipity_score(match_ratio)
                
                # Popular unexplored boost (if recipe is popular but user hasn't interacted)
                popular_unexplored_boost = 1.0
                if is_popular_in_group and group_popularity_score > 10:
                    # Check if user has interacted with this recipe
                    q_check_interaction = """
                    MATCH (u:User {user_id: $uid})
                    MATCH (r:Recipe {recipe_id: $rid})
                    RETURN EXISTS((u)-[:INTERACTED_WITH]->(r)) AS has_interacted
                    """
                    check_result = session.run(q_check_interaction, uid=user_id, rid=recipe_id).single()
                    has_interacted = check_result.get("has_interacted", False) if check_result else False
                    
                    if not has_interacted:
                        if group_popularity_score > 20:
                            popular_unexplored_boost = 1.5  # Very popular, unexplored
                        elif group_popularity_score > 10:
                            popular_unexplored_boost = 1.2  # Popular, unexplored
                
                # Build final recommendation
                recommendations.append({
                    'recipe_id': recipe_id,
                    'title': candidate.get('title'),
                    'cuisine': candidate.get('cuisine', []),
                    'tags': candidate.get('tags', []),
                    'recipe_category': candidate.get('recipe_category'),
                    'meal': candidate.get('meal', 'Dinner'),
                    'match_percent': round(match_ratio * 100, 1),
                    'cook_time_min': candidate.get('cook_time_min'),
                    'prep_time_min': candidate.get('prep_time_min'),
                    'total_time_min': candidate.get('total_time_min'),
                    'servings': candidate.get('servings'),
                    'yield': candidate.get('yield'),
                    'image': candidate.get('image'),
                    'matched_ing': candidate.get('matched_ing', []),
                    'missing_ing': candidate.get('missing_ing', []),
                    'ingredients': candidate.get('ingredients', []),
                    'reasoning': (
                        # Add meal type reasoning first if matches
                        (['🍽️ Matches your preferred meal type'] if recipe_category and candidate.get('meal') == recipe_category else []) +
                        kb_reasons + 
                        self._build_additional_reasoning(
                        match_ratio, cuisine_priority, history_score,
                        is_popular_in_group, group_popularity_score, group_prefs,
                    candidate.get('cuisine', []), candidate.get('recipe_category'),
                    similar_user_count, similar_recipe_count,
                    candidate.get('avg_rating', 0.0),  # Add rating for reasoning
                    candidate.get('global_like_count', 0),  # Add global likes for reasoning
                    nutrition_match_score, has_nutrition_data,  # Add nutrition match for reasoning
                    user_dietary_plan=user_dietary_plan,  # Add dietary plan for reasoning
                    cuisine_prioritizer=self.cuisine_prioritizer  # Pass prioritizer for group name
                        )
                    ),
                    # Store scores for sorting (will be removed later)
                    '_similar_user_score': similar_user_score,
                    '_similar_recipe_score': similar_recipe_score,
                    '_nutrition_match_score': nutrition_match_score,
                    # Global popularity metrics (from candidate query)
                    'avg_rating': candidate.get('avg_rating', 0.0),
                    'rating_count': candidate.get('rating_count', 0),
                    'global_like_count': candidate.get('global_like_count', 0),
                    'global_view_count': candidate.get('global_view_count', 0)
                })
            
            # Step 6: Sort by multiple factors (including group popularity, similar users, similar recipes, rating)
            # Add group popularity for sorting (similar scores already calculated and stored)
            for rec in recommendations:
                if user_id and user_gender and user_age_group:
                    recipe_id = rec.get('recipe_id')
                    is_pop, pop_score = self.group_extractor.is_popular_in_group(
                        session, recipe_id, user_gender, user_age_group
                    )
                    rec['_group_popularity'] = pop_score if is_pop else 0.0
                else:
                    rec['_group_popularity'] = 0.0
                
                # Calculate meal type match bonus (soft condition - boost score only)
                meal_type_bonus = 0.0
                if recipe_category:
                    recipe_meal = rec.get('meal', '')
                    # Boost if meal type matches user preference
                    if recipe_meal == recipe_category:
                        meal_type_bonus = 0.3  # Strong boost for exact match
                    # Also boost if user prefers "Main Dishes" and recipe is Breakfast/Lunch/Dinner
                    elif recipe_category == 'Main Dishes' and recipe_meal in ['Breakfast', 'Lunch', 'Dinner']:
                        meal_type_bonus = 0.15  # Partial boost
                    # Boost if recipe is in related category
                    elif recipe_category in ['Breakfast', 'Lunch', 'Dinner'] and recipe_meal == 'Main Dishes':
                        meal_type_bonus = 0.15  # Partial boost
                
                # Calculate composite score (includes similar scores + nutrition match + rating + global popularity + meal type bonus)
                rec['_composite_score'] = (
                    rec.get('_similar_user_score', 0.0) * 0.25 +  # Weight: 0.25 for similar users
                    rec.get('_similar_recipe_score', 0.0) * 0.25 +  # Weight: 0.25 for similar recipes
                    rec.get('_nutrition_match_score', 0.0) * 0.15 +  # Weight: 0.15 for nutrition match (NRKG)
                    (rec.get('avg_rating', 0.0) / 5.0) * 0.1 +  # Weight: 0.1 for rating (normalized to 0-1)
                    (min(rec.get('global_like_count', 0) / 100.0, 1.0)) * 0.1 +  # Weight: 0.1 for global likes (capped at 100)
                    rec.get('_group_popularity', 0.0) * 0.05 +  # Weight: 0.05 for group popularity
                    meal_type_bonus  # Weight: 0.3 for meal type match (soft boost)
                )
            
            recommendations.sort(
                key=lambda x: (
                    self.cuisine_prioritizer.calculate_priority(
                        x.get('cuisine', []),
                        effective_preferred_cuisines  # Use combined cuisines
                    ),
                    -x.get('match_percent', 0) / 100.0,
                    -x.get('_composite_score', 0.0),  # Use composite score (includes similar scores + rating + popularity)
                    -len(x.get('reasoning', []))
                )
            )
            
            # Step 7: Ensure minimum number of preferred cuisine recipes
            # Calculate minimum required: 10-20% of limit (10-20 recipes out of 100)
            if effective_preferred_cuisines:
                min_preferred_count = max(10, int(limit * 0.10))  # 15% of limit, minimum 10
                preferred_cuisine_lower = [c.lower() for c in effective_preferred_cuisines]
                
                # Count how many preferred cuisine recipes we have
                preferred_recipes = [
                    rec for rec in recommendations
                    if any(
                        pref_cuisine in [c.lower() if isinstance(c, str) else str(c).lower() for c in rec.get('cuisine', [])]
                        for pref_cuisine in preferred_cuisine_lower
                    )
                ]
                preferred_count = len(preferred_recipes)
                
                # If we don't have enough preferred cuisine recipes, find more
                if preferred_count < min_preferred_count:
                    needed_count = min_preferred_count - preferred_count
                    print(f"⚠️ Only found {preferred_count} preferred cuisine recipes, need {min_preferred_count}. Searching for {needed_count} more...", file=sys.stderr)
                    
                    # Get existing recipe IDs to avoid duplicates
                    existing_ids = {rec['recipe_id'] for rec in recommendations}
                    
                    # Find additional preferred cuisine recipes with relaxed match ratio
                    additional_preferred = self._find_preferred_cuisine_recipes(
                        session,
                        all_ingredient_ids,
                        match_context,
                        effective_preferred_cuisines,
                        effective_max_cook_time,
                        min_match_ratio * 0.7,  # Relaxed match ratio (50% of original)
                        user_allergies,
                        needed_count * 2,  # Get more candidates
                        existing_ids,
                        user_id,
                        user_knowledge,
                        group_knowledge,
                        group_prefs,
                        user_gender,
                        user_age_group,
                        user_dietary_plan  # Pass dietary plan for filtering
                    )
                    
                    # Add to recommendations
                    recommendations.extend(additional_preferred)
                    
                    # Re-sort after adding more preferred cuisine recipes
                    recommendations.sort(
                        key=lambda x: (
                            self.cuisine_prioritizer.calculate_priority(
                                x.get('cuisine', []),
                                effective_preferred_cuisines
                            ),
                            -x.get('match_percent', 0) / 100.0,
                            -x.get('_composite_score', 0.0),
                            -len(x.get('reasoning', []))
                        )
                    )
                    
                    print(f"✅ Added {len(additional_preferred)} more preferred cuisine recipes. Total preferred: {len([r for r in recommendations if any(pref_cuisine in [c.lower() if isinstance(c, str) else str(c).lower() for c in r.get('cuisine', [])] for pref_cuisine in preferred_cuisine_lower)])}", file=sys.stderr)
            
            # Remove temporary sorting fields
            for rec in recommendations:
                rec.pop('_group_popularity', None)
                rec.pop('_similar_user_score', None)
                rec.pop('_similar_recipe_score', None)
                rec.pop('_nutrition_match_score', None)
                rec.pop('_composite_score', None)
            
            return recommendations[:limit]
    
    def _find_candidate_recipes(
        self,
        session,
        ingredient_ids: List[str],
        match_context: IngredientMatchContext,
        max_cook_time: Optional[int],
        min_match_ratio: float,
        user_allergies: List[str],
        limit: int
    ) -> List[Dict]:
        """
        Find candidate recipes using a focused, smaller query.
        This replaces the massive 600-line query with a simpler one.
        
        Filters:
        - max_cook_time: Hard constraint (from user profile or parameter)
        - user_allergies: Hard constraint (filter early for safety)
        """
        q = """
        // Find recipes with matching ingredients
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE 
            i.ingredient_id IN $input_ing
            OR (i.base IS NOT NULL AND toLower(i.base) IN $input_bases)
            OR toLower(i.canonical_name) IN $input_synonyms
            OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) IN $input_synonyms)
        AND ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
        
        WITH r, collect(DISTINCT i.ingredient_id) AS matched_ing,
             collect(DISTINCT i.category) AS matched_categories
        WHERE size(matched_ing) >= CASE WHEN size($input_ing) >= 4 THEN 2 ELSE 1 END
        
        // Get all recipe ingredients (for allergen check)
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, matched_categories, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens early (HARD CONSTRAINT - safety first)
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        
        WITH r, matched_ing, matched_categories, all_ing, size(all_ing) AS ing_count
        
        // Calculate base Jaccard match ratio
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             CASE 
                 WHEN ing_count = 0 THEN 0.0
                 ELSE toFloat(size(matched_ing)) / 
                      toFloat(ing_count + size($input_ing) - size(matched_ing))
             END AS base_match_ratio,
             // Calculate ingredient importance bonus
             // Protein (meat, plant_protein, seafood): +0.3 per match
             // Carbo (grain): +0.2 per match
             // Vegetable: +0.1 per match
             (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) * 0.3 +
              size([cat IN matched_categories WHERE cat = 'grain']) * 0.2 +
              size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) * 0.1) AS importance_bonus
        
        // Calculate weighted match ratio: base + importance bonus (capped at 1.0)
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             base_match_ratio, importance_bonus,
             CASE 
                 WHEN base_match_ratio + importance_bonus > 1.0 THEN 1.0
                 ELSE base_match_ratio + importance_bonus
             END AS match_ratio
        
        WHERE match_ratio >= $min_match * CASE
            WHEN ing_count < 5 THEN 0.4
            WHEN ing_count < 10 THEN 0.25
            WHEN ing_count < 15 THEN 0.15
            ELSE 0.1
        END
        
        // Collect recipe details and global popularity metrics
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, all_ing, match_ratio,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             // Global popularity metrics
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             coalesce(toInteger(r.rating_count), 0) AS rating_count,
             sum(CASE WHEN iv.event_type = 'like' THEN 1 ELSE 0 END) AS global_like_count,
             sum(CASE WHEN iv.event_type = 'view' THEN 1 ELSE 0 END) AS global_view_count
        
        RETURN 
            r.recipe_id AS recipe_id,
            r.title AS title,
            coalesce(r.cuisine, []) AS cuisine,
            coalesce(r.tags, []) AS tags,
            r.recipe_category AS recipe_category,
            CASE 
                WHEN toLower(r.recipe_category) CONTAINS 'drink' OR
                     toLower(r.recipe_category) CONTAINS 'beverage' OR
                     toLower(r.recipe_category) CONTAINS 'cocktail' OR
                     toLower(r.recipe_category) CONTAINS 'smoothie' OR
                     toLower(r.recipe_category) CONTAINS 'juice' THEN 'Beverages'
                
                WHEN toLower(r.recipe_category) CONTAINS 'dessert' OR
                     toLower(r.recipe_category) CONTAINS 'cake' OR
                     toLower(r.recipe_category) CONTAINS 'pie' OR
                     toLower(r.recipe_category) CONTAINS 'cookie' OR
                     toLower(r.recipe_category) CONTAINS 'sweet' OR
                     toLower(r.recipe_category) CONTAINS 'pastry' OR
                     toLower(r.recipe_category) CONTAINS 'tart' THEN 'Desserts'
                
                WHEN toLower(r.recipe_category) CONTAINS 'appetizer' OR
                     toLower(r.recipe_category) CONTAINS 'starter' OR
                     toLower(r.recipe_category) CONTAINS 'hors' OR
                     toLower(r.recipe_category) CONTAINS 'finger food' THEN 'Appetizers'
                
                WHEN toLower(r.recipe_category) CONTAINS 'side' OR
                     toLower(r.recipe_category) CONTAINS 'salad' OR
                     toLower(r.recipe_category) CONTAINS 'accompaniment' THEN 'Side Dishes'
                
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR 
                     toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                
                WHEN toLower(r.recipe_category) CONTAINS 'snack' THEN 'Snacks'
                
                WHEN toLower(r.recipe_category) CONTAINS 'entree' OR
                     toLower(r.recipe_category) CONTAINS 'main' OR
                     toLower(r.recipe_category) CONTAINS 'lunch' OR
                     toLower(r.recipe_category) CONTAINS 'dinner' OR
                     r.recipe_category IS NULL OR r.recipe_category = '' THEN 'Main Dishes'
                
                ELSE 'Main Dishes'
            END AS meal,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            matched_ing,
            missing_ing,
            ingredients,
            all_ing AS all_ingredients,
            match_ratio,
            avg_rating,
            rating_count,
            global_like_count,
            global_view_count
        ORDER BY match_ratio DESC
        LIMIT $lim
        """
        
        result = session.run(
            q,
            input_ing=ingredient_ids,
            input_bases=match_context.bases,
            input_synonyms=match_context.synonyms,
            max_cook=max_cook_time,
            min_match=min_match_ratio,
            user_allergies=user_allergies or [],
            lim=limit
        )
        
        return [dict(row) for row in result]
    
    def _find_preferred_cuisine_recipes(
        self,
        session,
        ingredient_ids: List[str],
        match_context: IngredientMatchContext,
        preferred_cuisines: List[str],
        max_cook_time: Optional[int],
        min_match_ratio: float,
        user_allergies: List[str],
        limit: int,
        existing_ids: set,
        user_id: Optional[str],
        user_knowledge: Optional,
        group_knowledge: Optional,
        group_prefs: Optional[Dict],
        user_gender: Optional[str],
        user_age_group: Optional[str],
        user_dietary_plan: Optional[str] = None
    ) -> List[Dict]:
        """
        Find additional recipes from preferred cuisines with relaxed match ratio.
        Used to ensure minimum number of preferred cuisine recipes in recommendations.
        """
        preferred_cuisines_lower = [c.lower() for c in preferred_cuisines]
        
        q = """
        // Find recipes with preferred cuisine
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE 
            // Must have preferred cuisine
            any(cuisine IN r.cuisine WHERE toLower(cuisine) IN $preferred_cuisines)
            AND (
                i.ingredient_id IN $input_ing
                OR (i.base IS NOT NULL AND toLower(i.base) IN $input_bases)
                OR toLower(i.canonical_name) IN $input_synonyms
                OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) IN $input_synonyms)
            )
            AND ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
            AND NOT r.recipe_id IN $existing_ids
        
        WITH r, collect(DISTINCT i.ingredient_id) AS matched_ing,
             collect(DISTINCT i.category) AS matched_categories
        WHERE size(matched_ing) >= 1  // At least 1 ingredient match
        
        // Get all recipe ingredients (for allergen check)
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, matched_categories, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens early (HARD CONSTRAINT)
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        
        WITH r, matched_ing, matched_categories, all_ing, size(all_ing) AS ing_count
        
        // Calculate base Jaccard match ratio
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             CASE 
                 WHEN ing_count = 0 THEN 0.0
                 ELSE toFloat(size(matched_ing)) / 
                      toFloat(ing_count + size($input_ing) - size(matched_ing))
             END AS base_match_ratio,
             // Calculate ingredient importance bonus
             (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) * 0.3 +
              size([cat IN matched_categories WHERE cat = 'grain']) * 0.2 +
              size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) * 0.1) AS importance_bonus
        
        // Calculate weighted match ratio
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             base_match_ratio, importance_bonus,
             CASE 
                 WHEN base_match_ratio + importance_bonus > 1.0 THEN 1.0
                 ELSE base_match_ratio + importance_bonus
             END AS match_ratio
        
        WHERE match_ratio >= $min_match * CASE
            WHEN ing_count < 5 THEN 0.3
            WHEN ing_count < 10 THEN 0.2
            WHEN ing_count < 15 THEN 0.1
            ELSE 0.05
        END
        
        // Collect recipe details and global popularity metrics
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, all_ing, match_ratio,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             // Global popularity metrics
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             coalesce(toInteger(r.rating_count), 0) AS rating_count,
             sum(CASE WHEN iv.event_type = 'like' THEN 1 ELSE 0 END) AS global_like_count,
             sum(CASE WHEN iv.event_type = 'view' THEN 1 ELSE 0 END) AS global_view_count
        
        RETURN 
            r.recipe_id AS recipe_id,
            r.title AS title,
            coalesce(r.cuisine, []) AS cuisine,
            coalesce(r.tags, []) AS tags,
            r.recipe_category AS recipe_category,
            CASE 
                WHEN toLower(r.recipe_category) CONTAINS 'drink' OR
                     toLower(r.recipe_category) CONTAINS 'beverage' OR
                     toLower(r.recipe_category) CONTAINS 'cocktail' OR
                     toLower(r.recipe_category) CONTAINS 'smoothie' OR
                     toLower(r.recipe_category) CONTAINS 'juice' THEN 'Beverages'
                
                WHEN toLower(r.recipe_category) CONTAINS 'dessert' OR
                     toLower(r.recipe_category) CONTAINS 'cake' OR
                     toLower(r.recipe_category) CONTAINS 'pie' OR
                     toLower(r.recipe_category) CONTAINS 'cookie' OR
                     toLower(r.recipe_category) CONTAINS 'sweet' OR
                     toLower(r.recipe_category) CONTAINS 'pastry' OR
                     toLower(r.recipe_category) CONTAINS 'tart' THEN 'Desserts'
                
                WHEN toLower(r.recipe_category) CONTAINS 'appetizer' OR
                     toLower(r.recipe_category) CONTAINS 'starter' OR
                     toLower(r.recipe_category) CONTAINS 'hors' OR
                     toLower(r.recipe_category) CONTAINS 'finger food' THEN 'Appetizers'
                
                WHEN toLower(r.recipe_category) CONTAINS 'side' OR
                     toLower(r.recipe_category) CONTAINS 'salad' OR
                     toLower(r.recipe_category) CONTAINS 'accompaniment' THEN 'Side Dishes'
                
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR 
                     toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                
                WHEN toLower(r.recipe_category) CONTAINS 'snack' THEN 'Snacks'
                
                WHEN toLower(r.recipe_category) CONTAINS 'entree' OR
                     toLower(r.recipe_category) CONTAINS 'main' OR
                     toLower(r.recipe_category) CONTAINS 'lunch' OR
                     toLower(r.recipe_category) CONTAINS 'dinner' OR
                     r.recipe_category IS NULL OR r.recipe_category = '' THEN 'Main Dishes'
                
                ELSE 'Main Dishes'
            END AS meal,
            match_ratio,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            matched_ing,
            missing_ing,
            ingredients,
            all_ing AS all_ingredients,
            avg_rating,
            rating_count,
            global_like_count,
            global_view_count
        ORDER BY match_ratio DESC, avg_rating DESC, global_like_count DESC
        LIMIT $lim
        """
        
        result = session.run(
            q,
            input_ing=ingredient_ids,
            input_bases=match_context.bases,
            input_synonyms=match_context.synonyms,
            preferred_cuisines=preferred_cuisines_lower,
            max_cook=max_cook_time,
            min_match=min_match_ratio,
            user_allergies=user_allergies or [],
            existing_ids=list(existing_ids),
            lim=limit
        )
        
        candidates = [dict(row) for row in result]
        
        # Filter by dietary plan first (if provided)
        if user_dietary_plan:
            filtered_candidates = []
            for candidate in candidates:
                recipe_id = candidate.get('recipe_id')
                
                # Try to read classification flags from Recipe node
                q_flags = """
                MATCH (r:Recipe {recipe_id: $rid})
                RETURN r.is_low_carb AS is_low_carb,
                       r.is_high_protein AS is_high_protein,
                       r.is_keto AS is_keto,
                       r.is_low_fat AS is_low_fat
                """
                flags_result = session.run(q_flags, rid=recipe_id).single()
                
                if flags_result and flags_result.get("is_low_carb") is not None:
                    # Flags already computed
                    candidate.update({
                        "is_low_carb": flags_result.get("is_low_carb", False),
                        "is_high_protein": flags_result.get("is_high_protein", False),
                        "is_keto": flags_result.get("is_keto", False),
                        "is_low_fat": flags_result.get("is_low_fat", False)
                    })
                else:
                    # Fallback: compute on-the-fly
                    q_nutrition = """
                    MATCH (r:Recipe {recipe_id: $rid})-[rel:HAS_NUTRITION]->(n:Nutrition)
                    WHERE n.nutrition_id IN ['total_fat', 'total_carbohydrate', 'protein', 
                                             'saturated_fat', 'total_sugars', 'dietary_fiber', 'sodium', 'cholesterol']
                    RETURN n.nutrition_id AS nut_id, rel.original_value AS value
                    """
                    nutrition_result = session.run(q_nutrition, rid=recipe_id)
                    nutrition_dict = {}
                    for record in nutrition_result:
                        nut_id = record.get("nut_id")
                        value = record.get("value")
                        if nut_id and value is not None:
                            nutrition_dict[nut_id] = float(value)
                    
                    if nutrition_dict and classify_recipe_from_features:
                        classification = classify_recipe_from_features(nutrition_dict)
                        candidate.update({
                            "is_low_carb": classification.get("low_carb", False),
                            "is_high_protein": classification.get("high_protein", False),
                            "is_keto": classification.get("keto", False),
                            "is_low_fat": classification.get("low_fat", False)
                        })
                    else:
                        candidate.update({
                            "is_low_carb": False,
                            "is_high_protein": False,
                            "is_keto": False,
                            "is_low_fat": False
                        })
                
                # Filter by dietary plan
                if filter_recipe_by_dietary_plan(candidate, user_dietary_plan):
                    filtered_candidates.append(candidate)
            
            candidates = filtered_candidates
        
        # Process candidates similar to main recommend method
        recommendations = []
        for candidate in candidates:
            recipe_id = candidate['recipe_id']
            
            # Extract recipe knowledge
            recipe_knowledge = None
            if self.kb_recommender and self.kb_recommender.kb_recommender:
                recipe_knowledge = self.kb_recommender.kb_recommender.extract_recipe_knowledge(
                    session, recipe_id
                )
            
            # Apply knowledge rules
            if user_knowledge and recipe_knowledge:
                should_include, kb_reasons, kb_score = self.kb_recommender.apply_knowledge_rules(
                    user_knowledge, recipe_knowledge, group_knowledge
                )
                if not should_include:
                    continue
                kb_reasons = [
                    str(reason) for reason in kb_reasons 
                    if not (isinstance(reason, str) and (
                        'cuisine' in reason.lower() or 
                        'Matches your favorite' in reason or
                        'Similar to your preferred' in reason
                    ))
                ]
            else:
                kb_reasons = []
                kb_score = 0.0
            
            # Calculate scores
            match_ratio = candidate.get('match_ratio', 0.0)
            cuisine_priority = self.cuisine_prioritizer.calculate_priority(
                candidate.get('cuisine', []),
                preferred_cuisines
            )
            
            history_score = 0.0
            demo_signal = 0.0
            is_popular_in_group = False
            group_popularity_score = 0.0
            similar_user_score = 0.0
            similar_user_count = 0
            similar_recipe_score = 0.0
            similar_recipe_count = 0
            
            if user_id:
                history_score, _ = self.scoring_engine.calculate_history_score(
                    session, user_id, recipe_id,
                    candidate.get('all_ingredients', []),
                    candidate.get('cuisine', [])
                )
                
                similar_user_score, similar_user_count = self.scoring_engine.calculate_similar_user_score(
                    session, user_id, recipe_id
                )
                
                similar_recipe_score, similar_recipe_count = self.scoring_engine.calculate_similar_recipe_score(
                    session, user_id, recipe_id
                )
                
                nutrition_match_score, has_nutrition_data = self.scoring_engine.calculate_nutrition_match_score(
                    session, user_id, recipe_id
                )
                
                if group_prefs:
                    group_cuisines = [c.get('cuisine', '') for c in group_prefs.get('popular_cuisines', [])]
                    group_categories = [c.get('category', '') for c in group_prefs.get('popular_categories', [])]
                elif group_knowledge:
                    group_cuisines = [c[0] for c in (group_knowledge.popular_cuisines or [])]
                    group_categories = [c[0] for c in (group_knowledge.popular_categories or [])]
                else:
                    group_cuisines = []
                    group_categories = []
                
                demo_signal = self.scoring_engine.calculate_demographic_signal(
                    session, user_id, recipe_id, 
                    group_cuisines, group_categories,
                    group_extractor=self.group_extractor,
                    user_gender=user_gender,
                    user_age_group=user_age_group
                )
                
                if user_gender and user_age_group:
                    is_popular_in_group, group_popularity_score = self.group_extractor.is_popular_in_group(
                        session, recipe_id, user_gender, user_age_group
                    )
                    if is_popular_in_group:
                        demo_signal += log(1.0 + float(group_popularity_score)) * 0.3
            
            # Calculate composite score for sorting (includes nutrition match)
            composite_score = (
                similar_user_score * 0.25 +
                similar_recipe_score * 0.25 +
                nutrition_match_score * 0.2 +
                (candidate.get('avg_rating', 0.0) / 5.0) * 0.15 +
                (min(candidate.get('global_like_count', 0) / 100.0, 1.0)) * 0.1 +
                (group_popularity_score / 100.0 if is_popular_in_group else 0.0) * 0.05
            )
            
            # Build recommendation
            recommendations.append({
                'recipe_id': recipe_id,
                'title': candidate.get('title'),
                'cuisine': candidate.get('cuisine', []),
                'tags': candidate.get('tags', []),
                'recipe_category': candidate.get('recipe_category'),
                'meal': candidate.get('meal', 'Dinner'),
                'match_percent': round(match_ratio * 100, 1),
                'cook_time_min': candidate.get('cook_time_min'),
                'prep_time_min': candidate.get('prep_time_min'),
                'total_time_min': candidate.get('total_time_min'),
                'servings': candidate.get('servings'),
                'yield': candidate.get('yield'),
                'image': candidate.get('image'),
                'matched_ing': candidate.get('matched_ing', []),
                'missing_ing': candidate.get('missing_ing', []),
                'ingredients': candidate.get('ingredients', []),
                'reasoning': kb_reasons + self._build_additional_reasoning(
                    match_ratio, cuisine_priority, history_score,
                    is_popular_in_group, group_popularity_score, group_prefs,
                    candidate.get('cuisine', []), candidate.get('recipe_category'),
                    similar_user_count, similar_recipe_count,
                    candidate.get('avg_rating', 0.0),
                    candidate.get('global_like_count', 0),
                    nutrition_match_score, has_nutrition_data,
                    cuisine_prioritizer=self.cuisine_prioritizer
                ),
                '_similar_user_score': similar_user_score,
                '_similar_recipe_score': similar_recipe_score,
                '_composite_score': composite_score,
                'avg_rating': candidate.get('avg_rating', 0.0),
                'rating_count': candidate.get('rating_count', 0),
                'global_like_count': candidate.get('global_like_count', 0),
                'global_view_count': candidate.get('global_view_count', 0)
            })
        
        return recommendations
    
    def _build_additional_reasoning(
        self,
        match_ratio: float,
        cuisine_priority: int,
        history_score: float,
        is_popular_in_group: bool = False,
        group_popularity_score: float = 0.0,
        group_prefs: Optional[Dict] = None,
        recipe_cuisines: List[str] = None,
        recipe_category: Optional[str] = None,
        similar_user_count: int = 0,
        similar_recipe_count: int = 0,
        avg_rating: float = 0.0,
        global_like_count: int = 0,
        nutrition_match_score: float = 0.0,
        has_nutrition_data: bool = False,
        user_dietary_plan: Optional[str] = None,
        cuisine_prioritizer: Optional['CuisinePrioritizer'] = None
    ) -> List[str]:
        """Build additional reasoning explanations (enhanced with GROUP knowledge)"""
        reasons = []
        
        # Meal type reasoning (if user has meal type preference)
        if recipe_category:
            recipe_meal = recipe_category  # This is actually the meal type from the function parameter
            # Note: We pass recipe_category as the user's preferred meal type, not the actual recipe's category
            # So we need to check against the actual recipe's meal type
            # This reasoning is added in the main recommend function when we have access to rec['meal']
        
        # Dietary plan reasoning (if user has dietary plan)
        if user_dietary_plan:
            dietary_plan_names = {
                "low_carb": "Low-Carb Diet",
                "high_protein": "High-Protein Diet",
                "low_fat": "Low-Fat Diet",
                "keto": "Ketogenic Diet",
                "weight_gain": "Weight Gain (High-Protein + High-Calorie)",
                "weight_loss": "Weight Loss (Low-Carb + High-Protein + Low-Fat)"
            }
            plan_name = dietary_plan_names.get(user_dietary_plan, user_dietary_plan)
            reasons.append(f'✅ Fits your dietary plan: {plan_name}')
        
        if match_ratio >= 0.75:
            reasons.append('✅ Shares most of your given ingredients')
        elif match_ratio >= 0.5:
            reasons.append('🧂 Partially matches your given ingredients')
        elif match_ratio >= 0.3:
            reasons.append('🥄 Slightly matches your given ingredients')
        
        # Cuisine priority reasoning (avoid duplicates with kb_reasons)
        # Priority 1 = exact match with favorite cuisine
        # Priority 2 = same group as favorite cuisine (e.g., Vietnamese → Asian)
        if cuisine_priority == 1:
            reasons.append('🍜 Matches your favorite cuisine')
        elif cuisine_priority == 2:
            # Determine which cuisine group for more specific message
            if cuisine_prioritizer and recipe_cuisines:
                group_name = cuisine_prioritizer._get_cuisine_group_name_from_recipe(recipe_cuisines)
                if group_name:
                    reasons.append(f'🍲 Similar to your preferred {group_name.lower()} cuisine')
                else:
                    reasons.append('🍲 Similar to your preferred cuisine group')
            else:
                reasons.append('🍲 Similar to your preferred cuisine group')
        
        if history_score > 0.5:
            reasons.append('📚 Similar to recipes you interacted with before')
        
        # Enhanced group-based reasoning (using POPULAR_IN relationship)
        if is_popular_in_group:
            if group_popularity_score > 10:
                reasons.append('🏆 Very popular among people like you (via POPULAR_IN)')
            elif group_popularity_score > 5:
                reasons.append('🌟 Popular among people like you (via POPULAR_IN)')
            else:
                reasons.append('👥 Tried by people like you (via POPULAR_IN)')
        
        # Removed: "🍲 Cuisine preferred by your demographic group" reasoning
        # Reason: Redundant with POPULAR_IN reasoning and user's favorite cuisine reasoning
        
        # Global popularity reasoning (rating and crowd signals)
        # Note: avg_rating, rating_count, global_like_count, global_view_count are passed via candidate
        # These are added to recommendation dict but reasoning is built here if needed
        
        # Similar user reasoning (SIMILAR_USER relationship)
        if similar_user_count > 0:
            if similar_user_count > 5:
                reasons.append('👥 Liked by many users similar to you')
            elif similar_user_count > 2:
                reasons.append('👥 Liked by users similar to you')
            else:
                reasons.append('👥 Tried by a user similar to you')
        
        # Similar recipe reasoning (SIMILAR_NUTRITION relationship)
        if similar_recipe_count > 0:
            if similar_recipe_count > 3:
                reasons.append('🔗 Similar nutrition to multiple recipes you liked')
            else:
                reasons.append('🔗 Similar nutrition to a recipe you liked')
        
        # Nutrition match reasoning (user preferences vs recipe nutrition - NRKG)
        # Only show if user does NOT have dietary plan (when dietary plan is used, nutrition_match_score = 0.0)
        if not user_dietary_plan and has_nutrition_data and nutrition_match_score > 0:
            if nutrition_match_score >= 0.8:
                reasons.append('🥗 Excellent match with your nutrition preferences')
            elif nutrition_match_score >= 0.6:
                reasons.append('🥗 Good match with your nutrition preferences')
            elif nutrition_match_score >= 0.4:
                reasons.append('🥗 Reasonable match with your nutrition preferences')
        
        # Global popularity reasoning (rating and crowd signals)
        if avg_rating >= 4.5:
            reasons.append('⭐ Top-rated recipe')
        elif avg_rating >= 4.0:
            reasons.append('👍 Well-rated by users')
        
        if global_like_count > 50:
            reasons.append('❤️ Loved by many users')
        elif global_like_count > 20:
            reasons.append('👍 Popular recipe')
        
        return reasons


# =========================================================
# 🖥️ CLI Interface
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="Refactored Knowledge-Based Recipe Recommender")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--db", dest="database", default="test")
    parser.add_argument("--user-id", dest="user_id")
    parser.add_argument("--ingredients", dest="ingredients", help="Comma-separated ingredient IDs")
    parser.add_argument("--ingredient-names", dest="ingredient_names", help="Comma-separated ingredient names")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--min-match", type=float, default=0.3)
    parser.add_argument("--max-cook-time", type=int, dest="max_cook_time")
    parser.add_argument("--recipe-category", dest="recipe_category")
    parser.add_argument("--preferred-cuisines", dest="preferred_cuisines",
                       help="Comma-separated preferred cuisines")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ingredient_ids = [x.strip() for x in args.ingredients.split(",")] if args.ingredients else None
    ingredient_names = [x.strip() for x in args.ingredient_names.split(",")] if args.ingredient_names else None
    preferred_cuisines = [x.strip() for x in args.preferred_cuisines.split(",")] if args.preferred_cuisines else None
    
    rec = GraphHybridRecommender(args.uri, args.user, args.password, args.database)
    results = rec.recommend(
        user_id=args.user_id,
        ingredient_ids=ingredient_ids,
        ingredient_names=ingredient_names,
        limit=args.limit,
        min_match_ratio=args.min_match,
        max_cook_time=args.max_cook_time,
        recipe_category=args.recipe_category,
        preferred_cuisines=preferred_cuisines
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
            print()

    rec.close()


if __name__ == "__main__":
    main()

