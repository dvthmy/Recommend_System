#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pure Knowledge-Based Recipe Recommendation System 🧠
----------------------------------------------------
This recommender uses ONLY knowledge-based reasoning over the graph structure.
NO collaborative filtering, NO machine learning, NO scoring algorithms.

Knowledge Sources:
1. User Profile Knowledge (allergies, preferences, demographics)
2. Recipe Knowledge (ingredients, cuisine, category, nutrition)
3. Group Knowledge (demographic patterns)
4. Ingredient Knowledge (categories, substitutions)
5. Cuisine Knowledge (hierarchies, cultural patterns)

Reasoning Rules (IF-THEN logic):
- IF user has allergy THEN exclude recipes with allergen
- IF user prefers cuisine X THEN prioritize cuisine X recipes
- IF user is in demographic group Y THEN consider group Y preferences
- IF recipe matches user's ingredients THEN it's relevant
- IF recipe matches user's time constraints THEN it's practical
- IF recipe is popular in user's group THEN it's socially validated
"""

from neo4j import GraphDatabase
import argparse
import json
import sys
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass
from enum import Enum


# =========================================================
# 📊 Knowledge Structures
# =========================================================

class CuisineGroup(Enum):
    """Cuisine hierarchy knowledge"""
    ASIAN = ["vietnamese", "chinese", "japanese", "korean", "thai", "asian"]
    EUROPEAN = ["italian", "french", "british", "german", "spanish", "european"]
    LATIN = ["mexican", "caribbean", "brazilian", "argentinian"]
    MIDDLE_EASTERN = ["turkish", "lebanese", "persian", "moroccan"]
    AMERICAN = ["american", "southern", "cajun"]


class IngredientCategory(Enum):
    """Ingredient importance hierarchy"""
    PROTEIN = ["meat", "plant_protein", "seafood"]
    CARBOHYDRATE = ["grain", "pasta", "bread"]
    VEGETABLE = ["vegetable", "fruit"]
    DAIRY = ["dairy", "cheese"]
    SEASONING = ["herb", "spice", "seasoning"]
    CONDIMENT = ["sauce", "condiment"]


class MealType(Enum):
    """Meal category knowledge"""
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"


@dataclass
class UserKnowledge:
    """Knowledge about a user"""
    user_id: str
    gender: str
    age_group: str
    allergies: List[str]
    favorite_cuisines: List[str]
    max_cook_time: Optional[int]
    meal_preferences: List[str]
    dietary_restrictions: List[str]
    
    # Derived knowledge
    demographic_group: Optional[str] = None
    cuisine_preferences: List[str] = None
    
    def __post_init__(self):
        self.demographic_group = f"{self.gender}-{self.age_group}" if self.gender and self.age_group else None


@dataclass
class RecipeKnowledge:
    """Knowledge about a recipe"""
    recipe_id: str
    title: str
    cuisines: List[str]
    category: str
    ingredients: List[str]
    ingredient_categories: Dict[str, int]  # category -> count
    cook_time: Optional[int]
    prep_time: Optional[int]
    difficulty: str
    nutrition: Dict[str, float]
    tags: List[str]
    
    # Derived knowledge
    is_quick: bool = False
    is_healthy: bool = False
    is_vegetarian: bool = False
    complexity_level: str = "medium"
    
    def __post_init__(self):
        self.is_quick = self.cook_time and self.cook_time <= 30
        self.is_healthy = self._check_healthy()
        self.is_vegetarian = self._check_vegetarian()
        self.complexity_level = self._assess_complexity()
    
    def _check_healthy(self) -> bool:
        """Knowledge rule: healthy if low calories and high protein"""
        if not self.nutrition:
            return False
        calories = self.nutrition.get('calories', 0)
        protein = self.nutrition.get('protein', 0)
        return calories < 500 and protein > 20
    
    def _check_vegetarian(self) -> bool:
        """Knowledge rule: vegetarian if no meat/seafood"""
        meat_categories = {'meat', 'seafood', 'poultry'}
        return not any(cat in meat_categories for cat in self.ingredient_categories.keys())
    
    def _assess_complexity(self) -> str:
        """Knowledge rule: complexity based on ingredient count and cook time"""
        ing_count = sum(self.ingredient_categories.values())
        cook_time = self.cook_time or 0
        
        if ing_count <= 5 and cook_time <= 20:
            return "easy"
        elif ing_count <= 10 and cook_time <= 45:
            return "medium"
        else:
            return "hard"


@dataclass
class GroupKnowledge:
    """Knowledge about a demographic group"""
    group_id: str
    gender: str
    age_group: str
    size: int
    popular_cuisines: List[Tuple[str, int]]  # (cuisine, frequency)
    popular_categories: List[Tuple[str, int]]  # (category, frequency)
    popular_recipes: List[Tuple[str, int]]  # (recipe_id, score)
    avg_cook_time_preference: Optional[int]
    dietary_patterns: Dict[str, float]  # pattern -> percentage


@dataclass
class RecommendationReason:
    """Explanation for why a recipe was recommended"""
    rule_type: str
    description: str
    confidence: float  # 0.0 to 1.0
    
    def __str__(self):
        emoji_map = {
            "ingredient_match": "✅",
            "cuisine_match": "🍜",
            "group_popular": "👥",
            "time_match": "⏱️",
            "dietary_match": "🥗",
            "category_match": "🍽️",
            "health_match": "💚",
            "allergen_safe": "🛡️"
        }
        emoji = emoji_map.get(self.rule_type, "•")
        return f"{emoji} {self.description}"


# =========================================================
# 🧠 Knowledge-Based Recommender
# =========================================================

class KnowledgeBasedRecommender:
    """
    Pure knowledge-based recommender using graph reasoning.
    NO machine learning, NO collaborative filtering.
    """
    
    def __init__(self, uri="bolt://localhost:7687", username="neo4j",
                 password="Admin123!", database="test"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        
        # Knowledge bases (loaded from graph)
        self.cuisine_hierarchy = self._build_cuisine_hierarchy()
        self.ingredient_categories = self._build_ingredient_categories()
    
    def close(self):
        self.driver.close()
    
    # =========================================================
    # 📚 Knowledge Base Construction
    # =========================================================
    
    def _build_cuisine_hierarchy(self) -> Dict[str, List[str]]:
        """Build cuisine hierarchy knowledge from enum"""
        return {
            group.name: group.value for group in CuisineGroup
        }
    
    def _build_ingredient_categories(self) -> Dict[str, List[str]]:
        """Build ingredient category knowledge from enum"""
        return {
            cat.name: cat.value for cat in IngredientCategory
        }
    
    # =========================================================
    # 🔍 Knowledge Extraction from Graph
    # =========================================================
    
    def extract_user_knowledge(self, session, user_id: str) -> UserKnowledge:
        """Extract all knowledge about a user from the graph"""
        q = """
        MATCH (u:User {user_id: $uid})
        OPTIONAL MATCH (u)-[:ALLERGIC_TO]->(a:Ingredient)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        OPTIONAL MATCH (u)-[:DISLIKES]->(d:Ingredient)
        RETURN 
            u.user_id AS user_id,
            coalesce(u.gender, 'unknown') AS gender,
            coalesce(u.age_group, 'unknown') AS age_group,
            collect(DISTINCT a.ingredient_id) AS allergies,
            collect(DISTINCT c.name) AS favorite_cuisines,
            u.max_cook_time AS max_cook_time,
            coalesce(u.meal_preferences, []) AS meal_preferences,
            collect(DISTINCT d.ingredient_id) AS dislikes
        """
        
        result = session.run(q, uid=user_id).single()
        
        if not result:
            # Return default knowledge for unknown user
            return UserKnowledge(
                user_id=user_id,
                gender="unknown",
                age_group="unknown",
                allergies=[],
                favorite_cuisines=[],
                max_cook_time=None,
                meal_preferences=[],
                dietary_restrictions=[]
            )
        
        return UserKnowledge(
            user_id=result['user_id'],
            gender=result['gender'],
            age_group=result['age_group'],
            allergies=result['allergies'] or [],
            favorite_cuisines=[c.lower() for c in (result['favorite_cuisines'] or [])],
            max_cook_time=result['max_cook_time'],
            meal_preferences=result['meal_preferences'] or [],
            dietary_restrictions=result['dislikes'] or []
        )
    
    def extract_group_knowledge(self, session, gender: str, age_group: str) -> Optional[GroupKnowledge]:
        """
        Extract knowledge about a demographic group.
        
        Updated: Supports users with only gender OR only age_group (uses 'unknown' for missing).
        """
        # Use 'unknown' as placeholder if gender or age_group is missing
        gender_value = gender if gender and gender != "unknown" else 'unknown'
        age_group_value = age_group if age_group and age_group != "unknown" else 'unknown'
        
        # If both are unknown, return None
        if gender_value == 'unknown' and age_group_value == 'unknown':
            return None
        
        q = """
        MATCH (g:Group {gender: $gender, age_group: $age_group})
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u:User)
        WITH g, count(DISTINCT u) AS group_size
        
        // Popular cuisines
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u1:User)-[:INTERACTED_WITH]->(r1:Recipe)
        WHERE r1.cuisine IS NOT NULL
        UNWIND r1.cuisine AS cuisine_name
        WITH g, group_size, toLower(cuisine_name) AS cuisine, count(*) AS freq
        ORDER BY freq DESC
        WITH g, group_size, collect([cuisine, freq])[..5] AS top_cuisines
        
        // Popular categories
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u2:User)-[:INTERACTED_WITH]->(r2:Recipe)
        WHERE r2.recipe_category IS NOT NULL
        WITH g, group_size, top_cuisines, r2.recipe_category AS category, count(*) AS freq
        ORDER BY freq DESC
        WITH g, group_size, top_cuisines, collect([category, freq])[..3] AS top_categories
        
        // Popular recipes
        OPTIONAL MATCH (g)-[pop:POPULAR_IN]->(r3:Recipe)
        WITH g, group_size, top_cuisines, top_categories, r3.recipe_id AS recipe_id, pop.score AS score
        ORDER BY score DESC
        WITH g, group_size, top_cuisines, top_categories, collect([recipe_id, score])[..10] AS top_recipes
        
        // Average cook time preference
        OPTIONAL MATCH (g)<-[:BELONGS_TO]-(u3:User)-[:INTERACTED_WITH]->(r4:Recipe)
        WHERE r4.cook_time_min IS NOT NULL
        WITH g, group_size, top_cuisines, top_categories, top_recipes, avg(r4.cook_time_min) AS avg_cook_time
        
        RETURN 
            g.gender AS gender,
            g.age_group AS age_group,
            group_size,
            top_cuisines,
            top_categories,
            top_recipes,
            toInteger(avg_cook_time) AS avg_cook_time
        """
        
        result = session.run(q, gender=gender_value, age_group=age_group_value).single()
        
        if not result or result['group_size'] == 0:
            return None
        
        return GroupKnowledge(
            group_id=f"{gender}-{age_group}",
            gender=result['gender'],
            age_group=result['age_group'],
            size=result['group_size'],
            popular_cuisines=[(c[0], c[1]) for c in (result['top_cuisines'] or [])],
            popular_categories=[(c[0], c[1]) for c in (result['top_categories'] or [])],
            popular_recipes=[(r[0], r[1]) for r in (result['top_recipes'] or [])],
            avg_cook_time_preference=result['avg_cook_time'],
            dietary_patterns={}
        )
    
    def extract_recipe_knowledge(self, session, recipe_id: str) -> Optional[RecipeKnowledge]:
        """Extract all knowledge about a recipe"""
        q = """
        MATCH (r:Recipe {recipe_id: $rid})
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH r, collect(DISTINCT i.ingredient_id) AS ingredients,
             collect(DISTINCT i.category) AS categories
        RETURN 
            r.recipe_id AS recipe_id,
            r.title AS title,
            coalesce(r.cuisine, []) AS cuisines,
            r.recipe_category AS category,
            ingredients,
            categories,
            r.cook_time_min AS cook_time,
            r.prep_time_min AS prep_time,
            coalesce(r.tags, []) AS tags,
            r.nutrition_calories AS calories,
            r.nutrition_protein AS protein,
            r.nutrition_fat AS fat,
            r.nutrition_carbohydrate AS carbs
        """
        
        result = session.run(q, rid=recipe_id).single()
        
        if not result:
            return None
        
        # Count ingredients by category
        ingredient_categories = {}
        for cat in result['categories']:
            if cat:
                ingredient_categories[cat] = ingredient_categories.get(cat, 0) + 1
        
        nutrition = {
            'calories': result['calories'] or 0,
            'protein': result['protein'] or 0,
            'fat': result['fat'] or 0,
            'carbs': result['carbs'] or 0
        }
        
        return RecipeKnowledge(
            recipe_id=result['recipe_id'],
            title=result['title'],
            cuisines=[c.lower() for c in (result['cuisines'] or [])],
            category=result['category'] or "dinner",
            ingredients=result['ingredients'] or [],
            ingredient_categories=ingredient_categories,
            cook_time=result['cook_time'],
            prep_time=result['prep_time'],
            difficulty="medium",  # Could be derived from complexity
            nutrition=nutrition,
            tags=result['tags'] or []
        )
    
    # =========================================================
    # 🎯 Knowledge-Based Reasoning Rules
    # =========================================================
    
    def rule_allergen_safety(self, user: UserKnowledge, recipe: RecipeKnowledge) -> Tuple[bool, Optional[RecommendationReason]]:
        """
        RULE: IF recipe contains user's allergen THEN exclude
        ELSE IF recipe is allergen-free THEN add safety reason
        """
        if not user.allergies:
            return True, None
        
        # Check if recipe contains any allergens
        recipe_allergens = set(recipe.ingredients) & set(user.allergies)
        
        if recipe_allergens:
            # EXCLUDE: Contains allergen
            return False, None
        else:
            # INCLUDE: Safe from allergens
            return True, RecommendationReason(
                rule_type="allergen_safe",
                description="Safe for your dietary restrictions",
                confidence=1.0
            )
    
    def rule_cuisine_preference(self, user: UserKnowledge, recipe: RecipeKnowledge) -> Optional[RecommendationReason]:
        """
        RULE: IF recipe cuisine matches user's favorite cuisine THEN prioritize
        """
        if not user.favorite_cuisines:
            return None
        
        # Check exact match
        recipe_cuisines_set = set(recipe.cuisines)
        user_cuisines_set = set(user.favorite_cuisines)
        
        if recipe_cuisines_set & user_cuisines_set:
            return RecommendationReason(
                rule_type="cuisine_match",
                description=f"Matches your favorite cuisine",
                confidence=1.0
            )
        
        # Check cuisine group match
        for user_cuisine in user.favorite_cuisines:
            for group_name, group_cuisines in self.cuisine_hierarchy.items():
                if user_cuisine in [c.lower() for c in group_cuisines]:
                    # User likes this cuisine group
                    if any(rc in [c.lower() for c in group_cuisines] for rc in recipe.cuisines):
                        return RecommendationReason(
                            rule_type="cuisine_match",
                            description=f"Similar to your preferred {group_name.lower()} cuisine",
                            confidence=0.7
                        )
        
        return None
    
    def rule_time_constraint(self, user: UserKnowledge, recipe: RecipeKnowledge) -> Tuple[bool, Optional[RecommendationReason]]:
        """
        RULE: IF recipe cook_time > user's max_cook_time THEN exclude
        ELSE IF recipe is quick THEN add convenience reason
        """
        if not user.max_cook_time:
            # No time constraint
            if recipe.is_quick:
                return True, RecommendationReason(
                    rule_type="time_match",
                    description="Quick and easy to make",
                    confidence=0.8
                )
            return True, None
        
        if recipe.cook_time and recipe.cook_time > user.max_cook_time:
            # EXCLUDE: Too time-consuming
            return False, None
        else:
            # INCLUDE: Fits time constraint
            return True, RecommendationReason(
                rule_type="time_match",
                description=f"Fits your time budget ({recipe.cook_time or 0} min)",
                confidence=1.0
            )
    
    def rule_ingredient_match(self, available_ingredients: List[str], recipe: RecipeKnowledge) -> Tuple[float, Optional[RecommendationReason]]:
        """
        RULE: Calculate ingredient match ratio (Jaccard similarity)
        IF match_ratio > threshold THEN include with explanation
        """
        if not available_ingredients:
            return 0.0, None
        
        available_set = set(available_ingredients)
        recipe_set = set(recipe.ingredients)
        
        intersection = available_set & recipe_set
        union = available_set | recipe_set
        
        if not union:
            return 0.0, None
        
        match_ratio = len(intersection) / len(union)
        
        if match_ratio >= 0.7:
            return match_ratio, RecommendationReason(
                rule_type="ingredient_match",
                description=f"Uses most of your ingredients ({len(intersection)}/{len(recipe_set)})",
                confidence=match_ratio
            )
        elif match_ratio >= 0.4:
            return match_ratio, RecommendationReason(
                rule_type="ingredient_match",
                description=f"Partially matches your ingredients ({len(intersection)}/{len(recipe_set)})",
                confidence=match_ratio
            )
        elif match_ratio >= 0.2:
            return match_ratio, RecommendationReason(
                rule_type="ingredient_match",
                description=f"Uses some of your ingredients ({len(intersection)}/{len(recipe_set)})",
                confidence=match_ratio
            )
        else:
            return match_ratio, None
    
    def rule_group_popularity(self, group: Optional[GroupKnowledge], recipe: RecipeKnowledge) -> Optional[RecommendationReason]:
        """
        RULE: IF recipe is popular in user's demographic group THEN prioritize
        """
        if not group:
            return None
        
        # Check if recipe is in group's popular recipes
        popular_recipe_ids = [r[0] for r in group.popular_recipes]
        
        if recipe.recipe_id in popular_recipe_ids:
            # Find the score
            score = next((r[1] for r in group.popular_recipes if r[0] == recipe.recipe_id), 0)
            
            if score > 10:
                return RecommendationReason(
                    rule_type="group_popular",
                    description=f"Very popular among {group.gender} {group.age_group}",
                    confidence=0.9
                )
            elif score > 5:
                return RecommendationReason(
                    rule_type="group_popular",
                    description=f"Popular among people like you",
                    confidence=0.7
                )
            else:
                return RecommendationReason(
                    rule_type="group_popular",
                    description=f"Tried by people like you",
                    confidence=0.5
                )
        
        # Check if recipe cuisine is popular in group
        group_cuisines = [c[0] for c in group.popular_cuisines]
        if any(rc in group_cuisines for rc in recipe.cuisines):
            return RecommendationReason(
                rule_type="group_popular",
                description=f"Cuisine preferred by your demographic",
                confidence=0.6
            )
        
        return None
    
    def rule_category_match(self, user: UserKnowledge, recipe: RecipeKnowledge) -> Optional[RecommendationReason]:
        """
        RULE: IF recipe category matches user's meal preferences THEN prioritize
        """
        if not user.meal_preferences:
            return None
        
        recipe_category_lower = recipe.category.lower()
        
        for pref in user.meal_preferences:
            pref_lower = pref.lower()
            if pref_lower in recipe_category_lower or recipe_category_lower in pref_lower:
                return RecommendationReason(
                    rule_type="category_match",
                    description=f"Matches your meal preference",
                    confidence=0.8
                )
        
        return None
    
    def rule_health_match(self, user: UserKnowledge, recipe: RecipeKnowledge) -> Optional[RecommendationReason]:
        """
        RULE: IF user prefers healthy AND recipe is healthy THEN prioritize
        """
        # Check if user has health-related preferences
        health_keywords = ['healthy', 'low-calorie', 'diet', 'fitness']
        user_wants_healthy = any(kw in ' '.join(user.meal_preferences).lower() for kw in health_keywords)
        
        if user_wants_healthy and recipe.is_healthy:
            return RecommendationReason(
                rule_type="health_match",
                description="Healthy and nutritious option",
                confidence=0.8
            )
        
        if recipe.is_healthy:
            return RecommendationReason(
                rule_type="health_match",
                description="Balanced nutrition",
                confidence=0.5
            )
        
        return None
    
    # =========================================================
    # 🎯 Main Recommendation Logic
    # =========================================================
    
    def recommend(self, 
                  user_id: str,
                  available_ingredients: Optional[List[str]] = None,
                  limit: int = 20,
                  min_match_ratio: float = 0.2) -> List[Dict]:
        """
        Generate recommendations using pure knowledge-based reasoning.
        
        Args:
            user_id: User ID
            available_ingredients: List of ingredient IDs user has
            limit: Maximum number of recommendations
            min_match_ratio: Minimum ingredient match ratio (0.0 to 1.0)
        
        Returns:
            List of recommended recipes with reasoning
        """
        with self.driver.session(database=self.database) as session:
            # Step 1: Extract user knowledge
            print(f"📚 Extracting knowledge for user {user_id}...", file=sys.stderr)
            user = self.extract_user_knowledge(session, user_id)
            
            # Step 2: Extract group knowledge
            group = self.extract_group_knowledge(session, user.gender, user.age_group)
            if group:
                print(f"👥 Found demographic group: {group.group_id} ({group.size} users)", file=sys.stderr)
            
            # Step 3: Find candidate recipes
            print(f"🔍 Finding candidate recipes...", file=sys.stderr)
            candidate_recipes = self._find_candidate_recipes(
                session, 
                available_ingredients or [],
                user,
                limit * 3  # Get more candidates for filtering
            )
            
            print(f"📋 Found {len(candidate_recipes)} candidate recipes", file=sys.stderr)
            
            # Step 4: Apply knowledge-based reasoning to each candidate
            recommendations = []
            
            for recipe_id in candidate_recipes:
                # Extract recipe knowledge
                recipe = self.extract_recipe_knowledge(session, recipe_id)
                if not recipe:
                    continue
                
                # Apply reasoning rules
                reasons = []
                should_include = True
                match_score = 0.0
                
                # Rule 1: Allergen safety (HARD CONSTRAINT)
                is_safe, safety_reason = self.rule_allergen_safety(user, recipe)
                if not is_safe:
                    continue  # EXCLUDE
                if safety_reason:
                    reasons.append(safety_reason)
                
                # Rule 2: Time constraint (HARD CONSTRAINT)
                fits_time, time_reason = self.rule_time_constraint(user, recipe)
                if not fits_time:
                    continue  # EXCLUDE
                if time_reason:
                    reasons.append(time_reason)
                
                # Rule 3: Ingredient match (SCORING)
                if available_ingredients:
                    match_score, match_reason = self.rule_ingredient_match(available_ingredients, recipe)
                    if match_score < min_match_ratio:
                        continue  # EXCLUDE: Too few matching ingredients
                    if match_reason:
                        reasons.append(match_reason)
                
                # Rule 4: Cuisine preference (SOFT CONSTRAINT)
                cuisine_reason = self.rule_cuisine_preference(user, recipe)
                if cuisine_reason:
                    reasons.append(cuisine_reason)
                    match_score += 0.2  # Boost score
                
                # Rule 5: Group popularity (SOFT CONSTRAINT)
                group_reason = self.rule_group_popularity(group, recipe)
                if group_reason:
                    reasons.append(group_reason)
                    match_score += 0.15  # Boost score
                
                # Rule 6: Category match (SOFT CONSTRAINT)
                category_reason = self.rule_category_match(user, recipe)
                if category_reason:
                    reasons.append(category_reason)
                    match_score += 0.1  # Boost score
                
                # Rule 7: Health match (SOFT CONSTRAINT)
                health_reason = self.rule_health_match(user, recipe)
                if health_reason:
                    reasons.append(health_reason)
                    match_score += 0.05  # Small boost
                
                # Add to recommendations
                recommendations.append({
                    'recipe_id': recipe.recipe_id,
                    'title': recipe.title,
                    'cuisine': recipe.cuisines,
                    'category': recipe.category,
                    'cook_time_min': recipe.cook_time,
                    'match_score': round(match_score, 2),
                    'match_percent': round(match_score * 100, 1),
                    'reasoning': [str(r) for r in reasons],
                    'is_quick': recipe.is_quick,
                    'is_healthy': recipe.is_healthy,
                    'complexity': recipe.complexity_level
                })
            
            # Step 5: Sort by match score (knowledge-based ranking)
            recommendations.sort(key=lambda x: x['match_score'], reverse=True)
            
            # Step 6: Return top N
            final_recommendations = recommendations[:limit]
            
            print(f"✅ Generated {len(final_recommendations)} recommendations", file=sys.stderr)
            print(f"📊 Average match score: {sum(r['match_score'] for r in final_recommendations) / len(final_recommendations) if final_recommendations else 0:.2f}", file=sys.stderr)
            
            return final_recommendations
    
    def _find_candidate_recipes(self, session, available_ingredients: List[str], 
                                user: UserKnowledge, limit: int) -> List[str]:
        """
        Find candidate recipes using graph traversal.
        This is a knowledge-based query, not a scoring query.
        """
        if available_ingredients:
            # Find recipes that share ingredients with user
            q = """
            MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
            WHERE i.ingredient_id IN $ingredients
            WITH r, count(DISTINCT i) AS shared_count
            WHERE shared_count >= 1
            RETURN DISTINCT r.recipe_id AS recipe_id
            ORDER BY shared_count DESC
            LIMIT $limit
            """
            result = session.run(q, ingredients=available_ingredients, limit=limit)
        else:
            # Find popular recipes (knowledge: popularity indicates quality)
            q = """
            MATCH (r:Recipe)
            WHERE r.rating_value IS NOT NULL
            RETURN r.recipe_id AS recipe_id
            ORDER BY r.rating_value DESC, r.rating_count DESC
            LIMIT $limit
            """
            result = session.run(q, limit=limit)
        
        return [row['recipe_id'] for row in result]


# =========================================================
# 🖥️ CLI Interface
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="Pure Knowledge-Based Recipe Recommender")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--db", dest="database", default="test")
    parser.add_argument("--user-id", dest="user_id", required=True, help="User ID")
    parser.add_argument("--ingredients", dest="ingredients", help="Comma-separated ingredient IDs")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--min-match", type=float, default=0.2, help="Minimum ingredient match ratio (0.0-1.0)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    ingredient_ids = [x.strip() for x in args.ingredients.split(",")] if args.ingredients else None
    
    rec = KnowledgeBasedRecommender(args.uri, args.user, args.password, args.database)
    
    try:
        results = rec.recommend(
            user_id=args.user_id,
            available_ingredients=ingredient_ids,
            limit=args.limit,
            min_match_ratio=args.min_match
        )
        
        if args.json:
            print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        else:
            print("\n" + "="*80)
            print(f"🧠 KNOWLEDGE-BASED RECOMMENDATIONS FOR USER: {args.user_id}")
            print("="*80 + "\n")
            
            for i, r in enumerate(results, 1):
                print(f"#{i}. {r['title']}")
                print(f"   📊 Match Score: {r['match_score']:.2f} ({r['match_percent']}%)")
                print(f"   🍜 Cuisine: {', '.join(r['cuisine'])}")
                print(f"   🍽️  Category: {r['category']}")
                print(f"   ⏱️  Cook Time: {r['cook_time_min'] or 'N/A'} min")
                print(f"   🎯 Complexity: {r['complexity']}")
                
                if r['reasoning']:
                    print(f"   💡 Why recommended:")
                    for reason in r['reasoning']:
                        print(f"      {reason}")
                
                print()
            
            print("="*80)
            print(f"✅ Total recommendations: {len(results)}")
            print("="*80)
    
    finally:
        rec.close()


if __name__ == "__main__":
    main()

