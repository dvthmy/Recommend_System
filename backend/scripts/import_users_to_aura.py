#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Import Users từ Survey CSV lên Neo4j Aura
"""
import subprocess
import sys
import os
from pathlib import Path

# Fix encoding for Windows console
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

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
    print("🚀 Import Users từ Survey lên Neo4j Aura")
    print("=" * 60)
    print(f"URI: {AURA_URI}")
    print(f"Database: {AURA_DATABASE}")
    print()
    
    # Tìm file CSV survey
    # Thử các đường dẫn phổ biến
    possible_csv_paths = [
        Path("data/users/users.csv"),

    ]
    
    csv_path = None
    for path in possible_csv_paths:
        if path.exists():
            csv_path = path
            break
    
    if not csv_path:
        print("❌ Không tìm thấy file CSV survey!")
        print("   Đã thử các đường dẫn:")
        for path in possible_csv_paths:
            print(f"   - {path}")
        print()
        print("💡 Vui lòng chỉ định đường dẫn file CSV:")
        print("   python scripts/import_users_to_aura.py --csv <path_to_survey.csv>")
        sys.exit(1)
    
    print(f"✅ Tìm thấy CSV: {csv_path}")
    print()
    
    # Sử dụng python executable hiện tại (từ venv)
    python_exe = sys.executable
    
    cmd = [
        python_exe, "scripts/import_users_from_survey.py",
        "--csv", str(csv_path),
        "--uri", AURA_URI,
        "--user", AURA_USER,
        "--password", AURA_PASSWORD,
        "--db", AURA_DATABASE,
    ]
    
    print(f"📋 Command: {' '.join(cmd[:4])} ... (với Aura credentials)")
    print()
    print("🛡️  Xử lý duplicate:")
    print("   - Xóa user cũ nếu trùng email hoặc user_id")
    print("   - Xóa tất cả relationships cũ (ALLERGIC_TO, FAVORS_CUISINE, INTERACTED_WITH)")
    print("   - Tạo lại user và relationships mới từ survey")
    print()
    print("📝 Bắt đầu import users...")
    print()
    
    # Run import - với real-time output
    try:
        print("🔄 Đang chạy import_users_from_survey.py...")
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
        print("✅ Hoàn tất!")
        print("   ✓ Đã import users vào Neo4j Aura")
        print("   ✓ Đã tạo/cập nhật relationships")
        print("=" * 60)
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print(f"❌ Lỗi khi import users: {e}")
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
        print(f"❌ Không tìm thấy script: scripts/import_users_from_survey.py")
        print(f"   Đảm bảo đang chạy từ thư mục backend")
        print("=" * 60)
        return 1

if __name__ == "__main__":
    sys.exit(main())
