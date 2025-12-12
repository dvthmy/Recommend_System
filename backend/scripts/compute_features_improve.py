#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline: Normalize text + compute IDF + compute TF-IDF + update Neo4j + Hybrid Graph
- PASS1: stream toàn bộ recipe → normalize → đếm DF (text & ingredient)
- Tính IDF cho text token và ingredient_id
- PASS2: stream lại → tính TF-IDF từng recipe → lưu r.text_terms/text_weights
         → gán rel.idf_weight cho HAS_INGREDIENT
- Lưu thống kê Ingredient (doc_freq, ing_idf, total_docs)
- Xây user profile vector
- PASS3: Xây hybrid similarity graph (content + behavior + demographic)
"""

import math
import re
import time
import json
from collections import Counter
from dataclasses import dataclass
from typing import Dict, List
from neo4j import GraphDatabase
import sys, os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB, DEFAULT_BATCH, TOP_TERMS_PER_RECIPE


# =============== TEXT NORMALIZATION ===============
WORD_RE = re.compile(r"[a-z0-9]+")

def normalize_text(s: str) -> List[str]:
    if not s:
        return []
    s = s.lower()
    return WORD_RE.findall(s)


# =============== DATA MODEL ===============
@dataclass
class RowLite:
    rid: str
    title: str
    tags: List[str]
    instr: str
    cuisine: List[str]
    ing_ids: List[str]


# =============== CYPHER HELPERS ===============
def fetch_recipes_paged(tx, skip: int, limit: int):
    q = """
    MATCH (r:Recipe)
    OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
    WITH r, collect(DISTINCT i.ingredient_id) AS allIngIds
    WITH r, [x IN allIngIds WHERE x IS NOT NULL] AS ingIds
    RETURN r.recipe_id AS rid,
           coalesce(r.title,'') AS title,
           coalesce(r.tags, []) AS tags,
           coalesce(r.instructions,'') AS instr,
           coalesce(r.cuisine, []) AS cuisine,
           coalesce(ingIds, []) AS ingIds
    ORDER BY r.recipe_id
    SKIP $skip LIMIT $limit
    """
    return list(tx.run(q, skip=skip, limit=limit))


def fetch_recipes_paged_missing(tx, skip: int, limit: int):
    """Fetch recipes that don't have text_terms/text_weights yet"""
    q = """
    MATCH (r:Recipe)
    WHERE r.text_terms IS NULL OR r.text_weights IS NULL 
       OR size(r.text_terms) = 0 OR size(r.text_weights) = 0
       OR size(r.text_terms) != size(r.text_weights)
    OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
    WITH r, collect(DISTINCT i.ingredient_id) AS allIngIds
    WITH r, [x IN allIngIds WHERE x IS NOT NULL] AS ingIds
    RETURN r.recipe_id AS rid,
           coalesce(r.title,'') AS title,
           coalesce(r.tags, []) AS tags,
           coalesce(r.instructions,'') AS instr,
           coalesce(r.cuisine, []) AS cuisine,
           coalesce(ingIds, []) AS ingIds
    ORDER BY r.recipe_id
    SKIP $skip LIMIT $limit
    """
    return list(tx.run(q, skip=skip, limit=limit))


def check_text_vectors_status(driver, session_kwargs):
    """Check how many recipes already have text_terms/text_weights"""
    with driver.session(**session_kwargs) as session:
        q_total = "MATCH (r:Recipe) RETURN count(r) AS total"
        total = session.run(q_total).single()["total"]
        
        q_with_vectors = """
        MATCH (r:Recipe)
        WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
          AND size(r.text_terms) > 0 AND size(r.text_weights) > 0
          AND size(r.text_terms) = size(r.text_weights)
        RETURN count(r) AS count
        """
        with_vectors = session.run(q_with_vectors).single()["count"]
        
        return total, with_vectors


def fetch_recipes_with_nutrition(tx, skip: int, limit: int, nutrition_properties: List[str]):
    """Fetch recipes with nutrition data for PASS4 - lấy TẤT CẢ nutrition properties"""
    # Build dynamic RETURN clause
    return_clauses = ["r.recipe_id AS rid"]
    for prop in nutrition_properties:
        # nutrition_calories -> calories
        alias = prop.replace("nutrition_", "")
        return_clauses.append(f"r.{prop} AS {alias}")
    
    q = f"""
    MATCH (r:Recipe)
    WHERE r.nutrition_calories IS NOT NULL
    RETURN {', '.join(return_clauses)}
    ORDER BY r.recipe_id
    SKIP $skip LIMIT $limit
    """
    return list(tx.run(q, skip=skip, limit=limit))


def store_recipe_vectors(tx, recipe_id: str, text_tfidf: Dict[str, float]):
    terms = list(text_tfidf.keys())[:TOP_TERMS_PER_RECIPE]
    weights = [float(text_tfidf[t]) for t in terms]
    q = """
    MATCH (r:Recipe {recipe_id: $rid})
    SET r.text_terms = $terms,
        r.text_weights = $weights
    """
    tx.run(q, rid=recipe_id, terms=terms, weights=weights)


def store_recipe_vectors_batch(tx, updates: List[Dict]):
    """Batch update nhiều recipes trong một transaction"""
    if not updates:
        return
    q = """
    UNWIND $updates AS u
    MATCH (r:Recipe {recipe_id: u.rid})
    SET r.text_terms = u.terms,
        r.text_weights = u.weights
    """
    tx.run(q, updates=updates)


def set_ing_edge_weights(tx, recipe_id: str, pairs: List[Dict[str, float]]):
    if not pairs:
        return
    q = """
    MATCH (r:Recipe {recipe_id: $rid})
    WITH r
    UNWIND $pairs AS p
    MATCH (r)-[rel:HAS_INGREDIENT]->(i:Ingredient {ingredient_id: p.iid})
    SET rel.idf_weight = p.w
    """
    tx.run(q, rid=recipe_id, pairs=pairs)


def set_ing_edge_weights_batch(tx, updates: List[Dict]):
    """Batch update nhiều ingredient edge weights trong một transaction"""
    if not updates:
        return
    q = """
    UNWIND $updates AS u
    MATCH (r:Recipe {recipe_id: u.rid})
    WITH r, u.pairs AS pairs
    UNWIND pairs AS p
    MATCH (r)-[rel:HAS_INGREDIENT]->(i:Ingredient {ingredient_id: p.iid})
    SET rel.idf_weight = p.w
    """
    tx.run(q, updates=updates)


def store_ingredient_stats(tx, total_docs: int, stats: List[Dict[str, float]]):
    if not stats:
        return
    q = """
    UNWIND $stats AS s
    MATCH (i:Ingredient {ingredient_id: s.iid})
    SET i.doc_freq = s.df,
        i.ing_idf = s.idf,
        i.total_docs = $N
    """
    tx.run(q, stats=stats, N=total_docs)


def build_user_profile(tx):
    q = """
    MATCH (u:User)-[iv:INTERACTED_WITH]->(r:Recipe)
    WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
          AND size(r.text_terms) = size(r.text_weights)
    WITH u, iv, r
    WITH u, r,
         CASE iv.event_type 
            WHEN 'like' THEN 1.0 
            WHEN 'rating' THEN 0.8 
            WHEN 'view' THEN 0.2 
            ELSE 0.1 
         END AS w,
         coalesce(iv.updated_at, iv.created_at, datetime()) AS interaction_time
    WITH u, w, duration.between(interaction_time, datetime()).days AS daysAgo, r
    WITH u, w * exp(-log(2) * toFloat(daysAgo) / 90.0) AS weight, r
    WITH u, weight, r, range(0, size(r.text_terms)-1) AS idxs
    UNWIND idxs AS k
    WITH u, r.text_terms[k] AS term, (weight * coalesce(r.text_weights[k],0.0)) AS contrib
    WITH u, term, sum(contrib) AS val
    WITH u, collect([term, val]) AS vec
    WITH u, vec,
         [x IN vec | x[0]] AS terms,
         [x IN vec | x[1]] AS weights
    SET u.user_terms = terms, u.user_weights = weights
    """
    tx.run(q)



def build_similar_users_from_likes(driver, session_kwargs, threshold: float = 0.3, top_k: int = 10):
    """
    Build SIMILAR_USER relationships based on:
    - Recipe similarity (Jaccard): users who liked/rated common recipes (weight: 0.7)
    - Cuisine similarity: users who favor same cuisines (weight: 0.2)
    - Group similarity: users in same groups (weight: 0.1)
    
    Uses INTERACTED_WITH relationships where:
    - liked=true or event_type='like' (likes)
    - event_type='rating' and rating IS NOT NULL (ratings)
    
    Only keeps top K (default: 10) most similar users per user.
    
    Args:
        threshold: Minimum similarity score to create relationship (default: 0.3)
        top_k: Number of top similar users to keep per user (default: 10)
    """
    print(f">> Building SIMILAR_USER relationships from LIKES + RATINGS (Jaccard + Cuisine + Group, top {top_k} per user)...")
    
    # Cleanup old SIMILAR_USER relationships
    with driver.session(**session_kwargs) as session:
        cleanup_result = session.run("""
        MATCH ()-[r:SIMILAR_USER]->()
        DELETE r
        RETURN count(r) AS deleted
        """).single()
        deleted_count = cleanup_result["deleted"] if cleanup_result else 0
        if deleted_count > 0:
            print(f"  [Cleanup] Cleaned up {deleted_count} old SIMILAR_USER relationships")
    
    # Build SIMILAR_USER using the new logic
    # Includes both LIKES (liked=true or event_type='like') and RATINGS (event_type='rating' with rating IS NOT NULL)
    with driver.session(**session_kwargs) as session:
        q = """
        // Step 1: Find users who liked/rated common recipes
        // Include both likes (liked=true or event_type='like') and ratings (event_type='rating' with rating IS NOT NULL)
        MATCH (u1:User)-[rel1:INTERACTED_WITH]->(r:Recipe)<-[rel2:INTERACTED_WITH]-(u2:User)
        WHERE u1 <> u2
          AND ((rel1.liked = true OR rel1.event_type = 'like') OR (rel1.event_type = 'rating' AND rel1.rating IS NOT NULL))
          AND ((rel2.liked = true OR rel2.event_type = 'like') OR (rel2.event_type = 'rating' AND rel2.rating IS NOT NULL))
        WITH u1, u2, COLLECT(DISTINCT r) AS both
        WITH u1, u2, both, SIZE(both) AS bothCount
        // Count total liked/rated recipes for each user
        MATCH (u1)-[r1:INTERACTED_WITH]->(r1_all:Recipe)
        WHERE (r1.liked = true OR r1.event_type = 'like') OR (r1.event_type = 'rating' AND r1.rating IS NOT NULL)
        WITH u1, u2, bothCount, count(DISTINCT r1_all) AS total1
        MATCH (u2)-[r2:INTERACTED_WITH]->(r2_all:Recipe)
        WHERE (r2.liked = true OR r2.event_type = 'like') OR (r2.event_type = 'rating' AND r2.rating IS NOT NULL)
        WITH u1, u2, bothCount, total1, count(DISTINCT r2_all) AS total2
        WITH u1, u2,
             bothCount,
             (total1 + total2 - bothCount) AS eitherCount,
             CASE WHEN (total1 + total2 - bothCount) > 0 THEN toFloat(bothCount)/(total1 + total2 - bothCount) ELSE 0 END AS recipeSim
        
        // Step 2: Check cuisine similarity
        OPTIONAL MATCH (u1)-[:FAVORS_CUISINE]->(cuisine)<-[:FAVORS_CUISINE]-(u2)
        WITH u1, u2, recipeSim,
             CASE WHEN cuisine IS NULL THEN 0 ELSE 1 END AS cuisineSim
        
        // Step 3: Check group similarity
        OPTIONAL MATCH (u1)-[:BELONGS_TO]->(g)<-[:BELONGS_TO]-(u2)
        WITH u1, u2, recipeSim, cuisineSim,
             CASE WHEN g IS NULL THEN 0 ELSE 1 END AS groupSim
        
        // Step 4: Calculate weighted similarity score
        WITH u1, u2,
             0.7*recipeSim + 0.2*cuisineSim + 0.1*groupSim AS simScore,
             recipeSim, cuisineSim, groupSim
        WHERE simScore > $threshold
        MERGE (u1)-[s:SIMILAR_USER]->(u2)
        SET s.score = simScore,
            s.recipeSim = recipeSim,
            s.cuisineSim = cuisineSim,
            s.groupSim = groupSim,
            s.updated_at = datetime()
        RETURN count(s) AS created
        """
        
        result = session.run(q, threshold=threshold).single()
        created_count = result["created"] if result else 0
        print(f"  [Info] Created {created_count} SIMILAR_USER relationships (before top-K filtering)")
        
        # Keep only Top-K similar users for each user
        print(f"  [Filter] Keeping top {top_k} similar users per user...")
        q_topk = """
        // Keep only Top-K similar users for each user
        MATCH (u1:User)-[s:SIMILAR_USER]->(u2:User)
        WITH u1, u2, s
        ORDER BY s.score DESC
        WITH u1, COLLECT(s)[0..$top_k] AS topK
        UNWIND topK AS s
        SET s.keep = true
        RETURN count(s) AS marked
        """
        marked_result = session.run(q_topk, top_k=top_k).single()
        marked_count = marked_result["marked"] if marked_result else 0
        print(f"  [Info] Marked {marked_count} relationships as top-K")
        
        # Remove all SIMILAR_USER edges that are not in Top-K
        q_remove = """
        MATCH (:User)-[s:SIMILAR_USER]->(:User)
        WHERE s.keep IS NULL
        DELETE s
        RETURN count(s) AS deleted
        """
        deleted_result = session.run(q_remove).single()
        deleted_count = deleted_result["deleted"] if deleted_result else 0
        print(f"  [Deleted] Removed {deleted_count} relationships below top-K")
        
        # Cleanup temp flag
        q_cleanup = """
        MATCH ()-[s:SIMILAR_USER]->()
        REMOVE s.keep
        RETURN count(s) AS cleaned
        """
        cleanup_result = session.run(q_cleanup).single()
        cleaned_count = cleanup_result["cleaned"] if cleanup_result else 0
        
        # Count final relationships
        final_count_result = session.run("MATCH ()-[s:SIMILAR_USER]->() RETURN count(s) AS total").single()
        final_count = final_count_result["total"] if final_count_result else 0
        print(f"  [OK] Final: {final_count} SIMILAR_USER relationships (top {top_k} per user)\n")


def build_hybrid_similarity(driver, w_cf: float = 0.5, w_demo: float = 0.2, min_popular_score: int = 2):
    """
    Build collaborative graph components:
      - User–User similarity (CF + demographic)
      - Group aggregation (POPULAR_IN)
      - Recipe–Recipe similarity (collaborative, based on user co-interaction)
    
    Args:
        w_cf: Weight for collaborative filtering similarity (default: 0.5)
        w_demo: Weight for demographic similarity (default: 0.2)
        min_popular_score: Minimum interaction count to create POPULAR_IN relationship (default: 2)
                          Only recipes with at least this many interactions in a group will be marked as popular
    """
    session_kwargs = {"database": DEFAULT_DB}

    # Use new SIMILAR_USER logic based on LIKES + RATINGS (top 10 per user)
    build_similar_users_from_likes(driver, session_kwargs, threshold=0.3, top_k=10)

    # ---- Step 2: Delete all Group nodes and relationships ----
    print(f">> Deleting all existing Group nodes and relationships...")
    with driver.session(**session_kwargs) as session:
        # Delete all POPULAR_IN relationships first (no threshold check needed)
        pop_result = session.run("""
        MATCH (:Group)-[r:POPULAR_IN]->(:Recipe)
        DELETE r
        RETURN count(r) AS deleted
        """).single()
        pop_deleted = pop_result["deleted"] if pop_result else 0
        print(f"  [Deleted] Deleted {pop_deleted} POPULAR_IN relationships")
        
        # Delete all BELONGS_TO relationships
        belongs_result = session.run("""
        MATCH (:User)-[r:BELONGS_TO]->(:Group)
        DELETE r
        RETURN count(r) AS deleted
        """).single()
        belongs_deleted = belongs_result["deleted"] if belongs_result else 0
        print(f"  [Deleted] Deleted {belongs_deleted} BELONGS_TO relationships")
        
        # Delete all Group nodes
        group_result = session.run("""
        MATCH (g:Group)
        DELETE g
        RETURN count(g) AS deleted
        """).single()
        group_deleted = group_result["deleted"] if group_result else 0
        print(f"  [Deleted] Deleted {group_deleted} Group nodes")
    
    # ---- Step 3: Create Group nodes and BELONGS_TO relationships ----
    print(f">> Creating Group nodes and BELONGS_TO relationships (age_group + gender)...")
    with driver.session(**session_kwargs) as session:
        # Create Group nodes and BELONGS_TO relationships for all users based on age_group and gender
        q_create_groups = """
        MATCH (u:User)
        WHERE u.age_group IS NOT NULL AND u.gender IS NOT NULL
        WITH u, u.gender AS gender, coalesce(u.age_group, 'unknown') AS age_group
        MERGE (g:Group {
            gender: gender,
            age_group: age_group
        })
        ON CREATE SET 
            g.group_id = g.gender + '-' + g.age_group,
            g.created_at = datetime()
        MERGE (u)-[:BELONGS_TO]->(g)
        RETURN count(DISTINCT g) AS groups_created, count(u) AS users_linked
        """
        group_result = session.run(q_create_groups).single()
        groups_created = group_result["groups_created"] if group_result else 0
        users_linked = group_result["users_linked"] if group_result else 0
        print(f"  [Created] Created {groups_created} Group nodes and linked {users_linked} users")
    
    # ---- Step 4: Create POPULAR_IN relationships ----
    print(f">> Building POPULAR_IN relationships (no threshold - all interactions)...")
    with driver.session(**session_kwargs) as session:
        # Tính POPULAR_IN dựa trên Group nodes (age_group + gender)
        # Tạo POPULAR_IN cho TẤT CẢ recipes có ít nhất 1 interaction (likes hoặc ratings) trong nhóm
        # Không có threshold - tất cả interactions đều được tính
        q_group = """
        MATCH (g:Group)<-[:BELONGS_TO]-(u:User)-[rel:INTERACTED_WITH]->(r:Recipe)
        WHERE (rel.liked = true OR rel.event_type = 'like') OR (rel.event_type = 'rating' AND rel.rating IS NOT NULL)
        WITH g, r, count(DISTINCT u) AS freq
        WHERE freq > 0
        MERGE (g)-[l:POPULAR_IN]->(r)
        SET l.score = freq, 
            l.updated_at = datetime(),
            l.group_gender = g.gender,
            l.group_age_group = g.age_group
        RETURN count(l) AS created
        """
        result = session.run(q_group)
        # Count how many relationships were created/updated
        count_result = session.run("""
        MATCH (:Group)-[r:POPULAR_IN]->(:Recipe)
        RETURN count(r) AS total
        """).single()
        total_created = count_result["total"] if count_result else 0
    print(f"[OK] POPULAR_IN relationships created: {total_created} (no threshold)\n")

    print("[OK] Hybrid graph (user, group) completed.\n")


# =============== PASS2.5: CONTENT-BASED RECIPE SIMILARITY ===============

def compute_content_similarity_batch(tx, recipe_pairs: List[Dict], threshold: float, debug: bool = False):
    """PASS2.5: Tính content similarity cho một batch recipes dựa trên TF-IDF vectors"""
    if not recipe_pairs:
        return []
    
    # Tính tất cả cặp trong một query
    q = """
    UNWIND $pairs AS pair
    MATCH (r1:Recipe {recipe_id: pair.r1_id})
    MATCH (r2:Recipe {recipe_id: pair.r2_id})
    WHERE r1.text_terms IS NOT NULL AND r1.text_weights IS NOT NULL
      AND r2.text_terms IS NOT NULL AND r2.text_weights IS NOT NULL
      AND size(r1.text_terms) = size(r1.text_weights)
      AND size(r2.text_terms) = size(r2.text_weights)
      AND size(r1.text_terms) > 0 AND size(r2.text_terms) > 0
    WITH pair, r1, r2,
         [term IN r1.text_terms WHERE term IN r2.text_terms] AS common_terms
    WHERE size(common_terms) > 0
    WITH pair, r1, r2, common_terms,
         [x IN range(0, size(r1.text_terms)-1) | [r1.text_terms[x], r1.text_weights[x]]] AS vec1,
         [x IN range(0, size(r2.text_terms)-1) | [r2.text_terms[x], r2.text_weights[x]]] AS vec2
    WITH pair, r1, r2,
         reduce(dot=0.0, term IN common_terms |
             dot + coalesce([v IN vec1 WHERE v[0]=term][0][1],0.0) * coalesce([v IN vec2 WHERE v[0]=term][0][1],0.0)
         ) AS dot,
         sqrt(reduce(sum=0.0, v IN vec1 | sum + v[1]*v[1])) AS norm1,
         sqrt(reduce(sum=0.0, v IN vec2 | sum + v[1]*v[1])) AS norm2
    WITH pair,
         CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS similarity
    WHERE similarity > $threshold
    RETURN pair.r1_id AS r1_id, pair.r2_id AS r2_id, similarity
    """
    
    # Debug query: tính similarity cho tất cả pairs (không filter by threshold) để xem distribution
    q_debug = """
    UNWIND $pairs AS pair
    MATCH (r1:Recipe {recipe_id: pair.r1_id})
    MATCH (r2:Recipe {recipe_id: pair.r2_id})
    WHERE r1.text_terms IS NOT NULL AND r1.text_weights IS NOT NULL
      AND r2.text_terms IS NOT NULL AND r2.text_weights IS NOT NULL
      AND size(r1.text_terms) = size(r1.text_weights)
      AND size(r2.text_terms) = size(r2.text_weights)
      AND size(r1.text_terms) > 0 AND size(r2.text_terms) > 0
    WITH pair, r1, r2,
         [term IN r1.text_terms WHERE term IN r2.text_terms] AS common_terms
    WHERE size(common_terms) > 0
    WITH pair, r1, r2, common_terms,
         [x IN range(0, size(r1.text_terms)-1) | [r1.text_terms[x], r1.text_weights[x]]] AS vec1,
         [x IN range(0, size(r2.text_terms)-1) | [r2.text_terms[x], r2.text_weights[x]]] AS vec2
    WITH pair,
         reduce(dot=0.0, term IN common_terms |
             dot + coalesce([v IN vec1 WHERE v[0]=term][0][1],0.0) * coalesce([v IN vec2 WHERE v[0]=term][0][1],0.0)
         ) AS dot,
         sqrt(reduce(sum=0.0, v IN vec1 | sum + v[1]*v[1])) AS norm1,
         sqrt(reduce(sum=0.0, v IN vec2 | sum + v[1]*v[1])) AS norm2
    WITH pair, r1, r2, common_terms,
         CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS similarity
    RETURN pair.r1_id AS r1_id, pair.r2_id AS r2_id, similarity, size(common_terms) AS common_count
    ORDER BY similarity DESC
    LIMIT 10
    """
    
    pairs_list = [{"r1_id": p["r1_id"], "r2_id": p["r2_id"]} for p in recipe_pairs]
    
    # Debug: show top similarities
    if debug and len(pairs_list) > 0:
        debug_sample = pairs_list[:min(100, len(pairs_list))]  # Sample first 100 pairs
        print(f"    [DEBUG] Checking {len(debug_sample)} sample pairs for similarity scores...")
        try:
            debug_results = list(tx.run(q_debug, pairs=debug_sample))
            if debug_results:
                debug_sims = [(r["similarity"], r["common_count"]) for r in debug_results]
                max_sim = max(s[0] for s in debug_sims)
                min_sim = min(s[0] for s in debug_sims)
                avg_sim = sum(s[0] for s in debug_sims) / len(debug_sims)
                above_threshold = sum(1 for s in debug_sims if s[0] > threshold)
                print(f"    [DEBUG] Sample similarities: min={min_sim:.4f}, max={max_sim:.4f}, avg={avg_sim:.4f}")
                print(f"    [DEBUG] Threshold={threshold}, pairs above threshold: {above_threshold}/{len(debug_sims)}")
                print(f"    [DEBUG] Top 5 similarities: {sorted([s[0] for s in debug_sims], reverse=True)[:5]}")
            else:
                print(f"    [DEBUG] No results from debug query - có thể không có common terms hoặc vectors không hợp lệ")
        except Exception as e:
            print(f"    [DEBUG ERROR] {e}")
    
    results = tx.run(q, pairs=pairs_list, threshold=threshold)
    
    similarities = []
    for record in results:
        similarities.append({
            "r1_id": record["r1_id"],
            "r2_id": record["r2_id"],
            "similarity": float(record["similarity"])
        })
    
    return similarities


def create_similar_recipe_relationships(tx, similarities: List[Dict]):
    """Tạo SIMILAR_RECIPE relationships dựa trên content similarity"""
    if not similarities:
        return
    
    q = """
    UNWIND $sims AS sim
    MATCH (r1:Recipe {recipe_id: sim.r1_id})
    MATCH (r2:Recipe {recipe_id: sim.r2_id})
    MERGE (r1)-[rel:SIMILAR_RECIPE]->(r2)
    SET rel.similarity = sim.similarity,
        rel.similarity_type = 'content',
        rel.updated_at = datetime()
    """
    tx.run(q, sims=similarities)


def build_similar_recipes_from_likes(driver, session_kwargs, top_k: int = 10):
    """
    Build SIMILAR_RECIPE relationships based on Jaccard similarity of users who liked/rated both recipes.
    Only keeps top K (default: 10) most similar recipes per recipe.
    
    Uses INTERACTED_WITH relationships where:
    - liked=true or event_type='like' (likes)
    - event_type='rating' and rating IS NOT NULL (ratings)
    
    Args:
        top_k: Number of top similar recipes to keep per recipe (default: 10)
    """
    print(f">> Building SIMILAR_RECIPE relationships from LIKES + RATINGS (Jaccard, top {top_k} per recipe)...")
    
    # Cleanup old SIMILAR_RECIPE relationships
    with driver.session(**session_kwargs) as session:
        cleanup_result = session.run("""
        MATCH ()-[r:SIMILAR_RECIPE]->()
        DELETE r
        RETURN count(r) AS deleted
        """).single()
        deleted_count = cleanup_result["deleted"] if cleanup_result else 0
        if deleted_count > 0:
            print(f"  [Cleanup] Cleaned up {deleted_count} old SIMILAR_RECIPE relationships")
    
    # Build SIMILAR_RECIPE using the new logic
    # Includes both LIKES (liked=true or event_type='like') and RATINGS (event_type='rating' with rating IS NOT NULL)
    with driver.session(**session_kwargs) as session:
        # Compute similarities using Cypher query
        # This query finds users who liked/rated both recipes and calculates Jaccard similarity
        q_compute = """
        MATCH (r1:Recipe)<-[rel1:INTERACTED_WITH]-(u:User)-[rel2:INTERACTED_WITH]->(r2:Recipe)
        WHERE r1 <> r2
          AND ((rel1.liked = true OR rel1.event_type = 'like') OR (rel1.event_type = 'rating' AND rel1.rating IS NOT NULL))
          AND ((rel2.liked = true OR rel2.event_type = 'like') OR (rel2.event_type = 'rating' AND rel2.rating IS NOT NULL))
        WITH r1, r2, COLLECT(DISTINCT u) AS bothUsers
        WITH r1, r2, bothUsers, SIZE(bothUsers) AS both
        // Count total users who liked/rated each recipe
        MATCH (r1)<-[r1_rel:INTERACTED_WITH]-(u1_all:User)
        WHERE (r1_rel.liked = true OR r1_rel.event_type = 'like') OR (r1_rel.event_type = 'rating' AND r1_rel.rating IS NOT NULL)
        WITH r1, r2, both, count(DISTINCT u1_all) AS total1
        MATCH (r2)<-[r2_rel:INTERACTED_WITH]-(u2_all:User)
        WHERE (r2_rel.liked = true OR r2_rel.event_type = 'like') OR (r2_rel.event_type = 'rating' AND r2_rel.rating IS NOT NULL)
        WITH r1, r2, both, total1, count(DISTINCT u2_all) AS total2
        WITH r1, r2, both,
             (total1 + total2 - both) AS either
        WHERE either > 0
        WITH r1, r2, toFloat(both)/either AS score
        ORDER BY r1.recipe_id, score DESC
        RETURN r1.recipe_id AS r1_id, r2.recipe_id AS r2_id, score
        """
        
        # Process in batches to avoid memory issues
        print("  [Compute] Computing similarities...")
        all_similarities = []
        batch_size = 1000
        
        result = session.run(q_compute)
        for record in result:
            all_similarities.append({
                "r1_id": record["r1_id"],
                "r2_id": record["r2_id"],
                "score": float(record["score"])
            })
        
        print(f"  [Info] Found {len(all_similarities)} recipe pairs with similarity")
        
        # Group by r1_id and keep top K for each recipe
        from collections import defaultdict
        recipe_similarities = defaultdict(list)
        for sim in all_similarities:
            recipe_similarities[sim["r1_id"]].append((sim["r2_id"], sim["score"]))
        
        # Keep top K for each recipe
        top_similarities = []
        for r1_id, similarities in recipe_similarities.items():
            # Sort by score descending and take top K
            sorted_sims = sorted(similarities, key=lambda x: x[1], reverse=True)[:top_k]
            for r2_id, score in sorted_sims:
                top_similarities.append({
                    "r1_id": r1_id,
                    "r2_id": r2_id,
                    "score": score
                })
        
        print(f"  [Info] Keeping top {top_k} similarities per recipe: {len(top_similarities)} relationships")
        
        # Create relationships in batches
        if top_similarities:
            for i in range(0, len(top_similarities), batch_size):
                batch = top_similarities[i:i+batch_size]
                q_create = """
                UNWIND $sims AS sim
                MATCH (r1:Recipe {recipe_id: sim.r1_id})
                MATCH (r2:Recipe {recipe_id: sim.r2_id})
                MERGE (r1)-[s:SIMILAR_RECIPE]->(r2)
                SET s.score = sim.score,
                    s.similarity_type = 'collaborative',
                    s.updated_at = datetime()
                """
                session.run(q_create, sims=batch)
                print(f"  [OK] Created batch {i//batch_size + 1}: {len(batch)} relationships", flush=True)
            
            print(f"  [OK] Created {len(top_similarities)} SIMILAR_RECIPE relationships (top {top_k} per recipe)\n")
        else:
            print("  [WARNING] No similarities found\n")


def build_content_similarity(driver, session_kwargs, similarity_threshold: float = 0.3,
                             limit_recipes: int = None, top_by_interactions: bool = False,
                             cleanup_old: bool = False):
    """
    PASS2.5: Tính content similarity giữa recipes dựa trên TF-IDF vectors và tạo SIMILAR_RECIPE relationships
    
    Args:
        similarity_threshold: Threshold cho similarity (default: 0.3 - thấp hơn nutrition vì content có nhiều terms)
        limit_recipes: Giới hạn số recipes để tính (None = tất cả)
        top_by_interactions: Nếu True, chỉ lấy top recipes theo số interactions
        cleanup_old: Nếu True, xóa SIMILAR_RECIPE cũ trước khi tính lại (default: False - giữ lại relationships cũ)
    """
    print(f"[PASS2.5] Computing content-based recipe similarity (threshold={similarity_threshold})...")
    
    # Cảnh báo nếu threshold quá cao
    if similarity_threshold > 0.5:
        print(f"  ⚠️  WARNING: Threshold {similarity_threshold} có thể quá cao cho content-based similarity!")
        print(f"  💡 Content similarity thường thấp hơn (0.2-0.4). Hãy thử --content-threshold 0.3 nếu không tìm thấy similarities.")
    
    # Xóa SIMILAR_RECIPE cũ nếu cần
    if cleanup_old:
        print("  [2.5] Cleaning up old SIMILAR_RECIPE relationships...")
        with driver.session(**session_kwargs) as session:
            result = session.run("MATCH ()-[r:SIMILAR_RECIPE]->() DELETE r RETURN count(r) AS deleted").single()
            deleted_count = result["deleted"] if result else 0
            print(f"  [2.5] Deleted {deleted_count} old SIMILAR_RECIPE relationships")
    
    # Get recipes with text vectors
    with driver.session(**session_kwargs) as session:
        if top_by_interactions:
            # Lấy top recipes theo số interactions (weighted: like > rating > view)
            q_all = """
            MATCH (r:Recipe)
            WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
              AND size(r.text_terms) > 0
            OPTIONAL MATCH (u:User)-[iv:INTERACTED_WITH]->(r)
            WITH r, 
                 sum(CASE 
                     WHEN iv.event_type = 'like' OR iv.liked = true THEN 3
                     WHEN iv.event_type = 'rating' AND iv.rating IS NOT NULL THEN 2
                     WHEN iv.event_type = 'view' OR iv.view_count > 0 THEN 1
                     ELSE 0
                 END) AS weighted_interaction_count,
                 count(DISTINCT u) AS total_users
            ORDER BY weighted_interaction_count DESC, total_users DESC
            LIMIT $limit
            RETURN r.recipe_id AS rid
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all, limit=limit_recipes or 10000)]
        elif limit_recipes:
            # Lấy N recipes đầu tiên
            q_all = """
            MATCH (r:Recipe)
            WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
              AND size(r.text_terms) > 0
            RETURN r.recipe_id AS rid
            ORDER BY r.recipe_id
            LIMIT $limit
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all, limit=limit_recipes)]
        else:
            # Lấy tất cả
            q_all = """
            MATCH (r:Recipe)
            WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL
              AND size(r.text_terms) > 0
            RETURN r.recipe_id AS rid
            ORDER BY r.recipe_id
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all)]
        
        total_recipes = len(all_recipe_ids)
        print(f"  [2.5] Found {total_recipes} recipes with text vectors")
        if limit_recipes or top_by_interactions:
            print(f"  [2.5] ⚡ OPTIMIZED: Processing only {total_recipes} recipes (reduced from full dataset)")
    
    # Tính tổng số cặp cần xử lý (ước lượng)
    total_expected_pairs = total_recipes * (total_recipes - 1) // 2
    
    # Cảnh báo nếu quá nhiều pairs
    if total_expected_pairs > 100_000_000:  # Hơn 100 triệu pairs
        print(f"\n  ⚠️  CẢNH BÁO: Số lượng pairs quá lớn ({total_expected_pairs:,})!")
        print(f"  ⚠️  Điều này có thể gây ra lỗi 'Java heap space' (Neo4j hết bộ nhớ)")
        print(f"  💡 KHUYẾN NGHỊ: Sử dụng --limit-recipes để giới hạn số recipes")
        print(f"  💡 Ví dụ: --limit-recipes 5000 --top-by-interactions")
        print(f"  ⏸️  Đang tạm dừng 5 giây để bạn có thể hủy (Ctrl+C)...\n")
        time.sleep(5)
    
    # Process in batches to avoid memory issues
    # Giảm batch size nếu quá nhiều recipes để tránh memory issues
    if total_recipes > 20000:
        BATCH_SIZE = 100  # Giảm batch size
        MAX_PAIRS_PER_QUERY = 2000  # Giảm pairs per query
        print(f"  [2.5] ⚙️  Sử dụng batch size nhỏ hơn để tránh memory issues")
    else:
        BATCH_SIZE = 200
        MAX_PAIRS_PER_QUERY = 5000
    
    total_pairs = 0
    total_similarities = 0
    start_time = time.time()
    
    print(f"  [2.5] Estimated total pairs to process: {total_expected_pairs:,}")
    print(f"  [2.5] Batch size: {BATCH_SIZE}, Max pairs per query: {MAX_PAIRS_PER_QUERY}")
    
    for i in range(0, len(all_recipe_ids), BATCH_SIZE):
        batch1 = all_recipe_ids[i:i+BATCH_SIZE]
        
        for j in range(i, len(all_recipe_ids), BATCH_SIZE):
            batch2 = all_recipe_ids[j:j+BATCH_SIZE]
            
            # Create pairs (only upper triangle to avoid duplicates)
            pairs = []
            for r1_id in batch1:
                for r2_id in batch2:
                    if r1_id < r2_id:  # Only one direction
                        pairs.append({"r1_id": r1_id, "r2_id": r2_id})
            
            if not pairs:
                continue
            
            # Chia nhỏ pairs thành các chunk để tránh memory limit
            for chunk_start in range(0, len(pairs), MAX_PAIRS_PER_QUERY):
                pairs_chunk = pairs[chunk_start:chunk_start + MAX_PAIRS_PER_QUERY]
                total_pairs += len(pairs_chunk)
                
                # Compute similarities (enable debug for first batch only)
                with driver.session(**session_kwargs) as session:
                    debug_mode = (i == 0 and chunk_start == 0 and total_pairs == 0)  # Debug first chunk only
                    if debug_mode:
                        print(f"  [2.5] 🔍 DEBUG MODE: Analyzing first {len(pairs_chunk)} pairs...")
                    similarities = session.execute_read(compute_content_similarity_batch, pairs_chunk, similarity_threshold, debug=debug_mode)
                    if debug_mode:
                        print(f"  [2.5] 🔍 DEBUG: Found {len(similarities)} similarities above threshold")
                    
                    if similarities:
                        session.execute_write(create_similar_recipe_relationships, similarities)
                        total_similarities += len(similarities)
            
            # Progress logging với thời gian ước tính
            if total_pairs % 50000 == 0:
                elapsed = time.time() - start_time
                rate = total_pairs / elapsed if elapsed > 0 else 0
                remaining_pairs = total_expected_pairs - total_pairs
                eta_seconds = remaining_pairs / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                progress_pct = (total_pairs / total_expected_pairs * 100) if total_expected_pairs > 0 else 0
                print(f"  [2.5] Progress: {total_pairs:,}/{total_expected_pairs:,} pairs ({progress_pct:.1f}%), "
                      f"found {total_similarities:,} similarities, "
                      f"ETA: {eta_minutes:.1f} min...", flush=True)
    
    print(f"[PASS2.5] [OK] Created {total_similarities} SIMILAR_RECIPE relationships from {total_pairs} pairs.\n")




# =============== RECIPE CLASSIFICATION (Dietary Categories) ===============

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


def compute_and_store_recipe_classification(tx, recipe_id: str, nutrition_values: Dict[str, float]):
    """
    Tính toán và lưu classification flags vào Recipe node.
    
    Args:
        recipe_id: Recipe ID
        nutrition_values: Dict với nutrition values (per serving)
            - total_fat (g)
            - total_carbohydrate (g)
            - protein (g)
            - saturated_fat (g)
            - total_sugars (g)
            - dietary_fiber (g)
            - sodium (mg)
            - cholesterol (mg)
    """
    # Classify recipe
    classification = classify_recipe(nutrition_values)
    
    # Update Recipe node với classification flags
    q = """
    MATCH (r:Recipe {recipe_id: $rid})
    SET r.is_low_carb = $is_low_carb,
        r.is_high_protein = $is_high_protein,
        r.is_keto = $is_keto,
        r.is_low_fat = $is_low_fat
    """
    tx.run(q,
           rid=recipe_id,
           is_low_carb=classification.get("low_carb", False),
           is_high_protein=classification.get("high_protein", False),
           is_keto=classification.get("keto", False),
           is_low_fat=classification.get("low_fat", False))

# Mapping từ nutrition_id sang property name và display name
NUTRITION_PROPERTY_MAP = {
    "calories": ("nutrition_calories", "Calories"),
    "total_fat": ("nutrition_total_fat", "Total Fat"),
    "saturated_fat": ("nutrition_saturated_fat", "Saturated Fat"),
    "sodium": ("nutrition_sodium", "Sodium"),
    "protein": ("nutrition_protein", "Protein"),
    "total_sugars": ("nutrition_total_sugars", "Total Sugars"),
    "total_carbohydrate": ("nutrition_total_carbohydrate", "Total Carbohydrate"),
    # Additional nutrients
    "cholesterol": ("nutrition_cholesterol", "Cholesterol"),
    "dietary_fiber": ("nutrition_dietary_fiber", "Dietary Fiber"),
    "vitamin_c": ("nutrition_vitamin_c", "Vitamin C"),
    "calcium": ("nutrition_calcium", "Calcium"),
    "iron": ("nutrition_iron", "Iron"),
    "potassium": ("nutrition_potassium", "Potassium"),
    # Legacy fields (mapped to new names)
    "fat": ("nutrition_total_fat", "Fat"),  # Legacy, maps to total_fat
    "carbohydrate": ("nutrition_total_carbohydrate", "Carbohydrate"),  # Legacy, maps to total_carbohydrate
    "fiber": ("nutrition_dietary_fiber", "Fiber"),  # Legacy, maps to dietary_fiber
    "sugar": ("nutrition_total_sugars", "Sugar"),  # Legacy, maps to total_sugars
}

# Helper để lấy property name từ nutrition_id
def get_nutrition_property(nutrition_id: str) -> str:
    """Get Recipe property name for a nutrition_id"""
    return NUTRITION_PROPERTY_MAP.get(nutrition_id, (f"nutrition_{nutrition_id}", nutrition_id.title()))[0]

# Helper để lấy display name từ nutrition_id
def get_nutrition_name(nutrition_id: str) -> str:
    """Get display name for a nutrition_id"""
    return NUTRITION_PROPERTY_MAP.get(nutrition_id, (f"nutrition_{nutrition_id}", nutrition_id.title()))[1]


def discover_all_nutrition_properties(tx):
    """PASS4.1.0: Tự động phát hiện tất cả nutrition properties có trong Recipe nodes"""
    q = """
    MATCH (r:Recipe)
    WHERE r.nutrition_calories IS NOT NULL OR r.nutrition_protein IS NOT NULL
    WITH keys(r) AS props
    UNWIND props AS prop
    WITH prop
    WHERE prop STARTS WITH 'nutrition_'
    WITH DISTINCT prop AS nutrition_prop
    ORDER BY nutrition_prop
    RETURN collect(nutrition_prop) AS all_nutrition_props
    """
    result = tx.run(q).single()
    if result:
        all_props = result.get("all_nutrition_props", [])
        # Convert property names to nutrition_ids
        nutrition_ids = []
        for prop in all_props:
            # nutrition_calories -> calories
            # nutrition_total_fat -> total_fat
            nut_id = prop.replace("nutrition_", "")
            # Skip legacy duplicates (we'll use the new names)
            if nut_id not in ["fat", "carbohydrate", "fiber", "sugar"]:
                nutrition_ids.append(nut_id)
        return nutrition_ids
    return []


def compute_nutrition_stats(tx, nutrition_ids: List[str]):
    """PASS4.1.1: Tính min, max, mean cho mỗi nutrition component"""
    stats = {}
    for nut_id in nutrition_ids:
        prop = get_nutrition_property(nut_id)
        q = f"""
        MATCH (r:Recipe)
        WHERE r.{prop} IS NOT NULL
        WITH toFloatOrNull(r.{prop}) AS val
        WHERE val IS NOT NULL
        RETURN 
            min(val) AS min_val,
            max(val) AS max_val,
            avg(val) AS mean_val,
            count(val) AS count_val
        """
        result = tx.run(q).single()
        if result and result["min_val"] is not None:
            stats[nut_id] = {
                "min": float(result["min_val"]),
                "max": float(result["max_val"]),
                "mean": float(result["mean_val"]),
                "count": int(result["count_val"])
            }
    return stats


def create_nutrition_nodes(tx, stats: Dict):
    """PASS4.1.2: Tạo Nutrition nodes với statistics"""
    for nut_id, stat in stats.items():
        name = get_nutrition_name(nut_id)
        q = """
        MERGE (n:Nutrition {nutrition_id: $nut_id})
        SET n.nutrition_name = $name,
            n.min_value = $min_val,
            n.max_value = $max_val,
            n.mean_value = $mean_val,
            n.total_recipes = $count
        """
        tx.run(q, 
               nut_id=nut_id,
               name=name,
               min_val=stat["min"],
               max_val=stat["max"],
               mean_val=stat["mean"],
               count=stat["count"])


def create_has_nutrition_relationships(tx, recipe_id: str, nutrition_values: Dict[str, float], stats: Dict):
    """PASS4.1.3: Tạo HAS_NUTRITION relationships với original và normalized values cho TẤT CẢ nutrition"""
    for nut_id in nutrition_values.keys():
        if nutrition_values[nut_id] is None:
            continue
        if nut_id not in stats:
            continue
        
        original_value = nutrition_values[nut_id]
        min_val = stats[nut_id]["min"]
        max_val = stats[nut_id]["max"]
        
        # Normalize: (value - min) / (max - min)
        if max_val > min_val:
            normalized_value = (original_value - min_val) / (max_val - min_val)
        else:
            normalized_value = 0.0
        
        q = """
        MATCH (r:Recipe {recipe_id: $rid})
        MATCH (n:Nutrition {nutrition_id: $nut_id})
        MERGE (r)-[rel:HAS_NUTRITION]->(n)
        SET rel.original_value = $orig_val,
            rel.normalized_value = $norm_val
        """
        tx.run(q, 
               rid=recipe_id,
               nut_id=nut_id,
               orig_val=original_value,
               norm_val=normalized_value)


def build_nutrition_components(driver, session_kwargs):
    """PASS4.1: Tạo Nutrition nodes và HAS_NUTRITION relationships cho TẤT CẢ nutrition"""
    print("\n[PASS4.1] Building Nutrition nodes and HAS_NUTRITION relationships...")
    
    with driver.session(**session_kwargs) as session:
        # Step 0: Discover all nutrition properties
        print("  [4.1.0] Discovering all nutrition properties in Recipe nodes...")
        all_nutrition_ids = session.execute_read(discover_all_nutrition_properties)
        print(f"  [4.1.0] Found {len(all_nutrition_ids)} nutrition properties: {', '.join(all_nutrition_ids)}")
        
        if not all_nutrition_ids:
            print("  ⚠️ No nutrition properties found in Recipe nodes!")
            return
        
        # Step 1: Compute statistics for all nutrition
        print("  [4.1.1] Computing nutrition statistics for all nutrition properties...")
        stats = session.execute_read(compute_nutrition_stats, all_nutrition_ids)
        print(f"  [4.1.1] Found statistics for {len(stats)} nutrition components")
        for nut_id, stat in stats.items():
            print(f"    {nut_id}: min={stat['min']:.2f}, max={stat['max']:.2f}, mean={stat['mean']:.2f}, count={stat['count']}")
        
        # Step 2: Create Nutrition nodes for all
        print("  [4.1.2] Creating Nutrition nodes for all nutrition properties...")
        session.execute_write(create_nutrition_nodes, stats)
        print(f"  [4.1.2] Created {len(stats)} Nutrition nodes")
        
        # Step 3: Create HAS_NUTRITION relationships for all
        print("  [4.1.3] Creating HAS_NUTRITION relationships for all nutrition...")
        # Get all nutrition property names
        nutrition_properties = [get_nutrition_property(nut_id) for nut_id in all_nutrition_ids]
        
        skip, processed = 0, 0
        while True:
            rows = session.execute_read(fetch_recipes_with_nutrition, skip, DEFAULT_BATCH, nutrition_properties)
            if not rows:
                break
            
            for row in rows:
                recipe_id = row["rid"]
                # Build nutrition_values dict from row data
                nutrition_values = {}
                for nut_id in all_nutrition_ids:
                    alias = nut_id  # nutrition_calories -> calories
                    value = row.get(alias)
                    if value is not None:
                        nutrition_values[nut_id] = value
                
                if nutrition_values:
                    session.execute_write(create_has_nutrition_relationships, recipe_id, nutrition_values, stats)
                    # Compute and store classification flags (PASS4.1.4)
                    session.execute_write(compute_and_store_recipe_classification, recipe_id, nutrition_values)
                    processed += 1
            
            skip += DEFAULT_BATCH
            if processed % 1000 == 0:
                print(f"  [4.1.3] Processed {processed} recipes...", flush=True)
        
        print(f"  [4.1.3] Created HAS_NUTRITION relationships for {processed} recipes")
    
        # Step 4: Compute and store classification flags (PASS4.1.4)
        print("  [4.1.4] Computing and storing recipe classification flags...")
        # Classification flags đã được tính trong Step 3 (compute_and_store_recipe_classification)
        print(f"  [4.1.4] Stored classification flags for {processed} recipes")
    
    print("[PASS4.1] [OK] Nutrition nodes, relationships, and classification flags completed.\n")




# =============== UTILITIES ===============
def compute_tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    # Filter: bỏ số, chỉ lấy chữ (tokens có ít nhất 1 chữ cái)
    tokens_filtered = [t for t in tokens if any(c.isalpha() for c in t)]
    tf = Counter(tokens_filtered)
    if not tf:
        return {}
    L = len(tokens_filtered) or 1
    # Tính TF-IDF: chỉ giữ tokens có trong idf dictionary
    vec = {}
    for t, c in tf.items():
        if t in idf:  # Chỉ tính cho tokens có trong IDF dictionary
            vec[t] = (c / L) * idf[t]
    if not vec:
        return {}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {t: v / norm for t, v in vec.items()}


def get_idf_cache_path():
    """Lấy đường dẫn file cache IDF statistics"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(script_dir, "idf_statistics_cache.json")


def save_idf_statistics_to_db(driver, session_kwargs, text_idf: Dict[str, float], ing_idf: Dict[str, float], total_docs: int, df_ing: Dict[str, int]):
    """Lưu IDF statistics vào database (chỉ lưu metadata, không lưu toàn bộ dictionary)"""
    with driver.session(**session_kwargs) as session:
        # Chỉ lưu metadata vào database (total_docs, counts)
        # Không lưu toàn bộ text_idf/ing_idf vì quá lớn
        q = """
        MERGE (m:Metadata {key: 'idf_statistics'})
        SET m.total_docs = $total_docs,
            m.text_terms_count = $text_terms_count,
            m.ingredients_count = $ingredients_count,
            m.updated_at = datetime()
        """
        try:
            session.run(q, 
                       total_docs=total_docs,
                       text_terms_count=len(text_idf),
                       ingredients_count=len(ing_idf))
        except Exception as e:
            print(f"[IDF] ⚠️  Failed to save metadata to DB: {e}")


def save_idf_statistics_to_json(driver, session_kwargs, text_idf: Dict[str, float], ing_idf: Dict[str, float], total_docs: int, df_ing: Dict[str, int]):
    """Lưu IDF statistics vào file JSON để tái sử dụng"""
    cache_path = get_idf_cache_path()
    cache_data = {
        "text_idf": text_idf,
        "ing_idf": ing_idf,
        "total_docs": total_docs,
        "df_ing": dict(df_ing) if isinstance(df_ing, Counter) else df_ing
    }
    try:
        with open(cache_path, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[IDF] [OK] Cache saved to {cache_path}")
    except Exception as e:
        print(f"[IDF] ⚠️  Failed to save cache to JSON: {e}")


def save_idf_statistics(driver, session_kwargs, text_idf: Dict[str, float], ing_idf: Dict[str, float], total_docs: int, df_ing: Dict[str, int]):
    """Lưu IDF statistics vào cả database (metadata) và file JSON"""
    save_idf_statistics_to_db(driver, session_kwargs, text_idf, ing_idf, total_docs, df_ing)
    save_idf_statistics_to_json(driver, session_kwargs, text_idf, ing_idf, total_docs, df_ing)


def load_idf_statistics_from_db(driver, session_kwargs):
    """Kiểm tra xem database có metadata về IDF statistics không (chỉ kiểm tra, không load toàn bộ)"""
    with driver.session(**session_kwargs) as session:
        q = """
        MATCH (m:Metadata {key: 'idf_statistics'})
        RETURN m.total_docs AS total_docs,
               m.text_terms_count AS text_terms_count,
               m.ingredients_count AS ingredients_count
        """
        result = session.run(q).single()
        if result and result["total_docs"]:
            # Database có metadata, nhưng không có toàn bộ dictionary
            # Trả về True để báo rằng có trong DB, nhưng cần load từ JSON
            return True
    return False


def load_idf_statistics_from_json():
    """Load IDF statistics từ file JSON nếu có"""
    cache_path = get_idf_cache_path()
    if not os.path.exists(cache_path):
        return None, None, None, None
    
    try:
        with open(cache_path, 'r', encoding='utf-8') as f:
            cache_data = json.load(f)
        
        if cache_data and cache_data.get("text_idf") and cache_data.get("ing_idf"):
            return (
                cache_data["text_idf"],
                cache_data["ing_idf"],
                cache_data["total_docs"],
                cache_data.get("df_ing", {})
            )
    except Exception as e:
        print(f"[IDF] ⚠️  Failed to load cache from JSON: {e}")
    
    return None, None, None, None


def load_idf_statistics(driver, session_kwargs):
    """Load IDF statistics: ưu tiên từ database (nếu có metadata), sau đó từ JSON"""
    # Kiểm tra database có metadata không
    has_db_metadata = load_idf_statistics_from_db(driver, session_kwargs)
    
    if has_db_metadata:
        # Database có metadata, thử load từ JSON
        print("  🔍 Found IDF metadata in database, loading from JSON cache...")
        result = load_idf_statistics_from_json()
        if result[0] is not None:
            # Filter số từ IDF dictionary khi load
            text_idf, ing_idf, total_docs, df_ing = result
            text_idf_filtered = {k: v for k, v in text_idf.items() if any(c.isalpha() for c in k)}
            print(f"  [OK] Loaded IDF from JSON cache: {result[2]} docs, {len(text_idf)} text terms (filtered to {len(text_idf_filtered)} without numbers), {len(ing_idf)} ingredients")
            return text_idf_filtered, ing_idf, total_docs, df_ing
    
    # Nếu không có trong DB hoặc không load được từ JSON, thử load từ JSON trực tiếp
    print("  🔍 Checking JSON cache...")
    result = load_idf_statistics_from_json()
    if result[0] is not None:
        # Filter số từ IDF dictionary khi load
        text_idf, ing_idf, total_docs, df_ing = result
        text_idf_filtered = {k: v for k, v in text_idf.items() if any(c.isalpha() for c in k)}
        print(f"  ✅ Loaded IDF from JSON cache: {result[2]} docs, {len(text_idf)} text terms (filtered to {len(text_idf_filtered)} without numbers), {len(ing_idf)} ingredients")
        return text_idf_filtered, ing_idf, total_docs, df_ing
    
    return None, None, None, None


def compute_idf_statistics(driver, session_kwargs, verbose: bool = True, save_cache: bool = True):
    """
    Tính toán IDF statistics từ database (logic của PASS1).
    Returns: (text_idf, ing_idf, total_docs, df_ing)
    """
    df_text, df_ing = Counter(), Counter()
    total_docs = 0
    
    if verbose:
        print("[IDF] Computing DF for text tokens & ingredient IDs ...")
    
    with driver.session(**session_kwargs) as session:
        skip, pages = 0, 0
        while True:
            rows = session.execute_read(fetch_recipes_paged, skip, DEFAULT_BATCH)
            if not rows:
                break
            for row in rows:
                cuisine_str = " ".join(row["cuisine"]) if isinstance(row["cuisine"], list) else str(row["cuisine"] or "")
                text = " ".join([str(row["title"] or ""), " ".join(row["tags"] or []), str(row["instr"] or "")[:500], cuisine_str])
                tokens = normalize_text(text)
                # Filter: bỏ số, chỉ lấy chữ (tokens có ít nhất 1 chữ cái)
                tokens_filtered = [t for t in tokens if any(c.isalpha() for c in t)]
                for t in set(tokens_filtered):
                    df_text[t] += 1
                # Filter out None/null values từ ingredient IDs
                ing_ids = [iid for iid in (row["ingIds"] or []) if iid is not None]
                for iid in set(ing_ids):
                    df_ing[iid] += 1
                total_docs += 1
            skip += DEFAULT_BATCH
            pages += 1
            if verbose:
                print(f"[IDF] page={pages}, processed={skip} docs ...", flush=True)
    
    text_idf = {t: math.log(1.0 + (total_docs / max(df_text[t], 1))) for t in df_text}
    ing_idf = {t: math.log(1.0 + (total_docs / max(df_ing[t], 1))) for t in df_ing}
    
    if verbose:
        print(f"[IDF] Total docs = {total_docs}")
        print(f"[IDF] Unique text terms = {len(text_idf)}, unique ingredients = {len(ing_idf)}")
    
    # Lưu cache vào file JSON
    if save_cache:
        save_idf_statistics(driver, session_kwargs, text_idf, ing_idf, total_docs, df_ing)
    
    return text_idf, ing_idf, total_docs, df_ing


def cleanup_old_data(driver, session_kwargs):
    print("\n🧹 Cleaning up old TF-IDF & similarity data ...")
    with driver.session(**session_kwargs) as session:
        session.run("""
        MATCH ()-[r:SIMILAR_TO|SIMILAR_RECIPE]->() DELETE r
        """)
        # Chỉ xoá các quan hệ POPULAR_IN cũ, giữ nguyên Group và BELONGS_TO (được tạo từ survey)
        session.run("MATCH (:Group)-[r:POPULAR_IN]->(:Recipe) DELETE r")
        # Note: Nutrition nodes and HAS_NUTRITION relationships are no longer created (PASS4.1 removed)
    print("[OK] Cleanup done.\n")


# =============== PIPELINE MAIN ===============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute features for recommendation system")
    parser.add_argument(
        "--pass",
        dest="pass_num",
        type=str,
        choices=["1", "2", "2.5", "3", "all"],
        default="all",
        help="Which pass to run: 1, 2, 2.5, 3, or all (default: all)"
    )
    parser.add_argument(
        "--content-threshold",
        type=float,
        default=0.3,
        help="Similarity threshold for PASS2.5 (content-based recipe similarity, default: 0.3)"
    )
    parser.add_argument(
        "--limit-recipes",
        type=int,
        default=None,
        help="Limit number of recipes for PASS2.5 (for faster processing, e.g., 10000)"
    )
    parser.add_argument(
        "--top-by-interactions",
        action="store_true",
        help="For PASS2.5, only process top recipes by interaction count (use with --limit-recipes)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old data before running (default: skip cleanup)"
    )
    parser.add_argument(
        "--only-missing",
        action="store_true",
        help="For PASS2, only update recipes that don't have text_terms/text_weights yet (default: update all)"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Force recalculate TF-IDF for all recipes even if they already have text_terms/text_weights"
    )
    parser.add_argument(
        "--min-popular-score",
        type=int,
        default=5,
        help="Minimum interaction count to create POPULAR_IN relationship in PASS3 (default: 5). Only recipes with at least this many interactions in a group will be marked as popular."
    )
    
    args = parser.parse_args()
    
    driver = GraphDatabase.driver(
        DEFAULT_URI,
        auth=(DEFAULT_USER, DEFAULT_PASS),
        connection_timeout=120,
        max_connection_lifetime=3600,
        max_transaction_retry_time=30,
    )
    session_kwargs = {"database": DEFAULT_DB}

    if args.cleanup:
        cleanup_old_data(driver, session_kwargs)
    
    pass_num = args.pass_num

    # -------- PASS1 --------
    df_text, df_ing = Counter(), Counter()
    total_docs = 0
    text_idf = {}
    ing_idf = {}
    
    if pass_num in ["1", "all"]:
        print("\n[PASS1] Running PASS1...\n")
        text_idf, ing_idf, total_docs, df_ing = compute_idf_statistics(driver, session_kwargs, verbose=True, save_cache=True)
        print(f"[PASS1] [OK] Completed: {total_docs} docs, {len(text_idf)} text terms, {len(ing_idf)} ingredients")

    # -------- PASS2 --------
    if pass_num in ["2", "all"]:
        if pass_num == "2":
            print("\n[PASS2] Running PASS2...\n")
        print("\n[PASS2] Computing TF-IDF & updating Neo4j ...")
        
        # Check status of existing text_vectors
        only_missing = getattr(args, 'only_missing', False)
        force = getattr(args, 'force', False)
        skip_pass2 = False
        
        # Luôn check status để quyết định có cần tính lại không
        total_recipes, recipes_with_vectors = check_text_vectors_status(driver, session_kwargs)
        print(f"  📊 Status: {recipes_with_vectors}/{total_recipes} recipes already have text_terms/text_weights")
        
        if recipes_with_vectors == total_recipes and not force:
            print("  [OK] All recipes already have text_vectors. Skipping TF-IDF computation.")
            print("  💡 Tip: Use --force to recalculate anyway")
            skip_pass2 = True
        elif force:
            print(f"  🔄 Force mode: Will recalculate TF-IDF for ALL {total_recipes} recipes")
        elif only_missing:
            print(f"  ⚡ Will only update {total_recipes - recipes_with_vectors} missing recipes")
        else:
            print(f"  ⚠️  Will recalculate TF-IDF for ALL {total_recipes} recipes (use --only-missing to skip existing)")
        
        if not skip_pass2:
            # PASS2 tự động tính IDF nếu chưa có (không cần PASS1)
            if not text_idf or not ing_idf:
                # Thử load từ cache trước
                print("  🔍 Checking for cached IDF statistics...")
                cached_text_idf, cached_ing_idf, cached_total_docs, cached_df_ing = load_idf_statistics(driver, session_kwargs)
                
                if cached_text_idf and cached_ing_idf:
                    print(f"  [OK] Found cached IDF: {cached_total_docs} docs, {len(cached_text_idf)} text terms, {len(cached_ing_idf)} ingredients")
                    text_idf, ing_idf, total_docs, df_ing = cached_text_idf, cached_ing_idf, cached_total_docs, cached_df_ing
                else:
                    print("  ⚠️  IDF statistics not found. Computing IDF automatically...")
                    print("  ⏳ This may take a while for large datasets...")
                    text_idf, ing_idf, total_docs, df_ing = compute_idf_statistics(driver, session_kwargs, verbose=False, save_cache=True)
                    print(f"  [OK] IDF computed: {total_docs} docs, {len(text_idf)} text terms, {len(ing_idf)} ingredients")
            
            # Choose which fetch function to use
            fetch_func = fetch_recipes_paged_missing if only_missing else fetch_recipes_paged
            
            # Đếm tổng số recipes cần xử lý
            with driver.session(**session_kwargs) as session:
                if only_missing:
                    total_recipes, recipes_with_vectors = check_text_vectors_status(driver, session_kwargs)
                    total_to_process = total_recipes - recipes_with_vectors
                else:
                    count_q = "MATCH (r:Recipe) RETURN count(r) AS total"
                    total_to_process = session.run(count_q).single()["total"]
            
            print(f"  📊 Total recipes to process: {total_to_process}")
            print(f"  ⚙️  Batch size: {DEFAULT_BATCH}")
            print(f"  [Start] Starting processing...\n")
            
            start_time = time.time()
            with driver.session(**session_kwargs) as session:
                skip, updated = 0, 0
                batch_num = 0
                while True:
                    batch_start = time.time()
                    rows = session.execute_read(fetch_func, skip, DEFAULT_BATCH)
                    if not rows:
                        break
                    
                    batch_num += 1
                    batch_size = len(rows)
                    
                    # Chuẩn bị batch updates
                    recipe_updates = []
                    ing_updates = []
                    
                    # Xử lý tất cả recipes trong batch (tính toán)
                    for idx, row in enumerate(rows):
                        rid = row["rid"]
                        cuisine_str = " ".join(row["cuisine"]) if isinstance(row["cuisine"], list) else str(row["cuisine"] or "")
                        text = " ".join([str(row["title"] or ""), " ".join(row["tags"] or []), str(row["instr"] or "")[:500], cuisine_str])
                        tokens = normalize_text(text)
                        # Filter số ở đây để đảm bảo không có số trong tokens
                        tokens = [t for t in tokens if any(c.isalpha() for c in t)]
                        tfidf = compute_tfidf(tokens, text_idf)
                        
                        # Chuẩn bị data cho batch update
                        terms = list(tfidf.keys())[:TOP_TERMS_PER_RECIPE]
                        weights = [float(tfidf[t]) for t in terms]
                        recipe_updates.append({
                            "rid": rid,
                            "terms": terms,
                            "weights": weights
                        })
                        
                        # Chuẩn bị ingredient weights
                        ing_set = list({x for x in (row["ingIds"] or []) if x})
                        if ing_set:
                            pairs = [{"iid": iid, "w": float(ing_idf.get(iid, 0.0))} for iid in ing_set]
                            ing_updates.append({
                                "rid": rid,
                                "pairs": pairs
                            })
                    
                    # Batch update tất cả recipes trong một transaction
                    if recipe_updates:
                        session.execute_write(store_recipe_vectors_batch, recipe_updates)
                    
                    # Batch update tất cả ingredient weights trong một transaction
                    if ing_updates:
                        session.execute_write(set_ing_edge_weights_batch, ing_updates)
                    
                    updated += batch_size
                    
                    batch_time = time.time() - batch_start
                    skip += DEFAULT_BATCH
                    
                    # Log chi tiết mỗi batch
                    elapsed = time.time() - start_time
                    rate = updated / elapsed if elapsed > 0 else 0
                    remaining = (total_to_process - updated) / rate if rate > 0 else 0
                    percent = (updated / total_to_process * 100) if total_to_process > 0 else 0
                    
                    print(f"[PASS2] Batch {batch_num}: processed {batch_size} recipes in {batch_time:.2f}s | "
                          f"Total: {updated}/{total_to_process} ({percent:.1f}%) | "
                          f"Rate: {rate:.1f} recipes/s | "
                          f"ETA: {remaining/60:.1f} min", flush=True)

            # Store ingredient stats và build user profile trong session mới
            with driver.session(**session_kwargs) as session:
                if df_ing:
                    stats = [{"iid": iid, "df": int(df_ing[iid]), "idf": float(ing_idf.get(iid, 0.0))} for iid in df_ing.keys()]
                    session.execute_write(store_ingredient_stats, total_docs, stats)

                print("[PASS2] Building user profile vectors ...")
                session.execute_write(build_user_profile)

    # -------- PASS2.5: Recipe Similarity from LIKES --------
    if pass_num in ["2.5", "all"]:
        if pass_num == "2.5":
            print("\n[PASS2.5] Running PASS2.5...\n")
        print("[PASS2.5] Building SIMILAR_RECIPE relationships from LIKES (collaborative filtering)...")
        
        # Use new function based on LIKES (Jaccard similarity)
        build_similar_recipes_from_likes(driver, session_kwargs, top_k=10)

    # -------- PASS3 --------
    if pass_num in ["3", "all"]:
        if pass_num == "3":
            print("\n[PASS3] Running PASS3...\n")
        print("[PASS3] Building hybrid similarity graph (SIMILAR_USER + POPULAR_IN)...")
        min_popular_score = getattr(args, 'min_popular_score', 2)
        # build_hybrid_similarity now uses build_similar_users_from_likes internally
        build_hybrid_similarity(driver, min_popular_score=min_popular_score)
    
    driver.close()
    
    if pass_num == "all":
        print("\n[OK] DONE: FULL PIPELINE (PASS1-3) completed successfully!")
    else:
        print(f"\n[OK] DONE: PASS{pass_num} completed successfully!")
