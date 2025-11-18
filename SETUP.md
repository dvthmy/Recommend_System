# Hướng dẫn Setup và Import Dữ liệu - Recommendation System

Hướng dẫn đầy đủ để setup và import dữ liệu vào Neo4j từ đầu.

## ⚡ Quick Start - Chạy Nhanh Backend và Frontend

Nếu bạn đã có dữ liệu trong Neo4j và chỉ muốn chạy ứng dụng:

### Chạy Backend (Terminal 1)
```powershell
cd backend
.\.venv\Scripts\python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
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

> **Lưu ý:** Đảm bảo Neo4j đang chạy và đã import dữ liệu (xem các bước bên dưới)

## 📋 Yêu cầu

- Python 3.8+
- Neo4j Desktop hoặc Neo4j Community Edition
- PowerShell (Windows) hoặc Bash (Linux/Mac)

## 🔧 Bước 1: Setup Môi trường Python

### 1.1. Di chuyển đến thư mục project
```powershell
cd "D:\_Freelance-Project-Pool\Recommend foods"
# Hoặc đường dẫn tương ứng của bạn
```

### 1.2. Tạo virtual environment
```powershell
python -m venv .venv
```

### 1.3. Kích hoạt virtual environment
```powershell
# Windows PowerShell
.\.venv\Scripts\Activate.ps1

# Windows CMD
.\.venv\Scripts\activate.bat

# Linux/Mac
source .venv/bin/activate
```

### 1.4. Cài đặt dependencies
```powershell
.\.venv\Scripts\python -m pip install --upgrade pip
.\.venv\Scripts\pip install -r requirements.txt
```

## 🗄️ Bước 2: Setup Neo4j

### 2.1. Thêm Neo4j vào PATH
```powershell
# Thay đổi đường dẫn theo vị trí Neo4j của bạn
$env:Path = "C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-65bfacb2-4779-4e59-b1df-0434e4ce14f2\bin;$env:Path"
```

### 2.2. Kiểm tra kết nối Neo4j
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "SHOW DATABASES;"
```

### 2.3. Tạo Database
```powershell
# Drop database nếu đã tồn tại (an toàn)
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "DROP DATABASE test IF EXISTS;"

# Tạo database mới
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "CREATE DATABASE test;"

# Kiểm tra database đã được tạo
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "SHOW DATABASES YIELD name, currentStatus WHERE name='test' RETURN name, currentStatus;"
```

### 2.4. Tạo Schema (Constraints và Indexes)
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file db/neo4j/schema.cypher
```

## 🥬 Bước 3: Import Canonical Ingredients

**Quan trọng:** Phải import ingredients trước khi import recipes!

### 3.1. Tạo file Cypher để import (khuyến nghị)

Tạo file Cypher một lần, sau đó có thể import lại nhiều lần bằng cách chạy file Cypher:

```powershell
cd backend
.\.venv\Scripts\python scripts\import_canonical_ingredients.py `
  --input data/process/canonical_ingredients_migrated.json `
  --out-cypher db/neo4j/canonical_ingredients_import.cypher
```

**Lưu ý:** 
- Script sẽ đọc từ `data/process/canonical_ingredients_migrated.json` (file đã migrate với variants)
- Default input path đã là `canonical_ingredients_migrated.json`, nên có thể bỏ `--input` nếu dùng default

### 3.2. Import ingredients bằng file Cypher

Sau khi đã tạo file Cypher, bạn có thể import bằng cách:

**Cách 1: Sử dụng cypher-shell**
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file db/neo4j/canonical_ingredients_import.cypher
```

**Cách 2: Import trực tiếp bằng Python driver (nếu không muốn tạo file Cypher)**
```powershell
cd backend
.\.venv\Scripts\python scripts\import_canonical_ingredients.py `
  --input data/process/canonical_ingredients_migrated.json
```

**Hoặc chỉ định tham số khác:**
```powershell
cd backend
.\.venv\Scripts\python scripts\import_canonical_ingredients.py `
  --input data/process/canonical_ingredients_migrated.json `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password Admin123! `
  --db test `
  --batch-size 1000 `
  --verbose
```

**Lưu ý:** 
- File Cypher có thể được tái sử dụng nhiều lần
- Import bằng Cypher nhanh hơn và không cần Python environment

## 🍽️ Bước 4: Import Recipes

### 4.1. Import recipes cơ bản (khuyến nghị để test)

**Dùng cho:** Test nhanh với số lượng nhỏ recipes (100 recipes)

```powershell
.\.venv\Scripts\python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients_migrated.json `
  --use-driver `
  --threshold 0.85 `
  --verbose `
  --limit 100
```

**Đặc điểm:**
- ✅ Không cần cài thêm package (chỉ dùng fuzzy matching)
- ✅ Nhanh, phù hợp để test
- ⚠️ Chỉ import 100 recipes đầu tiên (`--limit 100`)
- ⚠️ Không có semantic fallback (có thể miss một số ingredients khó match)

### 4.2. Import recipes với semantic fallback (khuyến nghị cho production)

**Dùng cho:** Import toàn bộ recipes với độ chính xác cao

**Cách 1: Import trực tiếp (như cũ)**
```powershell
.\.venv\Scripts\python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients_migrated.json `
  --use-driver `
  --semantic `
  --threshold 0.80 `
  --semantic-threshold 0.85 `
  --verbose
```

**Cách 2: Tạo file Cypher để import lại nhiều lần (khuyến nghị)**
```powershell
.\.venv\Scripts\python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients_migrated.json `
  --semantic `
  --threshold 0.80 `
  --semantic-threshold 0.85 `
  --out-cypher db/neo4j/recipes_import.cypher `
  --verbose `
  --cypher-log-batch-size 100
```

Sau đó import file Cypher:
```powershell
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d test --file db/neo4j/recipes_import.cypher
```

**Đặc điểm:**
- ✅ Có semantic fallback (match tốt hơn với ingredients khó)
- ✅ Import toàn bộ recipes (không có `--limit`)
- ✅ Threshold thấp hơn (0.80) vì có semantic backup
- ⚠️ Cần cài thêm: `pip install sentence-transformers torch`
- ⚠️ Chậm hơn do phải encode embeddings

**So sánh:**

| Tính năng | 4.1 (Cơ bản) | 4.2 (Semantic) |
|-----------|--------------|----------------|
| Fuzzy matching | ✅ (threshold 0.85) | ✅ (threshold 0.80) |
| Semantic fallback | ❌ | ✅ (threshold 0.85) |
| Số lượng recipes | 100 (test) | Toàn bộ |
| Tốc độ | Nhanh | Chậm hơn |
| Độ chính xác | Tốt | Rất tốt |
| Yêu cầu | Không | sentence-transformers |

**Lưu ý:** Nếu chưa cài semantic packages, dùng lệnh 4.1. Nếu muốn độ chính xác cao, cài packages và dùng lệnh 4.2:

```powershell
pip install sentence-transformers torch
```

## 👥 Bước 5: Import Users

### 5.1. Import users từ survey CSV
```powershell
.\.venv\Scripts\python scripts\import_users_from_survey.py `
  --csv "data/users/users-survey.csv"
```

## 🧮 Bước 6: Compute Features

Tính toán các features cần thiết cho recommendation system (TF-IDF, user vectors, etc.)


### 6.2. Compute features nâng cao (khuyến nghị)
```powershell
.\.venv\Scripts\python scripts\compute_features_improve.py `
  --db test `
  --batch-size 500 `
  --topk-terms 256 `
  --topk-sim 50 `
  --half-life-days 90 `
  --min-sim 0.05 `
  --log-every 1000
```

**Các tham số:**
- `--batch-size`: Kích thước batch xử lý
- `--topk-terms`: Số lượng terms hàng đầu cho TF-IDF
- `--topk-sim`: Số lượng recipes tương tự hàng đầu
- `--half-life-days`: Thời gian bán hủy cho popularity decay
- `--min-sim`: Ngưỡng similarity tối thiểu

## 🚀 Bước 7: Chạy Backend và Frontend

### 7.1. Chạy Backend API Server

**Yêu cầu:**
- ✅ Neo4j đang chạy (kiểm tra: http://localhost:7474)
- ✅ Đã import dữ liệu (ingredients, recipes, users) - xem Bước 3, 4, 5
- ✅ Python virtual environment đã được kích hoạt

**Cách 1: Chạy trực tiếp với uvicorn (Khuyến nghị)**
```powershell
cd backend
.\.venv\Scripts\python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Cách 2: Chạy bằng script Python**
```powershell
cd backend
.\.venv\Scripts\python api/main.py
```

**Kiểm tra backend đang chạy:**
- ✅ Root endpoint: http://localhost:8000
- ✅ API Documentation: http://localhost:8000/docs (Swagger UI)
- ✅ API Schema: http://localhost:8000/openapi.json
- ✅ ReDoc: http://localhost:8000/redoc

**Cấu hình Backend:**
- **Port mặc định:** `8000` (có thể thay đổi bằng `--port`)
- **Host:** `0.0.0.0` (cho phép truy cập từ mọi IP)
- **Auto-reload:** Bật khi dùng `--reload` (tự động reload khi code thay đổi)
- **CORS:** Cho phép tất cả origins (`*`) trong development
- **Neo4j:** Kết nối đến `bolt://localhost:7687`, database `test`
- **Cấu hình nâng cao:** Có thể thay đổi trong `backend/api/config.py` hoặc file `.env`

**Troubleshooting Backend:**
- ❌ **Lỗi "Connection refused"**: Kiểm tra Neo4j đang chạy
- ❌ **Lỗi "Database not found"**: Đảm bảo database `test` đã được tạo
- ❌ **Lỗi "Module not found"**: Chạy `pip install -r requirements.txt` trong virtual environment
- ❌ **Port 8000 đã được sử dụng**: Thay đổi port bằng `--port 8001`

### 7.2. Chạy Frontend Application

**Yêu cầu:**
- ✅ Node.js 16+ (kiểm tra: `node --version`)
- ✅ npm hoặc yarn (kiểm tra: `npm --version` hoặc `yarn --version`)
- ✅ Backend API đang chạy (http://localhost:8000)

**Cài đặt dependencies (chỉ cần chạy lần đầu):**
```powershell
cd frontend
npm install
# Hoặc nếu dùng yarn
yarn install
```

**Chạy development server:**
```powershell
cd frontend
npm run dev
# Hoặc
yarn dev
```

**Frontend sẽ chạy tại:**
- ✅ URL: http://localhost:3000
- ✅ Tự động mở trình duyệt khi chạy (nếu `open: true` trong `vite.config.ts`)
- ✅ Hot Module Replacement (HMR) - tự động reload khi code thay đổi

**Cấu hình Frontend:**
- **Port mặc định:** `3000` (có thể thay đổi trong `frontend/vite.config.ts`)
- **API endpoint:** `http://localhost:8000` (có thể thay đổi trong `frontend/src/config/api.ts`)
- **Build tool:** Vite (nhanh hơn webpack)
- **Framework:** React 18 với TypeScript

**Troubleshooting Frontend:**
- ❌ **Lỗi "Cannot find module"**: Chạy `npm install` lại
- ❌ **Lỗi "Port 3000 already in use"**: Thay đổi port trong `vite.config.ts` hoặc dùng `npm run dev -- --port 3001`
- ❌ **Lỗi kết nối API**: Kiểm tra Backend đang chạy và URL trong `frontend/src/config/api.ts`
- ❌ **Lỗi CORS**: Kiểm tra cấu hình CORS trong Backend (`backend/api/config.py`)

### 7.3. Chạy cả Backend và Frontend cùng lúc

Để chạy cả hai, bạn cần mở **2 terminal riêng biệt**:

**Terminal 1 - Backend:**
```powershell
# Di chuyển đến thư mục backend
cd backend

# Kích hoạt virtual environment (nếu chưa kích hoạt)
.\.venv\Scripts\Activate.ps1

# Chạy Backend API
.\.venv\Scripts\python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend:**
```powershell
# Di chuyển đến thư mục frontend
cd frontend

# Chạy Frontend development server
npm run dev
```

**Kiểm tra ứng dụng:**
- ✅ **Backend API:** http://localhost:8000/docs
- ✅ **Frontend App:** http://localhost:3000
- ✅ **API Health:** http://localhost:8000/ (trả về JSON với version info)

**Lưu ý:**
- Backend phải chạy trước Frontend (hoặc cùng lúc)
- Nếu Backend dừng, Frontend sẽ không thể gọi API
- Cả hai đều hỗ trợ hot-reload (tự động reload khi code thay đổi)

### 7.4. Build Frontend cho Production

**Build production:**
```powershell
cd frontend
npm run build
# Hoặc
yarn build
```

**Preview production build (kiểm tra trước khi deploy):**
```powershell
npm run preview
# Hoặc
yarn preview
```

**Output:**
- ✅ File build sẽ nằm trong thư mục `frontend/dist/`
- ✅ Có thể deploy thư mục `dist/` lên bất kỳ static hosting nào (Vercel, Netlify, GitHub Pages, etc.)

**Lưu ý khi build:**
- Đảm bảo cấu hình API endpoint trong `frontend/src/config/api.ts` đúng với production URL
- Kiểm tra environment variables nếu có
- Test production build bằng `npm run preview` trước khi deploy

## 🎯 Bước 8: Test Recommendation với `recommend_graph.py`

Script `recommend_graph.py` sử dụng **Knowledge-Based Reasoning** (không tính điểm, dựa vào tri thức IF-THEN logic) với Jaccard similarity để gợi ý công thức nấu ăn.

### 8.1. Recommendation cơ bản dựa trên ingredient IDs

**Sử dụng ingredient IDs:**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredients ing_onion,ing_tomato,ing_chicken `
  --limit 10
```

**Sử dụng ingredient names (tự động map sang IDs):**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "onion,tomato,chicken" `
  --limit 10
```

### 8.2. Recommendation với user ID (có profile và lịch sử)

**Recommendation cho user cụ thể:**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --user-id survey_1 `
  --ingredient-names "onion,tomato,chicken" `
  --max-cook-time 45 `
  --limit 10
```

**Với preferred cuisines:**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --user-id survey_1 `
  --ingredient-names "onion,tomato,chicken" `
  --preferred-cuisines "Vietnamese,Korean,Japanese" `
  --max-cook-time 45 `
  --limit 10
```

### 8.3. Recommendation với filter recipe category

**Filter theo meal type (breakfast, lunch, dinner, etc.):**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "egg,bacon,cheese" `
  --recipe-category "breakfast" `
  --limit 10
```

**Không filter category (tất cả categories):**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "onion,tomato" `
  --recipe-category "no preference" `
  --limit 10
```

### 8.4. Recommendation với min match ratio

**Chỉ lấy recipes có match ratio >= 50%:**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "onion,tomato,chicken" `
  --min-match 0.5 `
  --limit 10
```

### 8.5. Recommendation với output JSON

**Output dạng JSON (để parse hoặc tích hợp):**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --db test `
  --password "Admin123!" `
  --ingredient-names "onion,tomato,chicken" `
  --limit 10 `
  --json
```

### 8.6. Recommendation đầy đủ tham số

**Ví dụ với tất cả tham số:**
```powershell
cd backend
.\.venv\Scripts\python scripts\recommend_graph.py `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db test `
  --user-id survey_1 `
  --ingredient-names "onion,tomato,chicken,garlic" `
  --max-cook-time 60 `
  --recipe-category "dinner" `
  --preferred-cuisines "Vietnamese,Korean" `
  --min-match 0.4 `
  --limit 20 `
  --json
```

### 8.7. Các tham số của `recommend_graph.py`

**Kết nối Neo4j:**
- `--uri`: Neo4j URI (mặc định: `bolt://localhost:7687`)
- `--user`: Username (mặc định: `neo4j`)
- `--password`: Password (mặc định: `Admin123!`)
- `--db`: Database name (mặc định: `test`)

**Input ingredients:**
- `--ingredients`: Danh sách ingredient IDs (phân cách bằng dấu phẩy), ví dụ: `ing_onion,ing_tomato`
- `--ingredient-names`: Danh sách ingredient names (tự động map sang IDs), ví dụ: `"onion,tomato,chicken"`

**User context:**
- `--user-id`: ID của user (optional, nếu có sẽ dùng profile và lịch sử tương tác)

**Filters:**
- `--max-cook-time`: Thời gian nấu tối đa (phút)
- `--recipe-category`: Filter theo meal type (`breakfast`, `lunch`, `dinner`, `snack`, etc.)
  - Dùng `"no preference"`, `"none"`, hoặc `"all"` để không filter
- `--preferred-cuisines`: Danh sách cuisines ưu tiên (phân cách bằng dấu phẩy), ví dụ: `"Vietnamese,Korean,Japanese"`
  - Hệ thống sẽ ưu tiên recipes có cuisine khớp với list này

**Recommendation settings:**
- `--limit`: Số lượng recommendations trả về (mặc định: `30`)
- `--min-match`: Minimum Jaccard match ratio (mặc định: `0.4`)
  - Recipes có match ratio < min-match sẽ bị loại bỏ

**Output:**
- `--json`: Output dạng JSON thay vì text format

### 8.8. Giải thích kết quả

**Text format (mặc định):**
```
#1. Recipe Title (rec_123)
   🍳 Match: 75.5%
   • ✅ Shares most of your given ingredients
   • 🍜 Matches your favorite cuisine
   • ⭐ Top-rated recipe
   ✅ Matched: ing_onion, ing_tomato, ing_chicken
   📝 Missing: ing_garlic, ing_pepper
   ⏱️  Cook time: 45 min
   🍽️  Category: dinner
```

**JSON format (`--json`):**
```json
{
  "results": [
    {
      "recipe_id": "rec_123",
      "title": "Recipe Title",
      "cuisine": ["Vietnamese", "Asian"],
      "tags": ["dinner", "main dish"],
      "recipe_category": "dinner",
      "match_percent": 75.5,
      "cook_time_min": 45,
      "image": "https://...",
      "matched_ing": ["ing_onion", "ing_tomato", "ing_chicken"],
      "missing_ing": ["ing_garlic", "ing_pepper"],
      "reasoning": [
        "✅ Shares most of your given ingredients",
        "🍜 Matches your favorite cuisine",
        "⭐ Top-rated recipe"
      ]
    }
  ]
}
```

### 8.9. Lưu ý về `recommend_graph.py`

**Đặc điểm:**
- ✅ **Knowledge-Based Reasoning**: Không tính điểm, dựa vào tri thức (IF-THEN logic)
- ✅ **Jaccard Similarity**: Tính độ tương đồng nguyên liệu bằng công thức Jaccard
- ✅ **Explainable**: Mỗi recommendation có lý do giải thích (`reasoning`)
- ✅ **Ingredient Importance**: Ưu tiên recipes có protein, carbo, vegetables hơn herbs/spices
- ✅ **Cuisine Priority**: Ưu tiên recipes khớp với preferred cuisines
- ✅ **User Profile**: Sử dụng allergies, fav_cuisines, max_cook_time từ user profile
- ✅ **Interaction History**: Xem xét lịch sử tương tác của user (nếu có `--user-id`)

**So sánh với `recommend.py`:**
- `recommend_graph.py`: Knowledge-based, explainable, không tính điểm
- `recommend.py`: Hybrid scoring (TF-IDF, popularity, collaborative filtering)

## 📝 Lưu ý Quan trọng

1. **Thứ tự import:** Phải import ingredients trước recipes
2. **Database name:** Thay `test` bằng tên database của bạn nếu khác
3. **Neo4j credentials:** Thay `Admin123!` bằng password Neo4j của bạn
4. **Đường dẫn:** Đảm bảo các đường dẫn file CSV/JSON đúng với cấu trúc thư mục của bạn
5. **Encoding:** Nếu gặp lỗi encoding, đảm bảo file CSV/JSON sử dụng UTF-8

## 🐛 Troubleshooting

### Lỗi encoding khi import
- Đảm bảo file CSV/JSON sử dụng UTF-8 encoding
- Script đã xử lý encoding errors tự động

### Lỗi kết nối Neo4j
- Kiểm tra Neo4j đang chạy
- Kiểm tra URI, username, password
- Kiểm tra database đã được tạo

### Lỗi missing ingredients
- Đảm bảo đã import canonical ingredients trước
- Kiểm tra ingredient IDs trong recipes match với canonical ingredients

### Lỗi import recipes
- Kiểm tra file CSV có đúng format
- Kiểm tra file canonical_ingredients.json tồn tại
- Sử dụng `--verbose` để xem log chi tiết

## 📚 Tài liệu tham khảo

- Neo4j Python Driver: https://neo4j.com/docs/python-manual/current/
- Sentence Transformers: https://www.sbert.net/
- Cypher Query Language: https://neo4j.com/docs/cypher-manual/current/

