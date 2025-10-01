import math
import re
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

from neo4j import GraphDatabase


WORD_RE = re.compile(r"[a-z0-9]+")


def normalize_text(s: str) -> List[str]:
    if not s:
        return []
    s = s.lower()
    return WORD_RE.findall(s)


@dataclass
class RecipeDoc:
    recipe_id: str
    ingredient_ids: List[str]
    text_tokens: List[str]


def fetch_recipes(tx) -> List[RecipeDoc]:
    q = (
        """
        MATCH (r:Recipe)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH r, collect(i.ingredient_id) AS ingIds
        RETURN r.recipe_id AS id,
               coalesce(r.title,'') AS title,
               coalesce(r.tags, []) AS tags,
               coalesce(r.instructions,'') AS instr,
               coalesce(r.cuisine,'') AS cuisine,
               ingIds AS ing
        """
    )
    rows = tx.run(q)
    out: List[RecipeDoc] = []
    for row in rows:
        text = " ".join([
            row["title"],
            " ".join(row["tags"]),
            row["instr"][:500],
            row["cuisine"],
        ])
        out.append(RecipeDoc(
            recipe_id=row["id"],
            ingredient_ids=[x for x in row["ing"] if x],
            text_tokens=normalize_text(text),
        ))
    return out


def compute_idf(docs: List[List[str]]) -> Dict[str, float]:
    N = len(docs)
    df = Counter()
    for doc in set(tuple(d) for d in docs):
        # Using per-doc set to avoid multiple counts in same doc
        for token in set(doc):
            df[token] += 1
    idf: Dict[str, float] = {}
    for t, dfi in df.items():
        idf[t] = math.log(1.0 + (N / max(dfi, 1)))
    return idf


def compute_tfidf(tokens: List[str], idf: Dict[str, float]) -> Dict[str, float]:
    tf = Counter(tokens)
    if not tf:
        return {}
    # l2 normalize
    vec: Dict[str, float] = {}
    for t, c in tf.items():
        vec[t] = (c / len(tokens)) * idf.get(t, 0.0)
    # normalize
    norm = math.sqrt(sum(v * v for v in vec.values())) or 1.0
    for k in list(vec.keys()):
        vec[k] /= norm
    return vec


def l2_normalize_map(values: Dict[str, float]) -> Dict[str, float]:
    norm = math.sqrt(sum(v * v for v in values.values())) or 1.0
    return {k: v / norm for k, v in values.items()}


def as_list(vec: Dict[str, float]) -> List[Tuple[str, float]]:
    return sorted(vec.items(), key=lambda kv: kv[1], reverse=True)[:512]


def store_recipe_vectors(tx, recipe_id: str, ingredient_weights: Dict[str, float], text_tfidf: Dict[str, float]):
    terms = list(text_tfidf.keys())
    weights = [float(text_tfidf[t]) for t in terms]
    q = (
        """
        MATCH (r:Recipe {recipe_id: $rid})
        SET r.text_terms = $terms,
            r.text_weights = $weights
        RETURN r.recipe_id AS id
        """
    )
    tx.run(q, rid=recipe_id, terms=terms, weights=weights)


def _set_ing_edge_weights(tx, recipe_id: str, pairs: List[Dict[str, float]]):
    # Set per-ingredient IDF weight on HAS_INGREDIENT edges for a given recipe
    q = (
        """
        MATCH (r:Recipe {recipe_id: $rid})
        WITH r
        UNWIND $pairs AS p
        MATCH (r)-[rel:HAS_INGREDIENT]->(i:Ingredient {ingredient_id: p.iid})
        SET rel.idf_weight = p.w
        RETURN count(rel) AS updated
        """
    )
    tx.run(q, rid=recipe_id, pairs=pairs)


def _store_ingredient_stats(tx, total_docs: int, stats: List[Dict[str, float]]):
    # Store global DF/IDF and corpus size on Ingredient nodes
    q = (
        """
        UNWIND $stats AS s
        MATCH (i:Ingredient {ingredient_id: s.iid})
        SET i.doc_freq = s.df,
            i.ing_idf = s.idf,
            i.total_docs = $N
        RETURN count(i) AS updated
        """
    )
    tx.run(q, stats=stats, N=total_docs)


def aggregate_user_profile(tx):
    # Build user profiles: weighted by event type and time decay (90d half-life)
    q = (
        """
        MATCH (u:User)-[iv:INTERACTED_WITH]->(r:Recipe)
        WHERE r.text_terms IS NOT NULL AND r.text_weights IS NOT NULL AND size(r.text_terms) = size(r.text_weights) AND size(r.text_terms) > 0
        WITH u, iv, r
        WITH u, r,
             CASE iv.event_type WHEN 'cook' THEN 1.0 WHEN 'save' THEN 0.6 ELSE 0.3 END AS w,
             duration.between(datetime(iv.timestamp), datetime()).days AS daysAgo
        WITH u, w * exp(-log(2) * toFloat(daysAgo) / 90.0) AS weight, r
        WITH u, weight, r, range(0, size(r.text_terms)-1) AS idxs
        UNWIND idxs AS k
        WITH u, r.text_terms[k] AS term, (weight * coalesce(r.text_weights[k],0.0)) AS contrib
        WITH u, term, sum(contrib) AS val
        WITH u, collect([term, val]) AS vec
        WITH u, vec,
             [x IN vec | x[0]] AS terms,
             [x IN vec | x[1]] AS weights
        SET u.user_terms = terms,
            u.user_weights = weights
        """
    )
    tx.run(q)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Compute ingredient IDF, recipe TF-IDF, and user profiles")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="neo4j")
    parser.add_argument("--db", dest="database", default="food")
    args = parser.parse_args()

    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    session_kwargs = {"database": args.database} if args.database else {}
    with driver.session(**session_kwargs) as session:
        recipes = session.read_transaction(fetch_recipes)

        # Ingredient IDF on ingredient_id tokens per recipe
        ing_docs = [doc.ingredient_ids for doc in recipes]
        # Compute DF and IDF for ingredients
        df_counter = Counter()
        for doc in ing_docs:
            for t in set(doc):
                df_counter[t] += 1
        total_docs = len(ing_docs)
        ing_idf = {t: math.log(1.0 + (total_docs / max(df_counter[t], 1))) for t in df_counter}

        # Text IDF on tokens
        text_docs = [doc.text_tokens for doc in recipes]
        text_idf = compute_idf(text_docs)

        # Store per-recipe vectors
        for doc in recipes:
            ing_weights = {ing: ing_idf.get(ing, 0.0) for ing in set(doc.ingredient_ids)}
            text_vec = compute_tfidf(doc.text_tokens, text_idf)
            session.write_transaction(store_recipe_vectors, doc.recipe_id, ing_weights, text_vec)
            # Annotate inverted index edges with IDF weight for efficient traversal
            if doc.ingredient_ids:
                pairs = [{"iid": ing, "w": float(ing_idf.get(ing, 0.0))} for ing in set(doc.ingredient_ids)]
                session.write_transaction(_set_ing_edge_weights, doc.recipe_id, pairs)

        # Store DF/IDF on Ingredient nodes for global stats
        if df_counter:
            stats = [{"iid": iid, "df": int(df_counter[iid]), "idf": float(ing_idf.get(iid, 0.0))} for iid in df_counter.keys()]
            session.write_transaction(_store_ingredient_stats, total_docs, stats)

        # Aggregate user profile vectors (TF-IDF)
        session.write_transaction(aggregate_user_profile)

    driver.close()


if __name__ == "__main__":
    main()


