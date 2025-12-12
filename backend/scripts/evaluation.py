#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hybrid Recommendation Evaluation Script for Recommend_System 🧪
---------------------------------------------------------------
- DB: test
- Labels: :User, :Recipe
- Relations: :INTERACTED_WITH {event_type: "like"}
- Recipe ID property: recipe_id
"""

from neo4j import GraphDatabase
from collections import defaultdict
import statistics as stats
import math

# ✨ Import đúng module recommender của bạn
from recommend_graph import GraphHybridRecommender   # ⚠ đổi nếu file tên khác

# Neo4j config
URI = "neo4j+s://3b0d8961.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0"
DATABASE = "neo4j"

K = 10
TOP_ING = 5
MIN_INTERACTIONS = 3
ALPHA_ING = 0.6
ALPHA_PREF = 0.4

# ========= Metrics =========
def hit_rate(pred, truth):
    truth = set(truth)
    return 1.0 if any(r in truth for r in pred) else 0.0

def precision_at_k(pred, truth):
    truth = set(truth)
    return sum(1 for r in pred if r in truth) / len(pred) if pred else 0.0

def recall_at_k(pred, truth):
    truth = set(truth)
    return sum(1 for r in pred if r in truth) / len(truth) if truth else 0.0

def ndcg_at_k(pred, truth, k):
    truth = set(truth)
    dcg, idcg = 0.0, 0.0
    for i, r in enumerate(pred[:k]):
        if r in truth:
            dcg += 1 / math.log2(i + 2)
    ideal = min(len(truth), k)
    for i in range(ideal):
        idcg += 1 / math.log2(i + 2)
    return dcg / idcg if idcg > 0 else 0.0

# ========= Neo4j Queries =========
def get_users(tx):
    q = """
    MATCH (u:User)-[i:INTERACTED_WITH {event_type:'like'}]->(:Recipe)
    WITH u, count(*) AS cnt
    WHERE cnt >= $min
    RETURN u.user_id AS uid
    ORDER BY cnt DESC
    """
    return [row["uid"] for row in tx.run(q, min=MIN_INTERACTIONS)]

def get_user_gt_pref(tx, uid):
    q = """
    MATCH (u:User {user_id:$uid})-[i:INTERACTED_WITH {event_type:'like'}]->(r:Recipe)
    RETURN r.recipe_id AS rid
    """
    return [row["rid"] for row in tx.run(q, uid=uid)]

def get_user_top_ingredients(tx, uid):
    q = """
    MATCH (u:User {user_id:$uid})-[:INTERACTED_WITH {event_type:'like'}]->(r:Recipe)
    MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
    RETURN toLower(i.canonical_name) AS ing, count(*) AS freq
    ORDER BY freq DESC
    LIMIT $n
    """
    return [row["ing"] for row in tx.run(q, uid=uid, n=TOP_ING)]

def get_gt_ingredient_recipes(tx, ingredients):
    if not ingredients:
        return []
    q = """
    MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
    WHERE toLower(i.canonical_name) IN $ings
    WITH r, count(*) AS matches
    WHERE matches >= 2
    RETURN DISTINCT r.recipe_id AS rid
    """
    return [row["rid"] for row in tx.run(q, ings=ingredients)]

# ========= Evaluate User =========
def evaluate_user(session, recommender, uid):
    pref_gt = get_user_gt_pref(session, uid)
    if len(pref_gt) < MIN_INTERACTIONS:
        return None

    inputs = get_user_top_ingredients(session, uid)
    if not inputs:
        return None

    preds = recommender.recommend(user_id=uid, ingredient_names=inputs, limit=K)
    pred_ids = [p["recipe_id"] for p in preds if p.get("recipe_id")]
    if not pred_ids:
        return None

    ing_gt = get_gt_ingredient_recipes(session, inputs)

    pref_hit = hit_rate(pred_ids, pref_gt)
    ing_hit = hit_rate(pred_ids, ing_gt) if ing_gt else 0.0

    return {
        "uid": uid,
        "pref": pref_hit,
        "ing": ing_hit,
        "hybrid": ALPHA_ING * ing_hit + ALPHA_PREF * pref_hit
    }

# ========= MAIN =========
def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    recommender = GraphHybridRecommender(uri=URI, username=USER, password=PASSWORD, database=DATABASE)
    results = []

    with driver.session(database=DATABASE) as sess:
        users = get_users(sess)
        print(f"🔍 Users evaluated: {len(users)}")

        for uid in users:
            r = evaluate_user(sess, recommender, uid)
            if r:
                results.append(r)

    recommender.close()
    driver.close()

    if not results:
        print("\n❌ No evaluation data.\n")
        return

    avg_pref = stats.mean(r["pref"] for r in results)
    avg_ing = stats.mean(r["ing"] for r in results)
    avg_hybrid = stats.mean(r["hybrid"] for r in results)

    print("\n===== 📌 HYBRID RECOMMENDER EVALUATION RESULTS =====")
    print(f"Preference HitRate@{K}: {avg_pref:.4f}")
    print(f"Ingredient HitRate@{K}: {avg_ing:.4f}")
    print(f"Hybrid HitRate@{K}: {avg_hybrid:.4f}")
    print("====================================================\n")


if __name__ == "__main__":
    main()
