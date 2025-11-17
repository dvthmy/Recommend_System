import argparse
import json
import math
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple
import time

from neo4j import GraphDatabase


# -------- Sparse vector helpers (list of [term, weight]) --------

def map_from_list(pairs: List[List]) -> Dict[str, float]:
    out: Dict[str, float] = {}
    if not pairs:
        return out
    for p in pairs:
        # expect [term, value]
        if isinstance(p, (list, tuple)) and len(p) == 2:
            t, v = p[0], p[1]
            try:
                out[str(t)] = float(v)
            except Exception:
                continue
    return out


def cosine_sparse(a: Dict[str, float], b: Dict[str, float]) -> float:
    if not a or not b:
        return 0.0
    # assume inputs already l2-normalized; if not, normalize defensively
    def norm(x: Dict[str, float]) -> float:
        s = sum(v * v for v in x.values())
        return math.sqrt(s) or 1.0

    a_norm = norm(a)
    b_norm = norm(b)
    dot = 0.0
    # iterate smaller map for speed
    (small, large) = (a, b) if len(a) < len(b) else (b, a)
    for k, v in small.items():
        if k in large:
            dot += v * large[k]
    return dot / (a_norm * b_norm)


def map_from_tf_object(tf_obj) -> Dict[str, float]:
    if not tf_obj or not isinstance(tf_obj, dict):
        return {}
    terms = tf_obj.get("terms") or []
    weights = tf_obj.get("weights") or []
    if not terms or not weights or len(terms) != len(weights):
        return {}
    out: Dict[str, float] = {}
    for i in range(len(terms)):
        try:
            out[str(terms[i])] = float(weights[i])
        except Exception:
            continue
    return out


# -------- Simple in-process caches --------

_USER_VEC_CACHE: Dict[str, Tuple[float, Dict[str, float]]] = {}
_POPULAR_CACHE: Dict[Tuple[Optional[str], Optional[int], int], Tuple[float, List[Dict]]] = {}


# -------- Normalization helpers --------

def _minmax(values: List[float]) -> List[float]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if hi <= lo:
        return [0.0 for _ in values]
    return [(v - lo) / (hi - lo) for v in values]


def _ranknorm(values: List[float]) -> List[float]:
    if not values:
        return []
    pairs = sorted([(v, i) for i, v in enumerate(values)])
    ranks = [0.0] * len(values)
    for r, (_v, i) in enumerate(pairs):
        ranks[i] = float(r)
    denom = float(max(1, len(values) - 1))
    return [r / denom for r in ranks]


def _normalize_parts(parts: List[Dict[str, float]], mode: str) -> List[Dict[str, float]]:
    if mode not in ("minmax", "rank"):
        return parts
    keys = ["s_ing", "s_text", "s_pop", "s_cf"]
    for k in keys:
        vals = [p.get(k, 0.0) for p in parts]
        normed = _ranknorm(vals) if mode == "rank" else _minmax(vals)
        for p, v in zip(parts, normed):
            p[k] = v
    return parts


# -------- Diversification (MMR) --------

def _mmr_diversify(scored: List[Tuple['CandidateRecipe', float, Dict[str, float]]], *, k: int, lam: float) -> List[Tuple['CandidateRecipe', float, Dict[str, float]]]:
    # Use recipe_text_tfidf cosine as similarity; fallback to 0 if missing
    if k <= 0 or not scored:
        return []
    k = min(k, len(scored))
    selected: List[Tuple['CandidateRecipe', float, Dict[str, float]]] = []
    remaining = scored[:]
    # Pre-extract vectors for speed
    vecs: Dict[str, Dict[str, float]] = {c.recipe_id: c.recipe_text_tfidf for (c, s, p) in remaining}
    while remaining and len(selected) < k:
        if not selected:
            # pick highest score first
            best = remaining[0]
            selected.append(best)
            remaining = remaining[1:]
            continue
        best_idx = 0
        best_mmr = -1e18
        for idx, (cand, s, parts) in enumerate(remaining):
            sim_to_selected = 0.0
            for (sel_c, _, _) in selected:
                sim_to_selected = max(sim_to_selected, cosine_sparse(vecs.get(cand.recipe_id, {}), vecs.get(sel_c.recipe_id, {})))
            mmr = lam * s - (1.0 - lam) * sim_to_selected
            if mmr > best_mmr:
                best_mmr = mmr
                best_idx = idx
        selected.append(remaining[best_idx])
        remaining.pop(best_idx)
    return selected


# -------- Data structures --------

@dataclass
class CandidateRecipe:
    recipe_id: str
    title: str
    cuisine: Optional[str]
    cook_time_min: Optional[int]
    ingredient_overlap_weight: float
    recipe_text_tfidf: Dict[str, float]
    popularity_score: float
    cf_score: float = 0.0
    updated_at: Optional[str] = None


# -------- Neo4j interactions --------

# def prefilter_and_candidates(session, *, ingredient_ids: Optional[List[str]], cuisine: Optional[str], max_cook_time: Optional[int], limit_candidates: int) -> List[CandidateRecipe]:
#     rows = None
#     if ingredient_ids:
#         # Candidate gen by ingredient overlap with idf-weighted edges
#         # q = (
#         #     """

#         #     UNWIND $ingIds AS iid
#         #     MATCH (r:Recipe)-[rel:HAS_INGREDIENT]->(i:Ingredient {ingredient_id: iid})
#         #     WITH r, sum(coalesce(rel.idf_weight, 0.0)) AS ingOverlap
#         #     WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
#         #       AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
#         #     RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
#         #            ingOverlap AS ingOverlap,
#         #            {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
#         #            {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop,
#         #            coalesce(r.updated_at, r.created_at) AS updated_at
#         #     ORDER BY ingOverlap DESC, coalesce(pop.views,0) DESC
#         #     LIMIT $lim
#         #     """
#         # )
#         q = (
#             """
#             // ✅ Lấy recipe có đầy đủ tất cả nguyên liệu trong danh sách (AND logic)
#             MATCH (r:Recipe)
#             WHERE all(iid IN $ingIds WHERE EXISTS {
#                 MATCH (r)-[:HAS_INGREDIENT]->(:Ingredient {ingredient_id: iid})
#             })
#             AND ( $cuisine IS NULL OR r.cuisine = $cuisine )
#             AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )

#             // ✅ Chỉ lấy quan hệ tới nguyên liệu trong danh sách $ingIds
#             MATCH (r)-[rel:HAS_INGREDIENT]->(i:Ingredient)
#             WHERE i.ingredient_id IN $ingIds

#             // ✅ Tổng idf_weight đúng, chỉ trên các nguyên liệu yêu cầu
#             WITH r, sum(coalesce(rel.idf_weight, 0.0)) AS ingOverlap,
#                 {views: coalesce(r.popularity_views,0),
#                 saves: coalesce(r.popularity_saves,0),
#                 cooks: coalesce(r.popularity_cooks,0),
#                 likes: coalesce(r.popularity_likes,0)} AS pop

#             RETURN r.recipe_id AS id,
#                 r.title AS title,
#                 r.cuisine AS cuisine,
#                 r.cook_time_min AS cook_time,
#                 ingOverlap AS ingOverlap,
#                 {terms: coalesce(r.text_terms, []),
#                     weights: coalesce(r.text_weights, [])} AS tf,
#                 pop AS pop,
#                 coalesce(r.updated_at, r.created_at) AS updated_at

#             ORDER BY ingOverlap DESC, coalesce(pop.views,0) DESC
#             LIMIT $lim
#             """
# )

#         try:
#             rows = session.run(q, ingIds=list(set(ingredient_ids)), cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates, timeout=8000)
#         except Exception:
#             rows = []
#         # Fallback: if no ingredient edges or properties exist yet, fall back to popularity-based seeds
#         peek = list(rows)
#         if not peek:
#             q_fallback = (
#                 """
#                 MATCH (r:Recipe)
#                 WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
#                   AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
#                 WITH r, {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop
#                 RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
#                        0.0 AS ingOverlap,
#                        {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
#                        pop AS pop,
#                        coalesce(r.updated_at, r.created_at) AS updated_at
#                 ORDER BY coalesce(pop.views,0) DESC, r.updated_at DESC
#                 LIMIT $lim
#                 """
#             )
#             try:
#                 rows = session.run(q_fallback, cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates, timeout=5000)
#             except Exception:
#                 rows = []
#         else:
#             # Reuse the peeked rows
#             rows = iter(peek)
#     else:
#         # Broad prefilter by cuisine/time then take popular as seeds
#         q = (
#             """
#             MATCH (r:Recipe)
#             WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
#               AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
#             WITH r, {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop
#             RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
#                    0.0 AS ingOverlap,
#                    {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
#                    pop AS pop,
#                    coalesce(r.updated_at, r.created_at) AS updated_at
#             ORDER BY coalesce(pop.views,0) DESC, r.updated_at DESC
#             LIMIT $lim
#             """
#         )
#         try:
#             rows = session.run(q, cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates, timeout=5000)
#         except Exception:
#             rows = []

#     out: List[CandidateRecipe] = []
#     for row in rows or []:
#         pop = row["pop"] or {}
#         # simple popularity score: log(1+views) + 0.5*log(1+saves) + 0.7*log(1+cooks) + 0.8*log(1+likes)
#         def lp(x: Optional[int]) -> float:
#             try:
#                 return math.log1p(float(x or 0))
#             except Exception:
#                 return 0.0

#         pop_score = lp(pop.get("views")) + 0.5 * lp(pop.get("saves")) + 0.7 * lp(pop.get("cooks")) + 0.8 * lp(pop.get("likes"))

#         out.append(CandidateRecipe(
#             recipe_id=row["id"],
#             title=row["title"] or "",
#             cuisine=row["cuisine"],
#             cook_time_min=row["cook_time"],
#             ingredient_overlap_weight=float(row.get("ingOverlap") or 0.0),
#             recipe_text_tfidf=map_from_tf_object(row["tf"]),
#             popularity_score=pop_score,
#             updated_at=row.get("updated_at"),
#         ))
#     return out

def prefilter_and_candidates(session, *, ingredient_ids: Optional[List[str]], cuisine: Optional[str],
                             max_cook_time: Optional[int], limit_candidates: int) -> List[CandidateRecipe]:
    out: List[CandidateRecipe] = []
    seen_ids = set()  # avoid duplicate recipes

    # ✅ Helper: compute popularity + rating score
    def compute_popularity_score(pop: Dict[str, float]) -> float:
        def lp(x: Optional[float]) -> float:
            try:
                return math.log1p(float(x or 0))
            except Exception:
                return 0.0
        views = lp(pop.get("views")) * 0.4
        saves = lp(pop.get("saves")) * 0.3
        cooks = lp(pop.get("cooks")) * 0.4
        likes = lp(pop.get("likes")) * 0.5

        # ✅ Rating-based components
        rating_val = 0.8 * float(pop.get("rating_value") or 0.0)
        rating_cnt = 0.3 * lp(pop.get("rating_count"))

        # ✅ Combine all signals
        score = (views + saves + cooks + likes + rating_val + rating_cnt)

        # ✅ Normalize slightly to keep scores in a manageable range
        return score / 10.0
    
    
    # ✅ Main logic: progressively relax ingredient matching threshold
    if ingredient_ids:
        ingIds = list(set(ingredient_ids))
        print(f"🧂 {len(ingIds)} input ingredients received.")

        required_counts = sorted(set([len(ingIds), len(ingIds)-1, 2, 1]), reverse=True)
        required_counts = [r for r in required_counts if r > 0]


        for req in required_counts:
            q = (
                """
                MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
                WHERE i.ingredient_id IN $ingIds
                  AND ( $cuisine IS NULL OR r.cuisine = $cuisine )
                  AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )

                // ✅ Compute both matchCount and rarityScore together (keep i in scope)
                WITH r,
                     collect(DISTINCT i.ingredient_id) AS matched,
                     count(DISTINCT i) AS matchCount,
                     sum(coalesce(i.ing_idf, 1.0)) AS rarityScore
                WHERE matchCount >= $reqCount

                // ✅ Combine with popularity and rating data
                WITH r, matchCount, rarityScore,
                     {views: coalesce(r.popularity_views,0),
                      saves: coalesce(r.popularity_saves,0),
                      cooks: coalesce(r.popularity_cooks,0),
                      likes: coalesce(r.popularity_likes,0),
                      rating_value: coalesce(r.rating_avg,0.0),
                      rating_count: coalesce(r.rating_count,0)} AS pop
                RETURN r.recipe_id AS id,
                       r.title AS title,
                       r.cuisine AS cuisine,
                       r.cook_time_min AS cook_time,
                       matchCount AS matchCount,
                       rarityScore AS rarityScore,
                       {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
                       pop AS pop,
                       coalesce(r.updated_at, r.created_at) AS updated_at
                ORDER BY matchCount DESC, rarityScore DESC, coalesce(pop.views,0) DESC
                LIMIT $lim
                """
            )

            rows = session.run(q, ingIds=ingIds, reqCount=req,
                               cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates)
            recipes = list(rows)

            if recipes:
                print(f"✅ Found {len(recipes)} recipes with ≥{req} matching ingredients.")
            else:
                continue  # try lower threshold if none found

            for row in recipes:
                rid = row["id"]
                if rid in seen_ids:
                    continue  # skip duplicates
                seen_ids.add(rid)

                match_count = float(row.get("matchCount") or 0.0)
                rarity_score = float(row.get("rarityScore") or 0.0)
                pop_score = compute_popularity_score(row["pop"] or {})

                # ✅ Ingredient score combines match count + rarity
                ingredient_score = 0.7 * match_count + 0.3 * rarity_score

                out.append(CandidateRecipe(
                    recipe_id=rid,
                    title=row["title"] or "",
                    cuisine=row["cuisine"],
                    cook_time_min=row["cook_time"],
                    ingredient_overlap_weight=ingredient_score,
                    recipe_text_tfidf=map_from_tf_object(row["tf"]),
                    popularity_score=pop_score,
                    updated_at=row.get("updated_at"),
                ))

            # stop early if we already have enough
            if len(out) >= limit_candidates:
                break

    # ⚠️ Fallback: if no recipes found at all, use popularity
    if not out:
        print("⚠️ No matches found — falling back to most popular recipes.")
        q = (
            """
            MATCH (r:Recipe)
            WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
              AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
            WITH r,
                 {views: coalesce(r.popularity_views,0),
                  saves: coalesce(r.popularity_saves,0),
                  cooks: coalesce(r.popularity_cooks,0),
                  likes: coalesce(r.popularity_likes,0),
                  rating_value: coalesce(r.rating_avg,0.0),
                  rating_count: coalesce(r.rating_count,0)} AS pop
            RETURN r.recipe_id AS id,
                   r.title AS title,
                   r.cuisine AS cuisine,
                   r.cook_time_min AS cook_time,
                   0.0 AS matchCount,
                   0.0 AS rarityScore,
                   {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
                   pop AS pop,
                   coalesce(r.updated_at, r.created_at) AS updated_at
            ORDER BY coalesce(pop.views,0) DESC, r.updated_at DESC
            LIMIT $lim
            """
        )
        rows = session.run(q, cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates)
        for row in rows:
            pop_score = compute_popularity_score(row["pop"] or {})
            out.append(CandidateRecipe(
                recipe_id=row["id"],
                title=row["title"] or "",
                cuisine=row["cuisine"],
                cook_time_min=row["cook_time"],
                ingredient_overlap_weight=0.0,
                recipe_text_tfidf=map_from_tf_object(row["tf"]),
                popularity_score=pop_score,
                updated_at=row.get("updated_at"),
            ))

    print(f"🚀 Total collected: {len(out)} recipes (unique).")
    return out


def load_user_vector(session, user_id: str) -> Dict[str, float]:
    q = (
        """
        MATCH (u:User {user_id: $uid})
        RETURN coalesce(u.user_terms, []) AS terms, coalesce(u.user_weights, []) AS weights
        """
    )
    # cache 5 minutes
    now = time.time()
    if user_id in _USER_VEC_CACHE and now - _USER_VEC_CACHE[user_id][0] < 300:
        return _USER_VEC_CACHE[user_id][1]
    row = session.run(q, uid=user_id, timeout=5000).single()
    if not row:
        return {}
    terms = row["terms"] or []
    weights = row["weights"] or []
    if not terms or not weights or len(terms) != len(weights):
        return {}
    out: Dict[str, float] = {}
    for i in range(len(terms)):
        try:
            out[str(terms[i])] = float(weights[i])
        except Exception:
            continue
    _USER_VEC_CACHE[user_id] = (now, out)
    return out


def load_user_profile_defaults(session, user_id: Optional[str]) -> Tuple[Optional[str], Optional[int]]:
    """Return (fav_cuisine, max_cook_time) if present for user, else (None, None).

    - fav_cuisine: first cuisine from FAVORS_CUISINE link
    - max_cook_time: from u.max_cook_time
    """
    if not user_id:
        return (None, None)
    q = (
        """
        MATCH (u:User {user_id: $uid})
        OPTIONAL MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        WITH u, collect(c.name) AS favs
        RETURN coalesce(head(favs), NULL) AS favCuisine, u.max_cook_time AS maxCook
        """
    )
    row = session.run(q, uid=user_id).single()
    if not row:
        return (None, None)
    fav = row.get("favCuisine")
    try:
        mx = row.get("maxCook")
        if mx is not None:
            mx = int(mx)
    except Exception:
        mx = None
    return (fav, mx)


def exclude_user_allergens_and_dislikes(session, user_id: Optional[str], candidate_ids: List[str]) -> List[str]:
    if not user_id or not candidate_ids:
        return candidate_ids
    q = (
        """
        UNWIND $ids AS rid
        MATCH (r:Recipe {recipe_id: rid})
        OPTIONAL MATCH (u:User {user_id: $uid})-[:ALLERGIC_TO|:DISLIKES]->(i:Ingredient)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(ri:Ingredient)
        WITH r, collect(i.ingredient_id) AS blocked, collect(ri.ingredient_id) AS rIngs
        // keep recipe if no ingredient in rIngs is in blocked
        WITH r, blocked, rIngs
        WHERE NONE(x IN rIngs WHERE x IN blocked)
        RETURN r.recipe_id AS id
        """
    )
    rows = session.run(q, uid=user_id, ids=candidate_ids)
    return [r["id"] for r in rows]


def load_user_recent_recipes(session, user_id: Optional[str], limit_per_type: int = 50) -> List[str]:
    if not user_id:
        return []
    q = (
        """
        MATCH (u:User {user_id: $uid})-[iv:INTERACTED_WITH]->(r:Recipe)
        WITH r, iv
        ORDER BY iv.timestamp DESC
        RETURN collect(r.recipe_id)[0..$lim] AS ids
        """
    )
    row = session.run(q, uid=user_id, lim=limit_per_type).single()
    return row["ids"] if row and row["ids"] else []


def load_cf_scores_for_candidates(session, user_seed_recipe_ids: List[str], candidate_ids: List[str]) -> Dict[str, float]:
    # Aggregate CF score for each candidate by summing SIMILAR_TO scores from user's seed recipes
    if not user_seed_recipe_ids or not candidate_ids:
        return {}
    q = (
        """
        UNWIND $seed AS sid
        UNWIND $cands AS cid
        MATCH (s:Recipe {recipe_id: sid})-[sim:SIMILAR_TO]->(c:Recipe {recipe_id: cid})
        RETURN c.recipe_id AS cid, sum(coalesce(sim.score, 0.0)) AS score
        """
    )
    rows = session.run(q, seed=list(set(user_seed_recipe_ids)), cands=list(set(candidate_ids)))
    out: Dict[str, float] = {}
    for r in rows:
        try:
            out[str(r["cid"])] = float(r["score"] or 0.0)
        except Exception:
            continue
    return out


# -------- Scoring and rerank --------

def _compute_recency_multiplier(updated_at_str: Optional[str], half_life_days: float) -> float:
    if not updated_at_str or not half_life_days or half_life_days <= 0:
        return 1.0
    try:
        # Try to parse ISO datetime, fall back to date
        dt = None
        try:
            dt = datetime.fromisoformat(updated_at_str.replace("Z", "+00:00"))
        except Exception:
            dt = datetime.strptime(updated_at_str, "%Y-%m-%d")
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        now = datetime.now(timezone.utc)
        days = max(0.0, (now - dt).total_seconds() / 86400.0)
        return math.exp(-math.log(2.0) * days / float(half_life_days))
    except Exception:
        return 1.0


def compute_scores(cands: List[CandidateRecipe], *, user_vec: Dict[str, float], w_ing: float, w_text: float, w_pop: float, w_cf: float, norm: str, pop_half_life: Optional[float]) -> List[Tuple[CandidateRecipe, float, Dict[str, float]]]:
    parts: List[Dict[str, float]] = []
    refs: List[CandidateRecipe] = []
    for c in cands:
        s_ing = c.ingredient_overlap_weight
        s_text = cosine_sparse(user_vec, c.recipe_text_tfidf) if user_vec else 0.0
        s_pop = c.popularity_score
        if pop_half_life and pop_half_life > 0:
            s_pop = s_pop * _compute_recency_multiplier(c.updated_at, pop_half_life)
        s_cf = getattr(c, "cf_score", 0.0)
        parts.append({"s_ing": s_ing, "s_text": s_text, "s_pop": s_pop, "s_cf": s_cf})
        refs.append(c)

    parts = _normalize_parts(parts, norm)

    scored: List[Tuple[CandidateRecipe, float, Dict[str, float]]] = []
    for c, p in zip(refs, parts):
        score = w_ing * p["s_ing"] + w_text * p["s_text"] + w_pop * p["s_pop"] + w_cf * p["s_cf"]
        scored.append((c, score, {"s_ing": p["s_ing"], "s_text": p["s_text"], "s_pop": p["s_pop"], "s_cf": p["s_cf"]}))
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored


def recommend(
    uri: str,
    user: str,
    password: str,
    *,
    database: Optional[str],
    user_id: Optional[str],
    ingredient_ids: Optional[List[str]],
    cuisine: Optional[str],
    max_cook_time: Optional[int],
    limit_candidates: int,
    limit_results: int,
    w_ing: float,
    w_text: float,
    w_pop: float,
    w_cf: float,
    norm: str,
    pop_half_life: Optional[float],
    diversify: bool,
    mmr_lambda: float,
) -> List[Dict]:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        session_kwargs = {"database": database} if database else {}
        with driver.session(**session_kwargs) as session:
            # Fallback to user profile defaults if CLI params not provided
            prof_cuisine, prof_max = (None, None)
            if user_id:
                try:
                    prof_cuisine, prof_max = load_user_profile_defaults(session, user_id)
                except Exception:
                    prof_cuisine, prof_max = (None, None)

            eff_cuisine = cuisine if cuisine else prof_cuisine
            eff_max_cook = max_cook_time if max_cook_time is not None else prof_max

            cands = prefilter_and_candidates(
                session,
                ingredient_ids=ingredient_ids,
                cuisine=eff_cuisine,
                max_cook_time=eff_max_cook,
                limit_candidates=limit_candidates,
            )

            # Guard: if no candidates due to missing idf_weight or query timeouts, fall back to popular small pool
            if not cands:
                try:
                    fallback = prefilter_and_candidates(
                        session,
                        ingredient_ids=None,
                        cuisine=eff_cuisine,
                        max_cook_time=eff_max_cook,
                        limit_candidates=min(200, limit_candidates),
                    )
                    cands = fallback
                except Exception:
                    cands = []

            # Optional: filter out allergens/dislikes for a given user
            if user_id and cands:
                cand_ids = [c.recipe_id for c in cands]
                ok_ids = set(exclude_user_allergens_and_dislikes(session, user_id, cand_ids))
                cands = [c for c in cands if c.recipe_id in ok_ids]

            # Load user vector when present
            user_vec: Dict[str, float] = load_user_vector(session, user_id) if user_id else {}

            # CF: load user's recent interacted recipes and compute CF scores toward current candidates
            if user_id and cands:
                seed_ids = load_user_recent_recipes(session, user_id)
                cf_scores = load_cf_scores_for_candidates(session, seed_ids, [c.recipe_id for c in cands])
                for c in cands:
                    c.cf_score = cf_scores.get(c.recipe_id, 0.0)

        # score and rerank client-side
        # Cap scoring pool to avoid heavy Python computations when very large
        pool = cands[: max(limit_results * 5, 200)] if cands else []
        scored = compute_scores(pool, user_vec=user_vec, w_ing=w_ing, w_text=w_text, w_pop=w_pop, w_cf=w_cf, norm=norm, pop_half_life=pop_half_life)
        if diversify:
            top = _mmr_diversify(scored, k=limit_results, lam=mmr_lambda)
        else:
            top = scored[:limit_results]
        results: List[Dict] = []
        for c, score, parts in top:
            results.append({
                "recipe_id": c.recipe_id,
                "title": c.title,
                "cuisine": c.cuisine,
                "cook_time_min": c.cook_time_min,
                "score": score,
                "scores": parts,
            })
        return results
    finally:
        driver.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Recommend recipes via prefilter → candidate → 4 scores (ing,text,pop,cf) → normalize → diversify(optional) → rerank")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="neo4j")
    parser.add_argument("--db", dest="database", default="food", help="Neo4j database name (default: food)")

    parser.add_argument("--user-id", dest="user_id", type=str, default=None, help="User ID to personalize with TF-IDF vector")
    parser.add_argument("--ing", dest="ing", type=str, default=None, help="Comma-separated ingredient_ids to seed candidates (e.g., ing_onion,ing_tomato)")

    parser.add_argument("--cuisine", type=str, default=None)
    parser.add_argument("--max-cook-time", type=int, default=None)
    parser.add_argument("--limit-candidates", type=int, default=1000)
    parser.add_argument("--limit", dest="limit_results", type=int, default=20)

    parser.add_argument("--w-ing", type=float, default=1.0, help="Weight for ingredient-overlap score")
    parser.add_argument("--w-text", type=float, default=1.0, help="Weight for text cosine score")
    parser.add_argument("--w-pop", type=float, default=0.2, help="Weight for popularity score")
    parser.add_argument("--w-cf", type=float, default=0.8, help="Weight for collaborative filtering score")
    parser.add_argument("--norm", type=str, default="rank", choices=["none", "minmax", "rank"], help="Normalization for component scores before weighting")
    parser.add_argument("--pop-half-life", dest="pop_half_life", type=float, default=60.0, help="Half-life in days for recency decay on popularity (0 to disable)")
    parser.add_argument("--diversify", action="store_true", help="Apply MMR diversification on the final top-N")
    parser.add_argument("--mmr-lambda", type=float, default=0.7, help="MMR lambda: trade-off relevance vs novelty (0..1)")

    # Scenario presets
    parser.add_argument("--profile", type=str, default=None, choices=["new", "history", "explore"], help="Scenario preset for weights/normalization/diversification")
    parser.add_argument("--apply-profile", action="store_true", help="Apply the selected profile to override weights and options")

    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    ing_ids = None
    if args.ing:
        ing_ids = [x.strip() for x in args.ing.split(",") if x.strip()]

    # Apply scenario-based presets if requested
    applied_profile = None
    if args.profile and args.apply_profile:
        has_user = bool(args.user_id)
        has_ing = bool(ing_ids)

        # Defaults derived from earlier recommendations
        if args.profile == "new":
            # New user: safe/popular; respect ingredients if present
            if has_ing:
                args.w_ing = 1.2
                args.w_text = 0.6
                args.w_pop = 1.0
                args.w_cf = 0.0
            else:
                args.w_ing = 0.6
                args.w_text = 0.4
                args.w_pop = 1.3
                args.w_cf = 0.0
            args.norm = "rank"
            args.pop_half_life = 60.0
            args.diversify = True
            args.mmr_lambda = 0.7
            applied_profile = "new"

        elif args.profile == "history":
            # Personalized: emphasize CF and text
            args.w_ing = 0.8
            args.w_text = 1.0
            args.w_pop = 0.2
            args.w_cf = 1.2 if has_user else 0.6
            args.norm = "rank"
            args.pop_half_life = 60.0
            args.diversify = True
            args.mmr_lambda = 0.7
            applied_profile = "history"

        elif args.profile == "explore":
            # Exploration: push diversity, reduce popularity weight
            args.w_ing = 0.8
            args.w_text = 1.1
            args.w_pop = 0.1
            args.w_cf = 0.6 if has_user else 0.3
            args.norm = "rank"
            args.pop_half_life = 45.0
            args.diversify = True
            args.mmr_lambda = 0.55
            applied_profile = "explore"

    results = recommend(
        args.uri,
        args.user,
        args.password,
        database=args.database,
        user_id=args.user_id,
        ingredient_ids=ing_ids,
        cuisine=args.cuisine,
        max_cook_time=args.max_cook_time,
        limit_candidates=args.limit_candidates,
        limit_results=args.limit_results,
        w_ing=args.w_ing,
        w_text=args.w_text,
        w_pop=args.w_pop,
        w_cf=args.w_cf,
        norm=args.norm,
        pop_half_life=args.pop_half_life,
        diversify=args.diversify,
        mmr_lambda=args.mmr_lambda,
    )

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        if applied_profile:
            print(f"Applied profile: {applied_profile} (w_ing={args.w_ing}, w_text={args.w_text}, w_pop={args.w_pop}, w_cf={args.w_cf}, norm={args.norm}, pop_half_life={args.pop_half_life}, diversify={args.diversify}, mmr_lambda={args.mmr_lambda})")
        for i, r in enumerate(results, 1):
            print(f"{i:2d}. {r['title']}  (id={r['recipe_id']}, cuisine={r['cuisine']}, cook={r['cook_time_min']})")
            s = r["scores"]
            print(f"     score={r['score']:.4f}   s_ing={s['s_ing']:.4f}  s_text={s['s_text']:.4f}  s_pop={s['s_pop']:.4f}  s_cf={s.get('s_cf',0.0):.4f}")


if __name__ == "__main__":
    main()


