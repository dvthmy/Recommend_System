#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Ingredient-Only Recipe Recommender
-----------------------------------
Chỉ dựa vào ingredients để gợi ý recipes, không có bất kỳ điều kiện nào khác.
- Không filter theo cuisine, cook_time, category
- Có filter allergies (nếu có user_allergies) - chỉ dùng ingredient_id, không dùng base
- Chỉ gợi ý recipes có số ingredients <= user ingredients
- Ưu tiên perfect match (recipe có đúng số ingredients user có)
"""

from neo4j import GraphDatabase
from typing import Dict, List, Optional
from dataclasses import dataclass
import sys
from pathlib import Path

# Define IngredientMatcher and IngredientMatchContext locally
# KHÔNG import từ recommend_graph.py để tránh circular import
# recommend_graph.py import IngredientOnlyRecommender từ file này
# Nếu import ngược lại sẽ gây circular import
@dataclass
class IngredientMatchContext:
    bases: List[str]
    synonyms: List[str]
    ingredient_ids: List[str]

class IngredientMatcher:
    """Local version to avoid circular import with recommend_graph.py"""
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


class IngredientOnlyRecommender:
    """
    Recommender chỉ dựa vào ingredients, không có preferences.
    """
    
    def __init__(self, driver: GraphDatabase.driver, database: str = "neo4j"):
        self.driver = driver
        self.database = database
        self.ingredient_matcher = IngredientMatcher(driver, database)
    
    def recommend(
        self,
        ingredient_ids: Optional[List[str]] = None,
        ingredient_names: Optional[List[str]] = None,
        limit: int = 30,
        min_match_ratio: float = 0.3,
        user_allergies: Optional[List[str]] = None,
    ) -> List[Dict]:
        """
        Get recommendations based ONLY on ingredients.
        
        Args:
            ingredient_ids: List of ingredient IDs
            ingredient_names: List of ingredient names (will be mapped to IDs)
            limit: Maximum number of results
            min_match_ratio: Minimum Jaccard match ratio (default: 0.3)
            user_allergies: List of allergic ingredient IDs to filter out (optional)
                          - Filter chỉ dùng ingredient_id trực tiếp, KHÔNG dùng base
        
        Returns:
            List of recipe recommendations
        """
        with self.driver.session(database=self.database) as session:
            # Step 1: Map ingredient names to IDs
            mapped_ids: List[str] = []
            if ingredient_names:
                mapped_ids = self.ingredient_matcher.map_names_to_ids(session, ingredient_names)
            
            # Combine ingredient IDs
            all_ingredient_ids: List[str] = list(set((ingredient_ids or []) + mapped_ids))
            
            if not all_ingredient_ids:
                return []
            
            # Step 2: Build ingredient match context
            match_context = self.ingredient_matcher.build_match_context(session, all_ingredient_ids)
            
            # Step 3: Find candidate recipes (ingredient-only mode)
            candidates = self._find_candidate_recipes(
                session,
                all_ingredient_ids,
                match_context,
                min_match_ratio=min_match_ratio,
                limit=limit * 3,  # Get more candidates for sorting
                user_allergies=user_allergies or [],
            )
            
            if not candidates:
                return []
            
            # Step 4: Process and sort candidates
            user_ing_count = len(all_ingredient_ids)
            recommendations = []
            
            for candidate in candidates:
                recipe_id = candidate.get('recipe_id')
                if not recipe_id:
                    continue
                
                # Calculate match ratio (already calculated in query)
                match_ratio = candidate.get('match_ratio', 0.0)
                
                # Build recommendation
                matched_ing_count = len(candidate.get('matched_ing', []))
                total_ing_count = len(candidate.get('ingredients', [])) if candidate.get('ingredients') else (matched_ing_count + len(candidate.get('missing_ing', [])))
                
                recommendations.append({
                    'recipe_id': recipe_id,
                    'title': candidate.get('title'),
                    'cuisine': candidate.get('cuisine', []),
                    'tags': candidate.get('tags', []),
                    'recipe_category': candidate.get('recipe_category'),
                    'meal': candidate.get('meal', 'Dinner'),
                    'match_percent': round(match_ratio * 100, 1),
                    '_matched_count': matched_ing_count,
                    '_total_ing_count': total_ing_count,
                    '_is_perfect_match': matched_ing_count == total_ing_count,
                    'cook_time_min': candidate.get('cook_time_min'),
                    'prep_time_min': candidate.get('prep_time_min'),
                    'total_time_min': candidate.get('total_time_min'),
                    'servings': candidate.get('servings'),
                    'yield': candidate.get('yield'),
                    'image': candidate.get('image'),
                    'matched_ing': candidate.get('matched_ing', []),
                    'missing_ing': candidate.get('missing_ing', []),
                    'ingredients': candidate.get('ingredients', []),
                    'avg_rating': candidate.get('avg_rating', 0.0),
                    '_match_ratio': match_ratio,
                })
            
            # Step 5: Sort recommendations
            recommendations = self._sort_recommendations(recommendations, user_ing_count)
            
            # Step 6: Limit results
            recommendations = recommendations[:limit]
            
            # Log best match
            if recommendations:
                best = recommendations[0]
                best_matched = best.get('_matched_count', 0)
                best_total = best.get('_total_ing_count', 0)
                best_is_perfect = best.get('_is_perfect_match', False)
                print(f"[INGREDIENT-ONLY] Best match: {best.get('title', 'N/A')} - Matched {best_matched}/{user_ing_count} user ingredients, Recipe has {best_total} ingredients, Perfect match: {best_is_perfect}", file=sys.stderr)
            
            # Remove temporary fields
            for rec in recommendations:
                rec.pop('_match_ratio', None)
            
            return recommendations
    
    def _find_candidate_recipes(
        self,
        session,
        ingredient_ids: List[str],
        match_context: IngredientMatchContext,
        min_match_ratio: float = 0.3,
        limit: int = 100,
        user_allergies: List[str] = None,
    ) -> List[Dict]:
        """
        Find candidate recipes using ingredient matching (ingredient-only mode).
        
        Logic:
        - Không filter theo cook_time, cuisine, category
        - Filter allergies (nếu có) - chỉ dùng ingredient_id trực tiếp, KHÔNG dùng base
        - Chỉ gợi ý recipes có số ingredients <= user ingredients
        - Tính match ratio (Jaccard similarity)
        - Perfect match bonus: +0.5 nếu matched = user ingredients
        """
        if user_allergies is None:
            user_allergies = []
        q = """
        // Find recipes with matching ingredients
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE 
            (i.ingredient_id IN $input_ing
            OR (i.base IS NOT NULL AND toLower(i.base) IN $input_bases)
            OR toLower(i.canonical_name) IN $input_synonyms
            OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) IN $input_synonyms))
        
        WITH r, collect(DISTINCT i.ingredient_id) AS matched_ing
        WHERE size(matched_ing) >= CASE WHEN size($input_ing) >= 4 THEN 2 ELSE 1 END
        
        // Get all recipe ingredients
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, collect(DISTINCT ai.ingredient_id) AS all_ing
        
        // Filter allergens early (HARD CONSTRAINT - safety first)
        // QUAN TRỌNG: Chỉ dùng ingredient_id trực tiếp, KHÔNG dùng base
        WITH r, matched_ing, all_ing
        WHERE size($user_allergies) = 0 OR NOT any(ing IN all_ing WHERE ing IN $user_allergies)
        
        // INGREDIENT-ONLY MODE: Chỉ gợi ý recipes có số ingredients <= user ingredients
        WITH r, matched_ing, all_ing, size(all_ing) AS ing_count
        WHERE ing_count <= size($input_ing)
        
        WITH r, matched_ing, all_ing, ing_count
        
        // Calculate base Jaccard match ratio
        WITH r, matched_ing, all_ing, ing_count,
             CASE 
                 WHEN ing_count = 0 AND size($input_ing) = 0 THEN 0.0
                 WHEN ing_count = 0 OR size($input_ing) = 0 THEN 0.0
                 ELSE toFloat(size(matched_ing)) / 
                      toFloat(ing_count + size($input_ing) - size(matched_ing))
             END AS base_match_ratio
        
        // PERFECT MATCH BONUS: Nếu user có đủ ingredients recipe cần (matched = user ingredients)
        WITH r, matched_ing, all_ing, ing_count, base_match_ratio,
             CASE 
                 WHEN size(matched_ing) = size($input_ing) AND size($input_ing) > 0 THEN 0.5  // Perfect match bonus
                 ELSE 0.0
             END AS perfect_match_bonus
        
        // Calculate weighted match ratio: base + perfect match bonus (capped at 1.0)
        WITH r, matched_ing, all_ing, ing_count, base_match_ratio, perfect_match_bonus,
             CASE 
                 WHEN base_match_ratio + perfect_match_bonus > 1.0 THEN 1.0
                 ELSE base_match_ratio + perfect_match_bonus
             END AS match_ratio
        
        WHERE match_ratio >= $min_match
        
        // Collect recipe details
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ing:Ingredient)
        WITH r, matched_ing, all_ing, match_ratio,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing,
             collect({
                 ingredient_id: ing.ingredient_id,
                 ingredient_name: coalesce(ing.name, ing.canonical_name),
                 base: coalesce(ing.base, ing.canonical_name),
                 category: ing.category
             }) AS ingredients,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             coalesce(toInteger(r.rating_count), 0) AS rating_count
        
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
            rating_count
        LIMIT $lim
        """
        
        result = session.run(
            q,
            input_ing=ingredient_ids,
            input_bases=match_context.bases,
            input_synonyms=match_context.synonyms,
            min_match=min_match_ratio,
            lim=limit,
            user_allergies=user_allergies or []
        )
        
        return [dict(row) for row in result]
    
    def _sort_recommendations(
        self,
        recommendations: List[Dict],
        user_ing_count: int
    ) -> List[Dict]:
        """
        Sort recommendations for ingredient-only mode.
        
        Logic:
        1. Perfect match: recipe có đúng số ingredients user có VÀ match đúng tất cả
        2. Sau đó: recipe có ít hơn ingredients VÀ match đúng tất cả
        3. Nếu không có recipe nào match đúng tất cả → quay về tính theo số lượng matched
        """
        # Kiểm tra xem có recipe nào match đúng tất cả ingredients của recipe không
        has_perfect_match_recipes = False
        for rec in recommendations:
            total_ing = rec.get('_total_ing_count', 0)
            matched_count = rec.get('_matched_count', 0)
            if matched_count == total_ing:  # Match đúng tất cả ingredients của recipe
                has_perfect_match_recipes = True
                break
        
        if has_perfect_match_recipes:
            # Có recipe match đúng tất cả → ưu tiên theo perfect match logic
            def get_sort_key(x):
                total_ing = x.get('_total_ing_count', 0)
                matched_count = x.get('_matched_count', 0)
                
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
                    -x.get('_matched_count', 0),
                    # Match ratio (Jaccard similarity)
                    -x.get('_match_ratio', 0.0),
                    # Rating
                    -x.get('avg_rating', 0.0)
                )
            )
        
        return recommendations

