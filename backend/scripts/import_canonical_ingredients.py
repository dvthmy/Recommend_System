#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import canonical ingredients from JSON file into Neo4j.

This script reads canonical_ingredients_migrated.json (created by add_variant_ingredients.py)
and imports all ingredients into Neo4j with their variations and alt_names.

Usage:
  python import_canonical_ingredients.py \
    --input data/process/canonical_ingredients_migrated.json \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password Admin123! \
    --db test
"""

import json
import sys
import os
from pathlib import Path
from typing import List, Dict, Optional
import argparse

# Add backend directory to path
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, backend_dir)

from config import DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB


def load_canonical_ingredients(json_path: Path) -> List[Dict]:
    """Load canonical ingredients from JSON file."""
    with open(json_path, 'r', encoding='utf-8') as f:
        ingredients = json.load(f)
    return ingredients


def import_ingredients_to_neo4j(
    ingredients: List[Dict],
    uri: str,
    user: str,
    password: str,
    database: str,
    batch_size: int = 1000,
    verbose: bool = False
) -> None:
    """Import ingredients into Neo4j using Python driver."""
    from neo4j import GraphDatabase
    
    driver = GraphDatabase.driver(uri, auth=(user, password))
    
    try:
        with driver.session(database=database) as session:
            # Process in batches
            total = len(ingredients)
            imported = 0
            errors = 0
            
            print(f"[*] Importing {total} ingredients in batches of {batch_size}...")
            
            for i in range(0, total, batch_size):
                batch = ingredients[i:i + batch_size]
                batch_num = (i // batch_size) + 1
                total_batches = (total + batch_size - 1) // batch_size
                
                try:
                    # Convert variations map to JSON string (Neo4j doesn't support nested maps)
                    batch_for_neo4j = []
                    for ing in batch:
                        ing_copy = ing.copy()
                        if "variations" in ing_copy and ing_copy["variations"]:
                            # Convert variations map to JSON string
                            ing_copy["variations_json"] = json.dumps(ing_copy["variations"], ensure_ascii=False)
                        else:
                            ing_copy["variations_json"] = None
                        # Remove original variations (map) - we'll store as JSON string
                        if "variations" in ing_copy:
                            del ing_copy["variations"]
                        batch_for_neo4j.append(ing_copy)
                    
                    query = """
                    UNWIND $ingredients AS ing
                    MERGE (i:Ingredient {ingredient_id: ing.ingredient_id})
                    SET i.canonical_name = ing.canonical_name,
                        i.category = ing.category,
                        i.base = coalesce(ing.base, null),
                        i.alt_names = coalesce(ing.alt_names, []),
                        i.variations = coalesce(ing.variations_json, null)
                    """
                    
                    result = session.run(query, {"ingredients": batch_for_neo4j})
                    result.consume()  # Consume result to ensure execution
                    
                    imported += len(batch)
                    print(f"  [OK] Batch {batch_num}/{total_batches}: Imported {len(batch)} ingredients "
                          f"({imported}/{total} total)")
                    
                    if verbose:
                        # Show sample from batch
                        sample = batch[0] if batch else None
                        if sample:
                            print(f"     Sample: {sample['canonical_name']} "
                                  f"({sample.get('category', 'N/A')})")
                
                except Exception as e:
                    errors += len(batch)
                    print(f"  [ERROR] Batch {batch_num}/{total_batches}: Error importing batch: {e}")
                    if verbose:
                        import traceback
                        traceback.print_exc()
            
            print(f"\n[*] Import Summary:")
            print(f"  [OK] Successfully imported: {imported}")
            print(f"  [ERROR] Errors: {errors}")
            print(f"  [*] Total processed: {total}")
            
            # Verify import
            verify_query = "MATCH (i:Ingredient) RETURN count(i) AS count"
            result = session.run(verify_query)
            count = result.single()["count"]
            print(f"\n[*] Verification: {count} ingredients in Neo4j database")
            
    finally:
        driver.close()


def generate_cypher_file(
    ingredients: List[Dict],
    output_path: Path,
    batch_size: int = 50,
    verbose: bool = False
) -> None:
    """Generate Cypher import file (alternative to direct import).
    
    Uses individual CREATE statements instead of :param to avoid JSON length issues.
    This is slower but more reliable for large datasets with complex JSON fields.
    """
    print(f"[*] Generating Cypher file: {output_path}")
    print(f"   Using individual MERGE statements (batch size: {batch_size} for grouping)")
    
    # Prepare data for Cypher
    rows = []
    for ing in ingredients:
        # Convert variations map to JSON string
        variations_json = None
        if ing.get("variations"):
            variations_json = json.dumps(ing.get("variations", {}), ensure_ascii=False)
        
        row = {
            "ingredient_id": ing["ingredient_id"],
            "canonical_name": ing["canonical_name"],
            "category": ing.get("category", "other"),
            "base": ing.get("base"),
            "alt_names": ing.get("alt_names", []),
            "variations_json": variations_json
        }
        rows.append(row)
    
    # Generate Cypher using individual MERGE statements
    # This avoids JSON parameter length issues
    cypher_lines = []
    total = len(rows)
    
    for idx, row in enumerate(rows, 1):
        if idx % 100 == 0:
            cypher_lines.append(f"// Progress: {idx}/{total} ingredients")
        
        # Escape strings for Cypher (escape single quotes)
        ing_id = row["ingredient_id"].replace("'", "\\'")
        canonical = row["canonical_name"].replace("'", "\\'")
        category = row["category"].replace("'", "\\'")
        base = row.get("base")
        if base:
            base_escaped = base.replace("'", "\\'")
            base_str = f"'{base_escaped}'"
        else:
            base_str = "null"
        
        # Format alt_names array - use JSON string directly
        alt_names_str = json.dumps(row["alt_names"], ensure_ascii=False)
        
        # Format variations_json - use apoc.convert.toJsonString or store as string
        # For Cypher, we'll store variations_json as a string property
        variations_str = "null"
        if row["variations_json"]:
            # Escape single quotes for Cypher string literal
            # Don't escape backslashes - they're needed for JSON escape sequences
            variations_escaped = row["variations_json"].replace("'", "\\'")
            variations_str = f"'{variations_escaped}'"
        
        # Use individual MERGE statement
        cypher_lines.append(f"MERGE (i:Ingredient {{ingredient_id: '{ing_id}'}})")
        cypher_lines.append(f"SET i.canonical_name = '{canonical}',")
        cypher_lines.append(f"    i.category = '{category}',")
        cypher_lines.append(f"    i.base = {base_str},")
        cypher_lines.append(f"    i.alt_names = {alt_names_str},")
        cypher_lines.append(f"    i.variations = {variations_str};")
        cypher_lines.append("")
    
    cypher_content = "\n".join(cypher_lines)
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(cypher_content, encoding="utf-8")
    
    print(f"[OK] Generated Cypher file with {len(rows)} ingredients")
    print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
    print(f"   To import: Run this file in Neo4j Browser or use cypher-shell")
    print(f"   Example: cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p 'password' -d test --file {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Import canonical ingredients from JSON into Neo4j"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/process/canonical_ingredients_migrated.json",
        help="Path to canonical_ingredients.json file (default: canonical_ingredients_migrated.json)"
    )
    parser.add_argument(
        "--out-cypher",
        type=str,
        default=None,
        help="Optional: Generate Cypher file instead of direct import"
    )
    parser.add_argument(
        "--cypher-batch-size",
        type=int,
        default=50,
        help="Batch size for progress logging (default: 50, not used for actual batching - each ingredient is processed individually)"
    )
    parser.add_argument(
        "--uri",
        default=DEFAULT_URI,
        help="Neo4j URI"
    )
    parser.add_argument(
        "--user",
        default=DEFAULT_USER,
        help="Neo4j username"
    )
    parser.add_argument(
        "--password",
        default=DEFAULT_PASS,
        help="Neo4j password"
    )
    parser.add_argument(
        "--db",
        dest="database",
        default=DEFAULT_DB,
        help="Neo4j database name"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=1000,
        help="Batch size for import"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    
    args = parser.parse_args()
    
    # Load ingredients
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"[*] Loading ingredients from {input_path}...")
    ingredients = load_canonical_ingredients(input_path)
    print(f"[OK] Loaded {len(ingredients)} ingredients")
    
    # Show statistics
    categories = {}
    with_variations = 0
    with_alt_names = 0
    total_variations = 0
    
    for ing in ingredients:
        cat = ing.get("category", "other")
        categories[cat] = categories.get(cat, 0) + 1
        
        if ing.get("variations"):
            with_variations += 1
            for var_list in ing["variations"].values():
                total_variations += len(var_list)
        
        if ing.get("alt_names"):
            with_alt_names += 1
    
    print(f"\n[*] Statistics:")
    print(f"  - Total ingredients: {len(ingredients)}")
    print(f"  - With variations: {with_variations}")
    print(f"  - With alt_names: {with_alt_names}")
    print(f"  - Total variations: {total_variations}")
    print(f"\n[*] Category distribution:")
    for cat, count in sorted(categories.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count}")
    
    # Generate Cypher file or import directly
    if args.out_cypher:
        output_path = Path(args.out_cypher)
        generate_cypher_file(ingredients, output_path, args.cypher_batch_size, args.verbose)
    else:
        # Direct import to Neo4j
        print(f"\n[*] Importing to Neo4j...")
        print(f"   URI: {args.uri}")
        print(f"   Database: {args.database}")
        print(f"   User: {args.user}")
        
        import_ingredients_to_neo4j(
            ingredients,
            args.uri,
            args.user,
            args.password,
            args.database,
            args.batch_size,
            args.verbose
        )
    
    print("\n[OK] Done!")


if __name__ == "__main__":
    main()

