#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hybrid ML + CF + Knowledge-Based Recommender System 🤖🧠
--------------------------------------------------------
This system combines THREE approaches:
1. Machine Learning (Content-Based Filtering with TF-IDF)
2. Collaborative Filtering (User-User & Item-Item similarity)
3. Knowledge-Based Reasoning (IF-THEN rules from graph)

The final recommendation is a weighted combination of all three.
"""

from neo4j import GraphDatabase
import argparse
import json
import sys
import math
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from collections import defaultdict


# =========================================================
# 📊 Data Structures
# =========================================================

@dataclass
class MLFeatures:
    """Machine Learning features for a recipe"""
    recipe_id: str
    tfidf_vector: Dict[str, float]  # term -> weight
    ingredient_vector: List[int]  # binary vector
    cuisine_vector: List[int]  # one-hot encoding
    nutrition_vector: List[float]  # normalized nutrition


@dataclass
class CFScores:
    """Collaborative Filtering scores"""
    user_based_score: float  # From similar users
    item_based_score: float  # From similar items
    popularity_score: float  # Global popularity


@dataclass
class KnowledgeScore:
    """Knowledge-based reasoning score"""
    rule_score: float  # From IF-THEN rules
    constraints_met: bool  # Hard constraints
    reasoning: List[str]  # Explanations


@dataclass
class HybridScore:
    """Combined hybrid score"""
    ml_score: float
    cf_score: float
    kb_score: float
    final_score: float
    components: Dict[str, float]
    reasoning: List[str]


# =========================================================
# 🤖 Machine Learning Component
# =========================================================

class MLRecommender:
    """
    Machine Learning based recommender using:
    - TF-IDF for text similarity
    - Content-based filtering
    - Feature engineering
    """
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
        self.idf_cache = {}
    
    def compute_tfidf_similarity(self, session, user_id: str, recipe_id: str) -> float:
        """
        Compute TF-IDF cosine similarity between user profile and recipe.
        This is MACHINE LEARNING approach using text vectorization.
        """
        # Get user's TF-IDF profile (built from interaction history)
        q_user = """
        MATCH (u:User {user_id: $uid})
        WHERE u.user_terms IS NOT NULL AND u.user_weights IS NOT NULL
        RETURN u.user_terms AS terms, u.user_weights AS weights
        """
        user_result = session.run(q_user, uid=user_id).single()
        
        if not user_result or not user_result['terms']:
            return 0.0
        
        user_vector = dict(zip(user_result['terms'], user_result['weights']))
        
        # Get recipe's TF-IDF profile
        q_recipe = """
        MATCH (r:Recipe {recipe_id: $rid})
        WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
        RETURN r.text_terms AS terms, r.text_weights AS weights
        """
        recipe_result = session.run(q_recipe, rid=recipe_id).single()
        
        if not recipe_result or not recipe_result['terms']:
            return 0.0
        
        recipe_vector = dict(zip(recipe_result['terms'], recipe_result['weights']))
        
        # Compute cosine similarity (ML approach)
        return self._cosine_similarity(user_vector, recipe_vector)
    
    def _cosine_similarity(self, vec1: Dict[str, float], vec2: Dict[str, float]) -> float:
        """Compute cosine similarity between two sparse vectors"""
        # Find common terms
        common_terms = set(vec1.keys()) & set(vec2.keys())
        
        if not common_terms:
            return 0.0
        
        # Dot product
        dot_product = sum(vec1[term] * vec2[term] for term in common_terms)
        
        # Magnitudes
        mag1 = math.sqrt(sum(v * v for v in vec1.values()))
        mag2 = math.sqrt(sum(v * v for v in vec2.values()))
        
        if mag1 == 0 or mag2 == 0:
            return 0.0
        
        return dot_product / (mag1 * mag2)
    
    def compute_content_similarity(self, session, user_id: str, recipe_id: str) -> float:
        """
        Compute content-based similarity using ingredient and cuisine features.
        This is MACHINE LEARNING approach using feature vectors.
        """
        # Get user's preferred ingredients (from interaction history)
        q_user_ingredients = """
        MATCH (u:User {user_id: $uid})-[:INTERACTED_WITH]->(r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH i.ingredient_id AS ing_id, count(*) AS freq
        ORDER BY freq DESC
        LIMIT 20
        RETURN collect(ing_id) AS preferred_ingredients
        """
        user_result = session.run(q_user_ingredients, uid=user_id).single()
        user_ingredients = set(user_result['preferred_ingredients'] if user_result else [])
        
        # Get recipe's ingredients
        q_recipe_ingredients = """
        MATCH (r:Recipe {recipe_id: $rid})-[:HAS_INGREDIENT]->(i:Ingredient)
        RETURN collect(i.ingredient_id) AS ingredients
        """
        recipe_result = session.run(q_recipe_ingredients, rid=recipe_id).single()
        recipe_ingredients = set(recipe_result['ingredients'] if recipe_result else [])
        
        if not user_ingredients or not recipe_ingredients:
            return 0.0
        
        # Jaccard similarity (ML feature)
        intersection = len(user_ingredients & recipe_ingredients)
        union = len(user_ingredients | recipe_ingredients)
        
        return intersection / union if union > 0 else 0.0
    
    def compute_ml_score(self, session, user_id: str, recipe_id: str) -> float:
        """
        Compute overall ML score combining multiple ML techniques.
        """
        # TF-IDF similarity (text mining)
        tfidf_sim = self.compute_tfidf_similarity(session, user_id, recipe_id)
        
        # Content similarity (feature engineering)
        content_sim = self.compute_content_similarity(session, user_id, recipe_id)
        
        # Weighted combination (ensemble learning)
        ml_score = (tfidf_sim * 0.6 + content_sim * 0.4)
        
        return ml_score


# =========================================================
# 👥 Collaborative Filtering Component
# =========================================================

class CFRecommender:
    """
    Collaborative Filtering based recommender using:
    - User-User similarity (User-based CF)
    - Item-Item similarity (Item-based CF)
    - Matrix factorization concepts
    """
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def compute_user_based_cf(self, session, user_id: str, recipe_id: str) -> float:
        """
        User-Based Collaborative Filtering:
        "Users who are similar to you also liked this recipe"
        """
        q = """
        MATCH (u:User {user_id: $uid})-[sim:SIMILAR_USER]->(u2:User)-[iv:INTERACTED_WITH]->(r:Recipe {recipe_id: $rid})
        WHERE iv.liked = true OR iv.rating >= 4
        WITH sim.score AS similarity, iv.rating AS rating
        RETURN 
            avg(similarity) AS avg_similarity,
            count(*) AS similar_user_count,
            avg(coalesce(rating, 4.0)) AS avg_rating
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id).single()
        
        if not result or result['similar_user_count'] == 0:
            return 0.0
        
        # CF score: weighted by similarity and rating
        avg_sim = result['avg_similarity'] or 0.0
        avg_rating = result['avg_rating'] or 0.0
        count = result['similar_user_count']
        
        # Normalize rating to 0-1
        normalized_rating = (avg_rating - 1) / 4.0  # Assuming 1-5 scale
        
        # Apply confidence based on count (more similar users = higher confidence)
        confidence = min(count / 10.0, 1.0)
        
        return avg_sim * normalized_rating * confidence
    
    def compute_item_based_cf(self, session, user_id: str, recipe_id: str) -> float:
        """
        Item-Based Collaborative Filtering:
        "This recipe is similar to recipes you liked before"
        """
        q = """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r1:Recipe)-[sim:SIMILAR_RECIPE]->(r2:Recipe {recipe_id: $rid})
        WHERE iv.liked = true OR iv.rating >= 4
        WITH sim.score AS similarity, iv.rating AS user_rating
        RETURN 
            avg(similarity) AS avg_similarity,
            count(*) AS similar_item_count,
            avg(coalesce(user_rating, 4.0)) AS avg_user_rating
        """
        
        result = session.run(q, uid=user_id, rid=recipe_id).single()
        
        if not result or result['similar_item_count'] == 0:
            return 0.0
        
        avg_sim = result['avg_similarity'] or 0.0
        avg_rating = result['avg_user_rating'] or 0.0
        count = result['similar_item_count']
        
        # Normalize rating
        normalized_rating = (avg_rating - 1) / 4.0
        
        # Confidence
        confidence = min(count / 5.0, 1.0)
        
        return avg_sim * normalized_rating * confidence
    
    def compute_popularity_score(self, session, recipe_id: str) -> float:
        """
        Popularity-based score (simple CF approach).
        """
        q = """
        MATCH (r:Recipe {recipe_id: $rid})
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-()
        WITH r,
            sum(CASE WHEN iv.liked = true THEN 1 ELSE 0 END) AS like_count,
            sum(CASE WHEN iv.rating IS NOT NULL THEN 1 ELSE 0 END) AS rating_count,
            avg(CASE WHEN iv.rating IS NOT NULL THEN iv.rating ELSE 0 END) AS avg_rating
        RETURN 
            like_count,
            rating_count,
            avg_rating,
            coalesce(r.rating_value, 0.0) AS global_rating
        """
        
        result = session.run(q, rid=recipe_id).single()
        
        if not result:
            return 0.0
        
        like_count = result['like_count'] or 0
        rating_count = result['rating_count'] or 0
        avg_rating = result['avg_rating'] or 0
        global_rating = result['global_rating'] or 0
        
        # Combine popularity signals
        like_score = math.log1p(like_count) / 10.0  # Log scale
        rating_score = (avg_rating / 5.0) if rating_count > 0 else (global_rating / 5.0)
        
        return min((like_score + rating_score) / 2.0, 1.0)
    
    def compute_cf_score(self, session, user_id: str, recipe_id: str) -> CFScores:
        """
        Compute overall CF score combining all CF approaches.
        """
        user_cf = self.compute_user_based_cf(session, user_id, recipe_id)
        item_cf = self.compute_item_based_cf(session, user_id, recipe_id)
        popularity = self.compute_popularity_score(session, recipe_id)
        
        return CFScores(
            user_based_score=user_cf,
            item_based_score=item_cf,
            popularity_score=popularity
        )


# =========================================================
# 🧠 Knowledge-Based Component
# =========================================================

class KBRecommender:
    """
    Knowledge-Based reasoning using IF-THEN rules.
    This provides explainable recommendations.
    """
    
    def __init__(self, driver, database):
        self.driver = driver
        self.database = database
    
    def check_hard_constraints(self, session, user_id: str, recipe_id: str) -> Tuple[bool, List[str]]:
        """
        Check hard constraints (MUST be satisfied).
        Returns: (constraints_met, reasons)
        """
        reasons = []
        
        # Rule 1: Allergen safety
        q_allergen = """
        MATCH (u:User {user_id: $uid})-[:ALLERGIC_TO]->(a:Ingredient)
        MATCH (r:Recipe {recipe_id: $rid})-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE i.ingredient_id IN collect(a.ingredient_id)
        RETURN count(*) AS allergen_count
        """
        result = session.run(q_allergen, uid=user_id, rid=recipe_id).single()
        
        if result and result['allergen_count'] > 0:
            return False, ["❌ Contains allergens"]
        else:
            reasons.append("🛡️ Safe for your dietary restrictions")
        
        # Rule 2: Time constraint
        q_time = """
        MATCH (u:User {user_id: $uid})
        MATCH (r:Recipe {recipe_id: $rid})
        WHERE u.max_cook_time IS NOT NULL AND r.cook_time_min IS NOT NULL
        RETURN 
            u.max_cook_time AS max_time,
            r.cook_time_min AS cook_time
        """
        result = session.run(q_time, uid=user_id, rid=recipe_id).single()
        
        if result and result['max_time'] and result['cook_time']:
            if result['cook_time'] > result['max_time']:
                return False, ["❌ Takes too long to cook"]
            else:
                reasons.append(f"⏱️ Fits your time budget ({result['cook_time']} min)")
        
        return True, reasons
    
    def apply_soft_rules(self, session, user_id: str, recipe_id: str) -> Tuple[float, List[str]]:
        """
        Apply soft rules (preferences, not requirements).
        Returns: (rule_score, reasons)
        """
        score = 0.0
        reasons = []
        
        # Rule 1: Cuisine preference
        q_cuisine = """
        MATCH (u:User {user_id: $uid})-[:FAVORS_CUISINE]->(c:Cuisine)
        MATCH (r:Recipe {recipe_id: $rid})
        WHERE any(cuisine IN r.cuisine WHERE toLower(cuisine) = toLower(c.name))
        RETURN count(*) AS match_count
        """
        result = session.run(q_cuisine, uid=user_id, rid=recipe_id).single()
        
        if result and result['match_count'] > 0:
            score += 0.3
            reasons.append("🍜 Matches your favorite cuisine")
        
        # Rule 2: Group popularity
        q_group = """
        MATCH (u:User {user_id: $uid})-[:BELONGS_TO]->(g:Group)-[pop:POPULAR_IN]->(r:Recipe {recipe_id: $rid})
        RETURN pop.score AS popularity
        """
        result = session.run(q_group, uid=user_id, rid=recipe_id).single()
        
        if result and result['popularity']:
            pop_score = result['popularity']
            if pop_score > 10:
                score += 0.2
                reasons.append("🏆 Very popular among people like you")
            elif pop_score > 5:
                score += 0.15
                reasons.append("👥 Popular among people like you")
        
        # Rule 3: Ingredient match
        q_ingredients = """
        MATCH (u:User {user_id: $uid})-[:INTERACTED_WITH]->(r1:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH collect(DISTINCT i.ingredient_id) AS user_ingredients
        MATCH (r:Recipe {recipe_id: $rid})-[:HAS_INGREDIENT]->(i2:Ingredient)
        WITH user_ingredients, collect(DISTINCT i2.ingredient_id) AS recipe_ingredients
        WITH user_ingredients, recipe_ingredients,
             [x IN user_ingredients WHERE x IN recipe_ingredients] AS intersection
        RETURN 
            size(intersection) AS shared_count,
            size(recipe_ingredients) AS total_count
        """
        result = session.run(q_ingredients, uid=user_id, rid=recipe_id).single()
        
        if result and result['total_count'] > 0:
            match_ratio = result['shared_count'] / result['total_count']
            if match_ratio >= 0.5:
                score += 0.2
                reasons.append(f"✅ Uses familiar ingredients ({result['shared_count']}/{result['total_count']})")
        
        return score, reasons
    
    def compute_kb_score(self, session, user_id: str, recipe_id: str) -> KnowledgeScore:
        """
        Compute overall knowledge-based score.
        """
        # Check hard constraints
        constraints_met, hard_reasons = self.check_hard_constraints(session, user_id, recipe_id)
        
        if not constraints_met:
            return KnowledgeScore(
                rule_score=0.0,
                constraints_met=False,
                reasoning=hard_reasons
            )
        
        # Apply soft rules
        rule_score, soft_reasons = self.apply_soft_rules(session, user_id, recipe_id)
        
        return KnowledgeScore(
            rule_score=rule_score,
            constraints_met=True,
            reasoning=hard_reasons + soft_reasons
        )


# =========================================================
# 🎯 Hybrid Recommender (Combines All Three)
# =========================================================

class HybridMLRecommender:
    """
    Hybrid recommender combining:
    1. Machine Learning (ML)
    2. Collaborative Filtering (CF)
    3. Knowledge-Based (KB)
    """
    
    def __init__(self, uri="bolt://localhost:7687", username="neo4j",
                 password="Admin123!", database="test"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database
        
        # Initialize components
        self.ml_recommender = MLRecommender(self.driver, self.database)
        self.cf_recommender = CFRecommender(self.driver, self.database)
        self.kb_recommender = KBRecommender(self.driver, self.database)
        
        # Weights for hybrid combination (can be tuned)
        self.weights = {
            'ml': 0.35,  # Machine Learning weight
            'cf': 0.35,  # Collaborative Filtering weight
            'kb': 0.30   # Knowledge-Based weight
        }
    
    def close(self):
        self.driver.close()
    
    def compute_hybrid_score(self, session, user_id: str, recipe_id: str) -> Optional[HybridScore]:
        """
        Compute hybrid score combining ML, CF, and KB approaches.
        """
        # 1. Knowledge-Based (check constraints first)
        kb_score = self.kb_recommender.compute_kb_score(session, user_id, recipe_id)
        
        if not kb_score.constraints_met:
            # Hard constraints not met - exclude this recipe
            return None
        
        # 2. Machine Learning
        ml_score = self.ml_recommender.compute_ml_score(session, user_id, recipe_id)
        
        # 3. Collaborative Filtering
        cf_scores = self.cf_recommender.compute_cf_score(session, user_id, recipe_id)
        
        # Combine CF scores
        cf_combined = (
            cf_scores.user_based_score * 0.4 +
            cf_scores.item_based_score * 0.4 +
            cf_scores.popularity_score * 0.2
        )
        
        # 4. Compute final hybrid score
        final_score = (
            ml_score * self.weights['ml'] +
            cf_combined * self.weights['cf'] +
            kb_score.rule_score * self.weights['kb']
        )
        
        # Build reasoning
        reasoning = kb_score.reasoning.copy()
        
        if ml_score > 0.5:
            reasoning.append(f"🤖 ML: High content similarity ({ml_score:.2f})")
        
        if cf_scores.user_based_score > 0.3:
            reasoning.append(f"👥 CF: Liked by similar users")
        
        if cf_scores.item_based_score > 0.3:
            reasoning.append(f"🔗 CF: Similar to recipes you liked")
        
        if cf_scores.popularity_score > 0.5:
            reasoning.append(f"⭐ Popular recipe")
        
        return HybridScore(
            ml_score=ml_score,
            cf_score=cf_combined,
            kb_score=kb_score.rule_score,
            final_score=final_score,
            components={
                'ml': ml_score,
                'cf_user': cf_scores.user_based_score,
                'cf_item': cf_scores.item_based_score,
                'cf_popularity': cf_scores.popularity_score,
                'kb_rules': kb_score.rule_score
            },
            reasoning=reasoning
        )
    
    def recommend(self, user_id: str, limit: int = 20, 
                  available_ingredients: Optional[List[str]] = None) -> List[Dict]:
        """
        Generate hybrid recommendations combining ML + CF + KB.
        """
        with self.driver.session(database=self.database) as session:
            print(f"🎯 Generating hybrid recommendations for user {user_id}...", file=sys.stderr)
            
            # Step 1: Find candidate recipes
            if available_ingredients:
                # Find recipes with these ingredients
                q_candidates = """
                MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
                WHERE i.ingredient_id IN $ingredients
                WITH r, count(DISTINCT i) AS shared_count
                WHERE shared_count >= 1
                RETURN DISTINCT r.recipe_id AS recipe_id
                ORDER BY shared_count DESC
                LIMIT $limit
                """
                candidates = session.run(q_candidates, 
                                       ingredients=available_ingredients,
                                       limit=limit * 3).data()
            else:
                # Find popular recipes
                q_candidates = """
                MATCH (r:Recipe)
                WHERE r.rating_value IS NOT NULL
                RETURN r.recipe_id AS recipe_id
                ORDER BY r.rating_value DESC, r.rating_count DESC
                LIMIT $limit
                """
                candidates = session.run(q_candidates, limit=limit * 3).data()
            
            candidate_ids = [c['recipe_id'] for c in candidates]
            print(f"📋 Found {len(candidate_ids)} candidate recipes", file=sys.stderr)
            
            # Step 2: Score each candidate with hybrid approach
            recommendations = []
            
            for recipe_id in candidate_ids:
                # Compute hybrid score
                hybrid_score = self.compute_hybrid_score(session, user_id, recipe_id)
                
                if hybrid_score is None:
                    # Constraints not met - skip
                    continue
                
                # Get recipe details
                q_details = """
                MATCH (r:Recipe {recipe_id: $rid})
                RETURN 
                    r.recipe_id AS recipe_id,
                    r.title AS title,
                    coalesce(r.cuisine, []) AS cuisine,
                    r.recipe_category AS category,
                    r.cook_time_min AS cook_time_min
                """
                details = session.run(q_details, rid=recipe_id).single()
                
                if not details:
                    continue
                
                recommendations.append({
                    'recipe_id': details['recipe_id'],
                    'title': details['title'],
                    'cuisine': details['cuisine'],
                    'category': details['category'],
                    'cook_time_min': details['cook_time_min'],
                    'final_score': round(hybrid_score.final_score, 3),
                    'ml_score': round(hybrid_score.ml_score, 3),
                    'cf_score': round(hybrid_score.cf_score, 3),
                    'kb_score': round(hybrid_score.kb_score, 3),
                    'components': {k: round(v, 3) for k, v in hybrid_score.components.items()},
                    'reasoning': hybrid_score.reasoning
                })
            
            # Step 3: Sort by final hybrid score
            recommendations.sort(key=lambda x: x['final_score'], reverse=True)
            
            # Step 4: Return top N
            final_recommendations = recommendations[:limit]
            
            print(f"✅ Generated {len(final_recommendations)} hybrid recommendations", file=sys.stderr)
            
            # Print score breakdown
            if final_recommendations:
                avg_ml = sum(r['ml_score'] for r in final_recommendations) / len(final_recommendations)
                avg_cf = sum(r['cf_score'] for r in final_recommendations) / len(final_recommendations)
                avg_kb = sum(r['kb_score'] for r in final_recommendations) / len(final_recommendations)
                
                print(f"📊 Average scores:", file=sys.stderr)
                print(f"   - ML: {avg_ml:.3f}", file=sys.stderr)
                print(f"   - CF: {avg_cf:.3f}", file=sys.stderr)
                print(f"   - KB: {avg_kb:.3f}", file=sys.stderr)
            
            return final_recommendations


# =========================================================
# 🖥️ CLI Interface
# =========================================================

def main():
    parser = argparse.ArgumentParser(description="Hybrid ML + CF + KB Recommender")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="Admin123!")
    parser.add_argument("--db", dest="database", default="test")
    parser.add_argument("--user-id", dest="user_id", required=True, help="User ID")
    parser.add_argument("--ingredients", dest="ingredients", help="Comma-separated ingredient IDs")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    
    ingredient_ids = [x.strip() for x in args.ingredients.split(",")] if args.ingredients else None
    
    rec = HybridMLRecommender(args.uri, args.user, args.password, args.database)
    
    try:
        results = rec.recommend(
            user_id=args.user_id,
            available_ingredients=ingredient_ids,
            limit=args.limit
        )
        
        if args.json:
            print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
        else:
            print("\n" + "="*80)
            print(f"🤖 HYBRID ML + CF + KB RECOMMENDATIONS FOR USER: {args.user_id}")
            print("="*80 + "\n")
            
            for i, r in enumerate(results, 1):
                print(f"#{i}. {r['title']}")
                print(f"   🎯 Final Score: {r['final_score']:.3f}")
                print(f"   📊 Component Scores:")
                print(f"      - 🤖 ML (Machine Learning): {r['ml_score']:.3f}")
                print(f"      - 👥 CF (Collaborative Filtering): {r['cf_score']:.3f}")
                print(f"      - 🧠 KB (Knowledge-Based): {r['kb_score']:.3f}")
                print(f"   🍜 Cuisine: {', '.join(r['cuisine'])}")
                print(f"   🍽️  Category: {r['category']}")
                print(f"   ⏱️  Cook Time: {r['cook_time_min'] or 'N/A'} min")
                
                if r['reasoning']:
                    print(f"   💡 Why recommended:")
                    for reason in r['reasoning']:
                        print(f"      {reason}")
                
                print()
            
            print("="*80)
            print(f"✅ Total recommendations: {len(results)}")
            print("\n📝 Note: This is a HYBRID system combining:")
            print("   🤖 Machine Learning (TF-IDF, content-based)")
            print("   👥 Collaborative Filtering (user-based, item-based)")
            print("   🧠 Knowledge-Based (IF-THEN rules)")
            print("="*80)
    
    finally:
        rec.close()


if __name__ == "__main__":
    main()

