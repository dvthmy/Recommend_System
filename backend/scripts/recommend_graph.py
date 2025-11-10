#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Graph-based Knowledge-Based Recipe Recommendation System 🧠
-----------------------------------------------------------
- Không tính điểm, reasoning dựa vào tri thức (IF–THEN logic)
- Áp dụng công thức Jaccard để tính độ tương đồng nguyên liệu
- Loại bỏ món đã tương tác, món có dị ứng, vượt thời gian nấu
- Giải thích lý do gợi ý (Explainable Recommendations)
"""

from neo4j import GraphDatabase
import argparse
import json
from typing import Dict, List


# =========================================================
# 🧩 Core Recommender Class
# =========================================================
class GraphHybridRecommender:
    def __init__(self, uri="bolt://localhost:7687", username="neo4j",
                 password="Admin123!", database="neo4j"):
        self.driver = GraphDatabase.driver(uri, auth=(username, password))
        self.database = database

    def close(self):
        self.driver.close()

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
            coalesce(u.age_group, 'unknown') AS age_group,
            collect(DISTINCT a.ingredient_id) AS allergies,
            collect(DISTINCT c.name) AS fav_cuisines,
            u.max_cook_time AS maxCook
        """
        row = session.run(q, uid=user_id).single()
        if not row:
            return {"allergies": [], "fav_cuisines": [], "maxCook": None,
                    "gender": "unknown", "age_group": "unknown"}
        try:
            maxCook = int(row.get("maxCook")) if row.get("maxCook") else None
        except:
            maxCook = None
        return {
            "allergies": row.get("allergies") or [],
            "fav_cuisines": row.get("fav_cuisines") or [],
            "maxCook": maxCook,
            "gender": row.get("gender") or "unknown",
            "age_group": row.get("age_group") or "unknown",
        }

    # ---------------------------------------------------
    # 🔍 Knowledge-Based Reasoning (no score, Jaccard)
    # ---------------------------------------------------
    def recommend_knowledge_based(self, session, user_id, ingredient_ids,
                                  user_profile, limit=10, min_match_ratio=0.8):
        fav_cuisines = user_profile.get("fav_cuisines", [])
        allergies = user_profile.get("allergies", [])
        max_cook = user_profile.get("maxCook", None)

        q = """
        MATCH (u:User {user_id:$uid})

        // --- Step 1️⃣: Load user context ---
        OPTIONAL MATCH (u)-[:ALLERGIC_TO]->(a:Ingredient)
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        OPTIONAL MATCH (u)-[:INTERACTED_WITH {event_type:'like'}]->(prev:Recipe)
        OPTIONAL MATCH (u)-[:INTERACTED_WITH]->(x:Recipe)
        WITH u,
            collect(DISTINCT a.ingredient_id) AS allergies,
            collect(DISTINCT c.name) AS fav_cuisines,
            collect(DISTINCT x.recipe_id) AS interacted_ids,
            collect(DISTINCT prev) AS liked_recipes,
            coalesce(u.max_cook_time, NULL) AS max_cook

        // --- Step 2️⃣: Candidate recipes ---
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE i.ingredient_id IN $input_ing
        AND NOT r.recipe_id IN interacted_ids
        AND ($max_cook IS NULL OR
            coalesce(r.total_time, r.cook_time, r.prep_time, 999999) <= $max_cook)
        WITH u, allergies, fav_cuisines, liked_recipes, r,
            collect(DISTINCT i.ingredient_id) AS matched_ing

        // --- Step 3️⃣: Collect all recipe ingredients ---
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH u, allergies, fav_cuisines, liked_recipes, r,
            matched_ing, collect(DISTINCT ai.ingredient_id) AS all_ing

        // --- Step 4️⃣: Compute Jaccard match ratio ---
        WITH u, allergies, fav_cuisines, liked_recipes, r, matched_ing, all_ing,
            CASE 
                WHEN size(all_ing)=0 THEN 0.0
                ELSE toFloat(size(matched_ing)) /
                    toFloat(size(all_ing) + size($input_ing) - size(matched_ing))
            END AS match_ratio,
            size(all_ing) AS ing_count
        WHERE 
            (
            (ing_count < 5  AND match_ratio >= 0.3) OR
            (ing_count >= 5 AND ing_count < 10 AND match_ratio >= 0.4) OR
            (ing_count >= 10 AND match_ratio >= 0.5)
            )
        AND NONE(ing IN all_ing WHERE ing IN allergies)
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, all_ing, match_ratio,
            [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing

        // --- Step 5️⃣: Reasoning flags ---
        WITH u, fav_cuisines, liked_recipes, r, matched_ing, missing_ing, match_ratio,
            (match_ratio >= 0.75) AS good_match,
            (match_ratio >= 0.5 AND match_ratio < 0.75) AS partial_match,
            (match_ratio >= 0.3 AND match_ratio < 0.5) AS slight_match,
            any(c IN r.cuisine WHERE c IN fav_cuisines) AS matches_cuisine

        // --- Step 6️⃣: Social & demographic signals ---
        OPTIONAL MATCH (u)-[:SIMILAR_USER]->(u2:User)-[:INTERACTED_WITH]->(r)
        WITH u, liked_recipes, r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            count(DISTINCT u2) AS similar_users

        OPTIONAL MATCH (u)-[:BELONGS_TO]->(g:Group)-[:POPULAR_IN]->(r)
        WITH u, liked_recipes, r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, count(g) AS demo_signal

                // --- Step 7️⃣: Semantic similarity (TF-IDF cosine) ---
        UNWIND liked_recipes AS lr
        WITH u, r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal, lr
        WHERE lr.text_weights IS NOT NULL AND r.text_weights IS NOT NULL
        WITH u, r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal,
            lr.text_weights AS lr_vec,
            r.text_weights AS r_vec
        WITH u, r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal,
            CASE 
            WHEN lr_vec IS NULL OR r_vec IS NULL 
                    OR size(lr_vec)=0 OR size(r_vec)=0 
                    OR size(lr_vec) <> size(r_vec)
            THEN 0.0
            ELSE gds.similarity.cosine(lr_vec, r_vec)
            END AS sim
        WITH r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal,
            max(sim) AS max_text_sim
        WITH r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal,
            (max_text_sim >= 0.6) AS text_similar
        // --- Step 8️⃣: Rating & popularity ---
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, missing_ing, match_ratio,
            good_match, partial_match, slight_match, matches_cuisine,
            similar_users, demo_signal, text_similar,
            coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
            coalesce(toInteger(r.rating_count), 0) AS rating_count,
            sum(CASE WHEN iv.event_type='like' THEN 1 ELSE 0 END) AS like_count,
            sum(CASE WHEN iv.event_type='view' THEN 1 ELSE 0 END) AS view_count

        // --- Step 9️⃣: Build reasoning explanations ---
        WITH r, matched_ing, missing_ing, match_ratio,
            [reason IN [
                CASE 
                WHEN good_match THEN '✅ Shares most of your given ingredients'
                WHEN partial_match THEN '🧂 Partially matches your given ingredients'
                WHEN slight_match THEN '🥄 Slightly matches your given ingredients'
                ELSE NULL END,
                CASE WHEN matches_cuisine THEN '🍜 Matches your favorite cuisine' ELSE NULL END,
                CASE WHEN text_similar THEN '🧠 Similar to recipes you liked before' ELSE NULL END,
                CASE WHEN similar_users > 0 THEN '👥 Liked by users similar to you' ELSE NULL END,
                CASE WHEN demo_signal > 0 THEN '🏷️ Popular among your demographic group' ELSE NULL END,
                CASE WHEN avg_rating >= 4.5 THEN '⭐ Top-rated recipe' ELSE NULL END,
                CASE WHEN avg_rating >= 4.0 AND avg_rating < 4.5 THEN '👍 Well-rated by users' ELSE NULL END,
                CASE WHEN like_count > 10 THEN '❤️ Liked by many users' ELSE NULL END,
                CASE WHEN view_count > 30 THEN '👀 Frequently viewed by users' ELSE NULL END
            ] WHERE reason IS NOT NULL] AS reasoning

        // --- Step 🔟: Return final explainable results ---
        RETURN
            r.recipe_id AS recipe_id,
            r.title AS title,
            coalesce(r.cuisine, []) AS cuisine,
            coalesce(r.tags, []) AS tags,
            round(match_ratio * 100, 1) AS match_percent,
            r.cook_time AS cook_time_min,
            coalesce(r.image, head(r.image_urls)) AS image,
            matched_ing,
            missing_ing,
            reasoning
        ORDER BY match_ratio DESC, size(reasoning) DESC
        LIMIT $lim

        """

        result = session.run(
            q,
            uid=user_id,
            input_ing=ingredient_ids,
            allergies=allergies,
            fav_cuisines=fav_cuisines,
            max_cook=max_cook,
            min_match=min_match_ratio,
            lim=limit
        )
        return [dict(r) for r in result]

        # ---------------------------------------------------
    # 🌿 Ingredient-only fallback (Explainable)
    # ---------------------------------------------------
    def recommend_ingredient_only(self, session, ingredient_ids, limit=10, min_match_ratio=0.5):
        q = """
        MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
        WHERE i.ingredient_id IN $input_ing
        WITH r, collect(DISTINCT i.ingredient_id) AS matched_ing
        MATCH (r)-[:HAS_INGREDIENT]->(ai:Ingredient)
        WITH r, matched_ing, collect(DISTINCT ai.ingredient_id) AS all_ing,
             CASE 
                WHEN size(all_ing)=0 THEN 0.0
                ELSE toFloat(size(matched_ing)) / 
                     toFloat(size(all_ing) + size($input_ing) - size(matched_ing))
             END AS match_ratio
        WHERE match_ratio >= $min_match
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matched_ing, all_ing, match_ratio,
             [x IN all_ing WHERE NOT x IN matched_ing] AS missing_ing,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             sum(CASE WHEN iv.event_type='like' THEN 1 ELSE 0 END) AS like_count
        WITH r, matched_ing, missing_ing, match_ratio, avg_rating, like_count,
             [reason IN [
                CASE WHEN match_ratio >= 0.75 THEN '✅ Shares most of your given ingredients'
                     WHEN match_ratio >= 0.5 THEN '🧂 Partially matches your given ingredients'
                     ELSE NULL END,
                CASE WHEN avg_rating >= 4.5 THEN '⭐ Top-rated recipe' ELSE NULL END,
                CASE WHEN like_count > 10 THEN '❤️ Liked by many users' ELSE NULL END
             ] WHERE reason IS NOT NULL] AS reasoning
        RETURN r.recipe_id AS recipe_id, r.title AS title,
               round(match_ratio*100,1) AS match_percent,
               r.cook_time AS cook_time_min,
               coalesce(r.image, head(r.image_urls)) AS image,
               matched_ing, missing_ing, reasoning
        ORDER BY match_ratio DESC, size(reasoning) DESC
        LIMIT $lim
        """
        result = session.run(q, input_ing=ingredient_ids, min_match=min_match_ratio, lim=limit)
        return [dict(r) for r in result]

    # ---------------------------------------------------
    # 👥 User-only fallback (Explainable)
    # ---------------------------------------------------
    def recommend_user_only(self, session, user_id, user_profile, limit=10):
        fav_cuisines = user_profile.get("fav_cuisines", [])
        q = """
        MATCH (u:User {user_id:$uid})
        OPTIONAL MATCH (u)-[:INTERACTED_WITH]->(x:Recipe)
        WITH u, collect(x.recipe_id) AS interacted_ids
        MATCH (r:Recipe)
        WHERE NOT r.recipe_id IN interacted_ids
        WITH u, r,
             any(c IN r.cuisine WHERE c IN $fav_cuisines) AS matches_cuisine
        OPTIONAL MATCH (u)-[:SIMILAR_USER]->(u2:User)-[:INTERACTED_WITH]->(r)
        WITH r, matches_cuisine, count(DISTINCT u2) AS similar_users
        OPTIONAL MATCH (r)<-[iv:INTERACTED_WITH]-(:User)
        WITH r, matches_cuisine, similar_users,
             coalesce(toFloat(r.rating_value), 0.0) AS avg_rating,
             sum(CASE WHEN iv.event_type='view' THEN 1 ELSE 0 END) AS view_count
        WITH r, matches_cuisine, similar_users, avg_rating, view_count,
             [reason IN [
                CASE WHEN matches_cuisine THEN '🍜 Matches your favorite cuisine' ELSE NULL END,
                CASE WHEN similar_users > 0 THEN '👥 Liked by users similar to you' ELSE NULL END,
                CASE WHEN avg_rating >= 4.5 THEN '⭐ Top-rated recipe' ELSE NULL END,
                CASE WHEN view_count > 30 THEN '👀 Frequently viewed by users' ELSE NULL END
             ] WHERE reason IS NOT NULL] AS reasoning
        RETURN r.recipe_id AS recipe_id, r.title AS title,
               coalesce(r.cuisine, []) AS cuisine,
               r.cook_time AS cook_time_min,
               coalesce(r.image, head(r.image_urls)) AS image,
               reasoning
        ORDER BY size(reasoning) DESC, avg_rating DESC
        LIMIT $lim
        """
        result = session.run(q, uid=user_id, fav_cuisines=fav_cuisines, lim=limit)
        return [dict(r) for r in result]

    # ---------------------------------------------------
    # 🧩 Main entrypoint
    # ---------------------------------------------------
    def recommend(self, user_id=None, ingredient_ids=None, limit=10, min_match_ratio=0.8):
        with self.driver.session(database=self.database) as session:
            if user_id and ingredient_ids:
                return self.recommend_knowledge_based(
                    session, user_id, ingredient_ids,
                    self.get_user_profile(session, user_id),
                    limit, min_match_ratio)
            elif ingredient_ids:
                return self.recommend_ingredient_only(session, ingredient_ids, limit, min_match_ratio)
            elif user_id:
                return self.recommend_user_only(session, user_id, self.get_user_profile(session, user_id), limit)
            else:
                # Default: return globally popular recipes
                q = """
                MATCH (r:Recipe)<-[iv:INTERACTED_WITH]-()
                WITH r, count(iv) AS pop
                RETURN r.recipe_id AS recipe_id, r.title AS title,
                       coalesce(r.image, head(r.image_urls)) AS image,
                       r.cook_time AS cook_time_min, pop
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
    parser.add_argument("--ingredients", dest="ingredients")
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--min-match", type=float, default=0.8)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    ingredient_ids = [x.strip() for x in args.ingredients.split(",")] if args.ingredients else None
    rec = GraphHybridRecommender(args.uri, args.user, args.password, args.database)
    results = rec.recommend(user_id=args.user_id, ingredient_ids=ingredient_ids,
                            limit=args.limit, min_match_ratio=args.min_match)

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
            print()

    rec.close()


if __name__ == "__main__":
    main()
