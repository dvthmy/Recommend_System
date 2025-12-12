#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import recipes với mapping đơn giản theo category.
Chỉ map ingredients theo 6 categories: grain, meat, seafood, sauce, vegetable, fruit
Không cần fuzzy matching phức tạp - nhanh hơn nhiều!

Usage:
  python import_recipes_simple.py \
    --csv data/recipes/full_data_ing.csv \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password "Admin123!" \
    --db neo4j \
    --batch-size 10000
"""

import csv
import json
import re
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from collections import defaultdict

from neo4j import GraphDatabase
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

# Category mapping - chỉ 6 categories đơn giản
CATEGORY_KEYWORDS = {
    "grain": {"rice", "flour", "bread", "pasta", "noodle", "wheat", "oats", "barley", "quinoa", "corn", "tortilla", "bagel", "cereal"},
    "meat": {"beef", "pork", "chicken", "turkey", "lamb", "bacon", "ham", "sausage", "steak", "duck"},
    "seafood": {"fish", "salmon", "tuna", "shrimp", "crab", "mussel", "scallop", "lobster", "cod", "sardine"},
    "sauce": {"sauce", "ketchup", "mustard", "mayonnaise", "soy sauce", "vinegar", "dressing", "gravy"},
    "vegetable": {"tomato", "onion", "garlic", "carrot", "potato", "pepper", "cabbage", "broccoli", "spinach", "lettuce", "cucumber", "celery"},
    "fruit": {"apple", "banana", "orange", "lemon", "lime", "berry", "grape", "mango", "pineapple", "strawberry"}
}

def normalize_text(text: str) -> str:
    """Normalize text to lowercase, remove extra spaces"""
    if not text:
        return ""
    return re.sub(r'\s+', ' ', text.lower().strip())

def guess_category_from_text(text: str) -> Optional[str]:
    """Đoán category từ text ingredient đơn giản"""
    text_lower = normalize_text(text)
    words = text_lower.split()
    
    # Check từng category
    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in text_lower:
                return category
    
    return None

def load_ingredients_by_category(uri: str, user: str, password: str, database: str) -> Dict[str, List[Dict]]:
    """Load ingredients từ Neo4j, group theo category"""
    driver = GraphDatabase.driver(uri, auth=(user, password))
    ingredients_by_category = defaultdict(list)
    
    try:
        with driver.session(database=database) as session:
            # Load tất cả ingredients, sau đó filter theo category keywords
            query = """
            MATCH (i:Ingredient)
            RETURN i.ingredient_id AS id, i.canonical_name AS name, i.category AS category
            """
            result = session.run(query)
            
            for record in result:
                cat = record["category"]
                name = record["name"] or ""
                
                # Map category về 6 categories chính
                mapped_cat = None
                if cat:
                    cat_lower = cat.lower()
                    if "grain" in cat_lower or "rice" in cat_lower or "flour" in cat_lower or "bread" in cat_lower or "pasta" in cat_lower:
                        mapped_cat = "grain"
                    elif "meat" in cat_lower or "beef" in cat_lower or "pork" in cat_lower or "chicken" in cat_lower:
                        mapped_cat = "meat"
                    elif "seafood" in cat_lower or "fish" in cat_lower or "shrimp" in cat_lower:
                        mapped_cat = "seafood"
                    elif "sauce" in cat_lower:
                        mapped_cat = "sauce"
                    elif "vegetable" in cat_lower:
                        mapped_cat = "vegetable"
                    elif "fruit" in cat_lower:
                        mapped_cat = "fruit"
                    else:
                        # Thử đoán từ tên
                        name_lower = name.lower()
                        for cat_key, keywords in CATEGORY_KEYWORDS.items():
                            for keyword in keywords:
                                if keyword in name_lower:
                                    mapped_cat = cat_key
                                    break
                            if mapped_cat:
                                break
                
                if mapped_cat:
                    ingredients_by_category[mapped_cat].append({
                        "id": record["id"],
                        "name": name
                    })
    finally:
        driver.close()
    
    print(f"[*] Loaded ingredients by category:")
    for cat in ["grain", "meat", "seafood", "sauce", "vegetable", "fruit"]:
        count = len(ingredients_by_category.get(cat, []))
        print(f"  - {cat}: {count} ingredients")
    
    return ingredients_by_category

def map_ingredient_simple(raw_text: str, ingredients_by_category: Dict[str, List[Dict]]) -> Optional[str]:
    """Map ingredient đơn giản: đoán category → lấy ingredient đầu tiên trong category đó"""
    category = guess_category_from_text(raw_text)
    
    if not category:
        return None
    
    # Lấy ingredient đầu tiên trong category (hoặc có thể match tên nếu có)
    category_ingredients = ingredients_by_category.get(category, [])
    
    if not category_ingredients:
        return None
    
    # Tìm ingredient có tên gần giống nhất (đơn giản)
    text_lower = normalize_text(raw_text)
    for ing in category_ingredients:
        name_lower = normalize_text(ing["name"])
        # Nếu tên ingredient có trong text hoặc ngược lại
        if name_lower in text_lower or text_lower in name_lower:
            return ing["id"]
    
    # Nếu không match, lấy ingredient đầu tiên trong category
    return category_ingredients[0]["id"]

def parse_ingredients_from_csv(raw: str) -> List[str]:
    """Parse ingredients từ CSV field (JSON array)"""
    if not raw:
        return []
    
    try:
        # Parse JSON array
        ingredients = json.loads(raw)
        if isinstance(ingredients, list):
            return [str(ing).strip() for ing in ingredients if ing]
    except:
        # Fallback: split by comma
        return [s.strip() for s in raw.split(',') if s.strip()]
    
    return []

def build_recipe_props(row: Dict[str, str]) -> Dict:
    """Build recipe properties từ CSV row"""
    def to_float(x: str) -> Optional[float]:
        if not x or x in ("", "N/A", "None"):
            return None
        try:
            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)', str(x).strip())
            if match:
                return float(match.group(1))
        except:
            pass
        return None
    
    def to_int(x: str) -> Optional[int]:
        try:
            return int(float(x)) if x not in (None, "", "N/A") else None
        except:
            return None
    
    def parse_cuisines(raw: Optional[str]) -> List[str]:
        if not raw:
            return []
        parts = re.split(r'[,;/|]+', str(raw))
        return [p.strip().title() for p in parts if p.strip()]
    
    return {
        "title": row.get("title") or "",
        "description": row.get("description") or "",
        "instructions": row.get("instructions") or "",
        "ingredient": row.get("ingredients") or "",
        "tags": [row.get("recipe_category")] if row.get("recipe_category") else [],
        "servings": to_int(row.get("servings")),
        "cuisine": parse_cuisines(row.get("recipe_cuisine")),
        "recipe_category": row.get("recipe_category"),
        "source_url": row.get("url"),
        "rating_value": to_float(row.get("rating_value")),
        "rating_count": to_int(row.get("rating_count")),
        "review_count": to_int(row.get("review_count")),
        "popularity_views": 0,
        "popularity_likes": 0,
        "nutrition_calories": to_float(row.get("calories")),
        "nutrition_protein": to_float(row.get("protein")),
        "nutrition_total_fat": to_float(row.get("total_fat")) or to_float(row.get("fat")),
        "nutrition_saturated_fat": to_float(row.get("saturated_fat")),
        "nutrition_sodium": to_float(row.get("sodium")),
        "nutrition_total_carbohydrate": to_float(row.get("total_carbohydrate")) or to_float(row.get("carbohydrate")),
        "nutrition_dietary_fiber": to_float(row.get("dietary_fiber")) or to_float(row.get("fiber")),
        "nutrition_total_sugars": to_float(row.get("total_sugars")) or to_float(row.get("sugar")),
        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
    }

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Import recipes với mapping đơn giản theo category")
    parser.add_argument("--csv", type=str, required=True, help="Path to CSV file")
    parser.add_argument("--uri", default=DEFAULT_URI, help="Neo4j URI")
    parser.add_argument("--user", default=DEFAULT_USER, help="Neo4j user")
    parser.add_argument("--password", default=DEFAULT_PASS, help="Neo4j password")
    parser.add_argument("--db", dest="database", default=DEFAULT_DB, help="Neo4j database")
    parser.add_argument("--batch-size", type=int, default=10000, help="Batch size (default: 10000)")
    parser.add_argument("--limit", type=int, default=None, help="Limit number of recipes to process")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    # Load ingredients by category từ Neo4j
    print("[*] Loading ingredients from Neo4j...")
    ingredients_by_category = load_ingredients_by_category(args.uri, args.user, args.password, args.database)
    
    if not ingredients_by_category:
        print("[ERROR] No ingredients found! Import ingredients first.")
        return
    
    # Read CSV
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        return
    
    print(f"[*] Reading CSV: {csv_path}")
    
    # Process recipes
    driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
    session_kwargs = {"database": args.database}
    
    batch_rows = []
    total_processed = 0
    total_mapped = 0
    
    try:
        with csv_path.open('r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            
            for idx, row in enumerate(reader, 1):
                if args.limit and idx > args.limit:
                    break
                
                recipe_id = f"rec_{idx}"
                props = build_recipe_props(row)
                
                # Parse và map ingredients
                raw_ingredients = parse_ingredients_from_csv(row.get("ingredients", ""))
                mapped_ids = []
                seen = set()
                
                for raw_ing in raw_ingredients:
                    ing_id = map_ingredient_simple(raw_ing, ingredients_by_category)
                    if ing_id and ing_id not in seen:
                        mapped_ids.append(ing_id)
                        seen.add(ing_id)
                        total_mapped += 1
                
                ingredients_edges = [{"ingredient_id": iid} for iid in mapped_ids]
                recipe_data = {
                    "recipe_id": recipe_id,
                    "props": props,
                    "ingredients": ingredients_edges
                }
                batch_rows.append(recipe_data)
                total_processed += 1
                
                # Batch import
                if len(batch_rows) >= args.batch_size:
                    import_batch(driver, session_kwargs, batch_rows)
                    print(f"[*] Processed {total_processed} recipes, mapped {total_mapped} ingredients")
                    batch_rows = []
                
                if args.verbose and idx <= 10:
                    print(f"  Recipe {idx}: {props['title'][:50]} -> {len(mapped_ids)} ingredients")
        
        # Final batch
        if batch_rows:
            import_batch(driver, session_kwargs, batch_rows)
        
        print(f"\n[OK] Import complete!")
        print(f"  - Recipes processed: {total_processed}")
        print(f"  - Ingredients mapped: {total_mapped}")
        
    finally:
        driver.close()

def import_batch(driver, session_kwargs, batch_rows: List[Dict]):
    """Import một batch recipes vào Neo4j"""
    query = """
    UNWIND $rows AS row
    MERGE (r:Recipe {recipe_id: row.recipe_id})
    SET r.title = row.props.title,
        r.description = row.props.description,
        r.instructions = row.props.instructions,
        r.ingredient = row.props.ingredient,
        r.tags = row.props.tags,
        r.servings = row.props.servings,
        r.cuisine = row.props.cuisine,
        r.recipe_category = row.props.recipe_category,
        r.source_url = row.props.source_url,
        r.rating_value = row.props.rating_value,
        r.rating_count = row.props.rating_count,
        r.review_count = row.props.review_count,
        r.popularity_views = coalesce(row.props.popularity_views, 0),
        r.popularity_likes = coalesce(row.props.popularity_likes, 0),
        r.nutrition_calories = row.props.nutrition_calories,
        r.nutrition_protein = row.props.nutrition_protein,
        r.nutrition_total_fat = row.props.nutrition_total_fat,
        r.nutrition_saturated_fat = row.props.nutrition_saturated_fat,
        r.nutrition_sodium = row.props.nutrition_sodium,
        r.nutrition_total_carbohydrate = row.props.nutrition_total_carbohydrate,
        r.nutrition_dietary_fiber = row.props.nutrition_dietary_fiber,
        r.nutrition_total_sugars = row.props.nutrition_total_sugars,
        r.image_urls = row.props.image_urls
    WITH r, row
    CALL {
        WITH r, row
        UNWIND coalesce(row.ingredients, []) AS ing
        MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})
        MERGE (r)-[:HAS_INGREDIENT]->(i)
    }
    RETURN count(r) AS count
    """
    
    with driver.session(**session_kwargs) as session:
        session.run(query, rows=batch_rows).consume()

if __name__ == "__main__":
    main()

