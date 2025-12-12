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

Có 2 cách để setup Neo4j: **Neo4j Community Edition trực tiếp** hoặc **Neo4j Desktop 2**.

### 2.1. Cách 1: Chạy Neo4j Community Edition trực tiếp (Đã tải về)

Nếu bạn đã tải và giải nén Neo4j Community Edition (ví dụ: `C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1`):

1. **Thiết lập mật khẩu ban đầu (Lần đầu tiên):**
```powershell
# Chuyển vào thư mục bin
cd C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin

# Thiết lập mật khẩu ban đầu cho user neo4j
.\neo4j-admin.bat dbms set-initial-password Admin123!
```

2. **Khởi động Neo4j:**
```powershell
# Từ thư mục bin
.\neo4j.bat console
```

3. **Kiểm tra Neo4j đã chạy:**
   - Đợi đến khi thấy dòng: `Started.`
   - Mở trình duyệt: http://localhost:7474
   - Đăng nhập:
     - **Username**: `neo4j`
     - **Password**: `Admin123!` (mật khẩu bạn đã đặt)

4. **Dừng Neo4j:**
   - Nhấn `Ctrl+C` trong terminal đang chạy `neo4j.bat console`

**Lưu ý:**
- Giữ terminal mở để Neo4j tiếp tục chạy
- Nếu đóng terminal, Neo4j sẽ dừng
- Dữ liệu được lưu trong thư mục `data` của Neo4j
- **Community Edition miễn phí vĩnh viễn, không cần license!**



### 2.2. Cách 2: Dùng Neo4j Desktop 2

**⚠️ Quan trọng:** Neo4j Desktop 2 **chỉ hỗ trợ Enterprise Edition** (trial 30 ngày), không có tùy chọn Community Edition trong giao diện.

**Các lựa chọn:**

#### Lựa chọn A: Dùng Neo4j Desktop 2 với Enterprise Edition (Trial 30 ngày)

1. **Tạo Instance mới trong Neo4j Desktop 2**
   - Mở Neo4j Desktop 2
   - **Lần đầu tiên:** Nhấn nút **"Create instance"** ở giữa màn hình
   - **Đã có instance:** Nhấn nút **"Create instance"** ở góc trên bên phải
   - Điền thông tin:
     - **Tên instance**: Tên cho instance (ví dụ: "My Recommendation DBMS")
     - **Phiên bản Neo4j**: Chọn phiên bản (chỉ có Enterprise Edition)
     - **Username**: `neo4j` (mặc định)
     - **Password**: `Admin123!` (hoặc mật khẩu khác - **ghi nhớ mật khẩu này!**)
   - Nhấn **"Create"** để tạo instance

2. **Khởi động Instance**
   - Tìm instance vừa tạo trong danh sách
   - Nhấn nút **"Play"** (▶️) trên thẻ instance
   - Đợi đến khi trạng thái là **"Running"**

3. **Chấp nhận License (Nếu cần)**
   ```powershell
   # Tìm đường dẫn bin của instance (thay dbms-XXXXX bằng ID instance của bạn)
   cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-XXXXX\bin
   .\neo4j-admin.bat server license --accept-evaluation
   ```

**Lưu ý về Neo4j Desktop 2:**
- Chỉ cho phép **một instance chạy tại một thời điểm**
- Enterprise Edition có trial 30 ngày, sau đó cần license trả phí
- ⚠️ **Không phù hợp cho development lâu dài**

### 2.2.1. Chạy Neo4j Community Edition đã tải về

Nếu bạn đã tải Neo4j Community Edition (ví dụ: `C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1`):

**Bước 1: Thiết lập mật khẩu ban đầu (Chỉ lần đầu tiên)**
```powershell
cd C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin
.\neo4j-admin.bat dbms set-initial-password Admin123!
```

**Bước 2: Khởi động Neo4j**
```powershell
# Từ thư mục bin
.\neo4j.bat console
```

**Bước 3: Kiểm tra**
- Đợi đến khi thấy: `Started.`
- Mở trình duyệt: http://localhost:7474
- Đăng nhập: Username `neo4j`, Password `Admin123!`

**Dừng Neo4j:** Nhấn `Ctrl+C` trong terminal

**Thông tin kết nối:**
- URI mặc định: `bolt://localhost:7687`
- Port có thể khác nếu có nhiều instance (7687, 7688, 7689...)
- Username: `neo4j` (mặc định)
- Password: Mật khẩu bạn đã đặt khi tạo instance

**Lưu ý về Neo4j Desktop 2:**
- Chỉ một instance có thể chạy tại một thời điểm
- Mỗi instance có thể chứa nhiều database
- **Nếu muốn chạy từ command line** (không khuyến nghị):
  ```powershell
  # Phải dùng .bat trên Windows
  # Chạy 2 lệnh riêng biệt (quan trọng: phải có khoảng trắng giữa các lệnh!)
  cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin
  .\neo4j.bat console
  ```
  **Hoặc chạy 1 lệnh duy nhất:**
  ```powershell
  cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin; .\neo4j.bat console
  ```
  ⚠️ **Lưu ý:** Tốt nhất là dùng nút Start trong Neo4j Desktop, không cần chạy lệnh console này!

### 2.3. Xử lý lỗi Authentication (Nếu gặp lỗi "Unauthorized")

Nếu bạn gặp lỗi **"The client is unauthorized due to authentication failure"**, có thể do:

1. **Mật khẩu sai** - Kiểm tra lại mật khẩu bạn đã đặt khi tạo DBMS
2. **Chưa đổi mật khẩu lần đầu** - Neo4j yêu cầu đổi mật khẩu lần đầu tiên

**Cách 1: Reset mật khẩu qua Neo4j Desktop (Dễ nhất)**
1. Mở Neo4j Desktop
2. Chọn DBMS của bạn
3. Nhấn nút **"Reset Password"** hoặc **"..."** → **"Reset Password"**
4. Đặt mật khẩu mới (ví dụ: `Admin123!`)
5. Ghi nhớ mật khẩu này để dùng trong các lệnh sau

**Cách 2: Đổi mật khẩu qua cypher-shell (Nếu biết mật khẩu cũ)**
```powershell
# Đổi mật khẩu từ mật khẩu cũ sang mật khẩu mới (dùng đường dẫn đầy đủ)
C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin\cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "password_cu" -d system "ALTER CURRENT USER SET PASSWORD FROM 'password_cu' TO 'Admin123!';"
```

**Cách 3: Reset mật khẩu bằng cách xóa file auth (Nếu quên mật khẩu)**
```powershell
# Dừng Neo4j trước (Ctrl+C trong terminal đang chạy neo4j.bat)
# Xóa file auth (thay dbms-XXXXX bằng ID DBMS của bạn)
Remove-Item "C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\data\dbms\auth"
# Khởi động lại Neo4j
cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin
.\neo4j.bat console
# Sau đó đăng nhập với mật khẩu mặc định (thường là mật khẩu bạn đặt khi tạo DBMS)
```

### 2.4. Chấp nhận License Agreement (Nếu dùng Enterprise Edition)

**⚠️ Lưu ý:** Nếu bạn dùng **Community Edition**, không cần chấp nhận license! Community Edition miễn phí và không giới hạn thời gian.

Nếu bạn gặp lỗi về license khi chạy `cypher-shell` (thường xảy ra với Enterprise Edition):

```powershell
# Chuyển vào thư mục bin
cd C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin

# Chấp nhận evaluation license (cho Enterprise Edition - trial 30 ngày)
.\neo4j-admin.bat server license --accept-evaluation
```

**Khuyến nghị:** 
- **Tốt nhất:** Dùng **Community Edition** (không cần license, miễn phí vĩnh viễn)
- Enterprise Edition chỉ dùng nếu bạn cần các tính năng enterprise (thường không cần cho development)

### 2.5. Xóa Database "test" (Nếu có) và Import vào Database "neo4j"

**Sử dụng database mặc định "neo4j"** thay vì tạo database mới. Nếu đã có database "test", xóa nó trước:

**Quan trọng:** `cypher-shell.bat` nằm trong thư mục `bin` của Neo4j. Bạn cần dùng đường dẫn đầy đủ hoặc cd vào thư mục đó trước.

**Cách 1: Dùng đường dẫn đầy đủ (Khuyến nghị)**

**Nếu dùng Neo4j Community Edition (port 7688):**
```powershell
# Xóa database "test" nếu có (từ thư mục gốc project)
C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin\cypher-shell.bat -a bolt://localhost:7688 -u neo4j -p "Admin123!" -d system "DROP DATABASE test IF EXISTS;"

# Kiểm tra databases
C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin\cypher-shell.bat -a bolt://localhost:7688 -u neo4j -p "Admin123!" -d system "SHOW DATABASES;"

# Tạo schema trong database "neo4j" (mặc định) - từ thư mục gốc của project
C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin\cypher-shell.bat -a bolt://localhost:7688 -u neo4j -p "Admin123!" -d neo4j --file backend/neo4j/schema.cypher
```

**Nếu dùng Neo4j Desktop 2 (port 7687):**
```powershell
# Xóa database "test" nếu có
C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin\cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "DROP DATABASE test IF EXISTS;"

# Kiểm tra databases
C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin\cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system "SHOW DATABASES;"

# Tạo schema trong database "neo4j" (mặc định)
C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin\cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d neo4j --file backend/neo4j/schema.cypher
```



## 🥬 Bước 3: Import Ingredients

**Quan trọng:** Phải import ingredients trước recipes!

### ⚡ Import nhanh lên Neo4j Desktop (Database: neo4j)

**Thông tin kết nối Neo4j Desktop:**
- URI: `bolt://localhost:7687`
- Database: `neo4j`
- User: `neo4j`
- Password: `Admin123!` (hoặc password bạn đã đặt)

**Bước 1: Import Ingredients (Nhanh với batch-size lớn)**
```powershell
cd backend
python scripts\import_canonical_ingredients.py `
  --input data/ingredients/canonical_ingredients_migrated.json `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j `
  --batch-size 5000
```

**Bước 2: Import Recipes (Mapping đơn giản theo category - Rất nhanh!)**
```powershell
cd backend
python scripts\import_recipes_simple.py `
  --csv data/recipes/full_data_ing.csv `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j `
  --batch-size 10000
```

**Lưu ý:** Script này map ingredients theo 6 categories đơn giản: `grain`, `meat`, `seafood`, `sauce`, `vegetable`, `fruit`. Không cần fuzzy matching phức tạp → nhanh hơn nhiều!

**Bước 3: Import Users**
```powershell
cd backend
python scripts\import_users_from_survey.py `
  --csv "data/users/users.csv" `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j
```

**Thời gian ước tính:**
- Ingredients: ~5-15 giây (với batch-size 5000)
- Recipes (40,000): ~1-2 phút (mapping đơn giản theo category)
- Users: ~10-30 giây
- **Tổng: ~2-3 phút**

---

### 📋 Import chi tiết (nếu cần)

### Nếu đã có file Cypher:

**Nếu dùng Neo4j Community Edition (port 7688):**
```powershell
# Từ thư mục gốc project
C:\Users\ThaoMuy\Downloads\neo4j-community-2025.10.1\bin\cypher-shell.bat -a bolt://localhost:7688 -u neo4j -p "Admin123!" -d neo4j --file backend/neo4j/canonical_ingredients_import.cypher
```

**Nếu dùng Neo4j Desktop 2 (port 7687):**
```powershell
# Từ thư mục gốc project
C:\Users\ThaoMuy\.Neo4jDesktop2\Data\dbmss\dbms-63cf7dd7-4183-4766-8e04-1985cd75de58\bin\cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d neo4j --file backend/neo4j/canonical_ingredients_import.cypher
```

### Nếu chưa có file Cypher:
```powershell
cd backend
python scripts\import_canonical_ingredients.py `
  --input data/ingredients/canonical_ingredients_migrated.json `
  --out-cypher neo4j/canonical_ingredients_import.cypher
```

Sau đó import file Cypher như trên.

## 🍽️ Bước 4: Import Recipes

### ⚡ Cách đơn giản nhất (Mapping theo category - Khuyến nghị)

**Import recipes với mapping đơn giản theo 6 categories:**
- `grain`: rice, flour, bread, pasta, wheat, oats...
- `meat`: beef, pork, chicken, turkey, lamb...
- `seafood`: fish, salmon, tuna, shrimp, crab...
- `sauce`: sauce, ketchup, mustard, mayonnaise...
- `vegetable`: tomato, onion, garlic, carrot, potato...
- `fruit`: apple, banana, orange, lemon, berry...

```powershell
cd backend
python scripts\import_recipes_simple.py `
  --csv data/recipes/full_data_ing.csv `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j `
  --batch-size 10000
```

**Test với số lượng nhỏ:**
```powershell
cd backend
python scripts\import_recipes_simple.py `
  --csv data/recipes/full_data_ing.csv `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j `
  --batch-size 10000 `
  --limit 100 `
  --verbose
```

**Ưu điểm:**
- ⚡ Rất nhanh (không cần fuzzy matching, semantic similarity)
- 🎯 Map đơn giản theo category keywords
- 💾 Batch size lớn (10,000) → ít round-trip database

### 🔧 Cách nâng cao (Nếu cần mapping chính xác hơn)

**Nếu cần mapping chính xác hơn với fuzzy matching:**
```powershell
cd backend
python scripts\import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/ingredients/canonical_ingredients_migrated.json `
  --uri bolt://localhost:7687 `
  --user neo4j `
  --password "Admin123!" `
  --db neo4j `
  --use-driver `
  --batch-size 8000 `
  --threshold 0.92 `
  --log-every 1000
```

**Lưu ý:** Cách này chậm hơn nhưng mapping chính xác hơn (có fuzzy matching, Levenshtein distance)

## 👥 Bước 5: Import Users (Optional)

```powershell
cd backend
python scripts\import_users_from_survey.py `
  --csv "data/users/users-survey.csv"
```

## 🧮 Bước 6: Compute Features

Tính toán TF-IDF, user vectors, và similarity graph:

**Chạy tất cả passes (PASS1, PASS2, PASS2.5, PASS3):**
```powershell
cd backend
python scripts\compute_features_improve.py --pass all
```

**Hoặc chạy từng pass riêng:**

**PASS1: Tính IDF statistics**
```powershell
cd backend
python scripts\compute_features_improve.py --pass 1
```

**PASS2: Tính TF-IDF và cập nhật Neo4j**
```powershell
cd backend
python scripts\compute_features_improve.py --pass 2
```

**PASS2: Chỉ cập nhật recipes chưa có text_terms/text_weights**
```powershell
cd backend
python scripts\compute_features_improve.py --pass 2 --only-missing
```

**PASS2.5: Tính content-based recipe similarity (có thể giới hạn số recipes để nhanh hơn)**
```powershell
cd backend
python scripts\compute_features_improve.py --pass 2.5 --content-threshold 0.3 --limit-recipes 10000
```

**PASS3: Xây hybrid similarity graph**
```powershell
cd backend
python scripts\compute_features_improve.py --pass 3 --min-popular-score 5
```

**Cleanup trước khi chạy (xóa dữ liệu cũ):**
```powershell
cd backend
python scripts\compute_features_improve.py --pass all --cleanup
```

**Lưu ý:**
- Script sử dụng cấu hình từ `config.py` (URI, user, password, database)
- Batch size mặc định: 5000 (từ `DEFAULT_BATCH` trong config)
- Top terms per recipe mặc định: 512 (từ `TOP_TERMS_PER_RECIPE` trong config)

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
  --db neo4j `
  --password "Admin123!" `
  --ingredient-names "onion,tomato,chicken" `
  --limit 10
```

**Với user ID:**
```powershell
cd backend
python scripts\recommend_graph.py `
  --db neo4j `
  --password "Admin123!" `
  --user-id survey_1 `
  --ingredient-names "onion,tomato,chicken" `
  --max-cook-time 45 `
  --preferred-cuisines "Vietnamese,Korean" `
  --limit 10
```

## 📝 Lưu ý Quan trọng

1. **Thứ tự import:** Ingredients → Recipes → Users → Compute Features
2. **Mapping đơn giản:** Dùng `import_recipes_simple.py` để import nhanh (mapping theo category)
3. **Mapping chính xác:** Dùng `import_recipe_AI.py` nếu cần mapping chính xác hơn (chậm hơn)
4. **Database:** Sử dụng database **`neo4j`** (mặc định) - không cần tạo database mới
5. **Neo4j credentials:** Thay `Admin123!` bằng password Neo4j của bạn
6. **Port:** Thay port `7688` (Community Edition) hoặc `7687` (Desktop 2) tùy theo Neo4j bạn đang dùng

## 🐛 Troubleshooting

- **Lỗi kết nối Neo4j:** Kiểm tra Neo4j đang chạy (http://localhost:7474)
- **Lỗi "Database not found":** Đảm bảo đã tạo database `test`
- **Lỗi "Module not found":** Chạy `pip install -r requirements.txt`
- **Lỗi encoding:** Đảm bảo file CSV/JSON dùng UTF-8
