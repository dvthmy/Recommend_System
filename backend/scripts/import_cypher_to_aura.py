#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import file Cypher lên Neo4j Aura
Sử dụng Neo4j Python driver để execute từng statement trong file Cypher
"""
import sys
import os
import argparse
from pathlib import Path
from neo4j import GraphDatabase

# Neo4j Aura credentials
AURA_URI = "neo4j+s://3b0d8961.databases.neo4j.io"
AURA_USER = "neo4j"
AURA_PASSWORD = "qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0"
AURA_DATABASE = "neo4j"

def execute_cypher_file(driver, database: str, cypher_file: Path, batch_size: int = 100):
    """Execute Cypher file lên Neo4j Aura"""
    print(f"📄 Đọc file: {cypher_file}")
    print(f"📊 Size: {cypher_file.stat().st_size / 1024:.1f} KB")
    print()
    
    # Đọc file Cypher
    with open(cypher_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Tách thành các statements (tách bởi dấu ;)
    # Loại bỏ comments và empty lines
    statements = []
    current_statement = []
    
    for line in content.split('\n'):
        line = line.strip()
        # Bỏ qua comments và empty lines
        if not line or line.startswith('//'):
            continue
        
        current_statement.append(line)
        
        # Nếu line kết thúc bằng ; thì đây là end of statement
        if line.endswith(';'):
            statement = ' '.join(current_statement)
            if statement.strip() and statement.strip() != ';':
                statements.append(statement)
            current_statement = []
    
    # Nếu còn statement chưa kết thúc
    if current_statement:
        statement = ' '.join(current_statement)
        if statement.strip():
            statements.append(statement)
    
    print(f"📝 Tìm thấy {len(statements)} statements")
    print()
    
    # Execute từng batch
    total = len(statements)
    executed = 0
    errors = 0
    
    with driver.session(database=database) as session:
        for i, stmt in enumerate(statements, 1):
            try:
                result = session.run(stmt)
                result.consume()  # Consume để đảm bảo execution
                executed += 1
                
                if i % batch_size == 0 or i == total:
                    print(f"  ✅ Progress: {i}/{total} statements ({i*100//total}%)")
            except Exception as e:
                errors += 1
                print(f"  ❌ Error at statement {i}: {str(e)[:100]}")
                # Continue với statement tiếp theo
                continue
    
    print()
    print("=" * 60)
    print(f"✅ Hoàn tất!")
    print(f"   Executed: {executed}/{total}")
    print(f"   Errors: {errors}")
    print("=" * 60)
    
    return executed, errors

def main():
    parser = argparse.ArgumentParser(description="Import Cypher file lên Neo4j Aura")
    parser.add_argument("--file", type=str, required=True, help="Path to Cypher file")
    parser.add_argument("--batch-size", type=int, default=100, help="Log progress every N statements")
    parser.add_argument("--uri", type=str, default=AURA_URI, help="Neo4j URI")
    parser.add_argument("--user", type=str, default=AURA_USER, help="Neo4j user")
    parser.add_argument("--password", type=str, default=AURA_PASSWORD, help="Neo4j password")
    parser.add_argument("--db", type=str, default=AURA_DATABASE, help="Neo4j database")
    
    args = parser.parse_args()
    
    cypher_file = Path(args.file)
    if not cypher_file.exists():
        print(f"❌ File không tồn tại: {cypher_file}")
        sys.exit(1)
    
    print("=" * 60)
    print("🚀 Import Cypher File lên Neo4j Aura")
    print("=" * 60)
    print(f"URI: {args.uri}")
    print(f"Database: {args.db}")
    print()
    
    # Kết nối Neo4j
    try:
        driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
        
        # Test connection
        with driver.session(database=args.db) as session:
            result = session.run("RETURN 1 as test")
            if result.single()["test"] == 1:
                print("✅ Kết nối thành công!")
                print()
        
        # Execute Cypher file
        executed, errors = execute_cypher_file(driver, args.db, cypher_file, args.batch_size)
        
        driver.close()
        
        if errors > 0:
            sys.exit(1)
        return 0
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        sys.exit(1)

if __name__ == "__main__":
    sys.exit(main())

