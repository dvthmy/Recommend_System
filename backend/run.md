## Cài đặt và chạy dự án (Windows + Neo4j local)

### 1) Yêu cầu
- Python 3.10+
- Neo4j local (Desktop/Server)
  - URI: bolt://localhost:7687
  - Database: food
  - User: neo4j
  - Password: Admin123!
- PowerShell

### 2) Thiết lập Python environment
```bash
python -m venv .venv
.venv\Scripts\python -m pip install --upgrade pip
.venv\Scripts\pip install -r requirements.txt
```

### 3) Khởi động Neo4j và seed nguyên liệu
- Bảo đảm database `food` đang RUNNING.
- (Nếu cần) Thêm Neo4j bin vào PATH của session PowerShell:
```powershell
$neoPath = "C:\Users\PC\.Neo4jDesktop2\Data\dbmss\{YOUR_DBMS_ID}\bin"
$env:Path = "$neoPath;" + $env:Path
$ neo4j console
```
- Tạo database `food` bằng lệnh (nếu chưa tồn tại):
```bash
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system -e "CREATE DATABASE food IF NOT EXISTS;"
# Kiểm tra trạng thái DB
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d system -e "SHOW DATABASES YIELD name, currentStatus WHERE name='food' RETURN name, currentStatus;"
```
- Seed Ingredient:
```bash
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food --file "D:\Recommend foods\Recommend foods\db\neo4j\ingredient.cypher"
```

### 4) Import dữ liệu công thức (200 dòng mẫu)
- Import qua Neo4j Python driver (không cần cypher-shell cho mỗi batch):
```bash
.venv\Scripts\python scripts\import_recipes_neo4j.py
  --neo4j-uri bolt://localhost:7687
  --neo4j-user neo4j
  --neo4j-pass "Admin123!"
  --db food
  --use-driver
  --limit 200
  --verbose
```

### 5) Tính đặc trưng và vector
- Thiết lập:
  - Trọng số IDF trên cạnh `HAS_INGREDIENT` (cho s_ing > 0)
  - TF‑IDF văn bản recipe: `r.text_terms[]`, `r.text_weights[]`
  - User vector: `u.user_terms[]`, `u.user_weights[]`
```bash
.venv\Scripts\python scripts\compute_features.py 
  --uri bolt://localhost:7687 --user neo4j --password "Admin123!" --db food
```

### 6) (Tùy chọn) Seed user và tương tác để có user vector
```bash
echo MERGE (u:User {user_id:'u_1'}) SET u.locale='vi-VN' RETURN u.user_id | cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food

echo MATCH (u:User {user_id:'u_1'}), (r:Recipe {recipe_id:'rec_demo'}) MERGE (u)-[:INTERACTED_WITH {event_type:'cook', timestamp: datetime()}]->(r) | cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food

.venv\Scripts\python scripts\compute_features.py --uri bolt://localhost:7687 --user neo4j --password "Admin123!" --db food
```

### 7) Chạy recommend
- Theo nguyên liệu (s_ing):
```bash
.venv\Scripts\python scripts\recommend.py 
  --db food --password "Admin123!" 
  --ing ing_onion
  --max-cook-time 45 --limit 5 --json
```
- Cá nhân hóa theo user (s_text):
```bash
.venv\Scripts\python scripts\recommend.py 
  --db food --password "Admin123!" 
  --user-id u_1 
  --max-cook-time 45 --limit 5 --json
```
- Kết hợp user + nguyên liệu (s_ing + s_text), trọng số mặc định w_ing=1.0, w_text=1.0, w_pop=0.2:
```bash
.venv\Scripts\python scripts\recommend.py 
  --db food --password "Admin123!" 
  --user-id u_1 --ing ing_onion,ing_tomato 
  --max-cook-time 45 --limit 5 
  --w-ing 1.0 --w-text 1.0 --w-pop 0.2 
  --json
```

### 8) Khắc phục sự cố
- Auth failed: kiểm tra user/password/DB.
- Kết quả rỗng/scores=0: chạy lại import (mục 4) và compute (mục 5); với user‑only cần có tương tác (mục 6).
- Cảnh báo APOC: code đã bỏ phụ thuộc APOC, có thể bỏ qua cảnh báo liên quan.
