#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FULL EVALUATION FOR HYBRID FOOD RECOMMENDER 🍽️
Metrics: HitRate@10, Precision@10, Recall@10, NDCG@10
Recommender signature: recommend(user_id, ingredient_names, limit)
"""

from neo4j import GraphDatabase
from statistics import mean
import math
from recommend_graph import GraphHybridRecommender

# ===== Neo4j config =====
URI = "neo4j+s://3b0d8961.databases.neo4j.io"
USER = "neo4j"
PASSWORD = "qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0"
DATABASE = "neo4j"

K = 10
TOP_ING = 5
MIN_INTERACTIONS = 3


# ===== Metrics =====
def hit_rate(pred, truth):
    return 1.0 if any(r in truth for r in pred) else 0.0

def precision_at_k(pred, truth):
    return sum(1 for r in pred if r in truth) / len(pred) if pred else 0.0

def recall_at_k(pred, truth):
    return sum(1 for r in pred if r in truth) / len(truth) if truth else 0.0

def ndcg_at_k(pred, truth, k):
    truth = set(truth)
    dcg = sum(1 / math.log2(i + 2) for i, r in enumerate(pred[:k]) if r in truth)
    ideal = min(len(truth), k)
    idcg = sum(1 / math.log2(i + 2) for i in range(ideal))
    return dcg / idcg if idcg > 0 else 0.0


# ===== Neo4j Queries =====
def get_users(tx):
    q = """
    MATCH (u:User)-[i:INTERACTED_WITH {event_type:'like'}]->(:Recipe)
    WITH u, count(*) AS cnt
    WHERE cnt >= $min
    RETURN u.user_id AS uid
    """
    return [row["uid"] for row in tx.run(q, min=MIN_INTERACTIONS)]

def get_user_ground_truth(tx, uid):
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


# ===== MAIN evaluation logic =====
def evaluate_user(session, recommender, uid):
    truth = get_user_ground_truth(session, uid)
    if len(truth) < MIN_INTERACTIONS:
        return None

    top_ings = get_user_top_ingredients(session, uid)
    if not top_ings:
        return None

    preds = recommender.recommend(
        user_id=uid,
        ingredient_names=top_ings,
        limit=K
    )
    pred_ids = [p["recipe_id"] for p in preds if p.get("recipe_id")]

    if not pred_ids:
        return None

    return {
        "hit": hit_rate(pred_ids, truth),
        "precision": precision_at_k(pred_ids, truth),
        "recall": recall_at_k(pred_ids, truth),
        "ndcg": ndcg_at_k(pred_ids, truth, K)
    }


def main():
    driver = GraphDatabase.driver(URI, auth=(USER, PASSWORD))
    recommender = GraphHybridRecommender(uri=URI, username=USER, password=PASSWORD, database=DATABASE)
    results = []

    with driver.session(database=DATABASE) as sess:
        users = get_users(sess)
        print(f"🔍 Users evaluated: {len(users)}")

        for uid in users:
            m = evaluate_user(sess, recommender, uid)
            if m:
                results.append(m)

    recommender.close()
    driver.close()

    if not results:
        print("\n❌ No evaluation results — recommend() returned no predictions.\n")
        return

    print("\n===== 📊 HYBRID RECOMMENDER EVALUATION RESULTS =====")
    print(f"HitRate@{K}:      {mean(m['hit'] for m in results):.4f}")
    print(f"Precision@{K}:    {mean(m['precision'] for m in results):.4f}")
    print(f"Recall@{K}:       {mean(m['recall'] for m in results):.4f}")
    print(f"NDCG@{K}:         {mean(m['ndcg'] for m in results):.4f}")
    print("====================================================\n")


if __name__ == "__main__":
    main()
