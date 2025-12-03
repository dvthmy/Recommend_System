#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
FAST VERSION: Import recipes from CSV into Neo4j with optimized ingredient mapping
- Focuses on speed over perfect accuracy
- Simplified exact matching only
- No semantic fallback (optional)
- Streamlined logic for maximum performance

Usage for fast import:
  python import_recipe_AI_fast.py \
    --csv data/recipes/full_data_ing.csv \
    --labels data/ingredients/canonical_ingredients_migrated.json \
    --out-cypher recipes_fast.cypher \
    --batch-size 10000

Expected performance: 50-200 rows/sec (vs 0.3 rows/sec original)
"""

import csv
import json
import re
import os
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from neo4j import GraphDatabase
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import NON_ING_WORDS, FIX_MAP, COMPOUND_INGREDIENTS, DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

# Simple regex patterns (only essential ones)
REGEX_WHITESPACE = re.compile(r'\s+')
REGEX_NON_ALNUM_SPACE = re.compile(r"[^a-z0-9_]+")
REGEX_INGREDIENT_SEPARATORS = re.compile(r"[\n\r;,•|]+")
REGEX_NUMBERS_UNITS = re.compile(r"\b\d+[\./\d]*(?:grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|oz|lb|pounds?|packages?|inch|inches)?\b", re.IGNORECASE)
REGEX_PREP_WORDS = re.compile(r"\b(chopped|diced|sliced|minced|grated|crushed|ground|fresh|frozen|dried|optional|plus more)\b", re.IGNORECASE)

# Fast token cache
TOKEN_CACHE: Dict[str, Optional[str]] = {}

@lru_cache(maxsize=50000)
def fast_normalize(text: str) -> str:
    """Ultra-fast normalization - essential only."""
    if not text:
        return ""
    
    # Basic cleaning only
    text = text.strip().lower()
    text = REGEX_NUMBERS_UNITS.sub(" ", text)
    text = REGEX_PREP_WORDS.sub(" ", text) 
    text = REGEX_NON_ALNUM_SPACE.sub(" ", text)
    text = REGEX_WHITESPACE.sub(" ", text).strip()
    
    # Simple fixes only
    if text in FIX_MAP:
        text = FIX_MAP[text]
    
    return text

@dataclass
class FastIngredientLabel:
    ingredient_id: str
    canonical_name: str
    search_terms: List[str]  # Pre-processed search terms

def fast_load_labels(path: Path) -> Tuple[List[FastIngredientLabel], Dict[str, str]]:
    """Fast label loading with pre-processed search terms."""
    data = json.loads(path.read_text(encoding="utf-8"))
    labels: List[FastIngredientLabel] = []
    exact_map: Dict[str, str] = {}
    
    for obj in data:
        canonical = obj.get("canonical_name") or obj.get("canonical") or ""
        if not canonical:
            continue
        
        iid = obj.get("ingredient_id") or obj.get("id") or f"ing_{canonical.lower().replace(' ', '_')}"
        canonical_norm = fast_normalize(canonical)
        
        # Build search terms: canonical + alt names
        search_terms = [canonical_norm]
        exact_map[canonical_norm] = iid
        
        # Add alternative names
        for alt in obj.get("alt", []):
            if alt:
                alt_norm = fast_normalize(alt)
                if alt_norm and alt_norm not in exact_map:
                    search_terms.append(alt_norm)
                    exact_map[alt_norm] = iid
        
        labels.append(FastIngredientLabel(
            ingredient_id=iid,
            canonical_name=canonical_norm, 
            search_terms=search_terms
        ))
    
    return labels, exact_map

def fast_match_ingredient(raw_part: str, exact_map: Dict[str, str]) -> Optional[str]:
    """Ultra-fast ingredient matching - exact only."""
    if not raw_part or len(raw_part) < 2:
        return None
    
    # Check cache first
    if raw_part in TOKEN_CACHE:
        return TOKEN_CACHE[raw_part]
    
    # Fast normalization
    normalized = fast_normalize(raw_part)
    if not normalized:
        TOKEN_CACHE[raw_part] = None
        return None
    
    # Direct exact match
    if normalized in exact_map:
        result = exact_map[normalized]
        TOKEN_CACHE[raw_part] = result
        return result
    
    # Try without last word (handles "garlic powder" -> "garlic")
    words = normalized.split()
    if len(words) > 1:
        for i in range(len(words)):
            subset = " ".join(words[:i+1])
            if subset in exact_map:
                result = exact_map[subset]
                TOKEN_CACHE[raw_part] = result
                return result
    
    TOKEN_CACHE[raw_part] = None
    return None

def fast_process_ingredients(raw_ingredients: str, exact_map: Dict[str, str]) -> List[str]:
    """Fast ingredient processing with minimal logic."""
    if not raw_ingredients:
        return []
    
    # Simple splitting
    parts = REGEX_INGREDIENT_SEPARATORS.split(raw_ingredients)
    matched_ids = []
    seen = set()
    
    for part in parts:
        part = part.strip()
        if not part or len(part) < 3:
            continue
        
        # Skip obvious non-ingredients
        part_lower = part.lower()
        if any(skip in part_lower for skip in ['serving', 'garnish', 'optional', 'to taste', 'cooking spray']):
            continue
        
        # Quick ingredient matching
        ing_id = fast_match_ingredient(part, exact_map)
        if ing_id and ing_id not in seen:
            matched_ids.append(ing_id)
            seen.add(ing_id)
    
    return matched_ids

def fast_build_recipe_props(row: Dict[str, str]) -> Dict:
    """Streamlined recipe property building."""
    def safe_int(x): 
        try: return int(float(x)) if x and x not in ("", "N/A") else None
        except: return None
    
    def safe_float(x):
        try: return float(x) if x and x not in ("", "N/A") else None  
        except: return None

    return {
        "title": row.get("title", ""),
        "description": row.get("description", ""),
        "instructions": row.get("instructions", ""),
        "ingredient": row.get("ingredients", ""),
        "tags": [row.get("recipe_category")] if row.get("recipe_category") else [],
        "prep_time_min": safe_int(row.get("prep_time")),
        "cook_time_min": safe_int(row.get("cook_time")),
        "total_time_min": safe_int(row.get("total_time")),
        "servings": safe_int(row.get("servings")),
        "yield": row.get("yield"),
        "cuisine": [row.get("recipe_cuisine")] if row.get("recipe_cuisine") else [],
        "recipe_category": row.get("recipe_category"),
        "source_url": row.get("url"),
        "rating_value": safe_float(row.get("rating_value")),
        "rating_count": safe_int(row.get("rating_count")),
        "review_count": safe_int(row.get("review_count")),
        "popularity_views": 0,
        "popularity_saves": 0,
        "popularity_cooks": 0,
        "popularity_likes": 0,
        "nutrition_calories": safe_float(row.get("calories")),
        "nutrition_protein": safe_float(row.get("protein")),
        "nutrition_fat": safe_float(row.get("fat")),
        "nutrition_carbohydrate": safe_float(row.get("carbohydrate")),
        "nutrition_fiber": safe_float(row.get("fiber")),
        "nutrition_sugar": safe_float(row.get("sugar")),
        "nutrition_sodium": safe_float(row.get("sodium")),
        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
    }

def fast_generate_cypher(recipes: List[Dict], output_path: Path, batch_size: int = 500) -> None:
    """Ultra-fast Cypher file generation with proper batching."""
    print(f"[FAST] Generating Cypher file: {output_path}")
    
    with output_path.open("w", encoding="utf-8") as f:
        # Process in batches to avoid memory issues
        for batch_idx in range(0, len(recipes), batch_size):
            batch = recipes[batch_idx:batch_idx + batch_size]
            
            # Write each recipe individually (more reliable for large datasets)
            for recipe in batch:
                recipe_id = recipe["recipe_id"]
                props = recipe["props"]
                ingredients = recipe.get("ingredients", [])
                
                # Escape strings for Cypher
                def escape_str(s):
                    if s is None:
                        return "null"
                    if isinstance(s, str):
                        # Escape quotes and backslashes
                        s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
                        return f'"{s}"'
                    if isinstance(s, bool):
                        return "true" if s else "false"
                    if isinstance(s, (int, float)):
                        return str(s) if s is not None else "null"
                    if isinstance(s, list):
                        # Handle arrays
                        items = [escape_str(item) for item in s if item]
                        return f'[{", ".join(items)}]'
                    return "null"
                
                # Build MERGE statement
                f.write(f"MERGE (r:Recipe {{recipe_id: {escape_str(recipe_id)}}})\n")
                f.write(f"SET r.title = {escape_str(props.get('title'))},\n")
                f.write(f"    r.description = {escape_str(props.get('description'))},\n")
                f.write(f"    r.instructions = {escape_str(props.get('instructions'))},\n")
                f.write(f"    r.ingredient = {escape_str(props.get('ingredient'))},\n")
                f.write(f"    r.prep_time_min = {escape_str(props.get('prep_time_min'))},\n")
                f.write(f"    r.cook_time_min = {escape_str(props.get('cook_time_min'))},\n")
                f.write(f"    r.total_time_min = {escape_str(props.get('total_time_min'))},\n")
                f.write(f"    r.servings = {escape_str(props.get('servings'))},\n")
                f.write(f"    r.cuisine = {escape_str(props.get('cuisine'))},\n")
                f.write(f"    r.rating_value = {escape_str(props.get('rating_value'))},\n")
                f.write(f"    r.nutrition_calories = {escape_str(props.get('nutrition_calories'))},\n")
                f.write(f"    r.nutrition_protein = {escape_str(props.get('nutrition_protein'))},\n")
                f.write(f"    r.nutrition_fat = {escape_str(props.get('nutrition_fat'))};\n")
                
                # Add ingredients
                for ing in ingredients:
                    ing_id = ing.get("ingredient_id")
                    if ing_id:
                        f.write(f"MATCH (r:Recipe {{recipe_id: {escape_str(recipe_id)}}})\n")
                        f.write(f"MATCH (i:CanonicalIngredient {{ingredient_id: {escape_str(ing_id)}}})\n")
                        f.write(f"MERGE (r)-[:HAS_INGREDIENT]->(i);\n")
                
                f.write("\n")
            
            if (batch_idx + batch_size) % 5000 == 0:
                print(f"  Written {min(batch_idx + batch_size, len(recipes))}/{len(recipes)} recipes...")
    
    file_size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[FAST] Generated {len(recipes)} recipes -> {file_size_mb:.1f}MB")

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="FAST recipe import - optimized for speed")
    parser.add_argument("--csv", type=str, default="data/recipes/full_data_ing.csv")
    parser.add_argument("--labels", type=str, default="data/ingredients/canonical_ingredients_migrated.json")
    parser.add_argument("--out-cypher", type=str, required=True, help="Output Cypher file (REQUIRED for fast mode)")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N rows")
    parser.add_argument("--batch-size", type=int, default=10000, help="Larger batch size for speed")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--profile", action="store_true", help="Enable performance profiling")
    args = parser.parse_args()

    if args.profile:
        import cProfile
        profiler = cProfile.Profile()
        profiler.enable()

    start_time = time.time()
    
    # Fast loading
    print("[FAST] Loading ingredients...")
    labels, exact_map = fast_load_labels(Path(args.labels))
    print(f"[FAST] Loaded {len(labels)} ingredients with {len(exact_map)} exact mappings")
    
    # Process CSV
    csv_path = Path(args.csv)
    print(f"[FAST] Processing {csv_path}...")
    
    recipes = []
    processed = 0
    last_log_time = start_time
    
    with csv_path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        
        for idx, row in enumerate(reader, 1):
            if args.limit and idx > args.limit:
                break
            
            # Fast processing
            recipe_id = f"rec_{idx}"
            props = fast_build_recipe_props(row)
            raw_ing = row.get("ingredients", "")
            
            # Fast ingredient matching
            ingredient_ids = fast_process_ingredients(raw_ing, exact_map)
            ingredients = [{"ingredient_id": iid} for iid in ingredient_ids]
            
            recipes.append({
                "recipe_id": recipe_id,
                "props": props,
                "ingredients": ingredients
            })
            
            processed = idx
            
            # Progress logging (less frequent for speed)
            current_time = time.time()
            if idx % 1000 == 0 or (current_time - last_log_time) >= 5:
                elapsed = current_time - start_time
                speed = idx / elapsed if elapsed > 0 else 0
                
                if args.limit:
                    progress = (idx / args.limit) * 100
                    remaining = args.limit - idx
                    eta = remaining / speed if speed > 0 else 0
                    print(f"[FAST] {idx:6d}/{args.limit} ({progress:5.1f}%) | {speed:6.1f} rows/sec | ETA: {eta/60:.1f}min")
                else:
                    print(f"[FAST] {idx:6d} rows processed | {speed:6.1f} rows/sec")
                
                last_log_time = current_time

    # Generate output
    fast_generate_cypher(recipes, Path(args.out_cypher))
    
    # Final summary
    total_time = time.time() - start_time
    avg_speed = processed / total_time if total_time > 0 else 0
    cache_size = len(TOKEN_CACHE)
    
    print(f"\n[FAST] ✅ COMPLETED!")
    print(f"  Processed: {processed:,} recipes")
    print(f"  Time: {total_time:.1f}s")
    print(f"  Speed: {avg_speed:.1f} rows/sec")
    print(f"  Cache entries: {cache_size:,}")
    
    # Estimate for 40k recipes
    if processed >= 10:
        estimated_40k_minutes = (40000 / avg_speed) / 60
        print(f"  📊 Estimated for 40,000 recipes: {estimated_40k_minutes:.1f} minutes ({estimated_40k_minutes/60:.1f} hours)")
    
    if args.profile:
        profiler.disable()
        import pstats
        import io
        s = io.StringIO()
        ps = pstats.Stats(profiler, stream=s).sort_stats('cumulative')
        ps.print_stats(10)
        print(f"\n[PROFILING]\n{s.getvalue()}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[FAST] Interrupted by user")
    except Exception as e:
        print(f"\n[FAST] Error: {e}")
        raise
