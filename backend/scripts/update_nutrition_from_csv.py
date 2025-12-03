#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Script để update nutrition data cho các recipes đã có trong Neo4j
Match recipes bằng URL (source_url) và update tất cả nutrition fields
"""

import csv
import re
import sys
import time
from pathlib import Path
from typing import Dict, Optional, List
import argparse

# Import neo4j only when needed (for direct mode)
GraphDatabase = None

# Add backend directory to path
backend_dir = Path(__file__).parent.parent
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

try:
    from api.config import settings
except ImportError:
    # Fallback if running as standalone script
    class Settings:
        NEO4J_URI = "bolt://localhost:7687"
        NEO4J_USER = "neo4j"
        NEO4J_PASSWORD = "Admin123!"
        NEO4J_DATABASE = "test"
    settings = Settings()


def to_float(x: str) -> Optional[float]:
    """Convert string to float, handling units and N/A values"""
    if not x or x in ("", "N/A", "None", "null"):
        return None
    try:
        # Try direct conversion first
        return float(x)
    except (ValueError, TypeError):
        # Extract number from string with units (e.g., "507 kcal" -> 507.0, "14 g" -> 14.0)
        match = re.match(r'^([0-9]+(?:\.[0-9]+)?)', str(x).strip())
        if match:
            return float(match.group(1))
        return None


def read_csv_nutrition(csv_path: Path) -> Dict[str, Dict]:
    """
    Đọc CSV và tạo dictionary: {url: {nutrition_data}}
    """
    print(f"[*] Reading CSV: {csv_path}")
    nutrition_data = {}
    
    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    for enc in encodings:
        try:
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                row_count = 0
                for row in reader:
                    url = row.get("url", "").strip()
                    if not url:
                        continue
                    
                    # Extract nutrition data
                    nutrition = {
                        "nutrition_calories": to_float(row.get("calories")),
                        "nutrition_protein": to_float(row.get("protein")),
                        "nutrition_total_fat": to_float(row.get("total_fat")) or to_float(row.get("fat")),
                        "nutrition_saturated_fat": to_float(row.get("saturated_fat")),
                        "nutrition_cholesterol": to_float(row.get("cholesterol")),
                        "nutrition_sodium": to_float(row.get("sodium")),
                        "nutrition_total_carbohydrate": to_float(row.get("total_carbohydrate")) or to_float(row.get("carbohydrate")),
                        "nutrition_dietary_fiber": to_float(row.get("dietary_fiber")) or to_float(row.get("fiber")),
                        "nutrition_total_sugars": to_float(row.get("total_sugars")) or to_float(row.get("sugar")),
                        "nutrition_vitamin_c": to_float(row.get("vitamin_c")),
                        "nutrition_calcium": to_float(row.get("calcium")),
                        "nutrition_iron": to_float(row.get("iron")),
                        "nutrition_potassium": to_float(row.get("potassium")),
                        # Legacy fields
                        "nutrition_fat": to_float(row.get("total_fat")) or to_float(row.get("fat")),
                        "nutrition_carbohydrate": to_float(row.get("total_carbohydrate")) or to_float(row.get("carbohydrate")),
                        "nutrition_fiber": to_float(row.get("dietary_fiber")) or to_float(row.get("fiber")),
                        "nutrition_sugar": to_float(row.get("total_sugars")) or to_float(row.get("sugar")),
                    }
                    
                    nutrition_data[url] = nutrition
                    row_count += 1
                    
                    if row_count % 1000 == 0:
                        print(f"  Read {row_count} rows...")
                
                print(f"[✓] Read {row_count} rows from CSV")
                return nutrition_data
        except UnicodeDecodeError:
            continue
    
    raise ValueError(f"Could not read CSV with any encoding: {encodings}")


def generate_update_cypher_file(nutrition_data: Dict[str, Dict], output_path: Path, verbose: bool = False):
    """
    Tạo Cypher file để update nutrition data
    Match recipes bằng source_url
    """
    print(f"[*] Generating Cypher update file: {output_path}")
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    def escape_str(s):
        if s is None:
            return "null"
        if isinstance(s, str):
            s = s.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
            return f'"{s}"'
        if isinstance(s, bool):
            return "true" if s else "false"
        if isinstance(s, (int, float)):
            return str(s) if s is not None else "null"
        return "null"
    
    updated_count = 0
    not_found_count = 0
    
    with output_path.open("w", encoding="utf-8") as f:
        f.write("// Update nutrition data for recipes based on URL\n")
        f.write("// Generated by update_nutrition_from_csv.py\n\n")
        
        for url, nutrition in nutrition_data.items():
            if not url:
                continue
            
            # Check if has any nutrition data
            has_nutrition = any(v is not None for v in nutrition.values())
            if not has_nutrition:
                continue
            
            # Build SET clause for nutrition fields
            set_clauses = []
            for key, value in nutrition.items():
                if value is not None:
                    set_clauses.append(f"    r.{key} = {escape_str(value)}")
            
            if not set_clauses:
                continue
            
            # Write UPDATE statement
            f.write(f"// Update nutrition for: {url[:80]}...\n")
            f.write(f"MATCH (r:Recipe {{source_url: {escape_str(url)}}})\n")
            f.write("SET\n")
            f.write(",\n".join(set_clauses))
            f.write(";\n\n")
            
            updated_count += 1
            
            if verbose and updated_count % 100 == 0:
                print(f"  Generated {updated_count} update statements...")
    
    print(f"[✓] Generated {updated_count} update statements")
    print(f"[*] Output file: {output_path}")
    print(f"[*] To execute: cypher-shell -u neo4j -p <password> -d <database> < {output_path}")


def update_directly(driver, database: str, nutrition_data: Dict[str, Dict], batch_size: int = 100, verbose: bool = False):
    """
    Update trực tiếp vào Neo4j qua driver
    """
    print(f"[*] Updating nutrition data directly in Neo4j (database: {database})")
    
    def escape_cypher_value(val):
        if val is None:
            return "null"
        if isinstance(val, (int, float)):
            return str(val)
        if isinstance(val, bool):
            return "true" if val else "false"
        # String - escape it
        s = str(val).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n").replace("\r", "\\r")
        return f'"{s}"'
    
    total = len(nutrition_data)
    updated = 0
    not_found = 0
    errors = 0
    
    with driver.session(database=database) as session:
        batch = []
        
        for url, nutrition in nutrition_data.items():
            if not url:
                continue
            
            # Check if has any nutrition data
            has_nutrition = any(v is not None for v in nutrition.values())
            if not has_nutrition:
                continue
            
            # Build SET clause
            set_clauses = []
            params = {"url": url}
            for key, value in nutrition.items():
                if value is not None:
                    param_name = key.replace("nutrition_", "nut_").replace("_", "")
                    set_clauses.append(f"r.{key} = ${param_name}")
                    params[param_name] = value
            
            if not set_clauses:
                continue
            
            query = f"""
            MATCH (r:Recipe {{source_url: $url}})
            SET {', '.join(set_clauses)}
            RETURN r.recipe_id AS recipe_id, r.title AS title
            """
            
            batch.append((query, params))
            
            # Execute batch
            if len(batch) >= batch_size:
                results = session.execute_write(_execute_batch, batch)
                for result in results:
                    if result:
                        updated += 1
                    else:
                        not_found += 1
                batch = []
                
                if verbose:
                    print(f"  Progress: {updated + not_found}/{total} processed ({updated} updated, {not_found} not found)")
        
        # Execute remaining batch
        if batch:
            results = session.execute_write(_execute_batch, batch)
            for result in results:
                if result:
                    updated += 1
                else:
                    not_found += 1
    
    print(f"[✓] Update complete:")
    print(f"  - Updated: {updated}")
    print(f"  - Not found: {not_found}")
    print(f"  - Errors: {errors}")


def _execute_batch(tx, batch: List[tuple]):
    """Execute a batch of queries"""
    results = []
    for query, params in batch:
        try:
            result = tx.run(query, **params).single()
            results.append(result)
        except Exception as e:
            print(f"  Error executing query: {e}")
            results.append(None)
    return results


def main():
    parser = argparse.ArgumentParser(description="Update nutrition data for recipes in Neo4j from CSV")
    parser.add_argument(
        "--csv",
        type=str,
        default="backend/data/recipes/full_data_ing.csv",
        help="Path to CSV file with nutrition data"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="backend/neo4j/update_nutrition.cypher",
        help="Output Cypher file path (if using --cypher mode)"
    )
    parser.add_argument(
        "--mode",
        choices=["cypher", "direct"],
        default="cypher",
        help="Mode: 'cypher' to generate file, 'direct' to update directly"
    )
    parser.add_argument(
        "--uri",
        type=str,
        default=None,
        help="Neo4j URI (default: from settings)"
    )
    parser.add_argument(
        "--username",
        type=str,
        default=None,
        help="Neo4j username (default: from settings)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default=None,
        help="Neo4j password (default: from settings)"
    )
    parser.add_argument(
        "--database",
        type=str,
        default=None,
        help="Neo4j database name (default: from settings)"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=100,
        help="Batch size for direct updates"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Read CSV
    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"[✗] CSV file not found: {csv_path}")
        sys.exit(1)
    
    nutrition_data = read_csv_nutrition(csv_path)
    
    if args.mode == "cypher":
        # Generate Cypher file
        output_path = Path(args.output)
        generate_update_cypher_file(nutrition_data, output_path, verbose=args.verbose)
        print(f"\n[✓] Cypher file generated: {output_path}")
        print(f"[*] To execute, run:")
        print(f"    cypher-shell -u neo4j -p <password> -d <database> < {output_path}")
    
    elif args.mode == "direct":
        # Import neo4j only when needed
        try:
            from neo4j import GraphDatabase
        except ImportError:
            print("[✗] Error: neo4j package not installed. Install with: pip install neo4j")
            sys.exit(1)
        
        # Update directly
        uri = args.uri or settings.NEO4J_URI
        username = args.username or settings.NEO4J_USER
        password = args.password or settings.NEO4J_PASSWORD
        database = args.database or settings.NEO4J_DATABASE
        
        print(f"[*] Connecting to Neo4j: {uri}")
        print(f"[*] Database: {database}")
        
        driver = GraphDatabase.driver(uri, auth=(username, password))
        try:
            update_directly(driver, database, nutrition_data, batch_size=args.batch_size, verbose=args.verbose)
        finally:
            driver.close()
    
    print("[✓] Done!")


if __name__ == "__main__":
    main()

