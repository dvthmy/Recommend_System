#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Recipes lên Neo4j Aura
Sử dụng thông tin từ test_aura_connection.py
"""
import subprocess
import sys
import os
from pathlib import Path

# Neo4j Aura credentials
AURA_URI = "neo4j+s://3b0d8961.databases.neo4j.io"
AURA_USER = "neo4j"
AURA_PASSWORD = "qV5l-Ck8vasO5qoM65gjWhuJTa2HBr4e6KwSYJ0RfT0"
AURA_DATABASE = "neo4j"

def main():
    # Đảm bảo đang ở thư mục backend
    script_dir = Path(__file__).parent
    backend_dir = script_dir.parent
    os.chdir(backend_dir)
    
    print("=" * 60)
    print("🚀 Import Recipes lên Neo4j Aura")
    print("=" * 60)
    print(f"URI: {AURA_URI}")
    print(f"Database: {AURA_DATABASE}")
    print()
    
    # Kiểm tra file CSV và labels
    csv_path = Path("data/recipes/full_data_ing.csv")
    labels_path = Path("data/ingredients/canonical_ingredients_migrated.json")
    
    if not csv_path.exists():
        print(f"❌ Không tìm thấy file CSV: {csv_path}")
        sys.exit(1)
    
    if not labels_path.exists():
        print(f"❌ Không tìm thấy file labels: {labels_path}")
        sys.exit(1)
    
    print(f"✅ CSV: {csv_path}")
    print(f"✅ Labels: {labels_path}")
    print()
    
    # Output Cypher file path (đầy đủ Recipe nodes và HAS_INGREDIENT relationships)
    output_cypher = Path("neo4j/recipes_import.cypher")
    output_cypher.parent.mkdir(parents=True, exist_ok=True)
    
    # Build command - Vừa import vào Aura vừa generate Cypher file
    # Sử dụng python executable hiện tại (từ venv)
    python_exe = sys.executable
    
    cmd = [
        python_exe, "scripts/import_recipe_AI.py",
        "--csv", str(csv_path),
        "--labels", str(labels_path),
        "--threshold", "0.80",
        "--use-driver",  # Import trực tiếp vào Aura
        "--out-cypher", str(output_cypher),  # Và đồng thời lưu vào file Cypher
        "--uri", AURA_URI,
        "--user", AURA_USER,
        "--password", AURA_PASSWORD,
        "--db", AURA_DATABASE,
        "--batch-size", "20",  # Batch size cho import (test với 20)
        "--cypher-log-batch-size", "20",  # Log mỗi 20 recipes khi generate Cypher
        "--log-every", "20",  # Log progress mỗi 20 recipes
         # Test với 100 recipes đầu tiên
        "--verbose"  # Verbose logging
    ]
    
    print(f"📋 Command: {' '.join(cmd[:6])} ... (với --use-driver và --out-cypher)")
    print("✨ Chế độ: Vừa import vào Aura vừa lưu file Cypher")
    print()
    
    print("📝 Bắt đầu import recipes...")
    print(f"   - Import trực tiếp vào Neo4j Aura")
    print(f"   - Đồng thời lưu Cypher file: {output_cypher}")
    print()
    print("🛡️  Xử lý duplicate:")
    print("   - Script sử dụng MERGE (không tạo duplicate)")
    print("   - Nếu recipe chưa tồn tại: tạo mới")
    print("   - Nếu recipe đã tồn tại: cập nhật properties")
    print()
    print("✅ Sẽ tạo/cập nhật:")
    print("   - Recipe nodes với đầy đủ properties")
    print("   - HAS_INGREDIENT relationships")
    print()
    
    # Run generate Cypher - với real-time output
    try:
        print("🔄 Đang chạy import_recipe_AI.py...")
        print()
        result = subprocess.run(
            cmd, 
            check=True,
            stdout=sys.stdout,  # Hiển thị output real-time
            stderr=sys.stderr,  # Hiển thị error real-time
            cwd=backend_dir
        )
        print()
        print("=" * 60)
        if output_cypher.exists():
            print("✅ Hoàn tất!")
            print(f"   ✓ Đã import vào Neo4j Aura")
            print(f"   ✓ Đã lưu Cypher file: {output_cypher}")
            print(f"   📊 File size: {output_cypher.stat().st_size / 1024:.1f} KB")
            print()
            print("💡 Bạn có thể dùng file Cypher để import lại nếu cần:")
            print(f"   python scripts/import_cypher_to_aura.py --file {output_cypher}")
        else:
            print("⚠️  File Cypher không được tạo. Kiểm tra lỗi ở trên.")
            print("   (Nhưng có thể đã import vào Aura thành công)")
        print("=" * 60)
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"❌ Lỗi khi generate Cypher: {e}")
        print(f"   Return code: {e.returncode}")
        print("=" * 60)
        return 1
    except KeyboardInterrupt:
        print()
        print("⚠️  Import bị hủy bởi người dùng")
        return 1
    except FileNotFoundError:
        print()
        print("=" * 60)
        print(f"❌ Không tìm thấy script: scripts/import_recipe_AI.py")
        print(f"   Đảm bảo đang chạy từ thư mục backend")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())

