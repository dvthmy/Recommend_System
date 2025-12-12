#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simplified Graph-based Recipe Recommendation System
----------------------------------------------------
- Dựa trên ingredient matching, cuisine priority, time constraints
- Sử dụng similar users, similar recipes, và demographic propagation (POPULAR_IN)
- Demographic propagation: ưu tiên recipes phổ biến trong nhóm demographic của user
"""

from neo4j import GraphDatabase
import argparse
import json
import sys
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass

# =========================================================
# 📊 Lightweight Metrics Stubs (for evaluation scripts)
# =========================================================

@dataclass
class RecommendationMetrics:
    """Lightweight version used only by evaluation scripts."""
    recipe_id: str
    title: str
    content_score: float = 0.0
    popularity_score: float = 0.0
    similar_user_score: float = 0.0
    similar_recipe_score: float = 0.0
    ingredient_match_ratio: float = 0.0
    cuisine_priority: int = 3
    avg_rating: float = 0.0
    global_likes: int = 0
    final_score: float = 0.0
    rank: int = 0

    def to_dict(self) -> Dict:
        return {
            "recipe_id": self.recipe_id,
            "title": self.title,
            "scores": {
                "content": self.content_score,
                "popularity": self.popularity_score,
                "final": self.final_score,
            },
        }


class RecommendationEvaluator:
    """Minimal evaluator stub used by generate_evaluation_report.py."""

    def __init__(self, enable_logging: bool = True):
        self.enable_logging = enable_logging
        self.metrics: List[RecommendationMetrics] = []

    def add_metric(self, metric: RecommendationMetrics):
        self.metrics.append(metric)

    def calculate_summary_stats(self) -> Dict:
        if not self.metrics:
            return {}
        total = len(self.metrics)
        avg_final = sum(m.final_score for m in self.metrics) / total
        return {
            "total_recommendations": total,
            "average_scores": {"final": round(avg_final, 3)},
        }

    def print_summary(self, output_stream=sys.stderr):
        if not self.enable_logging:
            return
        stats = self.calculate_summary_stats()
        if not stats:
            return
        print(
            f"[RecommendationEvaluator] total={stats['total_recommendations']}, "
            f"avg_final={stats['average_scores']['final']}",
            file=output_stream,
        )

    def export_metrics(self, filepath: str):
        import json
        data = {
            "summary": self.calculate_summary_stats(),
            "detailed_metrics": [m.to_dict() for m in self.metrics],
        }
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


# Import knowledge-based components
try:
    import sys
    from pathlib import Path
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
    print(f"⚠️ Warning: Could not import knowledge_based_recommender: {e}", file=sys.stderr)
    KnowledgeBasedRecommender = None
    UserKnowledge = None
    RecipeKnowledge = None
    GroupKnowledge = None
    RecommendationReason = None

# Import ingredient-only recommender
try:
    from ingredient_only_recommender import IngredientOnlyRecommender
except ImportError as e:
    print(f"⚠️ Warning: Could not import ingredient_only_recommender: {e}", file=sys.stderr)
    IngredientOnlyRecommender = None


# =========================================================
# 🔍 Ingredient Matcher Component
# =========================================================

@dataclass
class IngredientMatchContext:
    """Context for ingredient matching"""
    bases: List[str]
    synonyms: List[str]
    ingredient_ids: List[str]


class IngredientMatcher:
    """Handles ingredient name to ID mapping and matching context"""
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def map_names_to_ids(self, session, ingredient_names: List[str]) -> List[str]:
        """Map ingredient names to IDs using exact match, then fuzzy matching"""
        if not ingredient_names:
            return []
        
        ingredient_ids = []
        for name in ingredient_names:
            name = name.strip()
            if not name:
                continue
            
            mapped_id = None
            
            # Try exact match first
            q_exact = """
            MATCH (i:Ingredient)
            WHERE i.ingredient_id = $name 
               OR toLower(i.canonical_name) = toLower($name)
               OR $name IN coalesce(i.alt_names, [])
            RETURN i.ingredient_id AS id
            LIMIT 1
            """
            result = session.run(q_exact, name=name).single()
            if result:
                mapped_id = result["id"]
            
            # If no exact match, try starts-with match
            if not mapped_id:
                q_starts = """
                MATCH (i:Ingredient)
                WHERE toLower(i.canonical_name) STARTS WITH toLower($name)
                   OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) STARTS WITH toLower($name))
                RETURN i.ingredient_id AS id
                ORDER BY size(i.canonical_name) ASC
                LIMIT 1
                """
                result = session.run(q_starts, name=name).single()
                if result:
                    mapped_id = result["id"]
            
            # If still no match, try contains match
            if not mapped_id:
                q_contains = """
                MATCH (i:Ingredient)
                WHERE toLower(i.canonical_name) CONTAINS toLower($name)
                   OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) CONTAINS toLower($name))
                RETURN i.ingredient_id AS id
                ORDER BY 
                    CASE WHEN toLower(i.canonical_name) = toLower($name) THEN 1 ELSE 2 END,
                    size(i.canonical_name) ASC
                LIMIT 1
                """
                result = session.run(q_contains, name=name).single()
                if result:
                    mapped_id = result["id"]
            
            if mapped_id:
                ingredient_ids.append(mapped_id)
        
        # Return list without duplicates but preserve order
        seen = set()
        result = []
        for ing_id in ingredient_ids:
            if ing_id not in seen:
                seen.add(ing_id)
                result.append(ing_id)
        
        return result
    
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
        
        Giải thích:
        - Priority 1: Recipe có cuisine trùng chính xác với favorite cuisine của user (map đúng)
        - Priority 2: Recipe có cuisine trong cùng group với favorite cuisine (ví dụ: Vietnamese → Asian)
        - Priority 3: Recipe có cuisine khác hoàn toàn
        
        QUAN TRỌNG: Normalize và so sánh chính xác để map đúng với cuisine của người dùng
        """
        if not target_cuisines:
            return 3
        
        # Normalize: lowercase và strip whitespace
        recipe_lower = [c.lower().strip() if isinstance(c, str) else str(c).lower().strip() for c in recipe_cuisines if c]
        target_lower = [c.lower().strip() for c in target_cuisines if c]
        
        # Check exact match (map đúng với cuisine của người dùng)
        for tc in target_lower:
            for rc in recipe_lower:
                # Exact match sau khi normalize
                if tc == rc:
                    return 1
        
        # Check group match
        for target_cuisine in target_lower:
            target_group = self._get_cuisine_group(target_cuisine)
            if target_group:
                for recipe_cuisine in recipe_lower:
                    if self._is_in_group(recipe_cuisine, target_group):
                        return 2  # Cùng group → priority 2 (Similar to your preferred cuisine group)
        
        return 3
    
    def calculate_priority_with_implicit(
        self, 
        recipe_cuisines: List[str], 
        explicit_cuisines: List[str],
        implicit_cuisines: List[str]
    ) -> int:
        """
        Calculate cuisine priority với explicit và implicit cuisines riêng biệt.
        
        Giải thích:
        - Priority 1: Recipe có cuisine trùng chính xác với EXPLICIT cuisine (từ parameter hoặc FAVORS_CUISINE)
        - Priority 2: Recipe có cuisine trùng với IMPLICIT cuisine (từ real-time learning) HOẶC cùng group với explicit/implicit
        - Priority 3: Recipe có cuisine khác hoàn toàn
        
        QUAN TRỌNG: Implicit cuisines (real-time learning) → priority = 2 (không phải 1)
        """
        if not explicit_cuisines and not implicit_cuisines:
            return 3
        
        # Normalize: lowercase và strip whitespace
        recipe_lower = [c.lower().strip() if isinstance(c, str) else str(c).lower().strip() for c in recipe_cuisines if c]
        explicit_lower = [c.lower().strip() for c in explicit_cuisines if c]
        implicit_lower = [c.lower().strip() for c in implicit_cuisines if c]
        
        # Check exact match với EXPLICIT cuisines → priority = 1
        for ec in explicit_lower:
            for rc in recipe_lower:
                if ec == rc:
                    return 1
        
        # Check exact match với IMPLICIT cuisines → priority = 2
        for ic in implicit_lower:
            for rc in recipe_lower:
                if ic == rc:
                    return 2
        
        # Check group match với explicit cuisines → priority = 2
        for target_cuisine in explicit_lower:
            target_group = self._get_cuisine_group(target_cuisine)
            if target_group:
                for recipe_cuisine in recipe_lower:
                    if self._is_in_group(recipe_cuisine, target_group):
                        return 2
        
        # Check group match với implicit cuisines → priority = 2
        for target_cuisine in implicit_lower:
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


# =========================================================
# 🍽️ Category Mapper Component
# =========================================================

class CategoryMapper:
    """Maps main category groups (Main dish, Dessert, Drink) to specific recipe categories"""
    
    MAIN_GROUPS = {
        "Main dish": [
            "dinner", "lunch", "breakfast", "brunch", 
            "entree", "main course", "main dish", "main",
            "side dish", "appetizer", "snack",  # Snack có thể là main dish nếu không phải dessert
            "soup", "salad", "pasta", "sandwich"
        ],
        "Dessert": [
            "dessert", "cake", "pie", "candy", 
            "cookie", "pastry", "sweet", "sweets",
            "ice cream", "pudding", "muffin", "brownie"
        ],
        "Drink": [
            "drink", "beverage", "cocktail", "coffee", 
            "tea", "juice", "smoothie", "shake",
            "soda", "water", "wine", "beer"
        ]
    }
    
    def get_categories_for_main_group(self, main_group: str) -> List[str]:
        """
        Get list of specific categories that belong to a main group.
        
        Args:
            main_group: One of "Main dish", "Dessert", "Drink"
        
        Returns:
            List of category keywords to match against recipe_category
        """
        main_group_lower = main_group.lower().strip()
        return self.MAIN_GROUPS.get(main_group, [])
    
    def is_category_in_main_group(self, recipe_category: str, main_group: str) -> bool:
        """
        Check if a recipe category belongs to a main group.
        
        Args:
            recipe_category: The recipe's category (can be string or array)
            main_group: One of "Main dish", "Dessert", "Drink"
        
        Returns:
            True if recipe_category matches any category in the main group
        """
        if not recipe_category or not main_group:
            return False
        
        # Normalize main group
        main_group_lower = main_group.lower().strip()
        categories = self.get_categories_for_main_group(main_group)
        
        # Normalize recipe_category (handle both string and array)
        category_str = str(recipe_category).lower()
        
        # Check if any category keyword appears in the recipe_category
        for cat in categories:
            if cat in category_str:
                return True
        
        return False
    
    def normalize_category_input(self, category_input: Optional[str]) -> Optional[str]:
        """
        Normalize category input from user.
        - If it's a main group (Main dish, Dessert, Drink), return as-is
        - If it's a specific category, return as-is for backward compatibility
        
        Args:
            category_input: User-provided category (e.g., "Main dish", "Dinner", "Dessert")
        
        Returns:
            Normalized category string or None
        """
        if not category_input:
            return None
        
        # Normalize: capitalize first letter of each word
        normalized = category_input.strip()
        if normalized:
            # Check if it's a main group (handle both "Main dish", "MainDish", "main-dish" formats)
            # Replace underscores, hyphens, and split camelCase
            import re
            # Replace underscores and hyphens with spaces
            normalized_clean = normalized.replace("_", " ").replace("-", " ")
            # Split camelCase: "MainDish" -> "Main Dish"
            normalized_clean = re.sub(r'([a-z])([A-Z])', r'\1 \2', normalized_clean)
            normalized_lower = normalized_clean.lower().strip()
            
            for main_group in self.MAIN_GROUPS.keys():
                main_group_lower = main_group.lower()
                # Exact match
                if normalized_lower == main_group_lower:
                    return main_group  # Return exact main group name
                # Handle "MainDish" -> "Main dish" (remove space and compare)
                if normalized_lower.replace(" ", "") == main_group_lower.replace(" ", ""):
                    return main_group  # Return exact main group name
        
        return normalized  # Return as-is for specific categories


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
        input_ing: List[str]
    ) -> float:
        """
        Calculate Jaccard match ratio: intersection / union
        
        Giải thích:
        - Jaccard similarity đo độ tương đồng giữa 2 sets
        - intersection: số ingredients user có mà recipe cũng có
        - union: tổng số unique ingredients từ cả user và recipe
        - Match ratio càng cao = recipe càng phù hợp với ingredients user có
        """
        if not input_ing or not all_ing:
            return 0.0
        
        intersection = len(matched_ing)
        union = len(set(all_ing) | set(input_ing))
        return intersection / union if union > 0 else 0.0
    
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
        
        Giải thích:
        - Xem xét các recipes user đã tương tác trước đó (loại trừ recipe hiện tại)
        - Tính điểm dựa trên:
          + Số ingredients chung (Jaccard similarity: intersection / union)
          + Cuisine có trùng không
          + Loại tương tác: like = 1.0, rating >= 4.0 = 0.8, khác = 0.0
          + Độ mới của tương tác (exponential decay với half-life 90 ngày)
        - Similarity = (Jaccard similarity) * 0.6 + (shared_cuisine) * cuisine_weight
        - QUAN TRỌNG: Yêu cầu ít nhất 2 shared ingredients để tính similarity hợp lý
          Nếu chỉ có 1 shared ingredient, giảm cuisine_weight xuống 0.1 (thay vì 0.4)
        - Returns: (history_score, similar_interacted_count)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(interacted:Recipe)
        WHERE interacted.recipe_id <> $rid
        // QUAN TRỌNG: Filter interactions hợp lệ (like hoặc rating >= 4.0)
        // - Lấy liked = true HOẶC event_type = 'like' (một trong hai có thì được)
        // - Khi user unlike, backend set liked = false VÀ xóa event_type = 'like' (set thành null)
        // - Nhưng để an toàn, check cả hai điều kiện (OR) để tránh miss data
        // - Rating >= 4.0 vẫn được tính (không cần check liked)
        AND ((iv.liked = true OR iv.event_type = 'like') OR (iv.event_type = 'rating' AND iv.rating >= 4.0))
        WITH iv, interacted,
            CASE 
                // Tính khi liked = true HOẶC event_type = 'like' (một trong hai có thì được)
                WHEN iv.liked = true OR iv.event_type = 'like' THEN 1.0
                WHEN iv.event_type = 'rating' AND iv.rating >= 4.0 THEN 0.8
                ELSE 0.0
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 1.0
                ELSE exp(-duration.inDays(iv.timestamp, datetime()).days / 90.0)
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
            END AS shared_cuisine,
            size(interacted_ingredients) AS int_ing_count,
            size($recipe_ingredients) AS rec_ing_count
        WITH 
          interaction_weight,
          recency,
          interacted.recipe_id AS interacted_id,
          shared_cuisine,
          shared_ing_count,
          rec_ing_count,
          int_ing_count,
          // Tính Jaccard similarity (chỉ khi có shared ingredients)
          CASE 
            WHEN shared_ing_count > 0 THEN
              toFloat(shared_ing_count) /
              toFloat(rec_ing_count + int_ing_count - shared_ing_count)
            ELSE 0.0
          END AS jaccard_similarity,
          // Điều chỉnh cuisine_weight dựa trên số lượng shared ingredients
          // Nếu có >= 2 shared ingredients: cuisine_weight = 0.4 (bình thường)
          // Nếu chỉ có 1 shared ingredient: cuisine_weight = 0.1 (giảm đáng kể)
          // Nếu không có shared ingredients: cuisine_weight = 0.05 (rất thấp)
          CASE 
            WHEN shared_ing_count >= 2 THEN 0.4
            WHEN shared_ing_count = 1 THEN 0.1
            ELSE 0.05
          END AS cuisine_weight
        WITH 
          interaction_weight,
          recency,
          interacted_id,
          shared_ing_count,
          jaccard_similarity,
          shared_cuisine,
          cuisine_weight,
          // Tính similarity: Jaccard * 0.6 + shared_cuisine * cuisine_weight
          // QUAN TRỌNG: Chỉ tính khi có ít nhất 2 shared ingredients HOẶC (shared_ing_count = 1 AND shared_cuisine = 1.0)
          // Nếu chỉ có 1 shared ingredient và không có shared cuisine → không tính (quá yếu)
          jaccard_similarity * 0.6 + shared_cuisine * cuisine_weight AS similarity
        WHERE 
          // Yêu cầu: ít nhất 2 shared ingredients HOẶC (1 shared ingredient + shared cuisine)
          // Điều này đảm bảo similarity không quá cao khi chỉ có 1 ingredient chung
          (shared_ing_count >= 2) OR (shared_ing_count = 1 AND shared_cuisine > 0)
        RETURN 
            sum(interaction_weight * recency * similarity) AS history_score,
            count(DISTINCT interacted_id) AS similar_count
        """
        
        result = session.run(
            q,
            uid=user_id,
            rid=recipe_id,
            recipe_ingredients=recipe_ingredients,
            recipe_cuisines=recipe_cuisines
        ).single()
        
        if result:
            return (
                result.get("history_score", 0.0) or 0.0,
                result.get("similar_count", 0) or 0
            )
        return 0.0, 0
    
    def calculate_similar_user_score(
        self,
        session,
        user_id: str,
        recipe_id: str
    ) -> Tuple[float, int]:
        """
        Calculate score from similar users who interacted with this recipe.
        Uses SIMILAR_USER relationship.
        
        Giải thích:
        - Tìm các users tương tự với user hiện tại (qua SIMILAR_USER relationship)
        - Xem các users tương tự đã tương tác với recipe này như thế nào
        - Tính điểm dựa trên:
          + Similarity score giữa user và similar users
          + Loại tương tác (like > rating > view)
          + Độ mới của tương tác
        - Returns: (similar_user_score, similar_user_count)
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
        Calculate score from similar recipes that user has interacted with.
        Uses SIMILAR_RECIPE relationship.
        
        Giải thích:
        - Tìm các recipes user đã tương tác (đặc biệt là liked hoặc rated cao)
        - Xem các recipes đó có SIMILAR_RECIPE relationship với recipe hiện tại không
        - Tính điểm dựa trên:
          + Similarity score giữa recipes (từ SIMILAR_RECIPE relationship)
          + Loại tương tác user đã có với similar recipes (like > rating > view)
          + Độ mới của tương tác
        - Returns: (similar_recipe_score, similar_recipe_count)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(liked:Recipe)
        WHERE (iv.liked = true OR iv.rating >= 4.0 OR iv.event_type = 'like')
        MATCH (liked)-[sim:SIMILAR_RECIPE]->(r:Recipe {recipe_id: $rid})
        WITH sim, iv, liked,
            coalesce(sim.score, sim.similarity, 0.0) AS similarity_score,
            CASE 
                WHEN iv.event_type = 'like' OR iv.liked = true THEN 3.0
                WHEN iv.event_type = 'rating' AND iv.rating >= 4.0 THEN 2.5
                WHEN iv.event_type = 'rating' THEN 2.0
                ELSE 1.0
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv.timestamp, datetime()).days / 30.0)
            END AS recency
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
    
    def calculate_demographic_score(
        self,
        session,
        user_id: str,
        recipe_id: str,
        preferred_cuisines: Optional[List[str]] = None
    ) -> Tuple[float, int, str]:
        """
        Calculate demographic popularity score dựa trên:
        - User thuộc group nào (qua BELONGS_TO)
        - Group có POPULAR_IN relationship với recipe (nổi trong group)
        - Recipe có cuisine phù hợp với user preferences
        
        Logic:
        1. User thuộc group (BELONGS_TO)
        2. Group có POPULAR_IN với recipe này (nổi trong group từ interactions của BẤT KỲ user nào trong group)
        3. Recipe có cuisine match với user's favorite cuisines (hoặc preferred_cuisines)
        
        QUAN TRỌNG:
        - POPULAR_IN là thuộc tính của GROUP, không phải của từng user
        - Nếu group đã có POPULAR_IN (từ các users khác trong group) → User mới cũng sẽ có badge
        - POPULAR_IN được tạo khi có ít nhất 1 user trong group đã like/rate recipe
        
        Returns: (demographic_score, group_count, group_name)
        """
        # Normalize preferred_cuisines
        normalized_pref_cuisines = []
        if preferred_cuisines:
            normalized_pref_cuisines = [c.lower().strip() for c in preferred_cuisines if c]
        
        q = """
        // Tìm groups mà user thuộc về
        MATCH (u:User {user_id: $uid})-[:BELONGS_TO]->(g:Group)
        
        // Lấy recipe và kiểm tra group có POPULAR_IN relationship không (nổi trong group)
        MATCH (r:Recipe {recipe_id: $rid})
        OPTIONAL MATCH (g)-[pop:POPULAR_IN]->(r)
        
        // Lấy user's favorite cuisines
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(userFavCuisine:Cuisine)
        WITH u, g, r, pop, collect(DISTINCT toLower(userFavCuisine.name)) AS user_favorite_cuisines
        
        // Lấy recipe cuisine
        WITH u, g, r, pop, user_favorite_cuisines,
             coalesce(r.cuisine, []) AS recipe_cuisines
        
        // Xác định target cuisines: ưu tiên preferred_cuisines từ parameter, fallback về user favorites
        WITH u, g, r, pop, user_favorite_cuisines, recipe_cuisines,
             CASE 
                 WHEN size($preferred_cuisines) > 0 THEN [c IN $preferred_cuisines | toLower(c)]
                 WHEN size(user_favorite_cuisines) > 0 THEN user_favorite_cuisines
                 ELSE []
             END AS target_cuisines
        
        // Check cuisine match - giống logic query:
        // WHERE any(c IN coalesce(r.cuisine, [])
        //           WHERE toLower(c) CONTAINS "vietnam"
        //              OR "vietnam" CONTAINS toLower(c)
        // )
        WITH u, g, r, pop, target_cuisines, recipe_cuisines,
             CASE 
                 WHEN size(target_cuisines) > 0 AND 
                      any(rc IN recipe_cuisines WHERE 
                          any(tc IN target_cuisines WHERE 
                              toLower(toString(rc)) CONTAINS tc OR 
                              tc CONTAINS toLower(toString(rc))
                          )
                      )
                 THEN 1.0
                 ELSE 0.0
             END AS cuisine_match
        
        // Logic giống query: 
        // - Có POPULAR_IN (nổi trong group) VÀ
        // - Có cuisine match (phù hợp với user preferences)
        // Lưu ý: Chỉ tính điểm nếu có POPULAR_IN (giống query của user)
        WHERE pop IS NOT NULL AND cuisine_match > 0
        
        WITH g, pop, cuisine_match,
             coalesce(pop.score, 0) AS popularity_score,
             coalesce(g.group_id, g.gender + '-' + g.age_group) AS group_name
        
        // Tính demographic score: POPULAR_IN score * cuisine_match
        // POPULAR_IN score là số users trong group đã tương tác với recipe
        WITH collect({
            group_name: group_name,
            score: toFloat(popularity_score) * cuisine_match
        }) AS groups,
        sum(toFloat(popularity_score) * cuisine_match) AS total_score,
        count(DISTINCT g) AS group_count,
        head(collect(group_name)) AS first_group_name
        
        RETURN 
            total_score AS demographic_score,
            group_count,
            first_group_name AS group_name
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id, preferred_cuisines=normalized_pref_cuisines).single()
        
        # Debug logging (có thể bỏ sau)
        # if result:
        #     score = result.get("demographic_score", 0.0) or 0.0
        #     if score > 0:
        #         print(f"[DEBUG] Recipe {recipe_id}: demographic_score = {score}", file=sys.stderr)
        
        if result:
            score = result.get("demographic_score", 0.0) or 0.0
            group_count = result.get("group_count", 0) or 0
            group_name = result.get("group_name")
            
            # Normalize score: POPULAR_IN score là số users trong group đã tương tác
            # Chia cho 5 để có range 0-1 (giả sử max score = 5 là đủ popular)
            # Score càng cao = càng nhiều users trong group đã like/rate recipe này
            normalized_score = min(score / 5.0, 1.0)
            
            return normalized_score, group_count, group_name or ""
        
        return 0.0, 0, ""

    def calculate_all_scores_batch(
        self,
        session,
        user_id: str,
        recipe_data: List[Dict],  # List of {recipe_id, all_ingredients, cuisine}
        preferred_cuisines: Optional[List[str]] = None
    ) -> Dict[str, Dict]:
        """
        Calculate all scores (history, similar_user, similar_recipe, demographic) using BATCH queries.
        
        Giải thích vấn đề N+1 Query Problem:
        - Với 100 candidates, nếu tính từng score riêng lẻ:
          + calculate_history_score: 100 queries (1 query per recipe)
          + calculate_similar_user_score: 100 queries
          + calculate_similar_recipe_score: 100 queries
          + calculate_demographic_score: 100 queries
          = TỔNG: 400 queries tuần tự → RẤT CHẬM!
        
        Giải pháp: Batch processing - tính từng loại score cho TẤT CẢ recipes trong 1 query
        - Giảm từ 400 queries xuống 4 queries (1 query per score type)
        - Sử dụng UNWIND để xử lý batch recipes
        - Mỗi loại score được tính riêng để đảm bảo logic đúng
        
        Returns: Dict[recipe_id, {
            'history_score': float,
            'history_count': int,
            'similar_user_score': float,
            'similar_user_count': int,
            'similar_recipe_score': float,
            'similar_recipe_count': int,
            'demographic_score': float,
            'demographic_group_count': int,
            'demographic_group_name': str
        }]
        """
        if not recipe_data:
            return {}
        
        # Initialize result dict với zeros
        scores_dict = {}
        for r in recipe_data:
            recipe_id = r.get("recipe_id")
            if recipe_id:
                scores_dict[recipe_id] = {
                    "history_score": 0.0,
                    "history_count": 0,
                    "similar_user_score": 0.0,
                    "similar_user_count": 0,
                    "similar_recipe_score": 0.0,
                    "similar_recipe_count": 0,
                    "demographic_score": 0.0,
                    "demographic_group_count": 0,
                    "demographic_group_name": ""
                }
        
        # Normalize preferred cuisines
        normalized_pref_cuisines = []
        if preferred_cuisines:
            normalized_pref_cuisines = [c.lower().strip() for c in preferred_cuisines if c]
        
        recipe_ids = [r.get("recipe_id") for r in recipe_data if r.get("recipe_id")]
        if not recipe_ids:
            return scores_dict
        
        # ============================================================
        # 1. BATCH HISTORY SCORE (1 query cho tất cả recipes)
        # ============================================================
        q_history = """
        UNWIND $recipe_data AS recipe
        WITH recipe.recipe_id AS rid, recipe.all_ingredients AS recipe_ingredients, recipe.cuisine AS recipe_cuisines
        
        OPTIONAL MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(interacted:Recipe)
        WHERE interacted.recipe_id <> rid
        AND ((iv.liked = true OR iv.event_type = 'like') OR (iv.event_type = 'rating' AND iv.rating >= 4.0))
        WITH rid, recipe_ingredients, recipe_cuisines, iv, interacted,
            CASE 
                WHEN iv.liked = true OR iv.event_type = 'like' THEN 1.0
                WHEN iv.event_type = 'rating' AND iv.rating >= 4.0 THEN 0.8
                ELSE 0.0
            END AS interaction_weight,
            CASE 
                WHEN iv.timestamp IS NULL THEN 1.0
                ELSE exp(-duration.inDays(iv.timestamp, datetime()).days / 90.0)
            END AS recency
        OPTIONAL MATCH (interacted)-[:HAS_INGREDIENT]->(ri:Ingredient)
        WITH rid, recipe_ingredients, recipe_cuisines, iv, interacted, interaction_weight, recency,
            collect(DISTINCT ri.ingredient_id) AS interacted_ingredients,
            interacted.cuisine AS interacted_cuisines
        WITH rid, recipe_ingredients, recipe_cuisines, interaction_weight, recency, interacted,
            interacted_ingredients, interacted_cuisines,
            size([ing IN recipe_ingredients WHERE ing IN interacted_ingredients]) AS shared_ing_count,
            CASE 
                WHEN any(c IN recipe_cuisines WHERE c IN coalesce(interacted_cuisines, [])) THEN 1.0
                ELSE 0.0
            END AS shared_cuisine,
            size(interacted_ingredients) AS int_ing_count,
            size(recipe_ingredients) AS rec_ing_count
        WITH rid, interaction_weight, recency, interacted,
            shared_ing_count, shared_cuisine, int_ing_count, rec_ing_count,
            CASE 
                WHEN shared_ing_count > 0 THEN
                    toFloat(shared_ing_count) / toFloat(rec_ing_count + int_ing_count - shared_ing_count)
                ELSE 0.0
            END AS jaccard_similarity,
            CASE 
                WHEN shared_ing_count >= 2 THEN 0.4
                WHEN shared_ing_count = 1 THEN 0.1
                ELSE 0.05
            END AS cuisine_weight
        WITH rid, interaction_weight, recency, interacted,
            shared_ing_count, shared_cuisine, jaccard_similarity, cuisine_weight,
            jaccard_similarity * 0.6 + shared_cuisine * cuisine_weight AS similarity
        WHERE (shared_ing_count >= 2) OR (shared_ing_count = 1 AND shared_cuisine > 0)
        WITH rid,
            sum(interaction_weight * recency * similarity) AS history_score,
            count(DISTINCT interacted.recipe_id) AS history_count
        RETURN rid AS recipe_id, history_score, history_count
        """
        
        recipe_list = [
            {
                "recipe_id": r.get("recipe_id"),
                "all_ingredients": r.get("all_ingredients", []),
                "cuisine": r.get("cuisine", [])
            }
            for r in recipe_data
            if r.get("recipe_id")
        ]
        
        result_history = session.run(q_history, uid=user_id, recipe_data=recipe_list)
        for row in result_history:
            recipe_id = row.get("recipe_id")
            if recipe_id and recipe_id in scores_dict:
                scores_dict[recipe_id]["history_score"] = row.get("history_score", 0.0) or 0.0
                scores_dict[recipe_id]["history_count"] = row.get("history_count", 0) or 0
        
        # ============================================================
        # 2. BATCH SIMILAR USER SCORE (1 query cho tất cả recipes)
        # ============================================================
        q_similar_user = """
        UNWIND $recipe_ids AS rid
        OPTIONAL MATCH (u:User {user_id: $uid})-[sim:SIMILAR_USER]->(u2:User)-[iv2:INTERACTED_WITH]->(r:Recipe {recipe_id: rid})
        WITH rid, sim, iv2, u2,
            CASE 
                WHEN iv2.event_type = 'like' THEN 3.0
                WHEN iv2.event_type = 'rating' THEN 2.0
                WHEN iv2.event_type = 'view' THEN 1.0
                ELSE 0.5
            END AS interaction_weight,
            CASE 
                WHEN iv2.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv2.timestamp, datetime()).days / 30.0)
            END AS recency,
            coalesce(sim.score, 0.0) AS similarity_score
        WITH rid,
            sum(interaction_weight * recency * similarity_score) AS similar_user_score,
            count(DISTINCT u2) AS similar_user_count
        RETURN rid AS recipe_id, similar_user_score, similar_user_count
        """
        
        result_similar_user = session.run(q_similar_user, uid=user_id, recipe_ids=recipe_ids)
        for row in result_similar_user:
            recipe_id = row.get("recipe_id")
            if recipe_id and recipe_id in scores_dict:
                scores_dict[recipe_id]["similar_user_score"] = row.get("similar_user_score", 0.0) or 0.0
                scores_dict[recipe_id]["similar_user_count"] = row.get("similar_user_count", 0) or 0
        
        # ============================================================
        # 3. BATCH SIMILAR RECIPE SCORE (1 query cho tất cả recipes)
        # ============================================================
        q_similar_recipe = """
        UNWIND $recipe_ids AS rid
        OPTIONAL MATCH (u:User {user_id: $uid})-[iv3:INTERACTED_WITH]->(liked:Recipe)
        WHERE (iv3.liked = true OR iv3.rating >= 4.0 OR iv3.event_type = 'like')
        OPTIONAL MATCH (liked)-[sim2:SIMILAR_RECIPE]->(r2:Recipe {recipe_id: rid})
        WITH rid, sim2, iv3, liked,
            coalesce(sim2.score, sim2.similarity, 0.0) AS similarity_score,
            CASE 
                WHEN iv3.event_type = 'like' OR iv3.liked = true THEN 3.0
                WHEN iv3.event_type = 'rating' AND iv3.rating >= 4.0 THEN 2.5
                WHEN iv3.event_type = 'rating' THEN 2.0
                ELSE 1.0
            END AS interaction_weight,
            CASE 
                WHEN iv3.timestamp IS NULL THEN 0.0
                ELSE 1.0 / (1.0 + duration.inDays(iv3.timestamp, datetime()).days / 30.0)
            END AS recency
        WITH rid,
            sum(interaction_weight * recency * similarity_score) AS similar_recipe_score,
            count(DISTINCT liked) AS similar_recipe_count
        RETURN rid AS recipe_id, similar_recipe_score, similar_recipe_count
        """
        
        result_similar_recipe = session.run(q_similar_recipe, uid=user_id, recipe_ids=recipe_ids)
        for row in result_similar_recipe:
            recipe_id = row.get("recipe_id")
            if recipe_id and recipe_id in scores_dict:
                scores_dict[recipe_id]["similar_recipe_score"] = row.get("similar_recipe_score", 0.0) or 0.0
                scores_dict[recipe_id]["similar_recipe_count"] = row.get("similar_recipe_count", 0) or 0
        
        # ============================================================
        # 4. BATCH DEMOGRAPHIC SCORE (1 query cho tất cả recipes)
        # ============================================================
        q_demographic = """
        UNWIND $recipe_ids AS rid
        OPTIONAL MATCH (u:User {user_id: $uid})-[:BELONGS_TO]->(g:Group)
        OPTIONAL MATCH (r3:Recipe {recipe_id: rid})
        OPTIONAL MATCH (g)-[pop:POPULAR_IN]->(r3)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(userFavCuisine:Cuisine)
        WITH rid, u, g, r3, pop,
            collect(DISTINCT toLower(userFavCuisine.name)) AS user_favorite_cuisines,
            coalesce(r3.cuisine, []) AS recipe_cuisines_list
        WITH rid, g, pop, user_favorite_cuisines, recipe_cuisines_list,
            CASE 
                WHEN size($preferred_cuisines) > 0 THEN [c IN $preferred_cuisines | toLower(c)]
                WHEN size(user_favorite_cuisines) > 0 THEN user_favorite_cuisines
                ELSE []
            END AS target_cuisines
        WITH rid, g, pop, target_cuisines, recipe_cuisines_list,
            CASE 
                WHEN size(target_cuisines) > 0 AND 
                     any(rc IN recipe_cuisines_list WHERE 
                         any(tc IN target_cuisines WHERE 
                             toLower(toString(rc)) CONTAINS tc OR 
                             tc CONTAINS toLower(toString(rc))
                         )
                     )
                THEN 1.0
                ELSE 0.0
            END AS cuisine_match
        WHERE pop IS NOT NULL AND cuisine_match > 0
        WITH rid, g, pop, cuisine_match,
            coalesce(pop.score, 0) AS popularity_score,
            coalesce(g.group_id, g.gender + '-' + g.age_group) AS group_name
        WITH rid,
            sum(toFloat(popularity_score) * cuisine_match) AS total_demographic_score,
            count(DISTINCT g) AS demographic_group_count,
            head(collect(group_name)) AS first_group_name
        WITH rid, demographic_group_count, first_group_name,
            CASE 
                WHEN total_demographic_score / 5.0 > 1.0 THEN 1.0
                ELSE total_demographic_score / 5.0
            END AS demographic_score
        RETURN 
            rid AS recipe_id,
            demographic_score,
            demographic_group_count,
            coalesce(first_group_name, "") AS demographic_group_name
        """
        
        result_demographic = session.run(q_demographic, uid=user_id, recipe_ids=recipe_ids, preferred_cuisines=normalized_pref_cuisines)
        for row in result_demographic:
            recipe_id = row.get("recipe_id")
            if recipe_id and recipe_id in scores_dict:
                scores_dict[recipe_id]["demographic_score"] = min(row.get("demographic_score", 0.0) or 0.0, 1.0)
                scores_dict[recipe_id]["demographic_group_count"] = row.get("demographic_group_count", 0) or 0
                scores_dict[recipe_id]["demographic_group_name"] = row.get("demographic_group_name", "") or ""
        
        return scores_dict


# =========================================================
# 🧠 Knowledge-Based Logic (Removed - No longer needed)
# =========================================================
# QUAN TRỌNG: Đã loại bỏ EnhancedKnowledgeRecommender vì:
# 1. Allergen safety: đã filter trong query (line 2062, 2235, 2329, 2524)
# 2. Time constraints: đã filter trong query (line 2038, 2223, 2322, 2517)
# 3. Cuisine preference: đã xử lý bởi CuisinePrioritizer (line 1441)
# 4. User info extraction: đã có _extract_user_info method


# =========================================================
# 🎯 Main Recommender
# =========================================================

class GraphHybridRecommender:
    """
    Simplified graph-based hybrid recommender.
    
    Giải thích tổng quan:
    - Tìm candidates dựa trên ingredient matching
    - Tính điểm dựa trên:
      1. Ingredient match ratio (Jaccard similarity)
      2. Cuisine priority (favorite cuisines được ưu tiên)
      3. Time constraints (max_cook_time)
      4. Similar users (users tương tự đã tương tác với recipe)
      5. Similar recipes (recipes tương tự user đã thích)
    - Sắp xếp và trả về top recommendations
    """
    
    def __init__(self, uri="neo4j+s://3b0d8961.databases.neo4j.io", username="neo4j",
                 password="qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0", database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        
        # Initialize components
        # QUAN TRỌNG: Loại bỏ kb_recommender vì không cần thiết
        # - Allergen safety: đã filter trong query
        # - Time constraints: đã filter trong query
        # - Cuisine preference: đã xử lý bởi CuisinePrioritizer
        self.ingredient_matcher = IngredientMatcher(self.driver, database)
        self.cuisine_prioritizer = CuisinePrioritizer()
        self.category_mapper = CategoryMapper()
        self.scoring_engine = ScoringEngine(self.driver, database)
        self.ingredient_only_recommender = IngredientOnlyRecommender(self.driver, database) if IngredientOnlyRecommender else None
    
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
        preferred_cuisines: Optional[List[str]] = None,
        max_cuisine_priority_1_ratio: float = 0.3,  # Tỷ lệ tối đa món có cuisine_priority = 1 (60%)
        ingredient_only_mode: bool = False,  # Chỉ chạy ingredient-only mode khi được gọi rõ ràng
    ) -> List[Dict]:
        """
        Main recommendation entrypoint.
        
        Giải thích flow:
        1. Map ingredient names to IDs (nếu có)
        2. Build ingredient match context
        3. Extract user knowledge (allergies, max_cook_time, favorite cuisines)
        4. Find candidate recipes dựa trên ingredient matching
        5. Score và rank candidates:
           - Ingredient match ratio (Jaccard)
           - Cuisine priority
           - History score (similarity với past interactions)
           - Similar user score
           - Similar recipe score
        6. Sort và trả về top recommendations
        """
        with self.driver.session(database=self.database) as session:
            # Step 1: Map ingredient names to IDs
            mapped_ids: List[str] = []
            if ingredient_names:
                mapped_ids = self.ingredient_matcher.map_names_to_ids(session, ingredient_names)
            
            # Combine ingredient IDs
            all_ingredient_ids: List[str] = list(set((ingredient_ids or []) + mapped_ids))
            
            # Step 2: Build ingredient match context (empty if no ingredients)
            match_context = self.ingredient_matcher.build_match_context(session, all_ingredient_ids) if all_ingredient_ids else self.ingredient_matcher.build_match_context(session, [])
            
            # Step 2b: Identify important ingredients (protein: seafood, meat, plant_protein)
            important_ingredient_ids = self._identify_important_ingredients(session, all_ingredient_ids)
            print(f"[DEBUG] Important ingredients identified: {important_ingredient_ids} (from {all_ingredient_ids})", file=sys.stderr)
            
            # Step 3: Extract user knowledge (allergies, favorite_cuisines, max_cook_time)
            # QUAN TRỌNG: Extract trực tiếp từ database thay vì dùng knowledge_based_recommender
            # để loại bỏ dependency không cần thiết
            user_allergies = []
            user_favorite_cuisines = []
            user_max_cook_time = None
            
            if user_id:
                user_info = self._extract_user_info(session, user_id)
                user_allergies = user_info.get('allergies', [])
                user_favorite_cuisines = user_info.get('favorite_cuisines', [])
                user_max_cook_time = user_info.get('max_cook_time')
            
            # Step 4: Determine max_cook_time (use user_max_cook_time if available)
            effective_max_cook_time = max_cook_time
            if user_max_cook_time and not effective_max_cook_time:
                effective_max_cook_time = user_max_cook_time
            
            # Step 6: Extract implicit cuisine preferences from recent interactions (REAL-TIME LEARNING)
            implicit_cuisines = []
            if user_id:
                implicit_cuisines = self._extract_implicit_cuisine_preferences(session, user_id)
            
            # Step 6b: Tách riêng explicit và implicit cuisines
            # Explicit cuisines: từ parameter hoặc user profile (FAVORS_CUISINE)
            # Implicit cuisines: từ real-time learning (recent interactions)
            explicit_cuisines = []
            if preferred_cuisines:
                explicit_cuisines.extend(preferred_cuisines)
            if user_favorite_cuisines:
                explicit_cuisines.extend(user_favorite_cuisines)
            
            # Remove duplicates trong explicit cuisines
            seen_explicit = set()
            explicit_cuisines_clean = []
            for c in explicit_cuisines:
                if c:
                    c_lower = c.lower().strip()
                    if c_lower and c_lower not in seen_explicit:
                        seen_explicit.add(c_lower)
                        explicit_cuisines_clean.append(c.strip())
            
            # Implicit cuisines (từ real-time learning)
            implicit_cuisines_clean = []
            seen_implicit = set()
            for c in implicit_cuisines:
                if c:
                    c_lower = c.lower().strip()
                    # Chỉ thêm implicit nếu chưa có trong explicit (tránh duplicate)
                    if c_lower and c_lower not in seen_explicit and c_lower not in seen_implicit:
                        seen_implicit.add(c_lower)
                        implicit_cuisines_clean.append(c.strip())
            
            # Combine để dùng cho filtering (tất cả cuisines)
            effective_preferred_cuisines = explicit_cuisines_clean + implicit_cuisines_clean
            
            # Debug: Log preferred cuisines
            print(f"[DEBUG] Preferred cuisines - Parameter: {preferred_cuisines}, User profile: {user_favorite_cuisines}, Explicit: {explicit_cuisines_clean}, Implicit: {implicit_cuisines_clean}, Effective: {effective_preferred_cuisines}", file=sys.stderr)
            
            # Step 7: Find candidate recipes
            # QUAN TRỌNG: ingredient_only_mode chỉ chạy khi được gọi rõ ràng (parameter = True)
            # KHÔNG tự động chạy ingredient-only mode
            
            # Nếu KHÔNG có ingredients → NO INGREDIENTS MODE
            if not all_ingredient_ids:
                preferred_cuisine_candidates = []
                other_candidates = []
                
                # ƯU TIÊN: Tìm các món có POPULAR_IN với group của user (nếu có user_id)
                if user_id and effective_preferred_cuisines:
                    preferred_cuisine_candidates = self._find_popular_in_recipes(
                        session,
                        user_id,
                        effective_max_cook_time,
                        user_allergies,
                        recipe_category,
                        effective_preferred_cuisines,
                        limit * 2
                    )
                
                # Nếu không có POPULAR_IN hoặc không đủ, tìm món từ preferred cuisines
                if len(preferred_cuisine_candidates) < limit and effective_preferred_cuisines:
                    additional_candidates = self._find_cuisine_only_recipes(
                        session,
                        effective_preferred_cuisines,
                        effective_max_cook_time,
                        user_allergies,
                        recipe_category,
                        limit * 2
                    )
                    # Merge without duplicates
                    seen_ids = {c.get('recipe_id') for c in preferred_cuisine_candidates}
                    for candidate in additional_candidates:
                        if candidate.get('recipe_id') not in seen_ids:
                            preferred_cuisine_candidates.append(candidate)
                            seen_ids.add(candidate.get('recipe_id'))
                
                # Nếu vẫn không đủ candidates, tìm popular recipes
                if len(preferred_cuisine_candidates) < limit:
                    # Tìm popular recipes (có thể từ similar users/recipes nếu có user_id)
                    other_candidates = self._find_popular_recipes(
                        session,
                        user_id,
                        effective_max_cook_time,
                        user_allergies,
                        recipe_category,
                        limit * 2
                    )
            else:
                # Có ingredients
                # QUAN TRỌNG: ingredient_only_mode chỉ chạy khi được gọi rõ ràng (parameter = True)
                if ingredient_only_mode:
                    # INGREDIENT-ONLY MODE: Sử dụng IngredientOnlyRecommender
                    if self.ingredient_only_recommender:
                        # Sử dụng dedicated ingredient-only recommender
                        recommendations = self.ingredient_only_recommender.recommend(
                            ingredient_ids=all_ingredient_ids,
                            ingredient_names=None,  # Đã map rồi
                            limit=limit,
                            min_match_ratio=min_match_ratio,
                            user_allergies=user_allergies  # Filter allergies (chỉ dùng ingredient_id, không dùng base)
                        )
                        # Return ngay vì đã xử lý xong
                        # QUAN TRỌNG: Apply limit trước khi return
                        if limit > 0:
                            recommendations = recommendations[:limit]
                        return recommendations
                    else:
                        # Fallback: dùng logic cũ nếu không import được IngredientOnlyRecommender
                        other_candidates = self._find_candidate_recipes(
                            session,
                            all_ingredient_ids,
                            match_context,
                            max_cook_time=None,  # Không filter theo cook_time
                            min_match_ratio=min_match_ratio,
                            user_allergies=[],  # Không filter theo allergies
                            recipe_category=None,  # Không filter theo category
                            limit=limit * 3,  # Get more candidates
                            important_ingredient_ids=important_ingredient_ids,
                            preferred_cuisines=None,  # Không filter theo cuisine
                            ingredient_only_mode=True  # Explicit ingredient-only mode
                        )
                        preferred_cuisine_candidates = []  # Không tìm theo cuisine khi ingredient-only
                elif user_id:
                    # FULL MODE: Có user_id + ingredients + preferred_cuisines
                    # CÁCH LÀM MỚI: Ưu tiên cuisine trước, theo tầng A-D
                    preferred_cuisine_candidates = []
                    implicit_cuisine_candidates = []
                    group_cuisine_candidates = []
                    other_candidates = []

                    # Helper: expand cuisine groups (Japanese -> Asian group list)
                    def expand_cuisine_groups(cuisines: List[str]) -> List[str]:
                        groups = set()
                        for c in cuisines:
                            if not c:
                                continue
                            group = self.cuisine_prioritizer._get_cuisine_group(c.lower().strip())
                            if group and group in self.cuisine_prioritizer.CUISINE_GROUPS:
                                for gc in self.cuisine_prioritizer.CUISINE_GROUPS[group]:
                                    groups.add(gc.lower())
                        return list(groups)

                    tierA_candidates = []
                    tierB_candidates = []
                    tierC_candidates = []
                    tierD_candidates = []

                    # Tier A — Explicit cuisines
                    # OPTIMIZATION: Gộp 3 queries thành 1 query duy nhất với limit lớn hơn
                    # Giảm từ 3 queries xuống 1 query → tiết kiệm ~2-3 giây
                    if explicit_cuisines_clean:
                        # Gộp tất cả vào 1 query với limit lớn để đảm bảo không miss món
                        # Query này sẽ tự động ưu tiên món có important ingredients nhờ importance_bonus
                        tierA_candidates = self._find_candidate_recipes(
                            session,
                            all_ingredient_ids,
                            match_context,
                            effective_max_cook_time,
                            0.1,  # nới nhẹ nhưng vẫn giữ nhiều món
                            user_allergies,
                            recipe_category,
                            limit * 15,  # Tăng limit để bao gồm cả protein matches và important-only matches
                            important_ingredient_ids,
                            preferred_cuisines=explicit_cuisines_clean,
                            ingredient_only_mode=ingredient_only_mode
                        )
                        # Filter: Ưu tiên giữ món có important protein ingredients
                        # Nhưng vẫn giữ tất cả để đảm bảo coverage
                        tierA_candidates = tierA_candidates  # Không filter nữa, để query tự xử lý qua importance_bonus

                    # Tier B — Implicit cuisines
                    if implicit_cuisines_clean:
                        tierB_candidates = self._find_candidate_recipes(
                            session,
                            all_ingredient_ids,
                            match_context,
                            effective_max_cook_time,
                            0.1,
                            user_allergies,
                            recipe_category,
                            limit,
                            important_ingredient_ids,
                            preferred_cuisines=implicit_cuisines_clean,
                            ingredient_only_mode=ingredient_only_mode
                        )
                        # Filter: giữ món có protein match hoặc match_ratio >= 0.3
                        tierB_candidates = [
                            c for c in tierB_candidates
                            if (c.get('match_ratio', 0.0) >= 0.3) or
                               any(ing.get('ingredient_id') in (important_ingredient_ids or []) for ing in c.get('ingredients', []))
                        ]

                    # Tier C — Cuisine group expansion
                    group_cuisines = expand_cuisine_groups(explicit_cuisines_clean + implicit_cuisines_clean)
                    if group_cuisines:
                        tierC_candidates = self._find_candidate_recipes(
                            session,
                            all_ingredient_ids,
                            match_context,
                            effective_max_cook_time,
                            0.2,
                            user_allergies,
                            recipe_category,
                            limit * 2,
                            important_ingredient_ids,
                            preferred_cuisines=group_cuisines,
                            ingredient_only_mode=ingredient_only_mode
                        )
                        tierC_candidates = [
                            c for c in tierC_candidates
                            if (c.get('match_ratio', 0.0) >= 0.3) or
                               any(ing.get('ingredient_id') in (important_ingredient_ids or []) for ing in c.get('ingredients', []))
                        ]

                    # Tier D — Other cuisines with strong ingredient match
                    tierD_candidates = self._find_candidate_recipes(
                        session,
                        all_ingredient_ids,
                        match_context,
                        effective_max_cook_time,
                        0.3,  # cần match tốt
                        user_allergies,
                        recipe_category,
                        limit * 3,
                        important_ingredient_ids,
                        preferred_cuisines=None,
                        ingredient_only_mode=ingredient_only_mode
                    )

                    # Merge theo ưu tiên A > B > C > D
                    def merge_candidates(*lists):
                        merged = []
                        seen = set()
                        for lst in lists:
                            for c in lst:
                                rid = c.get('recipe_id')
                                if rid and rid not in seen:
                                    seen.add(rid)
                                    merged.append(c)
                        return merged

                    candidates_from_tiers = merge_candidates(
                        tierA_candidates,
                        tierB_candidates,
                        tierC_candidates,
                        tierD_candidates
                    )
                    # Giữ rõ Tier A để merge ưu tiên; phần còn lại coi như other
                    preferred_cuisine_candidates = tierA_candidates
                    other_candidates = [c for c in candidates_from_tiers if c.get('recipe_id') not in {r.get('recipe_id') for r in preferred_cuisine_candidates}]
                else:
                    # Có ingredients nhưng KHÔNG có user_id và KHÔNG có ingredient_only_mode
                    # → Tìm recipes match ingredients nhưng không có user preferences
                    other_candidates = self._find_candidate_recipes(
                        session,
                        all_ingredient_ids,
                        match_context,
                        max_cook_time=None,  # Không filter theo cook_time (vì không có user preferences)
                        min_match_ratio=min_match_ratio,
                        user_allergies=[],  # Không filter theo allergies (vì không có user_id)
                        recipe_category=None,  # Không filter theo category
                        limit=limit * 3,  # Get more candidates
                        important_ingredient_ids=important_ingredient_ids,
                        preferred_cuisines=None,  # Không filter theo cuisine
                        ingredient_only_mode=False  # Không phải ingredient-only mode
                    )
                    preferred_cuisine_candidates = []  # Không tìm theo cuisine khi không có user_id
            
            # Thêm các món có POPULAR_IN với group của user (ưu tiên cao nhất)
            # QUAN TRỌNG: Chỉ gọi khi KHÔNG có ingredients (no ingredients mode)
            demographic_popular_candidates = []
            if user_id and not all_ingredient_ids:
                demographic_popular_candidates = self._find_popular_in_recipes(
                    session,
                    user_id,
                    effective_max_cook_time,
                    user_allergies,
                    recipe_category,
                    effective_preferred_cuisines,
                    limit * 2
                )
            
            # Merge và loại bỏ duplicates (ưu tiên demographic popular candidates)
            seen_recipe_ids = set()
            candidates = []
            # Debug: track Onigiri presence
            debug_onigiri_id = "rec_19797"
            onigiri_in_candidates = False
            
            # Thêm demographic popular candidates trước (ưu tiên cao nhất)
            for candidate in demographic_popular_candidates:
                recipe_id = candidate.get('recipe_id')
                if recipe_id and recipe_id not in seen_recipe_ids:
                    seen_recipe_ids.add(recipe_id)
                    candidates.append(candidate)
                    if recipe_id == debug_onigiri_id:
                        onigiri_in_candidates = True
            
            # ✅ CRITICAL FIX: Thêm preferred cuisine candidates
            # QUAN TRỌNG: Không được bỏ qua bước này!
            # Đây là nguồn candidates quan trọng để có món Japanese + Salmon
            for candidate in preferred_cuisine_candidates:
                recipe_id = candidate.get('recipe_id')
                if recipe_id and recipe_id not in seen_recipe_ids:
                    seen_recipe_ids.add(recipe_id)
                    candidates.append(candidate)
                    if recipe_id == debug_onigiri_id:
                        onigiri_in_candidates = True
            
            # Thêm other candidates (nhưng không duplicate)
            for candidate in other_candidates:
                recipe_id = candidate.get('recipe_id')
                if recipe_id and recipe_id not in seen_recipe_ids:
                    seen_recipe_ids.add(recipe_id)
                    candidates.append(candidate)
                    if recipe_id == debug_onigiri_id:
                        onigiri_in_candidates = True
            
            # Step 8: Score and rank candidates
            # Debug: Log số lượng candidates
            print(f"[DEBUG] Total candidates found: {len(candidates)} (demographic_popular: {len(demographic_popular_candidates)}, preferred_cuisine: {len(preferred_cuisine_candidates)}, other: {len(other_candidates)})", file=sys.stderr)
            if onigiri_in_candidates:
                print("[DEBUG] Onigiri is present in candidates before scoring", file=sys.stderr)
            
            recommendations = []
            # Track which recipes came from demographic_popular_candidates (POPULAR_IN)
            demographic_popular_recipe_ids = {c.get('recipe_id') for c in demographic_popular_candidates if c.get('recipe_id')}
            # Track if user has no ingredients (để quyết định có ưu tiên badge không)
            has_no_ingredients = not all_ingredient_ids or len(all_ingredient_ids) == 0
            
            # Step 8a: Batch calculate all scores for all candidates (OPTIMIZATION: giảm từ 4N queries xuống N queries)
            batch_scores = {}
            if user_id and candidates:
                # Prepare recipe data for batch calculation
                recipe_data_for_batch = [
                    {
                        "recipe_id": c.get('recipe_id'),
                        "all_ingredients": c.get('all_ingredients', []),
                        "cuisine": c.get('cuisine', [])
                    }
                    for c in candidates
                    if c.get('recipe_id')
                ]
                
                if recipe_data_for_batch:
                    batch_scores = self.scoring_engine.calculate_all_scores_batch(
                        session,
                        user_id,
                        recipe_data_for_batch,
                        effective_preferred_cuisines
                    )
            
            for candidate in candidates:
                recipe_id = candidate['recipe_id']
                
                # Đánh dấu các món từ POPULAR_IN để ưu tiên cao hơn
                is_from_popular_in = recipe_id in demographic_popular_recipe_ids
                
                # QUAN TRỌNG: Không cần extract recipe knowledge và apply knowledge rules nữa
                # vì:
                # 1. Allergen safety: đã được filter trong query (line 2062, 2235, 2329, 2524)
                # 2. Time constraints: đã được filter trong query (line 2038, 2223, 2322, 2517)
                # 3. Cuisine preference: đã được xử lý bởi CuisinePrioritizer (line 1441)
                # → Loại bỏ dependency với knowledge_based_recommender
                kb_reasons = []
                kb_score = 0.0
                
                # Calculate scores
                match_ratio = candidate.get('match_ratio', 0.0)
                # QUAN TRỌNG: Tính cuisine_priority với explicit và implicit cuisines riêng biệt
                # Explicit cuisines → priority = 1 (exact match)
                # Implicit cuisines (real-time learning) → priority = 2 (group match)
                recipe_cuisines = candidate.get('cuisine', [])
                cuisine_priority = self.cuisine_prioritizer.calculate_priority_with_implicit(
                    recipe_cuisines,
                    explicit_cuisines_clean,
                    implicit_cuisines_clean
                )
                
                # Debug: In thông tin cuisine matching và protein match (chỉ khi có explicit cuisines hoặc important ingredients)
                if (explicit_cuisines_clean and recipe_cuisines) or important_ingredient_ids:
                    recipe_title = candidate.get('title', 'Unknown')[:50]
                    # Check if recipe has important protein ingredients
                    ingredients = candidate.get('ingredients', [])
                    has_salmon = any(
                        ing.get('ingredient_id') in important_ingredient_ids
                        for ing in ingredients
                    ) if important_ingredient_ids else False
                    
                    # Debug messages (commented out to reduce verbosity)
                    # should_debug = False
                    # if explicit_cuisines_clean and recipe_cuisines:
                    #     should_debug = 'japanese' in [c.lower() for c in explicit_cuisines_clean] or any('japanese' in str(c).lower() for c in recipe_cuisines)
                    # if important_ingredient_ids and has_salmon:
                    #     should_debug = True
                    # 
                    # if should_debug:
                    #     matched_ing = candidate.get('matched_ing', [])
                    #     has_salmon_matched = any(ing_id in matched_ing for ing_id in (important_ingredient_ids or []))
                    #     print(f"[DEBUG] Recipe: {recipe_title}, recipe_cuisines={recipe_cuisines}, explicit={explicit_cuisines_clean}, priority={cuisine_priority}, match_ratio={match_ratio:.3f}, has_salmon={has_salmon}, salmon_matched={has_salmon_matched}, matched_ing={matched_ing}", file=sys.stderr)
                
                # Calculate additional scores (if user_id provided)
                # OPTIMIZATION: Sử dụng batch scores thay vì tính từng cái riêng lẻ
                # QUAN TRỌNG: Loại bỏ fallback scoring để giảm thời gian chạy (từ 4N queries xuống 0)
                if user_id and recipe_id in batch_scores:
                    scores = batch_scores[recipe_id]
                    history_score = scores.get('history_score', 0.0)
                    similar_user_score = scores.get('similar_user_score', 0.0)
                    similar_user_count = scores.get('similar_user_count', 0)
                    similar_recipe_score = scores.get('similar_recipe_score', 0.0)
                    similar_recipe_count = scores.get('similar_recipe_count', 0)
                    demographic_score = scores.get('demographic_score', 0.0)
                    demographic_group_count = scores.get('demographic_group_count', 0)
                    demographic_group_name = scores.get('demographic_group_name', "")
                else:
                    # Không có batch scores → đặt về 0 (batch_scores đã được tính ở line 1594)
                    # Nếu không có trong batch_scores, có nghĩa là recipe không có scores
                    history_score = 0.0
                    similar_user_score = 0.0
                    similar_user_count = 0
                    similar_recipe_score = 0.0
                    similar_recipe_count = 0
                    demographic_score = 0.0
                    demographic_group_count = 0
                    demographic_group_name = ""
                
                # Build final recommendation
                matched_ing_count = len(candidate.get('matched_ing', []))
                total_ing_count = len(candidate.get('ingredients', [])) if candidate.get('ingredients') else (matched_ing_count + len(candidate.get('missing_ing', [])))
                
                # Check if matched ingredients contain protein (seafood, meat, plant_protein)
                # QUAN TRỌNG: Ưu tiên recipes có protein matches cao hơn
                # PHÂN BIỆT: seafood/meat > plant_protein (salmon > bean)
                matched_ing_ids = set(candidate.get('matched_ing', []))
                has_protein_match = False
                protein_match_count = 0
                has_important_protein_match = False  # QUAN TRỌNG: Phân biệt important protein (seafood/meat) vs plant_protein
                important_protein_match_count = 0
                
                # QUAN TRỌNG: Ưu tiên important protein ingredients của user (seafood/meat) hơn plant_protein
                # Ví dụ: salmon (seafood) > bean (plant_protein)
                # QUAN TRỌNG: Check xem recipe có chứa important protein ingredients của user không (KỂ CẢ CHƯA MATCH)
                # Điều này đảm bảo món có salmon sẽ được ưu tiên hơn món chỉ có butter, salt
                if important_ingredient_ids:
                    # Check xem recipe có chứa important protein ingredients của user không (kể cả chưa match)
                    ingredients = candidate.get('ingredients', [])
                    for ing in ingredients:
                        ing_id = ing.get('ingredient_id')
                        if ing_id and ing_id in important_ingredient_ids:
                            category = ing.get('category', '')
                            # Check cả base name nếu category không có (fallback)
                            if not category and ing.get('base'):
                                # Query category từ database nếu không có trong ingredients
                                q_cat = "MATCH (i:Ingredient {ingredient_id: $id}) RETURN i.category AS cat"
                                cat_result = session.run(q_cat, id=ing_id).single()
                                if cat_result:
                                    category = cat_result.get('cat', '')
                            
                            # Phân biệt: seafood/meat > plant_protein
                            # QUAN TRỌNG: Set has_important_protein_match = True nếu recipe CÓ chứa important protein (kể cả chưa match)
                            # Điều này đảm bảo món có salmon sẽ được ưu tiên hơn món chỉ có butter, salt
                            if category in ['seafood', 'meat']:
                                has_important_protein_match = True  # Set ngay cả khi chưa match
                                if ing_id in matched_ing_ids:
                                    important_protein_match_count += 1
                                    has_protein_match = True
                                    protein_match_count += 1
                            elif category == 'plant_protein':
                                # Plant protein vẫn được tính nhưng ưu tiên thấp hơn
                                if ing_id in matched_ing_ids:
                                    has_protein_match = True
                                    protein_match_count += 1
                
                # Check từ matched ingredients (logic cũ - vẫn giữ để check protein matches khác)
                if matched_ing_ids:
                    # Nếu matched ingredients có important protein → đánh dấu ngay (đề phòng thiếu category trong list)
                    if important_ingredient_ids and any(mid in important_ingredient_ids for mid in matched_ing_ids):
                        has_important_protein_match = True
                        important_protein_match_count += len([mid for mid in matched_ing_ids if mid in important_ingredient_ids])
                        has_protein_match = True
                        protein_match_count += important_protein_match_count
                    
                    # Check từ ingredients list đã có sẵn trong candidate
                    ingredients = candidate.get('ingredients', [])
                    for ing in ingredients:
                        ing_id = ing.get('ingredient_id')
                        if ing_id and ing_id in matched_ing_ids:
                            category = ing.get('category', '')
                            # Check cả base name nếu category không có (fallback)
                            if not category and ing.get('base'):
                                # Query category từ database nếu không có trong ingredients
                                q_cat = "MATCH (i:Ingredient {ingredient_id: $id}) RETURN i.category AS cat"
                                cat_result = session.run(q_cat, id=ing_id).single()
                                if cat_result:
                                    category = cat_result.get('cat', '')
                            if category in ['seafood', 'meat', 'plant_protein']:
                                # Chỉ set has_protein_match nếu chưa có (tránh override important protein)
                                if not has_protein_match:
                                    has_protein_match = True
                                protein_match_count += 1
                                
                                # Nếu là seafood/meat và chưa có important protein match → set
                                if category in ['seafood', 'meat'] and not has_important_protein_match:
                                    has_important_protein_match = True
                                    important_protein_match_count += 1
                
                # QUAN TRỌNG: Nếu recipe có important protein ingredient của user (kể cả chưa match) → ưu tiên
                # Điều này đảm bảo món có salmon sẽ được ưu tiên hơn món chỉ có bean
                if has_important_protein_match and not has_protein_match:
                    has_protein_match = True  # Ưu tiên recipes có important protein ingredients của user
                
                # QUAN TRỌNG: Nếu user có important protein (salmon) nhưng recipe KHÔNG có salmon trong ingredients list
                # → Recipe không có salmon → không set has_important_protein_match (để sort thấp hơn)
                # Logic này đảm bảo: recipes có salmon (trong ingredients list) → has_important_protein_match = True
                #                  recipes không có salmon → has_important_protein_match = False
                # → Sorting sẽ ưu tiên recipes có salmon trước
                
                recommendations.append({
                    'recipe_id': recipe_id,
                    'title': candidate.get('title'),
                    'cuisine': candidate.get('cuisine', []),
                    'tags': candidate.get('tags', []),
                    'recipe_category': candidate.get('recipe_category'),
                    'meal': candidate.get('meal', 'Dinner'),
                    'match_percent': round(match_ratio * 100, 1),
                    '_matched_count': matched_ing_count,  # Số lượng ingredients matched
                    '_total_ing_count': total_ing_count,  # Tổng số ingredients của recipe
                    '_is_perfect_match': matched_ing_count == total_ing_count,  # Match đúng tất cả ingredients của recipe
                    'cook_time_min': candidate.get('cook_time_min'),
                    'prep_time_min': candidate.get('prep_time_min'),
                    'total_time_min': candidate.get('total_time_min'),
                    'servings': candidate.get('servings'),
                    'yield': candidate.get('yield'),
                    'image': candidate.get('image'),
                    'matched_ing': candidate.get('matched_ing', []),
                    'missing_ing': candidate.get('missing_ing', []),
                    'ingredients': candidate.get('ingredients', []),
                    'reasoning': self._merge_reasoning(
                        kb_reasons,
                        self._build_reasoning(
                            match_ratio, cuisine_priority, history_score,
                            similar_user_count, similar_recipe_count,
                            candidate.get('avg_rating', 0.0),
                            candidate.get('global_like_count', 0),
                            candidate.get('cuisine', []),
                            demographic_score, demographic_group_count, demographic_group_name,
                            effective_preferred_cuisines,
                            cuisine_priority_for_reasoning=cuisine_priority  # Pass để reasoning biết có nên hiển thị history không
                        )
                    ),
                    # Store scores for sorting
                    '_match_ratio': match_ratio,
                    '_cuisine_priority': cuisine_priority,
                    '_history_score': history_score,
                    '_similar_user_score': similar_user_score,
                    '_similar_recipe_score': similar_recipe_score,
                    '_demographic_score': demographic_score,
                    '_is_from_popular_in': is_from_popular_in,  # Flag để ưu tiên món từ POPULAR_IN
                    '_has_protein_match': has_protein_match,  # Flag: có protein match không
                    '_protein_match_count': protein_match_count,  # Số lượng protein matches
                    '_has_important_protein_match': has_important_protein_match,  # QUAN TRỌNG: Phân biệt seafood/meat vs plant_protein
                    '_important_protein_match_count': important_protein_match_count,  # Số lượng important protein matches (seafood/meat)
                    'avg_rating': candidate.get('avg_rating', 0.0),
                    'rating_count': candidate.get('rating_count', 0),
                    'global_like_count': candidate.get('global_like_count', 0),
                    'global_view_count': candidate.get('global_view_count', 0)
                })
            
            # Step 8.5: Filter recommendations khi có ingredients
            # QUAN TRỌNG: Khi user có ingredients, chỉ giữ lại recipes có match_ratio > 0
            # Vì nếu không match bất kỳ ingredient nào thì không nên recommend
            # ĐỒNG THỜI: Filter out recipes có cuisine_priority = 2 (cùng nhóm) mà match_ratio < 0.3
            # Vì chỉ cùng cuisine group không đủ, cần match ingredient tối thiểu 30%
            # ÁP DỤNG FILTER CHO TẤT CẢ recommendations có match_ratio được tính (có ingredients được match)
            filtered_count_before = len(recommendations)
            filtered_out = []
            filtered_recommendations = []
            
            for rec in recommendations:
                match_ratio = rec.get('_match_ratio', 0.0)
                cuisine_priority = rec.get('_cuisine_priority', 3)
                recipe_id = rec.get('recipe_id', 'Unknown')
                title = rec.get('title', 'Unknown')[:50]
                
                # Debug: In thông tin các món có match_ratio thấp và cuisine_priority = 2 (TẮT để giảm noise)
                # if not has_no_ingredients and match_ratio > 0 and match_ratio < 0.3:
                #     print(f"[FILTER DEBUG] Recipe: {title[:40]}, match_ratio={match_ratio:.3f}, cuisine_priority={cuisine_priority}, should_filter={cuisine_priority == 2 and match_ratio < 0.3}", file=sys.stderr)
                
                # Chỉ filter khi có ingredients (match_ratio > 0 nghĩa là có ingredients được match)
                # Nếu has_no_ingredients = True, match_ratio sẽ là 0.0 và không cần filter
                if not has_no_ingredients:
                    # QUAN TRỌNG: Nếu có preferred cuisines, cho phép món có cuisine_priority = 1 (exact match)
                    # ngay cả khi match_ratio = 0.0 (không match ingredient nào)
                    # Vì user đã chọn explicit cuisine, nên ưu tiên hiển thị món từ cuisine đó
                    if match_ratio <= 0.0:
                        # Chỉ filter nếu KHÔNG phải exact cuisine match (cuisine_priority = 1)
                        if cuisine_priority != 1:
                            filtered_out.append(f"{title} (match_ratio={match_ratio:.3f}, cuisine_priority={cuisine_priority})")
                            continue
                        # Nếu cuisine_priority = 1 (exact match), cho phép qua (match_ratio có thể = 0.0)
                    
                    # Filter: cuisine_priority = 2 (cùng nhóm) và match_ratio < 0.3
                    if cuisine_priority == 2 and match_ratio < 0.3:
                        filtered_out.append(f"{title} (cuisine_priority=2, match_ratio={match_ratio:.3f})")
                        continue
                
                filtered_recommendations.append(rec)
            
            recommendations = filtered_recommendations
            filtered_count_after = len(recommendations)
            
            # Debug: Log số lượng recommendations sau filter
            print(f"[DEBUG] Recommendations after filter: {filtered_count_after} (before: {filtered_count_before}, filtered out: {len(filtered_out)})", file=sys.stderr)
            if filtered_out:
                print(f"[DEBUG] Filtered out recipes: {filtered_out[:10]}", file=sys.stderr)
            
            # Debug: Check if any recommendations have salmon/protein
            if important_ingredient_ids:
                salmon_recipes = []
                for r in recommendations:
                    matched_ing = r.get('matched_ing', [])
                    if any(ing_id in important_ingredient_ids for ing_id in matched_ing):
                        salmon_recipes.append(r)
                print(f"[DEBUG] Recommendations with salmon/protein match: {len(salmon_recipes)}", file=sys.stderr)
                if salmon_recipes:
                    for rec in salmon_recipes[:3]:
                        print(f"[DEBUG]   - {rec.get('title', 'Unknown')[:50]} (match={rec.get('match_percent')}%, matched={rec.get('matched_ing', [])})", file=sys.stderr)
                else:
                    print(f"[DEBUG]   ⚠️ NO SALMON RECIPES FOUND! Important ingredients: {important_ingredient_ids}", file=sys.stderr)
            
            # Debug: Log cuisine priority của recommendations
            if effective_preferred_cuisines and recommendations:
                japanese_recipes = [r for r in recommendations if r.get('_cuisine_priority', 3) == 1]
                print(f"[DEBUG] Recommendations with cuisine_priority=1 (exact match): {len(japanese_recipes)}", file=sys.stderr)
                if japanese_recipes:
                    for rec in japanese_recipes[:5]:
                        print(f"[DEBUG]   - {rec.get('title', 'Unknown')[:50]} (cuisine={rec.get('cuisine', [])}, priority={rec.get('_cuisine_priority', 3)}, match={rec.get('match_percent')}%)", file=sys.stderr)
                else:
                    print(f"[DEBUG]   ⚠️ NO JAPANESE RECIPES FOUND! Effective preferred cuisines: {effective_preferred_cuisines}", file=sys.stderr)
            
            # Debug messages (TẮT để giảm noise - chỉ bật khi cần debug)
            # if not has_no_ingredients:
            #     if filtered_out:
            #         print(f"[FILTER] Filtered out {len(filtered_out)} recipes (before={filtered_count_before}, after={filtered_count_after}):", file=sys.stderr)
            #         for item in filtered_out[:10]:  # Show first 10
            #             print(f"  - {item}", file=sys.stderr)
            #     else:
            #         print(f"[FILTER] No recipes filtered (before={filtered_count_before}, after={filtered_count_after})", file=sys.stderr)
            #     
            #     # Debug: In top 10 recommendations sau khi filter để xem có món nào bị mất không
            #     if recommendations:
            #         print(f"[FILTER] Top {min(10, len(recommendations))} recommendations after filter:", file=sys.stderr)
            #         for i, rec in enumerate(recommendations[:10], 1):
            #             title = rec.get('title', 'Unknown')[:40]
            #             match_ratio = rec.get('_match_ratio', 0.0)
            #             cuisine_priority = rec.get('_cuisine_priority', 3)
            #             print(f"  {i}. {title} (match={match_ratio:.3f}, cuisine_priority={cuisine_priority})", file=sys.stderr)
            
            # Step 9: Sort by multiple factors
            # QUAN TRỌNG: Ưu tiên Cuisine, nhưng Match Ingredient vẫn là yếu tố quan trọng
            # Ưu tiên các recipe thỏa mãn NHIỀU ĐIỀU KIỆN hơn
            # 
            # Strategy theo yêu cầu:
            #   1. Ưu tiên cuisine: exact match (1) > same group (2) > other (3)
            #   2. Trong cùng cuisine priority, sắp xếp theo match ratio (ingredient match) - match ingredient vẫn là cao nhất
            #   3. Cuisine cùng nhóm chỉ gợi ý sau khi đã gợi ý xong cuisine chính xác
            #   4. Cuisine khác có thể gợi ý nếu match ingredient nhiều (match ratio cao)
            #   5. Ưu tiên các recipe thỏa mãn NHIỀU ĐIỀU KIỆN hơn (có cả cuisine đúng, match cao, similar users, etc.)
            #
            # Tính composite score dựa trên số điều kiện được thỏa mãn:
            # - Recipe càng thỏa mãn nhiều điều kiện → composite score càng cao → ưu tiên hơn
            for rec in recommendations:
                match_ratio = rec.get('_match_ratio', 0.0)
                cuisine_priority = rec.get('_cuisine_priority', 3)
                similar_user_score = rec.get('_similar_user_score', 0.0)
                similar_recipe_score = rec.get('_similar_recipe_score', 0.0)
                history_score = rec.get('_history_score', 0.0)
                demographic_score = rec.get('_demographic_score', 0.0)
                avg_rating = rec.get('avg_rating', 0.0)
                
                # Đếm số điều kiện được thỏa mãn (conditions count)
                conditions_count = 0
                
                # Điều kiện 1: Cuisine đúng (priority = 1)
                if cuisine_priority == 1:
                    conditions_count += 1
                # Điều kiện 2: Cuisine cùng nhóm (priority = 2)
                # QUAN TRỌNG: Chỉ cộng điểm nếu match_ratio >= 0.3 (30%)
                # Vì nếu match < 0.3, recipe đã bị filter out ở Step 8.5
                elif cuisine_priority == 2 and match_ratio >= 0.3:
                    conditions_count += 0.5  # Một nửa điểm vì không phải exact match
                
                # Điều kiện 3: Match ingredient tốt (>= 0.5)
                if match_ratio >= 0.5:
                    conditions_count += 1
                elif match_ratio >= 0.3:
                    conditions_count += 0.5  # Match vừa phải
                
                # Điều kiện 4: Có similar users (similar_user_score > 0)
                if similar_user_score > 0:
                    conditions_count += 0.5
                
                # Điều kiện 5: Có similar recipes (similar_recipe_score > 0)
                if similar_recipe_score > 0:
                    conditions_count += 0.5
                
                # Điều kiện 6: Có history score (user đã tương tác với recipes tương tự)
                # QUAN TRỌNG: Khi đã có cuisine_priority = 1 (match cuisine), không nên boost thêm history_score
                # Vì đã được ưu tiên bởi cuisine rồi, history_score sẽ tạo double counting và quá bias
                # Chỉ tính history_score khi KHÔNG có cuisine match (cuisine_priority > 1)
                if history_score > 0 and cuisine_priority > 1:
                    conditions_count += 0.5
                
                # Điều kiện 7: Demographic popularity (POPULAR_IN - phổ biến trong nhóm)
                # KHÔNG tính demographic_score vào conditions_count nữa (không ưu tiên badge)
                # Demographic score vẫn được tính trong final_score nhưng không ưu tiên trong sorting
                
                # Điều kiện 8: Rating cao (>= 4.0)
                if avg_rating >= 4.0:
                    conditions_count += 0.5
                
                # Lưu số điều kiện được thỏa mãn
                rec['_conditions_count'] = conditions_count
            
            # Sắp xếp theo thứ tự ưu tiên:
            # KHI KHÔNG CÓ INGREDIENTS:
            #   1. Demographic score > 0 (có badge "Popular among people like you") - ƯU TIÊN CAO NHẤT
            #   2. Cuisine priority, conditions_count, match_ratio, etc.
            # KHI CÓ INGREDIENTS:
            #   1. Cuisine priority (1 < 2 < 3) - ưu tiên cuisine trước        
            #   2. Conditions_count, match_ratio, demographic_score, etc.
            if has_no_ingredients:
                # Khi không có ingredients: không ưu tiên badge nữa
                recommendations.sort(
                    key=lambda x: (
                        x.get('_cuisine_priority', 3),  # Ưu tiên cuisine trước (1 < 2 < 3)
                        -x.get('_conditions_count', 0.0),  # Recipe thỏa mãn NHIỀU ĐIỀU KIỆN hơn ưu tiên hơn
                        -x.get('_match_ratio', 0.0),  # Trong cùng cuisine và conditions, match ingredient nhiều hơn ưu tiên hơn
                        -x.get('_similar_user_score', 0.0),  # Similar users
                        -x.get('_similar_recipe_score', 0.0),  # Similar recipes
                        -x.get('_history_score', 0.0),  # History
                        -x.get('_demographic_score', 0.0),  # Demographic popularity (POPULAR_IN) - không ưu tiên nữa
                        -x.get('avg_rating', 0.0)  # Rating
                    )
                )
            else:
                # Khi có ingredients: ưu tiên ingredient match cao hơn POPULAR_IN
                user_ing_count = len(all_ingredient_ids) if all_ingredient_ids else 0
                
                if ingredient_only_mode:
                    # INGREDIENT-ONLY MODE: 
                    # 1. Perfect match: recipe có đúng số ingredients user có VÀ match đúng tất cả
                    #    - User có 10 → recipe có 10 ingredients và match đúng 10 → ưu tiên cao nhất
                    #    - User có 2 (chicken, tomato) → recipe có 2 và có đúng chicken, tomato → ưu tiên cao nhất
                    # 2. Sau đó: recipe có ít hơn 1 ingredient VÀ match đúng tất cả
                    #    - User có 10 → recipe có 9 ingredients và match đúng 9 → ưu tiên thứ 2
                    #    - User có 2 → recipe có 1 ingredient và có chicken hoặc tomato → ưu tiên thứ 2
                    # 3. Sau đó: recipe có ít hơn 2 ingredients VÀ match đúng tất cả
                    #    - User có 10 → recipe có 8 ingredients và match đúng 8 → ưu tiên thứ 3
                    # 4. ...
                    
                    # Logic: recipe có N ingredients và match đúng N ingredients (N <= user_ingredients)
                    # Sắp xếp theo: perfect match (N = user_ingredients) → N-1 → N-2 → ...
                    # Điều kiện: matched_count == total_ing (match đúng tất cả ingredients của recipe)
                    # Nếu không có recipe nào match đúng tất cả → quay về tính theo số lượng matched (nhiều hơn = tốt hơn)
                    
                    # Kiểm tra xem có recipe nào match đúng tất cả ingredients của recipe không
                    has_perfect_match_recipes = False
                    for rec in recommendations:
                        total_ing = rec.get('_total_ing_count', len(rec.get('ingredients', [])) if rec.get('ingredients') else (len(rec.get('matched_ing', [])) + len(rec.get('missing_ing', []))))
                        matched_count = rec.get('_matched_count', len(rec.get('matched_ing', [])))
                        if matched_count == total_ing:  # Match đúng tất cả ingredients của recipe
                            has_perfect_match_recipes = True
                            break
                    
                    if has_perfect_match_recipes:
                        # Có recipe match đúng tất cả → ưu tiên theo perfect match logic
                        def get_sort_key(x):
                            total_ing = x.get('_total_ing_count', len(x.get('ingredients', [])) if x.get('ingredients') else (len(x.get('matched_ing', [])) + len(x.get('missing_ing', []))))
                            matched_count = x.get('_matched_count', len(x.get('matched_ing', [])))
                            
                            # Chỉ ưu tiên recipes có matched_count == total_ing (match đúng tất cả ingredients của recipe)
                            if matched_count != total_ing:
                                return (2, -total_ing, -matched_count, -x.get('_match_ratio', 0.0), -x.get('avg_rating', 0.0))
                            
                            # PERFECT MATCH: recipe có đúng số ingredients user có VÀ match đúng tất cả
                            if total_ing == user_ing_count:
                                return (0, -total_ing, -matched_count, -x.get('_match_ratio', 0.0), -x.get('avg_rating', 0.0))
                            
                            # Recipe có ít hơn ingredients VÀ match đúng tất cả
                            return (1, -total_ing, -matched_count, -x.get('_match_ratio', 0.0), -x.get('avg_rating', 0.0))
                        
                        recommendations.sort(key=get_sort_key)
                    else:
                        # Không có recipe nào match đúng tất cả → quay về tính theo số lượng matched (nhiều hơn = tốt hơn)
                        recommendations.sort(
                            key=lambda x: (
                                # Số lượng ingredients matched (nhiều hơn = tốt hơn)
                                -x.get('_matched_count', len(x.get('matched_ing', []))),  # Ưu tiên match nhiều ingredients hơn
                                -x.get('_match_ratio', 0.0),  # Match ratio (Jaccard similarity)
                                -x.get('avg_rating', 0.0)  # Rating
                            )
                        )
                    
                    # Log thông tin match
                    if recommendations:
                        best = recommendations[0]
                        best_matched = best.get('_matched_count', len(best.get('matched_ing', [])))
                        best_total = best.get('_total_ing_count', len(best.get('ingredients', [])) if best.get('ingredients') else (len(best.get('matched_ing', [])) + len(best.get('missing_ing', []))))
                        best_is_perfect = best.get('_is_perfect_match', best_matched == best_total)
                        print(f"[INGREDIENT-ONLY] Best match: {best.get('title', 'N/A')} - Matched {best_matched}/{user_ing_count} user ingredients, Recipe has {best_total} ingredients, Perfect match: {best_is_perfect}", file=sys.stderr)
                else:
                    # Có user_id (có preferences) - tìm theo logic bình thường với importance bonus
                    # QUAN TRỌNG: Ưu tiên theo thứ tự:
                    # 1. Preferred cuisine (1 < 2 < 3)
                    #    - Lưu ý: Recipes có cuisine_priority = 2 mà match_ratio < 0.3 đã bị filter out ở Step 8.5
                    # 2. Match ratio (match ingredient nhiều hơn) - QUAN TRỌNG NHẤT sau cuisine
                    # 3. Protein matches (có protein match ưu tiên cao hơn) - nhưng sau match_ratio
                    # 4. Conditions count, similar users/recipes, history, rating
                    # QUAN TRỌNG: Khi cuisine_priority = 1 (đã match cuisine), ưu tiên match_ratio hơn history_score
                    # để tránh quá bias về một cuisine và tăng diversity
                    # Helper function để tính effective cuisine priority dựa trên protein match
                    def get_effective_cuisine_priority(rec):
                        """
                        Điều chỉnh cuisine priority dựa trên protein match.
                        Logic ưu tiên:
                        1. Protein match (salmon) + exact cuisine match (Japanese) → 0.5 (cao nhất)
                        2. Protein match (salmon) + cùng cuisine group → 1.0 (cao)
                        3. Protein match (salmon) + cuisine khác + match ratio cao → 1.5 (trung bình)
                        4. Exact cuisine match (Japanese) + match ratio cao (không có salmon) → 2.0 (trung bình)
                        5. Cùng cuisine group + match ratio cao (không có salmon) → 2.5 (thấp)
                        6. Cuisine khác + match ratio cao (không có salmon) → 3.0 (thấp nhất)
                        """
                        cuisine_priority = rec.get('_cuisine_priority', 3)
                        has_protein = rec.get('_has_important_protein_match', False)
                        match_ratio = rec.get('_match_ratio', 0.0)
                        
                        # QUAN TRỌNG: Ưu tiên protein match (salmon) hơn cuisine match
                        if important_ingredient_ids and has_protein:
                            # Có important protein ingredients (salmon) VÀ recipe có protein match
                            if cuisine_priority == 1:
                                return 0.5  # Nhóm 1: Protein match + exact cuisine match (Japanese) → cao nhất
                            elif cuisine_priority == 2:
                                return 1.0  # Nhóm 2: Protein match + cùng cuisine group → cao
                            else:
                                # Nhóm 3: Protein match + cuisine khác
                                # Ưu tiên match ratio cao hơn
                                if match_ratio >= 0.5:
                                    return 1.5  # Match ratio cao → trung bình
                                else:
                                    return 1.8  # Match ratio thấp → thấp hơn một chút
                        else:
                            # Không có protein match (salmon)
                            if cuisine_priority == 1:
                                # Nhóm 4: Exact cuisine match (Japanese) + match ratio cao
                                if match_ratio >= 0.5:
                                    return 2.0  # Match ratio cao → trung bình
                                else:
                                    return 2.3  # Match ratio thấp → thấp hơn
                            elif cuisine_priority == 2:
                                # Nhóm 5: Cùng cuisine group + match ratio cao
                                if match_ratio >= 0.5:
                                    return 2.5  # Match ratio cao → thấp
                                else:
                                    return 2.8  # Match ratio thấp → thấp hơn
                            else:
                                # Nhóm 6: Cuisine khác + match ratio cao
                                if match_ratio >= 0.5:
                                    return 3.0  # Match ratio cao → thấp nhất
                                else:
                                    return 3.5  # Match ratio thấp → thấp nhất
                    
                    recommendations.sort(
                        key=lambda x: (
                            get_effective_cuisine_priority(x),  # Use adjusted priority for sorting
                            -x.get('_has_important_protein_match', False),  # ƯU TIÊN CAO NHẤT: Có important protein match (seafood/meat) - ưu tiên hơn plant_protein
                            -x.get('_important_protein_match_count', 0),  # Số lượng important protein matches (nhiều hơn = tốt hơn)
                            -x.get('_has_protein_match', False),  # Có protein match (True > False) - bao gồm cả plant_protein
                            -x.get('_protein_match_count', 0),  # Số lượng protein matches (nhiều hơn = tốt hơn)
                            -x.get('_match_ratio', 0.0),  # Match ingredient nhiều hơn ưu tiên hơn - sau protein match
                            -x.get('_conditions_count', 0.0),  # Recipe thỏa mãn NHIỀU ĐIỀU KIỆN hơn ưu tiên hơn
                            -x.get('_similar_user_score', 0.0),  # Similar users
                            -x.get('_similar_recipe_score', 0.0),  # Similar recipes
                            # Khi cuisine_priority = 1, giảm weight của history_score để tránh double counting
                            # Ưu tiên match_ratio hơn history_score khi đã có cuisine match
                            -(x.get('_history_score', 0.0) * (0.5 if x.get('_cuisine_priority', 3) == 1 else 1.0)),  # History (giảm 50% khi cuisine_priority = 1)
                            -x.get('avg_rating', 0.0),  # Rating
                            -x.get('_demographic_score', 0.0)  # Demographic popularity (POPULAR_IN) - ưu tiên thấp nhất khi có ingredients
                        )
                    )
            
            # Calculate final_score before removing temporary fields
            # Final score combines CF scores (history, similar_user, similar_recipe, demographic)
            for rec in recommendations:
                history_score = rec.get('_history_score', 0.0)
                similar_user_score = rec.get('_similar_user_score', 0.0)
                similar_recipe_score = rec.get('_similar_recipe_score', 0.0)
                demographic_score = rec.get('_demographic_score', 0.0)
                
                # Normalize similar_user_score và similar_recipe_score (có thể rất lớn)
                # Giả sử max score = 100, normalize về 0-1
                normalized_similar_user = min(similar_user_score / 100.0, 1.0) if similar_user_score > 0 else 0.0
                normalized_similar_recipe = min(similar_recipe_score / 100.0, 1.0) if similar_recipe_score > 0 else 0.0
                
                # Calculate final CF score (weighted combination)
                # QUAN TRỌNG: Khi cuisine_priority = 1 (đã match cuisine), giảm weight của history_score
                # để tránh double counting (cuisine đã ưu tiên rồi, không cần boost thêm từ history)
                # Weights: history 30% (giảm 50% khi cuisine_priority = 1), similar_user 25%, similar_recipe 25%, demographic 20%
                history_weight = 0.15 if cuisine_priority == 1 else 0.3  # Giảm 50% khi đã match cuisine
                final_cf_score = (
                    history_score * history_weight +
                    normalized_similar_user * 0.25 +
                    normalized_similar_recipe * 0.25 +
                    demographic_score * 0.2
                )
                
                # Apply cuisine priority multiplier
                cuisine_priority = rec.get('_cuisine_priority', 3)
                if cuisine_priority == 1:
                    cuisine_multiplier = 1.5  # Exact match: boost 50%
                elif cuisine_priority == 2:
                    cuisine_multiplier = 1.2  # Same group: boost 20%
                else:
                    cuisine_multiplier = 1.0  # Other: no boost
                
                final_score = final_cf_score * cuisine_multiplier
                
                # Store final_score and individual scores for debugging
                rec['final_score'] = final_score
                rec['cuisine_priority'] = cuisine_priority
                rec['scores'] = {
                    'history': history_score,
                    'similar_user': similar_user_score,
                    'similar_recipe': similar_recipe_score,
                    'demographic': demographic_score,
                    'final': final_score
                }
            
            # Step 10: Apply diversity constraint - giới hạn số lượng món từ một cuisine
            # QUAN TRỌNG: Không cho một cuisine quá nhiều món nếu không có món nào phù hợp với ingredients
            # Logic: Chỉ giữ lại món từ một cuisine nếu chúng có protein match hoặc match ratio cao
            if recommendations and limit > 0 and effective_preferred_cuisines:
                # Tách recommendations theo cuisine và protein match
                # Group by cuisine để đếm số lượng món từ mỗi cuisine
                cuisine_groups = {}
                for rec in recommendations:
                    cuisine_priority = rec.get('_cuisine_priority', 3)
                    has_protein = rec.get('_has_important_protein_match', False)
                    match_ratio = rec.get('_match_ratio', 0.0)
                    
                    # Xác định cuisine group
                    if cuisine_priority == 1:
                        cuisine_key = "exact_match"  # Exact cuisine match (Japanese)
                    elif cuisine_priority == 2:
                        cuisine_key = "group_match"  # Cùng cuisine group
                    else:
                        cuisine_key = "other"  # Cuisine khác
                    
                    if cuisine_key not in cuisine_groups:
                        cuisine_groups[cuisine_key] = []
                    cuisine_groups[cuisine_key].append(rec)
                
                # Apply diversity constraint: Giới hạn số lượng món từ mỗi cuisine group
                # Chỉ giữ lại món phù hợp (có protein match hoặc match ratio >= 0.5)
                final_recommendations = []
                
                # Ưu tiên theo thứ tự: exact_match > group_match > other
                for cuisine_key in ["exact_match", "group_match", "other"]:
                    if cuisine_key not in cuisine_groups:
                        continue
                    
                    cuisine_recs = cuisine_groups[cuisine_key]
                    
                    # Tách thành 2 nhóm: phù hợp và không phù hợp
                    # Ưu tiên giữ TẤT CẢ các món cuisine_priority = 1 (preferred cuisines) để không bị mất món ưa thích
                    suitable_recs = [
                        r for r in cuisine_recs
                        if r.get('_cuisine_priority', 3) == 1
                        or r.get('_has_important_protein_match', False)
                        or r.get('_match_ratio', 0.0) >= 0.5
                    ]
                    unsuitable_recs = [r for r in cuisine_recs if r not in suitable_recs]
                    
                    # Ưu tiên món phù hợp trước
                    # Giới hạn số lượng món từ mỗi cuisine group để đảm bảo diversity
                    max_per_cuisine = max(12, int(limit * 0.4))  # Tối đa 40% của limit (30) = 12 món cho mỗi cuisine group
                    
                    # Lấy món phù hợp (có protein hoặc match ratio cao)
                    selected_suitable = suitable_recs[:max_per_cuisine]
                    
                    # Chỉ lấy món không phù hợp nếu còn slot và đã có ít nhất một số món phù hợp từ cuisine khác
                    remaining_slots = limit - len(final_recommendations)
                    if remaining_slots > 0 and len(selected_suitable) > 0:
                        # Chỉ lấy thêm món không phù hợp nếu còn nhiều slot
                        max_unsuitable = max(0, min(remaining_slots - len(selected_suitable), int(limit * 0.2)))  # Tối đa 20% = 6 món
                        selected_unsuitable = unsuitable_recs[:max_unsuitable]
                        final_recommendations.extend(selected_suitable + selected_unsuitable)
                    else:
                        final_recommendations.extend(selected_suitable)
                    
                    # Nếu đã đủ limit, dừng lại
                    if len(final_recommendations) >= limit:
                        break
                
                # Nếu chưa đủ limit, lấy thêm từ các nhóm còn lại
                if len(final_recommendations) < limit:
                    remaining = limit - len(final_recommendations)
                    all_remaining = []
                    for cuisine_key in ["exact_match", "group_match", "other"]:
                        if cuisine_key in cuisine_groups:
                            already_selected_ids = {r.get('recipe_id') for r in final_recommendations}
                            remaining_from_group = [r for r in cuisine_groups[cuisine_key] if r.get('recipe_id') not in already_selected_ids]
                            all_remaining.extend(remaining_from_group)
                    
                    # Sort lại và lấy thêm
                    all_remaining.sort(key=lambda x: (
                        x.get('_has_important_protein_match', False),
                        -x.get('_match_ratio', 0.0)
                    ), reverse=True)
                    final_recommendations.extend(all_remaining[:remaining])
                
                recommendations = final_recommendations[:limit]
                
                # Debug logging
                print(
                    f"[DIVERSITY] Applied diversity constraint: {len(recommendations)} recipes selected (limit={limit})",
                    file=sys.stderr
                )
            
            # QUAN TRỌNG: Luôn apply limit ở cuối, bất kể có diversity constraint hay không
            # Đảm bảo không bao giờ return nhiều hơn limit
            if limit > 0 and len(recommendations) > limit:
                recommendations = recommendations[:limit]
            
            # Remove temporary sorting fields (but keep final_score and scores)
            for rec in recommendations:
                rec.pop('_match_ratio', None)
                rec.pop('_cuisine_priority', None)
                rec.pop('_conditions_count', None)
                rec.pop('_demographic_score', None)
                rec.pop('_is_from_popular_in', None)
                rec.pop('_history_score', None)
                rec.pop('_similar_user_score', None)
                rec.pop('_similar_recipe_score', None)
                # Giữ lại _matched_count, _total_ing_count, _is_perfect_match để có thể sử dụng trong log hoặc frontend
                # rec.pop('_matched_count', None)
                # rec.pop('_total_ing_count', None)
                # rec.pop('_is_perfect_match', None)
            
            return recommendations
    
    def _build_category_filter_condition(self, recipe_category: Optional[str]) -> tuple:
        """
        Build category filter condition for Cypher query.
        
        Returns:
            (is_main_group: bool, main_group: Optional[str], category_filter: str)
        """
        if not recipe_category:
            return (False, None, "")
        
        # Check if recipe_category is a main group
        normalized_category = self.category_mapper.normalize_category_input(recipe_category)
        is_main_group = normalized_category in self.category_mapper.MAIN_GROUPS.keys()
        main_group = normalized_category if is_main_group else None
        
        if is_main_group:
            # Build main group filter
            # QUAN TRỌNG: recipe_category có thể là array hoặc string
            # Dùng UNWIND để handle cả hai: nếu là array thì unwind, nếu là string thì wrap thành array
            if main_group == "Main dish":
                # QUAN TRỌNG: recipe_category có thể là array hoặc string
                # Dùng toString() cho cả hai và check trong string đó
                category_filter = """(
                     toLower(toString(r.recipe_category)) CONTAINS 'dinner' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'lunch' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'breakfast' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'brunch' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'entree' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'main course' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'main dish' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'side dish' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'appetizer' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'soup' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'salad' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'pasta' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'sandwich'
                 )"""
            elif main_group == "Dessert":
                category_filter = """(
                     toLower(toString(r.recipe_category)) CONTAINS 'dessert' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'cake' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'pie' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'candy' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'cookie' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'pastry' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'sweet' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'sweets' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'ice cream' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'pudding' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'muffin' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'brownie'
                 )"""
            elif main_group == "Drink":
                category_filter = """(
                     toLower(toString(r.recipe_category)) CONTAINS 'drink' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'beverage' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'cocktail' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'coffee' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'tea' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'juice' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'smoothie' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'shake' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'soda' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'water' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'wine' OR
                     toLower(toString(r.recipe_category)) CONTAINS 'beer'
                 )"""
            else:
                category_filter = ""
        else:
            # Specific category (backward compatibility)
            category_filter = f"toLower(r.recipe_category) CONTAINS toLower('{recipe_category}')"
        
        return (is_main_group, main_group, category_filter)
    
    def _find_candidate_recipes(
        self,
        session,
        ingredient_ids: List[str],
        match_context: IngredientMatchContext,
        max_cook_time: Optional[int],
        min_match_ratio: float,
        user_allergies: List[str],
        recipe_category: Optional[str] = None,
        limit: int = 100,
        important_ingredient_ids: Optional[List[str]] = None,  # Important ingredients (protein) for boost
        preferred_cuisines: Optional[List[str]] = None,  # Filter by preferred cuisines if provided
        ingredient_only_mode: bool = False,  # Chỉ áp dụng perfect match khi ingredient-only (không có user_id)
    ) -> List[Dict]:
        """
        Find candidate recipes using ingredient matching.
        
        Giải thích:
        - Tìm recipes có ingredients match với user ingredients
        - Filter theo:
          + max_cook_time (HARD CONSTRAINT)
          + user_allergies (HARD CONSTRAINT - safety first)
          + recipe_category (HARD CONSTRAINT - meal type preference, lọc ra nếu không match)
          + preferred_cuisines (OPTIONAL - filter by cuisine if provided)
        - Tính match ratio (Jaccard similarity)
        - Trả về candidates có match_ratio >= min_match_ratio
        """
        # Normalize preferred cuisines for matching
        preferred_cuisines_lower = []
        if preferred_cuisines:
            preferred_cuisines_lower = [c.lower().strip() for c in preferred_cuisines if c]
        
        # REMOVED: recipe_category filter (quá chặt, gây ra chỉ có 3 món)
        # Không filter theo recipe_category nữa - để có nhiều recommendations hơn
        
        q = """
        // Find recipes with matching ingredients
        // CHỈ MATCH EXACT: ingredient_id exact match hoặc base exact match
        // KHÔNG match qua alt_names hoặc synonyms để tránh nhầm lẫn (ví dụ: coriander ↔ cilantro)
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE 
            (i.ingredient_id IN $input_ing
            OR (i.base IS NOT NULL AND toLower(i.base) IN $input_bases))
        // INGREDIENT-ONLY MODE: Không filter theo cook_time, cuisine, category
        AND ($ingredient_only_mode OR $max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
        // Filter by preferred cuisines if provided (chỉ khi KHÔNG phải ingredient-only mode)
        AND ($ingredient_only_mode OR size($preferred_cuisines) = 0 OR 
             any(cuisine IN coalesce(r.cuisine, []) 
                 WHERE any(pc IN $preferred_cuisines WHERE toLower(pc) = toLower(cuisine) OR toLower(cuisine) CONTAINS toLower(pc) OR toLower(pc) CONTAINS toLower(cuisine))))
        // REMOVED: recipe_category filter (quá chặt)
        
        WITH r, collect(DISTINCT i.ingredient_id) AS matched_ing
        // QUAN TRỌNG: Yêu cầu ít nhất 1 matched ingredient (giảm từ 2 xuống 1 để có nhiều candidates hơn)
        WHERE size(matched_ing) >= 1
        
        // Get all recipe ingredients (for allergen check)
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // INGREDIENT-ONLY MODE: Chỉ gợi ý recipes có số ingredients <= user ingredients
        // Ví dụ: user có 10 ingredients -> chỉ gợi ý recipes có <= 10 ingredients
        // Ví dụ: user có 2 ingredients (chicken, tomato) -> chỉ gợi ý recipes có <= 2 ingredients
        WITH r, matched_ing, all_ing, size(all_ing) AS ing_count
        WHERE (NOT $ingredient_only_mode OR ing_count <= size($input_ing))
        
        // Filter allergens early (HARD CONSTRAINT - safety first)
        // INGREDIENT-ONLY MODE: Không filter theo allergies
        WITH r, matched_ing, all_ing, ing_count
        WHERE ($ingredient_only_mode OR size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies))
        
        WITH r, matched_ing, all_ing, size(all_ing) AS ing_count
        
        // Get matched ingredient categories for importance bonus
        MATCH (r)-[:HAS_INGREDIENT]->(matched_ing_node:Ingredient)
        WHERE matched_ing_node.ingredient_id IN matched_ing
        WITH r, matched_ing, all_ing, ing_count,
             collect(DISTINCT matched_ing_node.category) AS matched_categories
        
        // Calculate base Jaccard match ratio
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             CASE 
                 WHEN ing_count = 0 AND size($input_ing) = 0 THEN 0.0
                 WHEN ing_count = 0 OR size($input_ing) = 0 THEN 0.0
                 ELSE toFloat(size(matched_ing)) / 
                      toFloat(ing_count + size($input_ing) - size(matched_ing))
             END AS base_match_ratio,
             // Importance bonus - CHỈ áp dụng khi KHÔNG phải ingredient-only mode
             // Khi ingredient-only mode: KHÔNG tính bonus cho protein/category
             CASE 
                 WHEN $ingredient_only_mode THEN 0.0  // Không tính bonus khi ingredient-only
                 WHEN size($important_ing) > 0 THEN
                     // Match với chính xác important ingredients của user (ví dụ salmon) -> +0.2 per match (cao nhất)
                     size([ing IN matched_ing WHERE ing IN $important_ing]) * 0.2 +
                     // Match với protein khác (không phải important ingredients của user, ví dụ chicken) -> +0.05 per match
                     // Tính: tổng số protein matches - số important ingredient matches
                     CASE 
                         WHEN (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) - 
                               size([ing IN matched_ing WHERE ing IN $important_ing])) > 0
                         THEN (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) - 
                               size([ing IN matched_ing WHERE ing IN $important_ing])) * 0.05
                         ELSE 0.0
                     END +
                     // Grain matches
                     size([cat IN matched_categories WHERE cat = 'grain']) * 0.02 +
                     // Vegetable/Fruit matches
                     size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) * 0.01
                 ELSE 
                     // Không có important ingredients từ user -> dùng logic cũ
                     (size([cat IN matched_categories WHERE cat IN ['meat', 'plant_protein', 'seafood']]) * 0.03 +
                      size([cat IN matched_categories WHERE cat = 'grain']) * 0.02 +
                      size([cat IN matched_categories WHERE cat IN ['vegetable', 'fruit']]) * 0.01)
             END AS importance_bonus
        
        // PERFECT MATCH BONUS: Chỉ áp dụng khi ingredient-only mode (không có user_id)
        // Nếu user có đủ ingredients recipe cần (matched = user ingredients)
        // Ưu tiên cao nhất: recipe có đúng số ingredients user có (không hơn, không kém)
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             base_match_ratio, importance_bonus,
             // Perfect match: số ingredients matched = số ingredients user có
             // CHỈ áp dụng khi ingredient_only_mode = true (user chỉ có ingredients, không có preferences)
             CASE 
                 WHEN $ingredient_only_mode AND size(matched_ing) = size($input_ing) AND size($input_ing) > 0 THEN 0.5  // Perfect match bonus
                 ELSE 0.0
             END AS perfect_match_bonus
        
        // Calculate weighted match ratio: base + importance bonus + perfect match bonus (capped at 1.0)
        // Khi ingredient-only mode: chỉ dùng base_match_ratio + perfect_match_bonus (không có importance_bonus)
        WITH r, matched_ing, all_ing, ing_count, matched_categories,
             base_match_ratio, importance_bonus, perfect_match_bonus,
             CASE 
                 WHEN base_match_ratio + importance_bonus + perfect_match_bonus > 1.0 THEN 1.0
                 ELSE base_match_ratio + importance_bonus + perfect_match_bonus
             END AS match_ratio
        
        WHERE match_ratio >= $min_match
        
        // OPTIMIZATION: Gộp các OPTIONAL MATCH để giảm số lượng passes
        // Collect recipe details and global popularity metrics trong 1 pass
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, matched_ing, all_ing, match_ratio,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, all_ing, match_ratio, ingredients, missing_ing,
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
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                ELSE 'Dinner'
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
            important_ing=important_ingredient_ids or [],
            preferred_cuisines=preferred_cuisines_lower or [],
            ingredient_only_mode=ingredient_only_mode,
            lim=limit
        )
        
        candidates = [dict(row) for row in result]
        print(f"[DEBUG _find_candidate_recipes] Found {len(candidates)} candidates (limit={limit}, min_match_ratio={min_match_ratio}, ingredient_ids={len(ingredient_ids) if ingredient_ids else 0})", file=sys.stderr)
        return candidates
    
    def _find_cuisine_only_recipes(
        self,
        session,
        preferred_cuisines: List[str],
        max_cook_time: Optional[int],
        user_allergies: List[str],
        recipe_category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Find recipes from preferred cuisines WITHOUT requiring ingredient match.
        Used as fallback when no recipes found with ingredient matching.
        
        Giải thích:
        - Tìm recipes từ preferred cuisines chỉ dựa trên cuisine
        - KHÔNG yêu cầu ingredient match
        - Filter theo max_cook_time, allergies, và category
        - Ưu tiên recipes có rating cao và popular
        """
        # Normalize preferred cuisines for matching
        preferred_cuisines_lower = [c.lower().strip() for c in preferred_cuisines if c]
        
        if not preferred_cuisines_lower:
            return []
        
        q = """
        // Find recipes from preferred cuisines (no ingredient match required)
        MATCH (r:Recipe)
        WHERE 
            ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
        AND any(cuisine IN coalesce(r.cuisine, []) 
                WHERE any(pc IN $preferred_cuisines 
                    WHERE toLower(pc) = toLower(cuisine) OR 
                          toLower(cuisine) CONTAINS toLower(pc) OR 
                          toLower(pc) CONTAINS toLower(cuisine)))
        
        // Get all recipe ingredients (for allergen check)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens early (HARD CONSTRAINT - safety first)
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        
        // Get recipe details and popularity metrics
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, all_ing,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
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
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                ELSE 'Dinner'
            END AS meal,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            [] AS matched_ing,  // No matched ingredients (cuisine-only search)
            all_ing AS missing_ing,
            ingredients,
            all_ing AS all_ingredients,
            0.0 AS match_ratio,  // No ingredient match
            avg_rating,
            rating_count,
            global_like_count,
            global_view_count
        LIMIT $lim
        """
        
        result = session.run(
            q,
            preferred_cuisines=preferred_cuisines_lower,
            max_cook=max_cook_time,
            user_allergies=user_allergies or [],
            lim=limit
        )
        
        return [dict(row) for row in result]
    
    def _find_popular_recipes(
        self,
        session,
        user_id: Optional[str],
        max_cook_time: Optional[int],
        user_allergies: List[str],
        recipe_category: Optional[str] = None,
        limit: int = 50,
    ) -> List[Dict]:
        """
        Find popular recipes when no ingredients provided.
        
        Giải thích:
        - Tìm recipes phổ biến dựa trên likes và ratings
        - Nếu có user_id, ưu tiên recipes từ similar users hoặc similar recipes
        - Filter theo max_cook_time, allergies, và category
        """
        # Nếu có user_id, tìm từ similar users/recipes trước
        if user_id:
            q = """
            // Tìm recipes từ similar users hoặc similar recipes
            OPTIONAL MATCH (u:User {user_id: $uid})-[sim:SIMILAR_USER]->(u2:User)-[iv1:INTERACTED_WITH]->(r1:Recipe)
            WHERE (iv1.liked = true OR iv1.rating >= 4.0 OR iv1.event_type = 'like')
            OPTIONAL MATCH (u:User {user_id: $uid})-[iv2:INTERACTED_WITH]->(liked:Recipe)
            WHERE (iv2.liked = true OR iv2.rating >= 4.0 OR iv2.event_type = 'like')
            OPTIONAL MATCH (liked)-[:SIMILAR_RECIPE]->(r2:Recipe)
            WITH collect(DISTINCT r1) + collect(DISTINCT r2) AS recipes
            UNWIND recipes AS r
            WITH DISTINCT r
            WHERE r IS NOT NULL AND ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
            
            // Get all recipe ingredients (for allergen check)
            OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
            WITH r, collect(DISTINCT ai.ingredient_id) AS all_ing
            
            // Filter allergens early (HARD CONSTRAINT - safety first)
            WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
            
            // Get recipe details and popularity metrics
            OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
            OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
            WITH r, all_ing,
                 collect({
                     ingredient_id: ing.ingredient_id,
                     ingredient_name: coalesce(ing.name, ing.canonical_name),
                     base: coalesce(ing.base, ing.canonical_name),
                     category: ing.category
                 }) AS ingredients,
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
                    WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                    WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                    WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                    WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                    ELSE 'Dinner'
                END AS meal,
                r.cook_time_min AS cook_time_min,
                r.prep_time_min AS prep_time_min,
                r.total_time_min AS total_time_min,
                r.servings AS servings,
                r.yield AS yield,
                head(coalesce(r.image_urls, [])) AS image,
                [] AS matched_ing,
                all_ing AS missing_ing,
                ingredients,
                all_ing AS all_ingredients,
                0.0 AS match_ratio,
                avg_rating,
                rating_count,
                global_like_count,
                global_view_count
            LIMIT $lim
            """
            result = session.run(
                q,
                uid=user_id,
                max_cook=max_cook_time,
                user_allergies=user_allergies or [],
                lim=limit
            )
            candidates = [dict(row) for row in result]
            
            # Nếu có đủ candidates, return
            if len(candidates) >= limit:
                return candidates
        
        # Nếu không có user_id hoặc không đủ candidates, tìm popular recipes chung
        q = """
        MATCH (r:Recipe)
        WHERE ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
        
        // Get all recipe ingredients (for allergen check)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens early (HARD CONSTRAINT - safety first)
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        
        // Get recipe details and popularity metrics
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, all_ing,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
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
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                ELSE 'Dinner'
            END AS meal,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            [] AS matched_ing,
            all_ing AS missing_ing,
            ingredients,
            all_ing AS all_ingredients,
            0.0 AS match_ratio,
            avg_rating,
            rating_count,
            global_like_count,
            global_view_count
        LIMIT $lim
        """
        
        result = session.run(
            q,
            max_cook=max_cook_time,
            user_allergies=user_allergies or [],
            lim=limit
        )
        
        return [dict(row) for row in result]
    
    def _find_popular_in_recipes(
        self,
        session,
        user_id: str,
        max_cook_time: Optional[int],
        user_allergies: List[str],
        recipe_category: Optional[str] = None,
        preferred_cuisines: Optional[List[str]] = None,
        limit: int = 20
    ) -> List[Dict]:
        """
        Tìm các recipes có POPULAR_IN với group của user và match cuisine.
        KHÔNG cần ingredient match - chỉ cần POPULAR_IN + cuisine match.
        
        Logic giống query của user:
        MATCH (u:User {user_id:"user_7e4ffbcb"})-[:BELONGS_TO]->(g:Group)
        MATCH (g)-[:POPULAR_IN]->(r:Recipe)
        WHERE any(c IN coalesce(r.cuisine, []) WHERE toLower(c) CONTAINS "vietnam" OR "vietnam" CONTAINS toLower(c))
        AND coalesce(r.cook_time_min, 999999) <= 180
        """
        if not user_id:
            return []
        
        # Lấy user's favorite cuisines
        user_fav_result = session.run("""
            MATCH (u:User {user_id: $uid})-[:FAVORS_CUISINE]->(c:Cuisine)
            RETURN collect(DISTINCT toLower(c.name)) AS favorite_cuisines
        """, uid=user_id).single()
        
        user_favorite_cuisines = user_fav_result.get('favorite_cuisines', []) if user_fav_result else []
        
        # Xác định target cuisines
        normalized_pref_cuisines = []
        if preferred_cuisines:
            normalized_pref_cuisines = [c.lower().strip() for c in preferred_cuisines if c]
        
        target_cuisines = normalized_pref_cuisines if normalized_pref_cuisines else user_favorite_cuisines
        
        # Build cuisine match condition - nếu không có target_cuisines, KHÔNG filter theo cuisine
        # Chỉ tìm các món có POPULAR_IN với group (bất kỳ cuisine nào)
        # QUAN TRỌNG: Không return [] khi không có target_cuisines - vẫn tìm POPULAR_IN
        if target_cuisines:
            cuisine_where = """        // Filter by cuisine match - giống logic calculate_demographic_score
        WHERE any(rc IN coalesce(r.cuisine, []) WHERE 
            any(tc IN $target_cuisines WHERE 
                toLower(toString(rc)) CONTAINS tc OR 
                tc CONTAINS toLower(toString(rc))
            )
        )
        AND"""
        else:
            # Không có target_cuisines -> không filter theo cuisine, chỉ lấy POPULAR_IN
            cuisine_where = "        WHERE"
        
        q = f"""
        MATCH (u:User {{user_id: $uid}})-[:BELONGS_TO]->(g:Group)
        MATCH (g)-[:POPULAR_IN]->(r:Recipe)
        
{cuisine_where}
        
        // Filter by cook_time
        ($max_cook IS NULL OR coalesce(r.cook_time_min, 999999) <= $max_cook)
        
        // Get all recipe ingredients (for allergen check)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH DISTINCT r, g, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens (HARD CONSTRAINT - safety first)
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        """
        
        # Add recipe_category filter if provided
        if recipe_category:
            q += """
        
        // Filter by recipe_category if provided
        AND ($recipe_category IS NULL OR toLower(r.recipe_category) CONTAINS toLower($recipe_category))
            """
        
        # Complete the query
        q += """
        
        // Get recipe details and popularity metrics
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, all_ing,
             collect(DISTINCT {
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
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
                WHEN toLower(r.recipe_category) CONTAINS 'breakfast' OR toLower(r.recipe_category) CONTAINS 'brunch' THEN 'Breakfast'
                WHEN toLower(r.recipe_category) CONTAINS 'lunch' THEN 'Lunch'
                WHEN toLower(r.recipe_category) CONTAINS 'dinner' THEN 'Dinner'
                WHEN toLower(r.recipe_category) CONTAINS 'snack' OR toLower(r.recipe_category) CONTAINS 'dessert' THEN 'Snack'
                ELSE 'Dinner'
            END AS meal,
            r.cook_time_min AS cook_time_min,
            r.prep_time_min AS prep_time_min,
            r.total_time_min AS total_time_min,
            r.servings AS servings,
            r.yield AS yield,
            head(coalesce(r.image_urls, [])) AS image,
            [] AS matched_ing,
            all_ing AS missing_ing,
            ingredients,
            all_ing AS all_ingredients,
            0.0 AS match_ratio,
            avg_rating,
            rating_count,
            global_like_count,
            global_view_count
        ORDER BY r.cook_time_min ASC
        LIMIT $lim
        """
        
        params = {
            "uid": user_id,
            "max_cook": max_cook_time,
            "user_allergies": user_allergies or [],
            "lim": limit
        }
        
        # Chỉ thêm target_cuisines vào params nếu có
        if target_cuisines:
            params["target_cuisines"] = target_cuisines
        
        if recipe_category:
            params["recipe_category"] = recipe_category
        
        result = session.run(q, **params)
        return [dict(row) for row in result]
    
    def _identify_important_ingredients(self, session, ingredient_ids: List[str]) -> List[str]:
        """
        Identify important ingredients (protein: seafood, meat only - NOT plant_protein).
        These are ingredients that should have higher weight in match ratio calculation.
        
        Giải thích:
        - Important ingredients là các protein (seafood, meat) - KHÔNG bao gồm plant_protein
        - Khi recipe match với important ingredients, sẽ được boost điểm cao hơn
        - Returns: List of important ingredient IDs
        """
        if not ingredient_ids:
            return []
        
        q = """
        MATCH (i:Ingredient)
        WHERE i.ingredient_id IN $ids
        RETURN i.ingredient_id AS id, i.category AS category
        """
        
        important = []
        result = session.run(q, ids=ingredient_ids)
        for row in result:
            category = row.get("category")
            # CHỈ lấy seafood và meat, KHÔNG lấy plant_protein
            if category in ['seafood', 'meat']:
                important.append(row["id"])
        
        return important
    
    def _extract_user_info(self, session, user_id: str) -> Dict:
        """
        Extract user information directly from database (allergies, favorite_cuisines, max_cook_time).
        
        QUAN TRỌNG: Thay thế extract_user_knowledge từ knowledge_based_recommender
        để loại bỏ dependency không cần thiết.
        
        Returns: Dict với keys: allergies, favorite_cuisines, max_cook_time
        """
        q = """
        MATCH (u:User {user_id: $uid})
        OPTIONAL MATCH (u)-[:ALLERGIC_TO]->(a:Ingredient)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        RETURN 
            collect(DISTINCT a.ingredient_id) AS allergies,
            collect(DISTINCT c.name) AS favorite_cuisines,
            u.max_cook_time AS max_cook_time
        """
        
        result = session.run(q, uid=user_id).single()
        
        if not result:
            return {
                'allergies': [],
                'favorite_cuisines': [],
                'max_cook_time': None
            }
        
        return {
            'allergies': result.get('allergies') or [],
            'favorite_cuisines': [c.lower().strip() for c in (result.get('favorite_cuisines') or []) if c],
            'max_cook_time': result.get('max_cook_time')
        }
    
    def _extract_implicit_cuisine_preferences(
        self, 
        session, 
        user_id: str,
        days_lookback: int = 30,
        min_interactions: int = 2,
        min_confidence: float = 0.3
    ) -> List[str]:
        """
        Extract implicit cuisine preferences from recent user interactions (REAL-TIME LEARNING).
        
        Giải thích:
        - Phân tích các recipes user đã like/rate cao trong N ngày gần đây (mặc định 30 ngày)
        - Đếm tần suất xuất hiện của mỗi cuisine
        - Tính confidence score dựa trên:
          + Số lượng interactions với cuisine đó
          + Loại interaction (like > rating >= 4.0 > rating < 4.0)
          + Độ mới của interaction (recent interactions có weight cao hơn)
        - Chỉ trả về cuisines có confidence >= min_confidence và có ít nhất min_interactions
        
        Logic:
        - Like = 1.0 weight
        - Rating >= 4.0 = 0.8 weight
        - Rating < 4.0 = 0.3 weight
        - Recency: exponential decay với half-life 15 ngày (gần đây hơn = weight cao hơn)
        - Confidence = (weighted_sum / max_possible_weight) * recency_factor
        
        Returns: List of cuisine names (normalized, lowercase)
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r:Recipe)
        WHERE 
            // Chỉ lấy interactions trong N ngày gần đây
            iv.timestamp IS NOT NULL 
            AND duration.inDays(iv.timestamp, datetime()).days <= $days_lookback
            // Chỉ lấy interactions tích cực (like hoặc rating >= 3.0)
            AND ((iv.liked = true OR iv.event_type = 'like') 
                 OR (iv.event_type = 'rating' AND iv.rating >= 3.0))
            // Recipe phải có cuisine
            AND r.cuisine IS NOT NULL 
            AND size(r.cuisine) > 0
        
        WITH iv, r,
            // Interaction weight: like > rating >= 4.0 > rating < 4.0
            CASE 
                WHEN iv.liked = true OR iv.event_type = 'like' THEN 1.0
                WHEN iv.event_type = 'rating' AND iv.rating >= 4.0 THEN 0.8
                WHEN iv.event_type = 'rating' AND iv.rating >= 3.0 THEN 0.3
                ELSE 0.0
            END AS interaction_weight,
            // Recency weight: exponential decay với half-life 15 ngày
            // Càng gần đây càng có weight cao
            CASE 
                WHEN iv.timestamp IS NULL THEN 0.5
                ELSE exp(-duration.inDays(iv.timestamp, datetime()).days / 15.0)
            END AS recency_weight,
            r.cuisine AS recipe_cuisines
        
        // Unwind cuisine list để đếm từng cuisine
        UNWIND recipe_cuisines AS cuisine
        WITH cuisine, interaction_weight, recency_weight,
             interaction_weight * recency_weight AS weighted_score
        
        // Aggregate: tính tổng weighted score cho mỗi cuisine
        WITH toLower(trim(cuisine)) AS cuisine_normalized,
             sum(weighted_score) AS total_weighted_score,
             count(*) AS interaction_count
        
        // Tính confidence score
        // max_possible_weight = số interactions * 1.0 (like) * 1.0 (recency = 1.0 nếu mới nhất)
        // Confidence = total_weighted_score / (interaction_count * 1.0) * recency_factor
        // recency_factor = average recency weight (đã tính trong weighted_score)
        WITH cuisine_normalized, total_weighted_score, interaction_count,
             // Confidence = weighted average / max possible
             total_weighted_score / toFloat(interaction_count) AS avg_weighted_score
        
        // Filter: chỉ lấy cuisines có đủ interactions và confidence
        WHERE interaction_count >= $min_interactions
          AND avg_weighted_score >= $min_confidence
        
        // Sắp xếp theo confidence (cao nhất trước)
        ORDER BY avg_weighted_score DESC, interaction_count DESC
        
        RETURN cuisine_normalized AS cuisine
        LIMIT 5  // Chỉ lấy top 5 cuisines để tránh quá nhiều
        """
        
        result = session.run(
            q,
            uid=user_id,
            days_lookback=days_lookback,
            min_interactions=min_interactions,
            min_confidence=min_confidence
        )
        
        implicit_cuisines = []
        for row in result:
            cuisine = row.get("cuisine")
            if cuisine and cuisine.strip():
                implicit_cuisines.append(cuisine.strip())
        
        # Debug logging (TẮT để giảm noise - chỉ bật khi cần debug)
        # if implicit_cuisines:
        #     print(f"[REAL-TIME LEARNING] User {user_id}: Detected implicit cuisine preferences: {implicit_cuisines}", file=sys.stderr)
        
        return implicit_cuisines
    
    def _merge_reasoning(self, kb_reasons: List[str], build_reasons: List[str]) -> List[str]:
        """
        Merge reasoning from knowledge-based rules and build_reasoning, removing duplicates.
        
        Giải thích:
        - kb_reasons: reasoning từ knowledge-based rules (có thể có cuisine preference)
        - build_reasons: reasoning từ _build_reasoning (có thể có cuisine priority)
        - Loại bỏ duplicate, đặc biệt là cuisine reasoning
        """
        if not kb_reasons:
            kb_reasons = []
        if not build_reasons:
            build_reasons = []
        
        # Convert kb_reasons to strings if needed
        kb_reasons_str = [str(r) if not isinstance(r, str) else r for r in kb_reasons]
        build_reasons_str = [str(r) if not isinstance(r, str) else r for r in build_reasons]
        
        # Kiểm tra xem kb_reasons đã có cuisine reasoning chưa
        # Kiểm tra cả emoji (🍜 hoặc 🍲) và nội dung (Matches your favorite cuisine, Similar to your preferred cuisine group)
        kb_has_cuisine = any(
            '🍜' in r or '🍲' in r or 
            'Matches your favorite cuisine' in r or 
            'Similar to your preferred cuisine group' in r
            for r in kb_reasons_str
        )
        build_has_cuisine = any(
            '🍜' in r or '🍲' in r or 
            'Matches your favorite cuisine' in r or 
            'Similar to your preferred cuisine group' in r
            for r in build_reasons_str
        )
        
        # QUAN TRỌNG: Chỉ giữ 1 cuisine tag
        # Nếu cả hai đều có cuisine tag, ưu tiên kb_reasons và loại bỏ từ build_reasons
        if kb_has_cuisine and build_has_cuisine:
            build_reasons_str = [
                r for r in build_reasons_str 
                if '🍜' not in r and '🍲' not in r and 
                   'Matches your favorite cuisine' not in r and 
                   'Similar to your preferred cuisine group' not in r
            ]
        # Nếu chỉ build_reasons có, giữ nguyên
        # Nếu chỉ kb_reasons có, giữ nguyên
        
        # Merge và loại bỏ duplicate (kiểm tra exact match)
        merged = []
        seen = set()
        
        # Thêm kb_reasons trước (ưu tiên)
        for reason in kb_reasons_str:
            if reason and reason.strip() and reason not in seen:
                seen.add(reason)
                merged.append(reason)
        
        # Thêm build_reasons (loại bỏ duplicate)
        for reason in build_reasons_str:
            if reason and reason.strip() and reason not in seen:
                seen.add(reason)
                merged.append(reason)
        
        return merged
    
    def _build_reasoning(
        self,
        match_ratio: float,
        cuisine_priority: int,
        history_score: float,
        similar_user_count: int,
        similar_recipe_count: int,
        avg_rating: float,
        global_like_count: int,
        recipe_cuisines: List[str] = None,
        demographic_score: float = 0.0,
        demographic_group_count: int = 0,
        demographic_group_name: str = "",
        effective_preferred_cuisines: List[str] = None,
        cuisine_priority_for_reasoning: int = None,  # Optional: để biết có nên hiển thị history reasoning không
        recipe_category: str = None,  # Recipe category để check match
        user_recipe_category: str = None  # User's selected recipe category (Main dish, Dessert, Drink)
    ) -> List[str]:
        """
        Build reasoning explanations for recommendations.
        
        Giải thích từng phần:
        - Ingredient matching: giải thích tại sao recipe phù hợp với ingredients user có
        - Cuisine priority: giải thích tại sao recipe từ favorite cuisine được recommend
        - History score: giải thích similarity với past interactions
        - Similar users: giải thích users tương tự đã thích recipe này
        - Similar recipes: giải thích recipes tương tự user đã thích
        - Demographic popularity: giải thích recipe phổ biến trong nhóm demographic của user
        - Global popularity: giải thích rating và likes
        """
        reasons = []
        
        # Ingredient matching reasoning
        # QUAN TRỌNG: Chỉ hiển thị ingredient matching reasoning khi match_ratio đủ cao
        # Và không hiển thị khi đã có cuisine match (cuisine_priority = 1) để tránh redundant
        # Vì khi đã match cuisine, ingredient matching là điều hiển nhiên
        effective_cuisine_priority = cuisine_priority_for_reasoning if cuisine_priority_for_reasoning is not None else cuisine_priority
        
        # Chỉ hiển thị ingredient matching khi:
        # 1. Match ratio đủ cao (>= 0.3)
        # 2. VÀ (không có exact cuisine match HOẶC match ratio rất cao >= 0.5)
        if match_ratio >= 0.75:
            reasons.append('✅ Shares most of your given ingredients')
        elif match_ratio >= 0.5:
            # Chỉ hiển thị khi không có exact cuisine match, hoặc match ratio rất cao
            if effective_cuisine_priority > 1 or match_ratio >= 0.6:
                reasons.append('🧂 Partially matches your given ingredients')
        elif match_ratio >= 0.3:
            # Chỉ hiển thị khi KHÔNG có cuisine match (priority = 3)
            # Vì match ratio thấp (0.3-0.5) + có cuisine match → không cần hiển thị
            if effective_cuisine_priority == 3:
                reasons.append('🥄 Slightly matches your given ingredients')
        
        # Recipe category reasoning (HARD CONSTRAINT - chỉ hiển thị khi match)
        # Nếu user có chọn recipe_category và recipe match → hiển thị badge
        if user_recipe_category and recipe_category:
            # Check if recipe category matches user's selected category
            # Sử dụng self.category_mapper để check match
            if self.category_mapper.is_category_in_main_group(recipe_category, user_recipe_category):
                # Map main group to display name
                category_display = {
                    "Main dish": "Main Dish",
                    "Dessert": "Dessert",
                    "Drink": "Drink"
                }
                display_name = category_display.get(user_recipe_category, user_recipe_category)
                reasons.append(f'🍽️ Matches your meal type ({display_name})')
        
        # Cuisine priority reasoning
        # cuisine_priority: 1=exact match, 2=group match, 3=no match
        if cuisine_priority == 1:
            reasons.append('🍜 Matches your favorite cuisine')
        elif cuisine_priority == 2:
            reasons.append('🍲 Similar to your preferred cuisine group')
        
        # History score reasoning
        # QUAN TRỌNG: Khi cuisine_priority = 1 (đã match cuisine), không hiển thị history reasoning
        # Vì đã có "Matches your favorite cuisine" rồi, không cần duplicate
        # Chỉ hiển thị history reasoning khi KHÔNG có cuisine match (cuisine_priority > 1)
        if history_score > 0.5:
            # Sử dụng cuisine_priority_for_reasoning nếu có, nếu không thì dùng cuisine_priority
            effective_cuisine_priority = cuisine_priority_for_reasoning if cuisine_priority_for_reasoning is not None else cuisine_priority
            if effective_cuisine_priority > 1:  # Chỉ hiển thị khi KHÔNG có exact cuisine match
                reasons.append('📚 Similar to recipes you interacted with before')
        
        # Similar user reasoning
        if similar_user_count > 0:
            if similar_user_count > 5:
                reasons.append('👥 Liked by many users similar to you')
            elif similar_user_count > 2:
                reasons.append('👥 Liked by users similar to you')
            else:
                reasons.append('👥 Tried by a user similar to you')
        
        # Similar recipe reasoning
        # QUAN TRỌNG: Khi cuisine_priority = 1 hoặc 2 (đã match cuisine), không hiển thị similar_recipe reasoning
        # Vì đã có "Matches your favorite cuisine" hoặc "Similar to your preferred cuisine group" rồi
        # Similar recipes thường cũng cùng cuisine → redundant
        # Chỉ hiển thị khi KHÔNG có cuisine match (cuisine_priority = 3)
        if similar_recipe_count > 0:
            # Sử dụng cuisine_priority_for_reasoning nếu có, nếu không thì dùng cuisine_priority
            effective_cuisine_priority = cuisine_priority_for_reasoning if cuisine_priority_for_reasoning is not None else cuisine_priority
            if effective_cuisine_priority == 3:  # Chỉ hiển thị khi KHÔNG có cuisine match
                if similar_recipe_count > 3:
                    reasons.append('🔗 Very similar to multiple recipes you liked')
                elif similar_recipe_count > 1:
                    reasons.append('🔗 Similar to recipes you liked')
                else:
                    reasons.append('🔗 Similar content to a recipe you liked')
        
        # Demographic popularity reasoning (POPULAR_IN)
        # Nếu có demographic_score > 0 (có POPULAR_IN và cuisine match) → hiển thị badge
        if demographic_score > 0:
            if demographic_group_count > 1:
                reasons.append('👥 Very popular among people like you')
            elif demographic_score > 0.5:  # Giảm threshold từ 0.5 xuống 0.1 để nhiều món hơn có badge
                reasons.append('👥 Popular among people like you')
            else:
                group_info = f" ({demographic_group_name})" if demographic_group_name else ""
                reasons.append(f'👥 Liked by people in your group{group_info}')
        
        # Global popularity reasoning (based on like count only)
        if global_like_count > 50:
            reasons.append('❤️ Loved by many users')
        elif global_like_count > 20:
            reasons.append('👍 Popular recipe')
        
        return reasons


# =========================================================
# 🖥️ CLI Interface
# =========================================================

def main():
    # Fix encoding for Windows console
    import io
    if sys.platform == 'win32':
        try:
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
            sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
        except (AttributeError, ValueError):
            pass  # If already wrapped or buffer not available, ignore
    
    parser = argparse.ArgumentParser(description="Simplified Graph-based Recipe Recommender")
    parser.add_argument("--uri", default="neo4j+s://3b0d8961.databases.neo4j.io")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0")
    parser.add_argument("--db", dest="database", default="neo4j")
    parser.add_argument("--user-id", dest="user_id")
    parser.add_argument("--ingredients", dest="ingredients", help="Comma-separated ingredient IDs")
    parser.add_argument("--ingredient-names", dest="ingredient_names", help="Comma-separated ingredient names")
    parser.add_argument("--limit", type=int, default=30)
    parser.add_argument("--min-match", type=float, default=0.3)
    parser.add_argument("--max-cook-time", type=int, dest="max_cook_time")
    parser.add_argument("--recipe-category", dest="recipe_category")
    parser.add_argument("--preferred-cuisines", dest="preferred_cuisines",
                       help="Comma-separated preferred cuisines")
    parser.add_argument("--max-cuisine-priority-1-ratio", type=float, default=0.6, dest="max_cuisine_priority_1_ratio",
                       help="Maximum ratio of recipes with cuisine_priority=1 (default: 0.6 = 60%%)")
    parser.add_argument("--ingredient-only-mode", action="store_true", dest="ingredient_only_mode",
                       help="Enable ingredient-only mode (only match ingredients, no user preferences)")
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
        preferred_cuisines=preferred_cuisines,
        max_cuisine_priority_1_ratio=args.max_cuisine_priority_1_ratio,
        ingredient_only_mode=args.ingredient_only_mode
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
