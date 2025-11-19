# Hướng dẫn Setup - Recommendation System

## Cài đặt và chạy dự án (Windows + Neo4j local)

 Yêu cầu
- Python 3.10+
- Neo4j local (Desktop/Server)
  - URI: bolt://localhost:7687
  - Database: 
  - User: neo4j
  - Password: Admin123!

- PowerShell
## 🔧 Bước 1: Setup Python Environment

```powershell
# Tạo virtual environment
python -m venv .venv

# Kích hoạt (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Cài đặt dependencies
.\.venv\Scripts\pip install -r requirements.txt
## ⚡ Quick Start

### Chạy Backend (Terminal 1)
```powershell
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Chạy Frontend (Terminal 2)
```powershell
cd frontend
npm install  # Chỉ cần chạy lần đầu
npm run dev
```

**Kiểm tra:**
- Backend API: http://localhost:8000/docs
- Frontend App: http://localhost:3000

> **Lưu ý:** Đảm bảo Neo4j đang chạy và đã import dữ liệu

```

## 🗄️ Bước 2: Setup Neo4j

### 2.1. cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-65bfacb2-4779-4e59-b1df-0434e4ce14f2\bin>
neo4j console

```

### 2.2. Tạo Database và Schema
```powershell
# Tạo database
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "CREATE DATABASE test IF NOT EXISTS;"

# Tạo schema
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file backend/neo4j/schema.cypher
```

## 🥬 Bước 3: Import Ingredients

**Quan trọng:** Phải import ingredients trước recipes!

### Nếu đã có file Cypher:
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file backend/neo4j/canonical_ingredients_import.cypher
```

### Nếu chưa có file Cypher:
```powershell
cd backend
python scripts\import_canonical_ingredients.py `
  --input data/process/canonical_ingredients_migrated.json `
  --out-cypher neo4j/canonical_ingredients_import.cypher
```

Sau đó import file Cypher như trên.

## 🍽️ Bước 4: Import Recipes

### Nếu đã có file Cypher:
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file backend/neo4j/recipes_import.cypher
```

### Nếu chưa có file Cypher:

**Cách 1: Test nhanh (100 recipes, không cần semantic)**
```powershell
cd backend
python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients_migrated.json `
  --use-driver `
  --threshold 0.85 `
  --limit 100 `
  --verbose
```

**Cách 2: Production (toàn bộ recipes, có semantic fallback)**
```powershell
cd backend
python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients_migrated.json `
  --semantic `
  --threshold 0.80 `
  --semantic-threshold 0.85 `
  --out-cypher neo4j/recipes_import.cypher `
  --verbose
```

**Lưu ý:** Cách 2 cần cài thêm: `pip install sentence-transformers torch`

## 👥 Bước 5: Import Users (Optional)

```powershell
cd backend
python scripts\import_users_from_survey.py `
  --csv "data/users/users-survey.csv"
```

## 🧮 Bước 6: Compute Features

Tính toán TF-IDF, user vectors, và similarity graph:

```powershell
cd backend
python scripts\compute_features_improve.py `
  --db test --batch-size 500 --topk-terms 256 --topk-sim 50 `
  --half-life-days 90 --min-sim 0.05 --log-every 1000
```

## 🚀 Bước 7: Chạy Ứng dụng

### Backend (Terminal 1)
```powershell
cd backend
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend (Terminal 2)
```powershell
cd frontend
npm install  # Chỉ cần chạy lần đầu
npm run dev
```

**Kiểm tra:**
- Backend: http://localhost:8000/docs
- Frontend: http://localhost:3000

## 🎯 Bước 8: Test Recommendation (Optional)

```powershell
cd backend
python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "onion,tomato,chicken" `
  --limit 10
```

**Với user ID:**
```powershell
cd backend
python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --user-id survey_1 `
  --ingredient-names "onion,tomato,chicken" `
  --max-cook-time 45 `
  --preferred-cuisines "Vietnamese,Korean" `
  --limit 10
```

## 📝 Lưu ý Quan trọng

1. **Thứ tự import:** Ingredients → Recipes → Users → Compute Features
2. **File Cypher:** Nếu đã có file Cypher, dùng `cypher-shell` để import nhanh hơn
3. **Database:** Thay `test` bằng tên database của bạn
4. **Neo4j credentials:** Thay `Admin123!` bằng password Neo4j của bạn

## 🐛 Troubleshooting

- **Lỗi kết nối Neo4j:** Kiểm tra Neo4j đang chạy (http://localhost:7474)
- **Lỗi "Database not found":** Đảm bảo đã tạo database `test`
- **Lỗi "Module not found":** Chạy `pip install -r requirements.txt`
- **Lỗi encoding:** Đảm bảo file CSV/JSON dùng UTF-8
