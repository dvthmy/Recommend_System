#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Pipeline: Normalize text + compute IDF + compute TF-IDF + update Neo4j + Hybrid Graph + Nutrition
- PASS1: stream toàn bộ recipe → normalize → đếm DF (text & ingredient)
- Tính IDF cho text token và ingredient_id
- PASS2: stream lại → tính TF-IDF từng recipe → lưu r.text_terms/text_weights
         → gán rel.idf_weight cho HAS_INGREDIENT
- Lưu thống kê Ingredient (doc_freq, ing_idf, total_docs)
- Xây user profile vector
- PASS3: Xây hybrid similarity graph (content + behavior + demographic)
- PASS4: Nutrition features (NRKG)
  - PASS4.1: Tạo Nutrition nodes và HAS_NUTRITION relationships
  - PASS4.2: Tính nutrition similarity và tạo SIMILAR_NUTRITION relationships
  - PASS4.3: Tính user nutrition preferences
  - PASS4.4: (Tùy chọn) Tạo SIMILAR_USER relationships dựa trên nutrition
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
        # Sử dụng sẵn Group và BELONGS_TO (được tạo từ survey) để build POPULAR_IN
        q_group = """
        MATCH (g:Group)<-[:BELONGS_TO]-(u:User)-[:INTERACTED_WITH]->(r:Recipe)
        WITH g, r, count(*) AS freq
        MERGE (g)-[l:POPULAR_IN]->(r)
        SET l.score = freq, l.updated_at = datetime()
        """
        session.run(q_group)
    print("✅ Group aggregation built (POPULAR_IN)\n")

    # Note: SIMILAR_RECIPE removed - using SIMILAR_NUTRITION instead (PASS4.2)

    print("✅ Hybrid graph (user, group) completed.\n")


# =============== PASS4: NUTRITION FEATURES (NRKG) ===============

# 7 chất dinh dưỡng chính theo NRKG paper (dùng cho SIMILAR_NUTRITION)
CORE_NUTRITION_IDS = [
    "calories",
    "total_fat",
    "saturated_fat",
    "sodium",
    "protein",
    "total_sugars",
    "total_carbohydrate"
]


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
    
    print("[PASS4.1] ✅ Nutrition nodes, relationships, and classification flags completed.\n")


def compute_nutrition_similarity_batch(tx, recipe_pairs: List[Dict], threshold: float):
    """PASS4.2: Tính nutrition similarity cho một batch recipes - TỐI ƯU: tính tất cả trong một query"""
    if not recipe_pairs:
        return []
    
    # Tối ưu: tính tất cả cặp trong một query thay vì từng cặp
    q = """
    UNWIND $pairs AS pair
    MATCH (r1:Recipe {recipe_id: pair.r1_id})-[rel1:HAS_NUTRITION]->(n:Nutrition)
    MATCH (r2:Recipe {recipe_id: pair.r2_id})-[rel2:HAS_NUTRITION]->(n)
    WHERE n.nutrition_id IN $core_nutrition_ids
      AND rel1.normalized_value IS NOT NULL AND rel2.normalized_value IS NOT NULL
    WITH pair, n.nutrition_id AS nut_id, 
         rel1.normalized_value AS v1, 
         rel2.normalized_value AS v2
    ORDER BY pair.r1_id, pair.r2_id, nut_id
    WITH pair, collect(v1) AS vec1, collect(v2) AS vec2
    WHERE size(vec1) = 7 AND size(vec2) = 7
    WITH pair, vec1, vec2,
         reduce(dot=0.0, i IN range(0, 6) | dot + vec1[i] * vec2[i]) AS dot,
         sqrt(reduce(sum=0.0, v IN vec1 | sum + v*v)) AS norm1,
         sqrt(reduce(sum=0.0, v IN vec2 | sum + v*v)) AS norm2
    WITH pair,
         CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS similarity
    WHERE similarity > $threshold
    RETURN pair.r1_id AS r1_id, pair.r2_id AS r2_id, similarity
    """
        
    pairs_list = [{"r1_id": p["r1_id"], "r2_id": p["r2_id"]} for p in recipe_pairs]
    results = tx.run(q, pairs=pairs_list, threshold=threshold, core_nutrition_ids=CORE_NUTRITION_IDS)
    
    similarities = []
    for record in results:
            similarities.append({
            "r1_id": record["r1_id"],
            "r2_id": record["r2_id"],
            "similarity": float(record["similarity"])
            })
    
    return similarities


def create_similar_nutrition_relationships(tx, similarities: List[Dict]):
    """Tạo SIMILAR_NUTRITION relationships"""
    if not similarities:
        return
    
    q = """
    UNWIND $sims AS sim
    MATCH (r1:Recipe {recipe_id: sim.r1_id})
    MATCH (r2:Recipe {recipe_id: sim.r2_id})
    MERGE (r1)-[rel:SIMILAR_NUTRITION]->(r2)
    SET rel.similarity = sim.similarity,
        rel.updated_at = datetime()
    """
    tx.run(q, sims=similarities)


def build_nutrition_similarity(driver, session_kwargs, similarity_threshold: float = 0.8, 
                                limit_recipes: int = None, top_by_interactions: bool = False):
    """
    PASS4.2: Tính nutrition similarity và tạo SIMILAR_NUTRITION relationships
    
    Args:
        similarity_threshold: Threshold cho similarity (default: 0.8)
        limit_recipes: Giới hạn số recipes để tính (None = tất cả)
        top_by_interactions: Nếu True, chỉ lấy top recipes theo số interactions
    """
    print(f"[PASS4.2] Computing nutrition similarity (threshold={similarity_threshold})...")
    
    # Get recipes with nutrition data
    with driver.session(**session_kwargs) as session:
        if top_by_interactions:
            # Lấy top recipes theo số interactions
            q_all = """
            MATCH (r:Recipe)-[:HAS_NUTRITION]->(n:Nutrition {nutrition_id: 'calories'})
            OPTIONAL MATCH (u:User)-[:INTERACTED_WITH]->(r)
            WITH r, count(u) AS interaction_count
            ORDER BY interaction_count DESC
            LIMIT $limit
            RETURN r.recipe_id AS rid
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all, limit=limit_recipes or 10000)]
        elif limit_recipes:
            # Lấy N recipes đầu tiên
            q_all = """
            MATCH (r:Recipe)-[:HAS_NUTRITION]->(n:Nutrition {nutrition_id: 'calories'})
            RETURN r.recipe_id AS rid
            ORDER BY r.recipe_id
            LIMIT $limit
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all, limit=limit_recipes)]
        else:
            # Lấy tất cả
            q_all = """
            MATCH (r:Recipe)-[:HAS_NUTRITION]->(n:Nutrition {nutrition_id: 'calories'})
            RETURN r.recipe_id AS rid
            ORDER BY r.recipe_id
            """
            all_recipe_ids = [record["rid"] for record in session.run(q_all)]
        
        total_recipes = len(all_recipe_ids)
        print(f"  [4.2] Found {total_recipes} recipes with nutrition data")
        if limit_recipes or top_by_interactions:
            print(f"  [4.2] ⚡ OPTIMIZED: Processing only {total_recipes} recipes (reduced from full dataset)")
    
    # Process in batches to avoid memory issues
    # Giảm batch size để tránh memory limit của Neo4j
    BATCH_SIZE = 200  # Giảm xuống 200 để tránh memory issues
    MAX_PAIRS_PER_QUERY = 5000  # Giới hạn số pairs trong mỗi query
    total_pairs = 0
    total_similarities = 0
    start_time = time.time()
    
    # Tính tổng số cặp cần xử lý (ước lượng)
    total_expected_pairs = total_recipes * (total_recipes - 1) // 2
    print(f"  [4.2] Estimated total pairs to process: {total_expected_pairs:,}")
    print(f"  [4.2] Batch size: {BATCH_SIZE}, Max pairs per query: {MAX_PAIRS_PER_QUERY}")
    
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
            
            # Compute similarities
            with driver.session(**session_kwargs) as session:
                similarities = session.execute_read(compute_nutrition_similarity_batch, pairs_chunk, similarity_threshold)
                
                if similarities:
                    session.execute_write(create_similar_nutrition_relationships, similarities)
                    total_similarities += len(similarities)
            
            # Progress logging với thời gian ước tính
            if total_pairs % 50000 == 0 or total_pairs == len(pairs):
                elapsed = time.time() - start_time
                rate = total_pairs / elapsed if elapsed > 0 else 0
                remaining_pairs = total_expected_pairs - total_pairs
                eta_seconds = remaining_pairs / rate if rate > 0 else 0
                eta_minutes = eta_seconds / 60
                progress_pct = (total_pairs / total_expected_pairs * 100) if total_expected_pairs > 0 else 0
                print(f"  [4.2] Progress: {total_pairs:,}/{total_expected_pairs:,} pairs ({progress_pct:.1f}%), "
                      f"found {total_similarities:,} similarities, "
                      f"ETA: {eta_minutes:.1f} min...", flush=True)
    
    print(f"[PASS4.2] ✅ Created {total_similarities} SIMILAR_NUTRITION relationships from {total_pairs} pairs.\n")


def compute_user_nutrition_preferences(tx, user_id: str, stats: Dict):
    """PASS4.3: Tính user nutrition preferences từ highly-rated recipes"""
    q = """
    MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r:Recipe)
    WHERE ((iv.rating IS NOT NULL AND iv.rating >= 4.0) 
           OR iv.event_type = 'like' 
           OR (iv.liked IS NOT NULL AND iv.liked = true))
       AND r.nutrition_calories IS NOT NULL
    WITH r, iv,
         CASE 
             WHEN iv.rating IS NOT NULL AND iv.rating >= 4.0 THEN 1.0
             WHEN iv.event_type = 'like' OR (iv.liked IS NOT NULL AND iv.liked = true) THEN 0.8
             ELSE 0.5
         END AS weight
    RETURN 
        avg(r.nutrition_calories * weight) AS avg_calories,
        avg(r.nutrition_protein * weight) AS avg_protein,
        avg(r.nutrition_total_fat * weight) AS avg_total_fat,
        avg(r.nutrition_saturated_fat * weight) AS avg_saturated_fat,
        avg(r.nutrition_sodium * weight) AS avg_sodium,
        avg(r.nutrition_total_sugars * weight) AS avg_total_sugars,
        avg(r.nutrition_total_carbohydrate * weight) AS avg_total_carbohydrate,
        count(r) AS recipe_count
    """
    
    result = tx.run(q, uid=user_id).single()
    
    if not result or result["recipe_count"] == 0:
        return None
    
    # Calculate original values
    prefs = {
        "calories": result.get("avg_calories"),
        "protein": result.get("avg_protein"),
        "total_fat": result.get("avg_total_fat"),
        "saturated_fat": result.get("avg_saturated_fat"),
        "sodium": result.get("avg_sodium"),
        "total_sugars": result.get("avg_total_sugars"),
        "total_carbohydrate": result.get("avg_total_carbohydrate")
    }
    
    # Calculate normalized values
    prefs_norm = {}
    for nut_id in CORE_NUTRITION_IDS:
        if nut_id not in stats or prefs.get(nut_id) is None:
            continue
        
        min_val = stats[nut_id]["min"]
        max_val = stats[nut_id]["max"]
        orig_val = prefs[nut_id]
        
        if max_val > min_val:
            norm_val = (orig_val - min_val) / (max_val - min_val)
        else:
            norm_val = 0.0
        
        prefs_norm[nut_id] = norm_val
    
    return {
        "original": prefs,
        "normalized": prefs_norm
    }


def update_user_nutrition_preferences(tx, user_id: str, prefs: Dict):
    """Update User properties với nutrition preferences"""
    if not prefs:
        return
    
    orig = prefs.get("original", {})
    norm = prefs.get("normalized", {})
    
    q = """
    MATCH (u:User {user_id: $uid})
    SET u.nutrition_pref_calories = $cal_orig,
        u.nutrition_pref_protein = $prot_orig,
        u.nutrition_pref_total_fat = $fat_orig,
        u.nutrition_pref_saturated_fat = $sat_fat_orig,
        u.nutrition_pref_sodium = $sod_orig,
        u.nutrition_pref_total_sugars = $sug_orig,
        u.nutrition_pref_total_carbohydrate = $carb_orig,
        u.nutrition_pref_calories_norm = $cal_norm,
        u.nutrition_pref_protein_norm = $prot_norm,
        u.nutrition_pref_total_fat_norm = $fat_norm,
        u.nutrition_pref_saturated_fat_norm = $sat_fat_norm,
        u.nutrition_pref_sodium_norm = $sod_norm,
        u.nutrition_pref_total_sugars_norm = $sug_norm,
        u.nutrition_pref_total_carbohydrate_norm = $carb_norm
    """
    
    tx.run(q,
           uid=user_id,
           cal_orig=orig.get("calories"),
           prot_orig=orig.get("protein"),
           fat_orig=orig.get("total_fat"),
           sat_fat_orig=orig.get("saturated_fat"),
           sod_orig=orig.get("sodium"),
           sug_orig=orig.get("total_sugars"),
           carb_orig=orig.get("total_carbohydrate"),
           cal_norm=norm.get("calories"),
           prot_norm=norm.get("protein"),
           fat_norm=norm.get("total_fat"),
           sat_fat_norm=norm.get("saturated_fat"),
           sod_norm=norm.get("sodium"),
           sug_norm=norm.get("total_sugars"),
           carb_norm=norm.get("total_carbohydrate"))


def build_user_nutrition_preferences(driver, session_kwargs):
    """PASS4.3: Tính user nutrition preferences"""
    print("[PASS4.3] Computing user nutrition preferences...")
    
    # Get nutrition stats first (only for 7 core nutrients)
    with driver.session(**session_kwargs) as session:
        # Compute stats only for core nutrition IDs (used in user preferences)
        stats = session.execute_read(compute_nutrition_stats, CORE_NUTRITION_IDS)
        if not stats:
            print("  ⚠️ ERROR: No nutrition stats found! Please run PASS4.1 first.")
            return
        print(f"  [4.3] Computed stats for {len(stats)} core nutrients")
        
        # Get all users
        q_users = "MATCH (u:User) RETURN u.user_id AS uid"
        all_users = [record["uid"] for record in session.run(q_users)]
        total_users = len(all_users)
        print(f"  [4.3] Processing {total_users} users...")
        
        processed = 0
        updated = 0
        
        for user_id in all_users:
            prefs = session.execute_read(compute_user_nutrition_preferences, user_id, stats)
            
            if prefs:
                session.execute_write(update_user_nutrition_preferences, user_id, prefs)
                updated += 1
            
            processed += 1
            if processed % 100 == 0:
                print(f"  [4.3] Processed {processed}/{total_users} users ({updated} with preferences)...", flush=True)
        
        print(f"  [4.3] Updated {updated}/{total_users} users with nutrition preferences")
    
    print("[PASS4.3] ✅ User nutrition preferences completed.\n")


def build_nutrition_similar_users(driver, session_kwargs, similarity_threshold: float = 0.8):
    """PASS4.4: (Tùy chọn) Tạo SIMILAR_USER relationships dựa trên nutrition preferences"""
    print(f"[PASS4.4] Building SIMILAR_USER relationships based on nutrition (threshold={similarity_threshold})...")
    
    with driver.session(**session_kwargs) as session:
        # Get users with nutrition preferences
        q_users = """
        MATCH (u:User)
        WHERE u.nutrition_pref_calories_norm IS NOT NULL
        RETURN u.user_id AS uid
        ORDER BY u.user_id
        """
        users = [record["uid"] for record in session.run(q_users)]
        total_users = len(users)
        print(f"  [4.4] Found {total_users} users with nutrition preferences")
        
        if total_users < 2:
            print("  [4.4] Not enough users, skipping...")
            return
        
        # Process in batches
        BATCH_SIZE = 50
        total_pairs = 0
        total_similarities = 0
        
        for i in range(0, len(users), BATCH_SIZE):
            batch1 = users[i:i+BATCH_SIZE]
            
            for j in range(i, len(users), BATCH_SIZE):
                batch2 = users[j:j+BATCH_SIZE]
                
                # Create pairs
                pairs = []
                for u1_id in batch1:
                    for u2_id in batch2:
                        if u1_id < u2_id:  # Only one direction
                            pairs.append({"u1_id": u1_id, "u2_id": u2_id})
                
                if not pairs:
                    continue
                
                # Compute similarities
                q_sim = """
                UNWIND $pairs AS p
                MATCH (u1:User {user_id: p.u1_id})
                MATCH (u2:User {user_id: p.u2_id})
                WHERE u1.nutrition_pref_calories_norm IS NOT NULL
                  AND u2.nutrition_pref_calories_norm IS NOT NULL
                WITH u1, u2,
                     [u1.nutrition_pref_calories_norm, u1.nutrition_pref_total_fat_norm, 
                      u1.nutrition_pref_saturated_fat_norm, u1.nutrition_pref_sodium_norm,
                      u1.nutrition_pref_protein_norm, u1.nutrition_pref_total_sugars_norm,
                      u1.nutrition_pref_total_carbohydrate_norm] AS vec1,
                     [u2.nutrition_pref_calories_norm, u2.nutrition_pref_total_fat_norm,
                      u2.nutrition_pref_saturated_fat_norm, u2.nutrition_pref_sodium_norm,
                      u2.nutrition_pref_protein_norm, u2.nutrition_pref_total_sugars_norm,
                      u2.nutrition_pref_total_carbohydrate_norm] AS vec2
                WHERE all(v IN vec1 WHERE v IS NOT NULL) AND all(v IN vec2 WHERE v IS NOT NULL)
                WITH u1, u2, vec1, vec2,
                     reduce(dot=0.0, i IN range(0, 6) | dot + vec1[i] * vec2[i]) AS dot,
                     sqrt(reduce(sum=0.0, v IN vec1 | sum + v*v)) AS norm1,
                     sqrt(reduce(sum=0.0, v IN vec2 | sum + v*v)) AS norm2
                WITH u1, u2,
                     CASE WHEN norm1=0 OR norm2=0 THEN 0.0 ELSE dot/(norm1*norm2) END AS sim
                WHERE sim > $threshold
                MERGE (u1)-[rel:SIMILAR_USER]->(u2)
                ON CREATE SET
                    rel.nutrition_similarity = sim,
                    rel.updated_at = datetime()
                ON MATCH SET
                    rel.nutrition_similarity = sim,
                    rel.combined_score = CASE
                        WHEN rel.score IS NOT NULL AND sim IS NOT NULL
                        THEN 0.4 * coalesce(rel.score, 0.0) + 0.3 * sim
                        WHEN rel.score IS NOT NULL THEN rel.score
                        WHEN sim IS NOT NULL THEN sim
                        ELSE 0.0
                    END,
                    rel.updated_at = datetime()
                RETURN count(rel) AS created
                """
                
                result = session.run(q_sim, pairs=pairs, threshold=similarity_threshold).single()
                if result:
                    created = result["created"] or 0
                    total_similarities += created
                    total_pairs += len(pairs)
        
        print(f"  [4.4] Created {total_similarities} SIMILAR_USER relationships from {total_pairs} pairs")
    
    print("[PASS4.4] ✅ SIMILAR_USER (nutrition-based) completed.\n")


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
        MATCH ()-[r:SIMILAR_TO|SIMILAR_RECIPE|SIMILAR_NUTRITION]->() DELETE r
        """)
        # Chỉ xoá các quan hệ POPULAR_IN cũ, giữ nguyên Group và BELONGS_TO (được tạo từ survey)
        session.run("MATCH (:Group)-[r:POPULAR_IN]->(:Recipe) DELETE r")
        # Clean up old nutrition data (will be recreated in PASS4)
        session.run("MATCH ()-[r:HAS_NUTRITION]->() DELETE r")
        session.run("MATCH (n:Nutrition) DELETE n")
        # Clean up SIMILAR_RECIPE if exists (removed feature)
        session.run("MATCH ()-[r:SIMILAR_RECIPE]->() DELETE r")
    print("✅ Cleanup done.\n")


# =============== PIPELINE MAIN ===============
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Compute features for recommendation system")
    parser.add_argument(
        "--pass",
        dest="pass_num",
        type=str,
        choices=["1", "2", "3", "4", "4.1", "4.2", "4.3", "4.4", "all"],
        default="all",
        help="Which pass to run: 1, 2, 3, 4, 4.1, 4.2, 4.3, 4.4, or all (default: all)"
    )
    parser.add_argument(
        "--threshold",
        type=float,
        default=0.8,
        help="Similarity threshold for PASS4.2 (default: 0.8)"
    )
    parser.add_argument(
        "--limit-recipes",
        type=int,
        default=None,
        help="Limit number of recipes for PASS4.2 (for faster processing, e.g., 10000)"
    )
    parser.add_argument(
        "--top-by-interactions",
        action="store_true",
        help="For PASS4.2, only process top recipes by interaction count (use with --limit-recipes)"
    )
    parser.add_argument(
        "--cleanup",
        action="store_true",
        help="Clean up old data before running (default: skip cleanup)"
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
        print("\n🚀 Running PASS1...\n")
        print("[PASS1] Counting DF for text tokens & ingredient IDs ...")

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
    if pass_num in ["2", "all"]:
        if pass_num == "2":
            print("\n🚀 Running PASS2...\n")
        print("\n[PASS2] Computing TF-IDF & updating Neo4j ...")
        
        # PASS2 cần kết quả từ PASS1
        if not text_idf or not ing_idf:
            print("  ⚠️ ERROR: PASS2 requires PASS1 to run first!")
            print("  Please run: python scripts/compute_features_improve.py --pass 1")
            driver.close()
            exit(1)
        
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
    if pass_num in ["3", "all"]:
        if pass_num == "3":
            print("\n🚀 Running PASS3...\n")
        print("[PASS3] Building hybrid similarity graph ...")
        build_hybrid_similarity(driver)
    
    # -------- PASS4: Nutrition Features (NRKG) --------
    if pass_num in ["4", "4.1", "4.2", "4.3", "4.4", "all"]:
        if pass_num.startswith("4") and pass_num != "all":
            print(f"\n🚀 Running PASS{pass_num}...\n")
        if pass_num in ["4", "all"]:
            print("\n[PASS4] Building nutrition features (NRKG)...")
        
        # PASS4.1: Nutrition nodes and HAS_NUTRITION relationships
        if pass_num in ["4", "4.1", "all"]:
            build_nutrition_components(driver, session_kwargs)
        
        # PASS4.2: Nutrition similarity between recipes
        if pass_num in ["4", "4.2", "all"]:
            # Check if PASS4.1 has been run (need Nutrition nodes and HAS_NUTRITION relationships)
            with driver.session(**session_kwargs) as session:
                check = session.run("MATCH (n:Nutrition) RETURN count(n) AS count").single()
                if check and check["count"] == 0:
                    print("  ⚠️ ERROR: PASS4.2 requires PASS4.1 to run first!")
                    print("  Please run: python scripts/compute_features_improve.py --pass 4.1")
                    driver.close()
                    exit(1)
            # Get optimization options from args
            limit_recipes = getattr(args, 'limit_recipes', None)
            top_by_interactions = getattr(args, 'top_by_interactions', False)
            
            build_nutrition_similarity(
                driver, 
                session_kwargs, 
                similarity_threshold=args.threshold,
                limit_recipes=limit_recipes,
                top_by_interactions=top_by_interactions
            )
        
        # PASS4.3: User nutrition preferences
        if pass_num in ["4", "4.3", "all"]:
            build_user_nutrition_preferences(driver, session_kwargs)
        
        # PASS4.4: (Optional) SIMILAR_USER based on nutrition
        if pass_num in ["4", "4.4", "all"]:
            build_nutrition_similar_users(driver, session_kwargs, similarity_threshold=0.7)
    
    driver.close()
    
    if pass_num == "all":
        print("\n✅ DONE: FULL PIPELINE (PASS1-4) completed successfully!")
    else:
        print(f"\n✅ DONE: PASS{pass_num} completed successfully!")
