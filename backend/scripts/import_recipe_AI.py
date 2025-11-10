#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import recipes from CSV into Neo4j, with smart ingredient mapping:
- Exact/fuzzy (Levenshtein) match first
- Semantic fallback (SentenceTransformer "paraphrase-MiniLM-L6-v2") for tokens not matched

Usage (ví dụ):
  python import_recipes_neo4j.py \
    --csv data/recipes/full_data_ing.csv \
    --labels data/ingredients/ingredients.json \
    --use-driver \
    --semantic \
    --threshold 0.80 \
    --semantic-threshold 0.78 \
    --verbose

Yêu cầu:
  pip install sentence-transformers torch neo4j
"""

import csv
import json
import re
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from turtle import title
from typing import Dict, List, Optional, Tuple

from neo4j import GraphDatabase
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import NON_ING_WORDS, FIX_MAP,ALT_MAP, PACKING_PATTERNS, COMPOUND_INGREDIENTS, DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

# ===== Optional: semantic fallback (có cài mới dùng) =====
_HAS_SEMANTIC = True
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
except Exception:
    _HAS_SEMANTIC = False


# ==========================================
# 🧩 BASIC TEXT UTILITIES
# ==========================================



def preprocess_compound_phrases(text: str) -> str:
    """Giữ nguyên các cụm đặc biệt trước khi tokenize."""
    for phrase in COMPOUND_INGREDIENTS:
        safe = phrase.replace(" ", "_")
        # Bắt cả dạng số nhiều (hot dogs)
        pattern = rf"\b{re.escape(phrase)}s?\b"
        text = re.sub(pattern, safe, text, flags=re.IGNORECASE)
    return text

# Một số FIX phổ biến để tăng chất lượng token
FIX_MAP_TOKEN = {

}

def normalize_text(value: str) -> str:
    """Normalize text: lowercase, remove non-alphanumeric chars, collapse spaces."""
    if value is None:
        return ""
    lowered = value.strip().lower()
    # ⚠️ CHỈNH DÒNG NÀY:
    normalized = re.sub(r"[^a-z0-9_]+", " ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def _simplify_token(token: str) -> str:
    token = re.sub(r"\b(green|red|white|yellow|fresh|dried|chopped|sliced|minced|softened|unsalted|salted|well|drained)\b", " ", token)
    token = re.sub(r"\s+", " ", token).strip()
    if token.endswith("ies"):
        token = token[:-3] + "y"
    elif token.endswith("es"):
        token = token[:-2]
    elif token.endswith("s"):
        token = token[:-1]
    return token.strip()

def strip_packing_phrases(s: str) -> str:
    """Xử lý 'in brine', 'packed in oil', 'well drained'... → giữ nguyên phần chính"""
    s = re.sub(r"\s*,\s*", " ", s)
    for pat in PACKING_PATTERNS:
        s = re.sub(pat, "", s)
    m = re.search(r"^(.*?)(?:\s+packed\s+in\s+|\s+in\s+)(?:oil|water|brine|juice|syrup)\b.*$", s)
    if m:
        s = m.group(1).strip()
    return re.sub(r"\s+", " ", s).strip()

def _simplify_token(token: str) -> str:
    """Simplify ingredient tokens to a core noun form."""
    # Bỏ các tính chất miêu tả thường gặp
    token = re.sub(
        r"\b(green|red|white|yellow|fresh|dried|ground|powder|powdered|canned|chopped|diced|sliced|minced|softened|lower|sodium|unsalted|salted|well|drained|dry)\b",
        " ",
        token,
    )
    # dính từ phổ biến


    token = re.sub(r"\s+", " ", token).strip()
    parts = token.split(" ")
    head = parts[-1] if parts else token

    # Heuristic plural→singular
    if head.endswith("ies"):
        head = head[:-3] + "i"
    elif head.endswith("oes"):
        head = head[:-2]
    elif head.endswith("es"):
        head = head[:-2]
    elif head.endswith("s"):
        head = head[:-1]

    # Áp FIX_MAP
    head = FIX_MAP_TOKEN.get(head, head)
    head = head.replace("_", " ")
    return head


def tokenize_ingredients(raw: str) -> List[str]:
    """Tokenize & normalize nguyên liệu với rule tổng quát (fix 'capers in brine', '... well drained', etc.)."""
    if not raw:
        return []
    raw = preprocess_compound_phrases(raw) 
    
    parts = re.split(r"[\n\r;,•|]+", raw)
    tokens: List[str] = []

    # Các nhóm khái quát
    MEAT_FISH = {
        "beef","pork","chicken","duck","lamb","turkey","bacon","ham","sausage","prosciutto","pancetta",
        "brisket","meatball","steak","salami","rib","tenderloin","cutlet","sirloin",
        "fish","salmon","tuna","shrimp","crab","mussel","scallop","crawfish","fillet","bronzino","crabmeat","katsuobushi"
    }
    OIL_BASE = {
        "oil"
    }
    POWDER_ENDINGS = {"powder","powdered","ground","crushed"}
    SEASONING_ENDINGS = {"seasoning","spice","mix","rub","blend","masala","curry","salt","pepper"}

    for p in parts:
        t = normalize_text(p)
        if not t:
            continue

        # Loại đơn vị/số lượng
        t = re.sub(r"\b(grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|oz|lb|pounds?|packages?)\b", " ", t)
        t = re.sub(r"\d+[\./\d]*", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if not t:
            continue

        # ⚠️ CẮT 'in brine / packed in / well drained' GIỮ HẠT CHÍNH (capers, olives, …)
        t = strip_packing_phrases(t)
        if not t:
            continue
        
        lower = f" {t} "
        if re.search(r"\b(\w+\s+)?salt\b", lower):
            tokens.append("salt")
            continue
            
        # 💡 Phát hiện cụm '... with ... and ...' (ví dụ: 'tomatoes with basil garlic and olive oil')
        if " with " in t or " and " in t:
            sub_parts = re.split(r"\bwith\b|\band\b|,|&", t)
            sub_tokens = []
            for sub in sub_parts:
                sub = sub.strip()
                if not sub:
                    continue
                # normalize lại để tách nhiều nguyên liệu con
                sub = re.sub(r"\s+", " ", sub)
                # nếu có nhiều từ (như 'olive oil'), tách rule riêng phía sau
                sub_tokens.append(sub)
            # nếu có nhiều nguyên liệu con → xử lý từng cái
            if len(sub_tokens) > 1:
                for sub in sub_tokens:
                    sub_lower = f" {sub} "
                    mapped = None

                    # match lại từng phần theo rule cũ
                    # → giữ nguyên xử lý thịt/cá, dầu, seasoning, powder…
                    # sử dụng _simplify_token() để rút gọn
                    if any(x in sub_lower for x in [" oil ", "olive oil", "sesame oil"]):
                        tokens.append("oil")
                    elif any(x in sub_lower for x in ["tomato", "basil", "garlic", "onion"]):
                        tokens.append(_simplify_token(sub))
                    else:
                        tokens.append(_simplify_token(sub))
                continue


        lower = f" {t} "

        # Bỏ những từ không phải nguyên liệu (đề phòng lọt)
        if t in NON_ING_WORDS:
            continue

        mapped = None

        # 1) Thịt/cá → lấy danh từ chính (salmon fillet → salmon)
        for k in MEAT_FISH:
            if f" {k} " in lower:
                # Ưu tiên tên cụ thể nếu có (salmon/tuna/shrimp/crab/…)
                specific = [x for x in ("salmon","tuna","shrimp","crab","mussel","scallop","fish","chicken","beef","pork","duck","lamb","turkey") if f" {x} " in lower]
                mapped = specific[0] if specific else k
                break

        # 2) Dầu/mỡ → ‘almond oil’, ‘olive oil’, ‘ghee’ → 'oil'
        if not mapped and " oil " in lower:
                mapped = "oil"

        # 3) Bột/gia vị dạng bột → 'garlic powder' → 'garlic'
        if not mapped and any(f" {end} " in lower or lower.endswith(f" {end}") for end in POWDER_ENDINGS):
            main = re.sub(r"\b(powder|powdered|ground|crushed)\b", "", t).strip()
            main = re.sub(r"\s+", " ", main)
            mapped = _simplify_token(main)

        # 4) Hỗn hợp gia vị / seasoning → 'furikake seasoning' → 'furikake'
        if not mapped and any(f" {end} " in lower or lower.endswith(f" {end}") for end in SEASONING_ENDINGS):
            main = re.sub(r"\b(seasoning|spice|mix|rub|blend|masala|curry|salt|pepper)\b", "", t).strip()
            main = re.sub(r"\s+", " ", main)
            mapped = _simplify_token(main)

        if not mapped and any(f" {end} " in lower or lower.endswith(f" {end}") for end in SEASONING_ENDINGS):
            main = re.sub(r"\b(seasoning|spice|mix|rub|blend|masala|curry|salt|pepper)\b", "", t).strip()
            main = re.sub(r"\s+", " ", main)
            mapped = _simplify_token(main)

        # 4.5) Soup dạng 'tomato soup' → 'tomato', 'pumpkin soup' → 'pumpkin', 

        if not mapped and " soup" in lower:
            # loại bỏ từ 'soup' hoặc 'soups'
            main = re.sub(r"\b(soup|soups)\b", "", t).strip()
            # nếu vẫn còn danh từ (ví dụ 'tomato'), giữ lại nó
            if main:
                mapped = _simplify_token(main)
            # nếu chỉ còn trống hoặc chung chung (instant soup) → để là 'soup'
            else:
                mapped = "soup"
        # 5) Các cụm đặc biệt
        if not mapped:
            # olive oil 
            if " olive " in lower and " oil " in lower:
                mapped = "oil"
            # chicken breast/thigh/tenderloin…
            elif " chicken " in lower and any(w in lower for w in [" breast "," thigh "," tenderloin "," drumstick "]):
                mapped = "chicken"

        # 6) Fallback chung
        if not mapped:
            mapped = _simplify_token(t)

        # Bỏ token rỗng hoặc noise cuối cùng (phòng hờ)
        if not mapped or mapped in NON_ING_WORDS:
            continue

        tokens.append(mapped)

    # unique giữ thứ tự
    return list(dict.fromkeys(tokens))


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
    """Load canonical ingredient names from a text file (one name per line)."""
    labels: List[IngredientLabel] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            name = normalize_text(line)
            if not name:
                continue
            slug = NON_ALNUM_PATTERN.sub("_", name).strip("_")
            labels.append(IngredientLabel(ingredient_id=f"ing_{slug}", canonical_name=name, synonyms=[]))
    return labels


def load_label_json(path: Path) -> List[IngredientLabel]:
    """Load canonical ingredient names from a JSON list with fields id, canonical, alt."""
    data = json.loads(path.read_text(encoding="utf-8"))
    labels: List[IngredientLabel] = []
    for obj in data:
        # chấp nhận cả 'canonical_name' hoặc 'canonical'
        canonical = normalize_text(obj.get("canonical_name") or obj.get("canonical") or "")
        if not canonical:
            continue
        iid = obj.get("ingredient_id") or obj.get("id") or f"ing_{NON_ALNUM_PATTERN.sub('_', canonical).strip('_')}"
        synonyms = obj.get("alt") or obj.get("alt_names") or []
        syn_norm = [normalize_text(s) for s in synonyms if s]
        labels.append(IngredientLabel(ingredient_id=iid, canonical_name=canonical, synonyms=syn_norm))
    return labels


def build_lookup(labels: List[IngredientLabel]) -> Tuple[Dict[str, str], List[IngredientLabel]]:
    """Build exact and synonym lookup maps."""
    exact: Dict[str, str] = {}
    for lab in labels:
        exact[normalize_text(lab.canonical_name)] = lab.ingredient_id
        for s in lab.synonyms:
            exact[normalize_text(s)] = lab.ingredient_id
    return exact, labels


def map_ingredient(token: str, exact: Dict[str, str], labels: List[IngredientLabel], threshold: float) -> Optional[str]:
    if not token:
        return None
    tok = normalize_text(token)
    # exact
    if tok in exact:
        return exact[tok]
    # fuzzy against canonical and synonyms
    best_id: Optional[str] = None
    best_score: float = 0.0
    for lab in labels:
        score = similarity_ratio(tok, lab.canonical_name)
        if score > best_score:
            best_score = score
            best_id = lab.ingredient_id
        for syn in lab.synonyms:
            sscore = similarity_ratio(tok, normalize_text(syn))
            if sscore > best_score:
                best_score = sscore
                best_id = lab.ingredient_id
    if best_id and best_score >= threshold:
        return best_id
    return None


# ==========================================
# 🔤 SEMANTIC FALLBACK (optional)
# ==========================================
def semantic_prepare(label_list: List[IngredientLabel], device: Optional[str] = None):
    if not _HAS_SEMANTIC:
        raise RuntimeError("sentence-transformers/torch not installed.")
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(torch.device(device))
    label_names = [lab.canonical_name for lab in label_list]
    label_embeds = model.encode(label_names, convert_to_tensor=True, normalize_embeddings=True, batch_size=256)
    if device == "cuda":
        label_embeds = label_embeds.to(torch.device("cuda"))
    return model, label_embeds


def semantic_fallback_batch(tokens: List[str],
                            model: "SentenceTransformer",
                            label_embeds: "torch.Tensor",
                            label_list: List[IngredientLabel],
                            threshold: float = 0.78) -> Dict[str, Optional[str]]:
    """Return map token → ingredient_id (or None) using embeddings."""
    if not tokens:
        return {}
    qs = [normalize_text(t) for t in tokens]
    q_embs = model.encode(qs, convert_to_tensor=True, normalize_embeddings=True, batch_size=128)
    if label_embeds.is_cuda:
        q_embs = q_embs.to(torch.device("cuda"))
    cos = util.cos_sim(q_embs, label_embeds)  # B x N
    best_idx = torch.argmax(cos, dim=1)       # B
    best_scores = torch.gather(cos, 1, best_idx.unsqueeze(1)).squeeze(1)  # B
    out: Dict[str, Optional[str]] = {}
    for i, tok in enumerate(tokens):
        score = float(best_scores[i].item())
        idx = int(best_idx[i].item())
        out[tok] = label_list[idx].ingredient_id if score >= threshold else None
    return out


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

    encodings = ["utf-8-sig", "utf-8", "latin-1"]
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
            return int(float(x)) if x not in (None, "", "N/A") else None
        except Exception:
            return None

    tags = []
    if row.get("recipe_category"):
        tags = [normalize_text(row["recipe_category"])]

    return {
        # Basic info
        "title": row.get("title") or "",
        "description": row.get("description") or "",
        "instructions": row.get("instructions") or "",
        "tags": tags,

        # Times
        "prep_time_min": parse_minutes(row.get("prep_time")),
        "cook_time_min": parse_minutes(row.get("cook_time")),
        "total_time_min": parse_minutes(row.get("total_time")),

        # Meta
        "servings": to_int(row.get("servings")),
        "yield": row.get("yield"),
        "cuisine": parse_cuisines(row.get("recipe_cuisine")),
        "recipe_category": row.get("recipe_category"),
        "source_url": row.get("url"),

        # Ratings
        "rating_avg": to_float(row.get("rating_value")),
        "rating_count": to_int(row.get("rating_count")),
        "review_count": to_int(row.get("review_count")),

        # Popularity counters (default 0)
        "popularity_views": 0,
        "popularity_likes": 0,

        # Nutrition
        "nutrition_calories": to_float(row.get("calories")),
        "nutrition_protein": to_float(row.get("protein")),
        "nutrition_fat": to_float(row.get("fat")),
        "nutrition_carbohydrate": to_float(row.get("carbohydrate")),
        "nutrition_fiber": to_float(row.get("fiber")),
        "nutrition_sugar": to_float(row.get("sugar")),
        "nutrition_sodium": to_float(row.get("sodium")),

        # Media
        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
    }


# ==========================================
# 🧱 CYPHER BUILDER
# ==========================================
def build_cypher_batch(_: List[Dict]) -> str:
    """Construct Cypher query for batch import into Neo4j (params come in $rows)."""
    lines: List[str] = []
    lines.append("UNWIND $rows AS row")
    lines.append("MERGE (r:Recipe {recipe_id: row.recipe_id})")
    lines.append("SET r.title = row.props.title,")
    lines.append("    r.description = row.props.description,")
    lines.append("    r.instructions = row.props.instructions,")
    lines.append("    r.tags = row.props.tags,")
    lines.append("    r.prep_time_min = row.props.prep_time_min,")
    lines.append("    r.cook_time_min = row.props.cook_time_min,")
    lines.append("    r.total_time_min = row.props.total_time_min,")
    lines.append("    r.servings = row.props.servings,")
    lines.append("    r.yield = row.props.yield,")
    lines.append("    r.cuisine = row.props.cuisine,")
    lines.append("    r.recipe_category = row.props.recipe_category,")
    lines.append("    r.source_url = row.props.source_url,")
    lines.append("    r.rating_avg = row.props.rating_avg,")
    lines.append("    r.rating_count = row.props.rating_count,")
    lines.append("    r.review_count = row.props.review_count,")
    lines.append("    r.popularity_views = coalesce(row.props.popularity_views,0),")
    lines.append("    r.popularity_saves = coalesce(row.props.popularity_saves,0),")
    lines.append("    r.popularity_cooks = coalesce(row.props.popularity_cooks,0),")
    lines.append("    r.popularity_likes = coalesce(row.props.popularity_likes,0),")
    lines.append("    r.nutrition_calories = row.props.nutrition_calories,")
    lines.append("    r.nutrition_protein = row.props.nutrition_protein,")
    lines.append("    r.nutrition_fat = row.props.nutrition_fat,")
    lines.append("    r.nutrition_carbohydrate = row.props.nutrition_carbohydrate,")
    lines.append("    r.nutrition_fiber = row.props.nutrition_fiber,")
    lines.append("    r.nutrition_sugar = row.props.nutrition_sugar,")
    lines.append("    r.nutrition_sodium = row.props.nutrition_sodium,")
    lines.append("    r.image_urls = row.props.image_urls")
    lines.append("WITH r, row")

    # Tag relationships
    lines.append("UNWIND coalesce(row.tags, []) AS tagName")
    lines.append("MERGE (t:Tag {name: tagName})")
    lines.append("MERGE (r)-[:TAGGED_AS]->(t)")
    lines.append("WITH r, row")

    # Ingredient relationships
    lines.append("CALL { WITH r, row")
    lines.append("  UNWIND coalesce(row.ingredients, []) AS ing")
    lines.append("  MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})")
    lines.append("  MERGE (r)-[rel:HAS_INGREDIENT]->(i)")
    lines.append("  SET rel.qty = ing.qty, rel.unit = ing.unit, rel.optional = coalesce(ing.optional_flag,false), rel.prep = ing.prep")
    lines.append("  RETURN count(*) AS _")
    lines.append("}")
    lines.append("WITH r, row")

    # Cuisine relationships
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
    """Send batched queries using the official Neo4j Python driver (with retry)."""
    query = build_cypher_batch(rows)
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session_kwargs = {"database": database} if database else {}
    for attempt in range(3):
        try:
            with driver.session(**session_kwargs) as session:
                session.run(query, rows=rows).consume()
            print(f"[neo4j] batch inserted successfully ({len(rows)} rows)")
            break
        except Exception as e:
            print(f"[retry] Neo4j error at batch ({attempt+1}/3): {e}")
            import time
            time.sleep(2)
    driver.close()



# ==========================================
# 🚀 MAIN FUNCTION
# ==========================================
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import recipes from CSV into Neo4j with ingredient mapping (fuzzy + semantic fallback)")
    parser.add_argument("--csv", type=str, default=str(Path("data/recipes/full_data_ing.csv")), help="Path to CSV with recipes")
    parser.add_argument("--labels", type=str, default=str(Path("data/ingredients/ingredients.json")), help="Path to ingredient labels (.json or .txt)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Fuzzy (Levenshtein) match threshold (0-1)")
    parser.add_argument("--semantic", action="store_true", help="Enable semantic fallback with SentenceTransformer")
    parser.add_argument("--semantic-threshold", type=float, default=0.78, help="Cosine threshold for semantic fallback (0-1)")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASS)
    parser.add_argument("--db", dest="database", default=DEFAULT_DB)
    parser.add_argument("--use-driver", action="store_true", help="Use Neo4j Python driver for import (recommended)")
    parser.add_argument("--batch-size", type=int, default=500)
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher only, do not execute")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N rows")
    parser.add_argument("--verbose", action="store_true", help="Print debug logs while processing")
    parser.add_argument("--log-every", type=int, default=1000, help="Log progress every N rows")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    labels_path = Path(args.labels)

    # Load labels (json ưu tiên)
    if labels_path.suffix.lower() == ".json":
        label_list = load_label_json(labels_path)
    else:
        label_list = load_label_set(labels_path)
    exact, label_list = build_lookup(label_list)

    # Semantic init (nếu bật)
    model = None
    label_embeds = None
    if args.semantic:
        if not _HAS_SEMANTIC:
            raise RuntimeError("Bạn bật --semantic nhưng chưa cài sentence-transformers/torch.")
        if args.verbose:
            print("[semantic] initializing model & encoding label embeddings…")
        model, label_embeds = semantic_prepare(label_list)
        if args.verbose:
            device = "cuda" if (hasattr(label_embeds, "is_cuda") and label_embeds.is_cuda) else "cpu"
            print(f"[semantic] ready (device={device}, labels={len(label_list)})")

    iterator = read_csv_rows(csv_path, verbose=args.verbose)
    batch_rows: List[Dict] = []
    cypher_batches: List[str] = []
    
    for idx, row in enumerate(iterator, 1):
        try:
            if args.limit and idx > args.limit:
                break
            # title = (row.get("title") or "").lower()
            # if "baked chili hot dog" not in title:
            #     continue

            recipe_id = f"rec_{idx}"
            props = build_recipe_props(row)
            raw_ing = row.get("ingredients", "")
            tokens = tokenize_ingredients(raw_ing)

            # 1️⃣ exact/fuzzy trước
            mapped_first: Dict[str, Optional[str]] = {}
            unmatched: List[str] = []
            for tok in tokens:
                ing_id = map_ingredient(tok, exact, label_list, args.threshold)
                if ing_id:
                    mapped_first[tok] = ing_id
                else:
                    unmatched.append(tok)
                    mapped_first[tok] = None

            # 2️⃣ semantic fallback cho unmatched
            sem_map: Dict[str, Optional[str]] = {}
            if args.semantic and unmatched:
                sem_map = semantic_fallback_batch(unmatched, model, label_embeds, label_list, threshold=args.semantic_threshold)

            # 3️⃣ gom kết quả theo thứ tự, loại trùng
            seen = set()
            mapped_ids: List[str] = []
            for tok in tokens:
                ing_id = mapped_first.get(tok) or sem_map.get(tok)
                if ing_id and ing_id not in seen:
                    mapped_ids.append(ing_id)
                    seen.add(ing_id)

            ingredients_edges = [{"ingredient_id": iid, "qty": None, "unit": None, "optional_flag": False, "prep": None} for iid in mapped_ids]
            batch_rows.append({"recipe_id": recipe_id, "props": props, "tags": props.get("tags", []), "ingredients": ingredients_edges})

            # Logging
            if args.verbose and (idx <= 20 or (args.log_every and idx % args.log_every == 0)):
                preview_tokens = tokens[:12]
                preview_ing = (raw_ing[:140] + "...") if isinstance(raw_ing, str) and len(raw_ing) > 140 else raw_ing
                print(f"[row] #{idx} title='{(props.get('title') or '')[:60]}' servings_raw='{row.get('servings')}' cuisine='{props.get('cuisine')}'")
                print(f"      ingredients_raw='{preview_ing}'")
                print(f"      tokens={preview_tokens}")
                print(f"      mapped_ids={mapped_ids}")
                if args.semantic and unmatched:
                    rescued = [t for t in unmatched if sem_map.get(t)]
                    missed = [t for t in unmatched if not sem_map.get(t)]
                    if rescued:
                        print(f"      [semantic] rescued={[(t, sem_map[t]) for t in rescued]}")
                    if missed:
                        print(f"      [warn] unmatched(after semantic)={missed[:10]}{'...' if len(missed)>10 else ''}")

            # Batch flush
            if len(batch_rows) >= args.batch_size:
                print(f"[batch] importing up to row #{idx} (size={len(batch_rows)})")
                if args.use_driver and not args.dry_run:
                    run_via_driver(batch_rows, uri=args.uri, user=args.user, password=args.password, database=args.database)

                else:
                    cypher = build_cypher_batch([])
                    param_json = json.dumps({"rows": batch_rows})
                    full = f":param rows => {param_json};\n{cypher}"
                    cypher_batches.append(full)
                    if not args.dry_run:
                        run_cypher_shell(full, args.uri, args.user, args.password)

                batch_rows = []

        except Exception as e:
            print(f"[error] row #{idx}: {e}")
            continue


    # Final leftover batch
    if batch_rows:
        if args.use_driver and not args.dry_run:
            run_via_driver(batch_rows, uri=args.uri, user=args.user, password=args.password, database=args.database)
        else:
            cypher = build_cypher_batch([])
            param_json = json.dumps({"rows": batch_rows})
            full = f":param rows => {param_json};\n{cypher}"
            cypher_batches.append(full)
            if not args.dry_run:
                run_cypher_shell(full, args.uri, args.user, args.password)

    # Preview file nếu dry-run
    if args.dry_run:
        out_path = Path("data/recipes/recipes_import.cypher")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text("\n\n".join(cypher_batches), encoding="utf-8")
        print(f"[dry-run] wrote Cypher preview to {out_path} (batches={len(cypher_batches)})")

    print("✅ Import completed!")


if __name__ == "__main__":
    main()
