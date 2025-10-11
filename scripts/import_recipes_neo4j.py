import csv
import json
import re
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from neo4j import GraphDatabase

# ==========================================
# 🧩 BASIC TEXT UTILITIES
# ==========================================
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def normalize_text(value: str) -> str:
    """Normalize text: lowercase, remove non-alphanumeric chars, collapse spaces."""
    if value is None:
        return ""
    lowered = value.strip().lower()
    normalized = NON_ALNUM_PATTERN.sub(" ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def _simplify_token(token: str) -> str:
    """Simplify ingredient tokens to a core noun form."""
    token = re.sub(
        r"\b(green|red|white|yellow|fresh|dried|ground|powder|powdered|canned|chopped|diced|sliced|minced|softened)\b",
        " ",
        token,
    )
    token = re.sub(r"\s+", " ", token).strip()
    parts = token.split(" ")
    head = parts[-1] if parts else token
    # Plural → singular heuristics
    if head.endswith("ies"):
        head = head[:-3] + "i"
    elif head.endswith("oes"):
        head = head[:-2]
    elif head.endswith("es"):
        head = head[:-2]
    elif head.endswith("s") and len(head) > 3:
        head = head[:-1]
    return head


def tokenize_ingredients(raw: str) -> List[str]:
    """Tokenize and normalize the raw ingredient list."""
    if not raw:
        return []
    parts = re.split(r"[\n\r;,•|]+", raw)
    tokens: List[str] = []
    for p in parts:
        t = normalize_text(p)
        if not t:
            continue
        # Remove units and common words
        t = re.sub(r"\b(grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|oz|lb|pounds?)\b", " ", t)
        t = re.sub(r"\b(of|and|or|optional|can|slice|slices|teaspoon|tablespoon)\b", " ", t)
        t = re.sub(r"\d+[\./\d]*", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            head = _simplify_token(t)
            if head:
                tokens.append(head)
    return tokens

# ==========================================
# 🍜 CUISINE NORMALIZATION
# ==========================================
def normalize_cuisine_name(name: Optional[str]) -> Optional[str]:
    """Standardize cuisine names for consistency."""
    if not name:
        return None
    name = normalize_text(name)

    replacements = {
        "modern thai": "Thai",
        "portuguese inspired": "portuguese",
        "vietnam": "vietnamese",
        "viet nam": "vietnamese",
        "usa": "american",
        "us": "american",
        "latin america": "latin american",
        "western": "western",
        "asian": "asian",
    }

    return replacements.get(name, name.title())


def parse_cuisines(raw: Optional[str]) -> List[str]:
    """Split and normalize multiple cuisines from CSV field."""
    if not raw:
        return []
    parts = re.split(r"[,;/|]+", str(raw))
    cuisines: List[str] = []
    for c in parts:
        cname = normalize_cuisine_name(c.strip())
        if cname and cname not in cuisines:
            cuisines.append(cname)
    return cuisines



# ==========================================
# 🧮 STRING SIMILARITY (for fuzzy ingredient matching)
# ==========================================
def levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            insert_cost = cur[j - 1] + 1
            delete_cost = prev[j] + 1
            replace_cost = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(insert_cost, delete_cost, replace_cost))
        prev = cur
    return prev[-1]


def similarity_ratio(a: str, b: str) -> float:
    # Simple normalized edit similarity
    if not a and not b:
        return 1.0
    dist = levenshtein_distance(a, b)
    denom = max(len(a), len(b))
    if denom == 0:
        return 0.0
    return 1.0 - (dist / denom)



# ==========================================
# 🧾 INGREDIENT LABEL LOADING
# ==========================================
@dataclass
class IngredientLabel:
    ingredient_id: str
    canonical_name: str
    synonyms: List[str]


def load_label_set(path: Path) -> List[IngredientLabel]:
    """Load canonical ingredient names from a text file."""
    labels: List[IngredientLabel] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            name = normalize_text(line)
            if not name:
                continue
            slug = NON_ALNUM_PATTERN.sub("_", name).strip("_")
            labels.append(IngredientLabel(ingredient_id=f"ing_{slug}", canonical_name=name, synonyms=[]))
    return labels


def build_lookup(labels: List[IngredientLabel]) -> Tuple[Dict[str, str], List[IngredientLabel]]:
    """Build exact and synonym lookup maps."""
    exact: Dict[str, str] = {}
    for lab in labels:
        exact[lab.canonical_name] = lab.ingredient_id
        for s in lab.synonyms:
            exact[normalize_text(s)] = lab.ingredient_id
    return exact, labels


def map_ingredient(token: str, exact: Dict[str, str], labels: List[IngredientLabel], threshold: float) -> Optional[str]:
    if not token:
        return None
    # exact
    if token in exact:
        return exact[token]
    # fuzzy against canonical and synonyms
    best_id: Optional[str] = None
    best_score: float = 0.0
    for lab in labels:
        score = similarity_ratio(token, lab.canonical_name)
        if score > best_score:
            best_score = score
            best_id = lab.ingredient_id
        for syn in lab.synonyms:
            sscore = similarity_ratio(token, normalize_text(syn))
            if sscore > best_score:
                best_score = sscore
                best_id = lab.ingredient_id
    if best_id and best_score >= threshold:
        return best_id
    return None

# ==========================================
# 📂 CSV READER
# ==========================================
def read_csv_rows(csv_path: Path, verbose: bool = False):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    try:
        size_mb = round(csv_path.stat().st_size / (1024*1024), 2)
    except Exception:
        size_mb = None
    if verbose:
        print(f"[csv] opening {csv_path} size={size_mb}MB")

    encodings = ["utf-8-sig","utf-8", "latin-1"]
    last_err: Exception | None = None
    for enc in encodings:
        try:
            if verbose:
                print(f"[csv] try encoding={enc}")
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
            return
        except UnicodeDecodeError as e:
            last_err = e
            if verbose:
                print(f"[csv] decode failed for {enc}: {e}")
            continue
    # If we get here, all encodings failed
    if last_err:
        raise last_err


# ==========================================
# 🍽️ RECIPE PROPERTY BUILDER
# ==========================================
def build_recipe_props(row: Dict[str, str]) -> Dict:
    """Convert a CSV row into a dictionary of Neo4j node properties."""

    def parse_minutes(x: Optional[str]) -> Optional[int]:
        if not x:
            return None
        s = str(x).strip().lower()
        total = 0
        h = re.findall(r"(\d+)\s*h", s)
        if h:
            total += 60 * int(h[0])
        m = re.findall(r"(\d+)\s*m", s)
        if m:
            total += int(m[0])
        if total == 0:
            m3 = re.search(r"(\d+)", s)
            return int(m3.group(1)) if m3 else None
        return total

    def to_float(x: str) -> Optional[float]:
        try:
            return float(x) if x not in (None, "", "N/A") else None
        except Exception:
            return None

    def to_int(x: str) -> Optional[int]:
        try:
            return int(float(x))
        except Exception:
            return None

    tags = []
    if row.get("keywords"):
        tags = [normalize_text(t) for t in row["keywords"].split(",") if normalize_text(t)]

    return {
        "title": row.get("title") or "",
        "instructions": row.get("instructions") or "",
        "tags": tags,
        "cook_time_min": parse_minutes(row.get("cook_time")) or parse_minutes(row.get("total_time")),
        "servings": to_int(row.get("servings")),
        "cuisine": parse_cuisines(row.get("recipe_cuisine")),
        # Ratings
        "rating_avg": to_float(row.get("rating_value")),
        "rating_count": to_int(row.get("rating_count") or 0),
        "popularity_score": to_float(row.get("weighted_rating")) or to_float(row.get("rating_value")),
        # Nutrition & misc
        "nutrition_calories": to_float(row.get("calories")),
        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
        "allergens": [],
        # store popularity as scalar properties to satisfy Neo4j property type rules
        "popularity_views": 0,
        "popularity_saves": 0,
        "popularity_cooks": 0,
        "popularity_likes": 0,
        "cost_estimate": None,
        "equipment_needed": [],
        "video_url": None,
        "alternative_ingredients": [],
    }


# ==========================================
# 🧱 CYPHER BUILDER
# ==========================================
def build_cypher_batch(batch: List[Tuple[str, Dict, List[str], List[Dict]]]) -> str:
    """Construct Cypher query for batch import into Neo4j."""
    lines: List[str] = []
    lines.append("UNWIND $rows AS row")
    lines.append("MERGE (r:Recipe {recipe_id: row.recipe_id})")
    lines.append("SET r.title = row.props.title,")
    lines.append("    r.instructions = row.props.instructions,")
    lines.append("    r.tags = row.props.tags,")
    lines.append("    r.cook_time_min = row.props.cook_time_min,")
    lines.append("    r.servings = row.props.servings,")
    lines.append("    r.cuisine = row.props.cuisine,")
    lines.append("    r.rating_avg = row.props.rating_avg,")
    lines.append("    r.rating_count = row.props.rating_count,")
    lines.append("    r.image_urls = row.props.image_urls,")
    lines.append("    r.source_url = row.props.source_url,")
    lines.append("    r.recipe_category = row.props.recipe_category,")
    lines.append("    r.popularity_score = coalesce(row.props.popularity_score, 0),")
    lines.append("    r.popularity_views = coalesce(row.props.popularity_views,0),")
    lines.append("    r.popularity_saves = coalesce(row.props.popularity_saves,0),")
    lines.append("    r.popularity_cooks = coalesce(row.props.popularity_cooks,0),")
    lines.append("    r.popularity_likes = coalesce(row.props.popularity_likes,0),")
    lines.append("    r.nutrition_calories = row.props.nutrition_calories,")
    lines.append("    r.cost_estimate = row.props.cost_estimate,")
    lines.append("    r.equipment_needed = row.props.equipment_needed,")
    lines.append("    r.video_url = row.props.video_url,")
    lines.append("    r.alternative_ingredients = row.props.alternative_ingredients,")  
    lines.append("    r.allergens = row.props.allergens")
    lines.append("WITH r, row")
    lines.append("UNWIND coalesce(row.tags, []) AS tagName")
    lines.append("MERGE (t:Tag {name: tagName})")
    lines.append("MERGE (r)-[:TAGGED_AS]->(t)")
    lines.append("WITH r, row")
    lines.append("CALL { WITH r, row")
    lines.append("  UNWIND coalesce(row.ingredients, []) AS ing")
    lines.append("  MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})")
    lines.append("  MERGE (r)-[rel:HAS_INGREDIENT]->(i)")
    lines.append("  SET rel.qty = ing.qty, rel.unit = ing.unit, rel.optional = coalesce(ing.optional_flag,false), rel.prep = ing.prep")
    lines.append("  RETURN count(*) AS _")
    lines.append("}")
    lines.append("WITH r, row")
    lines.append("UNWIND coalesce(row.props.cuisine, []) AS cuisineName")
    lines.append("MERGE (cu:Cuisine {name: cuisineName})")
    lines.append("MERGE (r)-[:OF_CUISINE]->(cu)")
    return "\n".join(lines)


# ==========================================
# ⚙️ EXECUTION UTILITIES
# ==========================================
def run_cypher_shell(cypher: str, neo4j_uri: str, user: str, password: str) -> None:
    """Run Cypher query via cypher-shell."""
    proc = subprocess.Popen(
        ["cypher-shell.bat" if os.name == "nt" else "cypher-shell", "-a", neo4j_uri, "-u", user, "-p", password],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate(cypher)
    if proc.returncode != 0:
        raise RuntimeError(f"cypher-shell error: {err}\nOutput: {out}")


def run_via_driver(rows: List[Dict], *, uri: str, user: str, password: str, database: Optional[str]) -> None:
    """Send batched queries using the official Neo4j Python driver."""
    query = build_cypher_batch(rows)
    driver = GraphDatabase.driver(uri, auth=(user, password))
    try:
        session_kwargs = {"database": database} if database else {}
        with driver.session(**session_kwargs) as session:
            session.run(query, rows=rows).consume()
    finally:
        driver.close()


# ==========================================
# 🚀 MAIN FUNCTION
# ==========================================
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import recipes from CSV into Neo4j with ingredient mapping")
    parser.add_argument("--csv", type=str, default=str(Path("data/recipes/all_recipes_weighted.csv")), help="Path to all_recipes_weighted.csv")
    parser.add_argument("--labels", type=str, default=str(Path("data/ingredients/data.txt")), help="Path to canonical ingredient labels (56 items)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Fuzzy match threshold (0-1)")
    parser.add_argument("--neo4j-uri", type=str, default="bolt://localhost:7687")
    parser.add_argument("--neo4j-user", type=str, default="neo4j")
    parser.add_argument("--neo4j-pass", type=str, default="neo4j")
    parser.add_argument("--db", dest="database", type=str, default="food", help="Neo4j database name (default: food)")
    parser.add_argument("--use-driver", action="store_true", help="Use Neo4j Python driver for import (recommended)")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher only, do not execute")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N rows")
    parser.add_argument("--verbose", action="store_true", help="Print debug logs while processing")
    parser.add_argument("--log-every", type=int, default=1000, help="Log progress every N rows")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    labels_path = Path(args.labels)
    labels = load_label_set(labels_path)
    exact, label_list = build_lookup(labels)

    iterator = read_csv_rows(csv_path, verbose=args.verbose)
    batch_rows: List[Dict] = []
    cypher_batches: List[str] = []

    for idx, row in enumerate(iterator, 1):
        recipe_id = f"rec_{idx}"
        props = build_recipe_props(row)
        raw_ing = row.get("ingredients", "")
        tokens = tokenize_ingredients(raw_ing)

        mapped_ids = []
        for tok in tokens:
            ing_id = map_ingredient(tok, exact, label_list, args.threshold)
            if ing_id:
                mapped_ids.append(ing_id)

        # Remove duplicates while preserving order
        seen = set()
        mapped_unique = [x for x in mapped_ids if not (x in seen or seen.add(x))]

        ingredients_edges = [{"ingredient_id": iid, "qty": None, "unit": None, "optional_flag": False, "prep": None} for iid in mapped_unique]

        batch_rows.append({"recipe_id": recipe_id, "props": props, "tags": props.get("tags", []), "ingredients": ingredients_edges})


        if args.verbose and (idx <= 5 or (args.log_every and idx % args.log_every == 0)):
            preview_tokens = tokens[:10]
            preview_ing = (raw_ing[:140] + "...") if isinstance(raw_ing, str) and len(raw_ing) > 140 else raw_ing
            print(
                "[row] #{} title='{}' servings_raw='{}' cuisine='{}'\n      ingredients_raw='{}'\n      tokens={}\n      mapped_ids={}".format(
                    idx,
                    (props.get("title") or "")[:60],
                    row.get("servings"),
                    props.get("cuisine"),
                    preview_ing,
                    preview_tokens,
                    mapped_unique,
                )
            )
        # Batch processing
        if len(batch_rows) >= args.batch_size:
            if args.use_driver and not args.dry_run:
                run_via_driver(batch_rows, uri=args.neo4j_uri, user=args.neo4j_user, password=args.neo4j_pass, database=args.database)
            else:
                cypher = build_cypher_batch([])
                param_json = json.dumps({"rows": batch_rows})
                full = f":param rows => {param_json};\n{cypher}"
                cypher_batches.append(full)
                if not args.dry_run:
                    run_cypher_shell(full, args.neo4j_uri, args.neo4j_user, args.neo4j_pass)
            batch_rows = []

    # Final leftover batch
    if batch_rows:
        if args.use_driver and not args.dry_run:
            run_via_driver(batch_rows, uri=args.neo4j_uri, user=args.neo4j_user, password=args.neo4j_pass, database=args.database)
        else:
            cypher = build_cypher_batch([])
            param_json = json.dumps({"rows": batch_rows})
            full = f":param rows => {param_json};\n{cypher}"
            cypher_batches.append(full)
            if not args.dry_run:
                run_cypher_shell(full, args.neo4j_uri, args.neo4j_user, args.neo4j_pass)

    # --- KEEP THIS BLOCK EXACTLY AS YOU REQUESTED ---
    if args.dry_run: 
        # Save output to file for review
        out_path = Path("data/recipes/recipes_import.cypher")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n\n".join(cypher_batches), encoding="utf-8")
        print(f"[dry-run] wrote Cypher preview to {out_path} (batches={len(cypher_batches)})")

    print("✅ Import completed!")


if __name__ == "__main__":
    main()
