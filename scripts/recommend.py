import argparse
import json
import math
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

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


# -------- Neo4j interactions --------

def prefilter_and_candidates(session, *, ingredient_ids: Optional[List[str]], cuisine: Optional[str], max_cook_time: Optional[int], limit_candidates: int) -> List[CandidateRecipe]:
    rows = None
    if ingredient_ids:
        # Candidate gen by ingredient overlap with idf-weighted edges
        q = (
            """
            UNWIND $ingIds AS iid
            MATCH (r:Recipe)-[rel:HAS_INGREDIENT]->(i:Ingredient {ingredient_id: iid})
            WITH r, sum(coalesce(rel.idf_weight, 0.0)) AS ingOverlap
            WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
              AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
            RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
                   ingOverlap AS ingOverlap,
                   {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
                   {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop
            ORDER BY ingOverlap DESC, coalesce(pop.views,0) DESC
            LIMIT $lim
            """
        )
        rows = session.run(q, ingIds=list(set(ingredient_ids)), cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates)
        # Fallback: if no ingredient edges or properties exist yet, fall back to popularity-based seeds
        peek = list(rows)
        if not peek:
            q_fallback = (
                """
                MATCH (r:Recipe)
                WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
                  AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
                WITH r, {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop
                RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
                       0.0 AS ingOverlap,
                       {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
                       pop AS pop
                ORDER BY coalesce(pop.views,0) DESC, r.updated_at DESC
                LIMIT $lim
                """
            )
            rows = session.run(q_fallback, cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates)
        else:
            # Reuse the peeked rows
            rows = iter(peek)
    else:
        # Broad prefilter by cuisine/time then take popular as seeds
        q = (
            """
            MATCH (r:Recipe)
            WHERE ( $cuisine IS NULL OR r.cuisine = $cuisine )
              AND ( $maxCook IS NULL OR r.cook_time_min IS NULL OR r.cook_time_min <= $maxCook )
            WITH r, {views: coalesce(r.popularity_views,0), saves: coalesce(r.popularity_saves,0), cooks: coalesce(r.popularity_cooks,0), likes: coalesce(r.popularity_likes,0)} AS pop
            RETURN r.recipe_id AS id, r.title AS title, r.cuisine AS cuisine, r.cook_time_min AS cook_time,
                   0.0 AS ingOverlap,
                   {terms: coalesce(r.text_terms, []), weights: coalesce(r.text_weights, [])} AS tf,
                   pop AS pop
            ORDER BY coalesce(pop.views,0) DESC, r.updated_at DESC
            LIMIT $lim
            """
        )
        rows = session.run(q, cuisine=cuisine, maxCook=max_cook_time, lim=limit_candidates)

    out: List[CandidateRecipe] = []
    for row in rows:
        pop = row["pop"] or {}
        # simple popularity score: log(1+views) + 0.5*log(1+saves) + 0.7*log(1+cooks) + 0.8*log(1+likes)
        def lp(x: Optional[int]) -> float:
            try:
                return math.log1p(float(x or 0))
            except Exception:
                return 0.0

        pop_score = lp(pop.get("views")) + 0.5 * lp(pop.get("saves")) + 0.7 * lp(pop.get("cooks")) + 0.8 * lp(pop.get("likes"))

        out.append(CandidateRecipe(
            recipe_id=row["id"],
            title=row["title"] or "",
            cuisine=row["cuisine"],
            cook_time_min=row["cook_time"],
            ingredient_overlap_weight=float(row["ingOverlap"] or 0.0),
            recipe_text_tfidf=map_from_tf_object(row["tf"]),
            popularity_score=pop_score,
        ))
    return out


def load_user_vector(session, user_id: str) -> Dict[str, float]:
    q = (
        """
        MATCH (u:User {user_id: $uid})
        RETURN coalesce(u.user_terms, []) AS terms, coalesce(u.user_weights, []) AS weights
        """
    )
    row = session.run(q, uid=user_id).single()
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
    return out


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


# -------- Scoring and rerank --------

def compute_scores(cands: List[CandidateRecipe], *, user_vec: Dict[str, float], w_ing: float, w_text: float, w_pop: float) -> List[Tuple[CandidateRecipe, float, Dict[str, float]]]:
    scored: List[Tuple[CandidateRecipe, float, Dict[str, float]]] = []
    for c in cands:
        s_ing = c.ingredient_overlap_weight
        s_text = cosine_sparse(user_vec, c.recipe_text_tfidf) if user_vec else 0.0
        s_pop = c.popularity_score
        score = w_ing * s_ing + w_text * s_text + w_pop * s_pop
        scored.append((c, score, {"s_ing": s_ing, "s_text": s_text, "s_pop": s_pop}))
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
) -> List[Dict]:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        session_kwargs = {"database": database} if database else {}
        with driver.session(**session_kwargs) as session:
            cands = prefilter_and_candidates(
                session,
                ingredient_ids=ingredient_ids,
                cuisine=cuisine,
                max_cook_time=max_cook_time,
                limit_candidates=limit_candidates,
            )

            # Optional: filter out allergens/dislikes for a given user
            if user_id and cands:
                cand_ids = [c.recipe_id for c in cands]
                ok_ids = set(exclude_user_allergens_and_dislikes(session, user_id, cand_ids))
                cands = [c for c in cands if c.recipe_id in ok_ids]

            # Load user vector when present
            user_vec: Dict[str, float] = load_user_vector(session, user_id) if user_id else {}

        # score and rerank client-side
        scored = compute_scores(cands, user_vec=user_vec, w_ing=w_ing, w_text=w_text, w_pop=w_pop)
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
    parser = argparse.ArgumentParser(description="Recommend recipes via prefilter → candidate → 3 scores → combine → rerank")
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

    parser.add_argument("--json", action="store_true", help="Output JSON only")

    args = parser.parse_args()

    ing_ids = None
    if args.ing:
        ing_ids = [x.strip() for x in args.ing.split(",") if x.strip()]

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
    )

    if args.json:
        print(json.dumps({"results": results}, ensure_ascii=False, indent=2))
    else:
        for i, r in enumerate(results, 1):
            print(f"{i:2d}. {r['title']}  (id={r['recipe_id']}, cuisine={r['cuisine']}, cook={r['cook_time_min']})")
            s = r["scores"]
            print(f"     score={r['score']:.4f}   s_ing={s['s_ing']:.4f}  s_text={s['s_text']:.4f}  s_pop={s['s_pop']:.4f}")


if __name__ == "__main__":
    main()


