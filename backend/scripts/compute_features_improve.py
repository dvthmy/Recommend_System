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
    WITH r, collect(DISTINCT i.ingredient_id) AS ingIds
    RETURN r.recipe_id AS rid,
           coalesce(r.title,'') AS title,
           coalesce(r.tags, []) AS tags,
           coalesce(r.instructions,'') AS instr,
           coalesce(r.cuisine, []) AS cuisine,
           ingIds AS ingIds
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



def build_hybrid_similarity(driver, w_cf: float = 0.5, w_demo: float = 0.2):
    """
    Build collaborative graph components:
      - User–User similarity (CF + demographic)
      - Group aggregation (POPULAR_IN)
      - Recipe–Recipe similarity (collaborative, based on user co-interaction)
    """
    session_kwargs = {"database": DEFAULT_DB}

    # ---- Step 1: User–User Similarity ----
    print("➡️  Building user–user similarity in batches (safe mode)...")

    BATCH_SIZE = 50
    MIN_SCORE = 0.2

    with driver.session(**session_kwargs) as session:
        session.run("MATCH (u:User) REMOVE u.temp_batch")

        session.run("""
        MATCH (u:User)
        WHERE size(u.user_terms) > 100
        SET u.user_terms = u.user_terms[0..100],
            u.user_weights = u.user_weights[0..100]
        """)

        session.run("""
        MATCH (u:User)
        WITH u ORDER BY elementId(u)
        WITH collect(u) AS users
        UNWIND range(0, toInteger(ceil(size(users)*1.0 / $batch_size)) - 1) AS i
        UNWIND users[toInteger(i*$batch_size)..toInteger((i+1)*$batch_size - 1)] AS u
        SET u.temp_batch = i
        """, {"batch_size": BATCH_SIZE})

        batches = [
            record["b"]
            for record in session.run(
                "MATCH (u:User) WHERE u.temp_batch IS NOT NULL RETURN DISTINCT u.temp_batch AS b ORDER BY b"
            )
        ]
        print(f"   ⚙️ Total batches = {len(batches)} (batch size={BATCH_SIZE})")

    for b in batches:
        if b is None:
            continue
        print(f"   🔹 Processing batch {b} ...", flush=True)
        t_batch = time.time()

        q_batch = f"""
        MATCH (u1:User {{temp_batch:{b}}})
        WHERE u1.user_terms IS NOT NULL AND size(u1.user_terms) > 0
        MATCH (u2:User)
        WHERE elementId(u2) > elementId(u1)
          AND u2.user_terms IS NOT NULL AND size(u2.user_terms) > 0
          AND (u1.gender = u2.gender OR u1.age_group = u2.age_group)
        WITH u1, u2, apoc.coll.intersection(u1.user_terms, u2.user_terms) AS common_terms
        WHERE size(common_terms) > 0
        WITH u1, u2, common_terms,
             [x IN range(0, size(u1.user_terms)-1) | [u1.user_terms[x], u1.user_weights[x]]] AS vec1,
             [x IN range(0, size(u2.user_terms)-1) | [u2.user_terms[x], u2.user_weights[x]]] AS vec2
        WITH u1, u2,
             reduce(dot=0.0, term IN common_terms |
                 dot + coalesce([v IN vec1 WHERE v[0]=term][0][1],0.0) * coalesce([v IN vec2 WHERE v[0]=term][0][1],0.0)
             ) AS dot,
             sqrt(reduce(sum=0.0, v IN vec1 | sum + v[1]*v[1])) AS norm1,
             sqrt(reduce(sum=0.0, v IN vec2 | sum + v[1]*v[1])) AS norm2
        WITH u1, u2,
             CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS s_cf
        WHERE s_cf > 0.05
        WITH u1, u2, s_cf,
             (CASE WHEN u1.gender = u2.gender THEN 1 ELSE 0 END +
              CASE WHEN u1.age_group = u2.age_group THEN 1 ELSE 0 END)/2.0 AS s_demo
        WITH u1, u2, s_cf, s_demo,
             {w_cf}*s_cf + {w_demo}*s_demo AS score
        WHERE score > {MIN_SCORE}
        MERGE (u1)-[s:SIMILAR_USER]->(u2)
        SET s.s_cf = s_cf, s.s_demo = s_demo, s.score = score, s.updated_at = datetime()
        """

        try:
            with driver.session(**session_kwargs) as batch_sess:
                batch_sess.execute_write(lambda tx: tx.run(q_batch))
            print(f"   ✅ Batch {b} done in {time.time() - t_batch:.2f}s", flush=True)
        except Exception as e:
            print(f"   ⚠️ Batch {b} failed: {e}")

    with driver.session(**session_kwargs) as session:
        session.run("MATCH (u:User) REMOVE u.temp_batch")

    print("✅ User–User similarity done (SIMILAR_USER).\n")

    # ---- Step 2: Group POPULAR_IN ----
    print("➡️  Building demographic group aggregation...")
    with driver.session(**session_kwargs) as session:
        q_group = """
        MATCH (u:User)
        WHERE u.gender IS NOT NULL AND u.age_group IS NOT NULL
        MERGE (g:Group {gender:u.gender, age_group:u.age_group})
        MERGE (u)-[:BELONGS_TO]->(g)
        WITH g
        MATCH (g)<-[:BELONGS_TO]-(u)-[:INTERACTED_WITH]->(r)
        WITH g, r, count(*) AS freq
        MERGE (g)-[l:POPULAR_IN]->(r)
        SET l.score = freq, l.updated_at = datetime()
        """
        session.run(q_group)
    print("✅ Group aggregation built (POPULAR_IN)\n")

    # ---- Step 3: Collaborative Recipe Similarity ----
    print("➡️  Building collaborative SIMILAR_RECIPE based on user co-interactions...")

    q_collab = """
    MATCH (u:User)-[:INTERACTED_WITH]->(r1:Recipe)
    MATCH (u)-[:INTERACTED_WITH]->(r2:Recipe)
    WHERE r1 <> r2
    WITH r1, r2, count(*) AS c
    WITH r1, r2,
         toFloat(c) / sqrt(
             COUNT { (r1)<-[:INTERACTED_WITH]-(:User) } *
             COUNT { (r2)<-[:INTERACTED_WITH]-(:User) }
         ) AS sim
    WHERE sim >= $minSim
    WITH r1, r2, sim
    LIMIT $maxPairs
    MERGE (r1)-[s:SIMILAR_RECIPE]->(r2)
    SET s.score = sim,
        s.method = 'collab',
        s.updated_at = datetime()
    RETURN count(s) AS created
    """

    try:
        with driver.session(**session_kwargs) as session:
            result = session.run(q_collab, minSim=0.05, maxPairs=500000).data()
            count_rel = result[0]["created"] if result else 0
            print(f"✅ Created {count_rel} SIMILAR_RECIPE (collaborative user co-interaction)\n")
    except Exception as e:
        print(f"⚠️ Collaborative similarity failed: {e}")

    print("✅ Hybrid graph (user, group, recipe-collab) completed.\n")



# =============== UTILITIES ===============
def compute_tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf = Counter(tokens)
    if not tf:
        return {}
    L = len(tokens) or 1
    vec = {t: (c / L) * idf.get(t, 0.0) for t, c in tf.items()}
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    return {t: v / norm for t, v in vec.items()}


def cleanup_old_data(driver, session_kwargs):
    print("\n🧹 Cleaning up old TF-IDF & similarity data ...")
    with driver.session(**session_kwargs) as session:
        session.run("""
        MATCH ()-[r:SIMILAR_TO|SIMILAR_RECIPE|SIMILAR_USER]->() DELETE r
        """)
        session.run("MATCH (:Group)-[r:POPULAR_IN|LIKES]->(:Recipe) DELETE r")
        session.run("MATCH (:User)-[r:BELONGS_TO]->(:Group) DELETE r")
        session.run("MATCH (g:Group) DETACH DELETE g")
    print("✅ Cleanup done.\n")


# =============== PIPELINE MAIN ===============
if __name__ == "__main__":
    driver = GraphDatabase.driver(
        DEFAULT_URI,
        auth=(DEFAULT_USER, DEFAULT_PASS),
        connection_timeout=120,
        max_connection_lifetime=3600,
        max_transaction_retry_time=30,
    )
    session_kwargs = {"database": DEFAULT_DB}

    cleanup_old_data(driver, session_kwargs)
    print("\n🚀 Running FULL PIPELINE (PASS1 + PASS2 + PASS3)...\n")

    # -------- PASS1 --------
    print("[PASS1] Counting DF for text tokens & ingredient IDs ...")
    df_text, df_ing = Counter(), Counter()
    total_docs = 0

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
                for t in set(tokens):
                    df_text[t] += 1
                for iid in set(row["ingIds"] or []):
                    df_ing[iid] += 1
                total_docs += 1
            skip += DEFAULT_BATCH
            pages += 1
            print(f"[PASS1] page={pages}, processed={skip} docs ...", flush=True)

    text_idf = {t: math.log(1.0 + (total_docs / max(df_text[t], 1))) for t in df_text}
    ing_idf = {t: math.log(1.0 + (total_docs / max(df_ing[t], 1))) for t in df_ing}
    print(f"[PASS1] Total docs = {total_docs}")
    print(f"[PASS1] Unique text terms = {len(text_idf)}, unique ingredients = {len(ing_idf)}")

    # -------- PASS2 --------
    print("\n[PASS2] Computing TF-IDF & updating Neo4j ...")
    with driver.session(**session_kwargs) as session:
        skip, updated = 0, 0
        while True:
            rows = session.execute_read(fetch_recipes_paged, skip, DEFAULT_BATCH)
            if not rows:
                break
            for row in rows:
                rid = row["rid"]
                cuisine_str = " ".join(row["cuisine"]) if isinstance(row["cuisine"], list) else str(row["cuisine"] or "")
                text = " ".join([str(row["title"] or ""), " ".join(row["tags"] or []), str(row["instr"] or "")[:500], cuisine_str])
                tokens = normalize_text(text)
                tfidf = compute_tfidf(tokens, text_idf)
                session.execute_write(store_recipe_vectors, rid, tfidf)

                ing_set = list({x for x in (row["ingIds"] or []) if x})
                if ing_set:
                    pairs = [{"iid": iid, "w": float(ing_idf.get(iid, 0.0))} for iid in ing_set]
                    session.execute_write(set_ing_edge_weights, rid, pairs)

                updated += 1
            skip += DEFAULT_BATCH
            print(f"[PASS2] updated={updated}/{total_docs} recipes ...", flush=True)

        if df_ing:
            stats = [{"iid": iid, "df": int(df_ing[iid]), "idf": float(ing_idf.get(iid, 0.0))} for iid in df_ing.keys()]
            session.execute_write(store_ingredient_stats, total_docs, stats)

        print("[PASS2] Building user profile vectors ...")
        session.execute_write(build_user_profile)

    # -------- PASS3 --------
    print("[PASS3] Building hybrid similarity graph ...")
    build_hybrid_similarity(driver)
    driver.close()
    print("\n✅ DONE: FULL PIPELINE completed successfully!")
