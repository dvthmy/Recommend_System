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
.venv\Scripts\pip install -r requirements_api.txt
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
cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food --file db/neo4j/ingredient.cypher
```

### 4) Import dữ liệu công thức (200 dòng mẫu)
- Import qua Neo4j Python driver (không cần cypher-shell cho mỗi batch):
```bash
.venv\Scripts\python scripts\import_recipes_neo4j.py \
  --neo4j-uri bolt://localhost:7687 \
  --neo4j-user neo4j \
  --neo4j-pass "Admin123!" \
  --db food \
  --use-driver \
  --limit 200 \
  --verbose
```
  .venv\Scripts\python scripts\import_recipes_neo4j.py 
    --csv data\recipes\recipetineats_final.csv 
    --labels data\ingredients\data.txt 
    --neo4j-uri bolt://localhost:7687 --neo4j-user neo4j --neo4j-pass "Admin123!" 
    --db food --use-driver --limit 200 --verbose
    
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
echo "MERGE (u:User {user_id:'u_1'}) SET u.locale='vi-VN' RETURN u.user_id" | \
  cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food

echo "MATCH (u:User {user_id:'u_1'}), (r:Recipe {recipe_id:'rec_demo'}) \
MERGE (u)-[:INTERACTED_WITH {event_type:'cook', timestamp: datetime()}]->(r)" | \
  cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d food

.venv\Scripts\python scripts\compute_features.py \
  --uri bolt://localhost:7687 --user neo4j --password "Admin123!" --db food
```

### 7) Chạy recommend
- Theo nguyên liệu (s_ing):
```bash
.venv\Scripts\python scripts\recommend.py \
  --db food --password "Admin123!" \
  --ing ing_onion,ing_tomato \
  --max-cook-time 45 --limit 5 --json
```
- Cá nhân hóa theo user (s_text):
```bash
.venv\Scripts\python scripts\recommend.py \
  --db food --password "Admin123!" \
  --user-id u_1 \
  --max-cook-time 45 --limit 5 --json
```
- Kết hợp user + nguyên liệu (s_ing + s_text), trọng số mặc định w_ing=1.0, w_text=1.0, w_pop=0.2:
```bash
.venv\Scripts\python scripts\recommend.py 
  --db food --password "Admin123!"
  --user-id u_1 --ing ing_onion,ing_tomato 
  --max-cook-time 45 --limit 10 --w-ing 1.0 --w-text 1.0 --w-pop 1.0 --w-cf 1.0 --norm rank  --pop-half-life 60 --json
```

### 7.1) Import dữ liệu khảo sát user và dùng profile mặc định
- Import CSV khảo sát để tạo `User`, liên kết `ALLERGIC_TO` theo category (seafood/nut/dairy), và thêm `FAVORS_CUISINE` + cập nhật `skill_level`, `max_cook_time`, `dietary_preferences`.
```bash
.venv\Scripts\python scripts\import_users_from_survey.py 
  --csv data\users\users-survey.csv 
  --uri bolt://localhost:7687 --user neo4j --password "Admin123!" --db food
```
- Sau khi import, `scripts\recommend.py` sẽ tự động:
  - Nếu không truyền `--cuisine`, dùng cuisine yêu thích đầu tiên từ `(:User)-[:FAVORS_CUISINE]->(:Cuisine)`.
  - Nếu không truyền `--max-cook-time`, dùng `u.max_cook_time` từ profile.
  - Vẫn loại trừ công thức có nguyên liệu user dị ứng/không thích (nếu có quan hệ `ALLERGIC_TO`/`DISLIKES`).


### 8) Khắc phục sự cố
- Auth failed: kiểm tra user/password/DB.
- Kết quả rỗng/scores=0: chạy lại import (mục 4) và compute (mục 5); với user‑only cần có tương tác (mục 6).
- Cảnh báo APOC: code đã bỏ phụ thuộc APOC, có thể bỏ qua cảnh báo liên quan.


PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak  "MATCH (r:Recipe)-[rel:HAS_INGREDIENT]->(i:Ingredient) RETURN r.recipe_id, i.ingredient_id, rel.idf_weight LIMIT 5;"
+------------------------------------------------+
| r.recipe_id | i.ingredient_id | rel.idf_weight |
+------------------------------------------------+
+------------------------------------------------+

0 rows
ready to start consuming query after 1 ms, results consumed after another 1 ms      
PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak "MATCH (r:Recipe) RETURN count(r) AS recipe_count;"
+--------------+
| recipe_count |
+--------------+
| 200          |
+--------------+

1 row
ready to start consuming query after 32 ms, results consumed after another 1 ms     
PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak "MATCH (i:Ingredient) RETURN count(i) AS ingredient_count;"
+------------------+
| ingredient_count |
+------------------+
| 56               |
+------------------+

1 row
ready to start consuming query after 34 ms, results consumed after another 1 ms     
PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak  "MATCH ()-[r]->() RETURN type(r) AS rel_type, count(r) AS count;"
+-------------------------+
| rel_type        | count |
+-------------------------+
| "TAGGED_AS"     | 1162  |
| "OF_CUISINE"    | 197   |
| "HAS_IN_PANTRY" | 1905  |
+-------------------------+

3 rows
ready to start consuming query after 46 ms, results consumed after another 167 ms   
PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak "MATCH (r:Recipe) RETURN r.recipe_id, r.title, keys(r) LIMIT 3;"
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| r.recipe_id | r.title                                                            | keys(r)                                                                            
                                                                                    
                                                                                    
                                          |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+
| "rec_1"     | "Southwest Breakfast Casserole"                                    | ["recipe_id", "title", "cook_time_min", "cuisine", "instructions", "tags", "servings", "image_urls", "popularity_views", "popularity_saves", "popularity_cooks", "popularity_likes", "allergens", "nutrition_calories", "equipment_needed", "alternative_ingredients", "text_terms", "text_weights"] |
| "rec_2"     | "Real, &quot;down Home&quot; Southern Country Biscuits and Gravy:" | ["recipe_id", "title", "cook_time_min", "cuisine", "instructions", "tags", "servings", "image_urls", "popularity_views", "popularity_saves", "popularity_cooks", "popularity_likes", "allergens", "nutrition_calories", "equipment_needed", "alternative_ingredients", "text_terms", "text_weights"] |
| "rec_3"     | "Dutch Baby"                                                       | ["recipe_id", "title", "cook_time_min", "cuisine", "instructions", "tags", "servings", "image_urls", "popularity_views", "popularity_saves", "popularity_cooks", "popularity_likes", "allergens", "nutrition_calories", "equipment_needed", "alternative_ingredients", "text_terms", "text_weights"] |
+-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------+

3 rows
ready to start consuming query after 39 ms, results consumed after another 2 ms     
PS D:\_Freelance-Project-Pool\Recommend foods> cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p "Admin123!" -d foodbak "MATCH (i:Ingredient) WHERE i.ingredient_id IN ['ing_onion', 'ing_tomato'] RETURN i.ingredient_id, i.canonical_name;"
+------------------------------------+
| i.ingredient_id | i.canonical_name |
+------------------------------------+
| "ing_onion"     | "onion"          |
| "ing_tomato"    | "tomato"         |
+------------------------------------+

2 rows
ready to start consuming query after 52 ms, results consumed after another 3 ms     
PS D:\_Freelance-Project-Pool\Recommend foods> .\.venv\Scripts\python .\scripts\import_recipes_neo4j.py `  --neo4j-uri bolt://localhost:7687 `  --neo4j-user neo4j `  --neo4j-pass "Admin123!" `  --db foodbak `  --use-driver `  --limit 5 `  --verbose
[labels] loaded=23 exact_keys_sample=['id ing orange canonical orange category fruit', 'id ing oysters canonical oysters category seafood allergen true', 'id ing pawpaw canonical pawpaw category fruit alt papaya', 'id ing peanuts canonical peanuts category nut allergen true', 'id ing peas canonical peas category legume', 'id ing pepper canonical pepper category spice alt peper', 'id ing pineapple canonical pineapple category fruit', 'id ing pork belly canonical pork belly category meat', 'id ing potato canonical potato category vegetable alt potatoes', 'id ing pumpkin canonical pumpkin category vegetable']
[csv] opening data\recipes\full_dataset.csv size=0.81MB
[csv] try encoding=utf-8
[csv] header_keys=['title', 'description', 'url', 'prep_time', 'cook_time', 'total_time', 'servings', 'ingredients', 'instructions', 'image_url', 'recipe_category', 'recipe_cuisine', 'keywords', 'calories']
[row] #1 title='Southwest Breakfast Casserole' servings_raw='8 serving(s)' cuisine='all'
      ingredients_raw='6   slices    white bread, crust removed | 1   lb    pork sausage | 4   cups    colby or 4   cups    monterey jack cheese | 6       eggs | 2...' 
      tokens=['bread', 'removed', 'sausage', 'cheese', 'egg', 'chili', 'salt', 'mustard', 'half', 'margarine']
      mapped_ids=[]
[row] #2 title='Real, &quot;down Home&quot; Southern Country Biscuits and Gr' servings_raw='8 biscuits, 4 serving(s)' cuisine='all'
      ingredients_raw='2   cups    self-rising flour | 1   large    egg | 1/4  cup    oil | 1   cup    buttermilk | 3   tablespoons    flour | 3   tablespoons    o...' 
      tokens=['flour', 'egg', 'oil', 'buttermilk', 'flour', 'oil', 'milk', 'water', 'salt', 'pepper']
      mapped_ids=[]
[row] #3 title='Dutch Baby' servings_raw='2-3 serving(s)' cuisine='all'
      ingredients_raw='3/4  cup    milk | 1/2  cup    unbleached all-purpose flour | 2   large    eggs | 1 1/2  tablespoons    sugar | 1/2  teaspoon    pure vanill...' 
      tokens=['milk', 'flour', 'egg', 'sugar', 'extract', 'butter', 'sugar', 'fruit', 'peach', 'nectarin']
      mapped_ids=[]
[row] #4 title='Tasty Oatmeal the Microwave Way!' servings_raw='1 serving(s)' cuisine='all'
      ingredients_raw='1   cup    water | 1/2  cup    rolled oats | 1   dash    salt | 2   tablespoons    brown sugar | cinnamon (I must use a teaspoon) | 2   tabl...' 
      tokens=['water', 'oat', 'salt', 'sugar', 'a', 'walnut', 'below']
      mapped_ids=[]
[row] #5 title='Quiche Lorraine Cups' servings_raw='12 Quiche Lorraines, 6 serving(s)' cuisine='all'
      ingredients_raw='12      cooked crepes (, see <a href="https://www.food.com/recipe/all-purpose-dinner-crepes-batter-19104">All Purpose Dinner Crepes Batter</...' 
      tokens=['crep', 'a', 'bacon', 'amp', 'crumbled', 'cheese', 'grated', 'flour', 'salt', 'egg']
      mapped_ids=[]
Received notification from DBMS server: {severity: WARNING} {code: Neo.ClientNotification.Statement.FeatureDeprecationWarning} {category: DEPRECATION} {title: This feature is deprecated and will be removed in future versions.} {description: CALL subquery without a variable scope clause is now deprecated. Use CALL (r, row) { ... }} {position: line: 27, column: 1, offset: 1099} for query: "UNWIND $rows AS row\nMERGE (ration.Statement.FeatureDeprecationWarning} {category: DEPRECATION} {title: This feature is deprecated and will be removed in future versions.} {description: CALL subquery without a variable scope clause is now deprecated. Use CALL (r, row) { ... }} {position: line: 27, column: 1, offset: 1099} for query: "UNWIND $rows AS row\nMERGE (rure is deprecated and will be removed in future versions.} {description: CALL subquery without a variable scope clause is now deprecated. Use CALL (r, row) { ... }} {position: line: 27, column: 1, offset: 1099} for query: "UNWIND $rows AS row\nMERGE (rsition: line: 27, column: 1, offset: 1099} for query: "UNWIND $rows AS row\nMERGE (r:Recipe {recipe_id: row.recipe_id})\nSET r.title = row.props.title,\n    r.instructi:Recipe {recipe_id: row.recipe_id})\nSET r.title = row.props.title,\n    r.instructions = row.props.instructions,\n    r.tags = row.props.tags,\n    r.cook_time_min = row.props.cook_time_min,\n    r.servings = row.props.servings,\n    r.cuisine = row.props.cuisine,\n    r.rating_avg = row.props.rating_avg,\n    r.rating_count = row.props.rating_count,\n    r.image_urls = row.props.image_urls,\n    r.popularity_views = coalesce(row.props.popularity_views,0),\n    r.popularity_saves = coalesce(row.props.popularity_saves,0),\n    r.popularity_cooks = coalesce(row.props.popularity_cooks,0),\n    r.popularity_likes = coalesce(row.props.popularity_likes,0),\n    r.allergens = row.props.allergens,\n    r.nutrition_calories = row.props.nutrition_calories,\n    r.cost_estimate = row.props.cost_estimate,\n    r.equipment_needed = row.props.equipment_needed,\n    r.video_url = row.props.video_url,\n    r.alternative_ingredients = row.props.alternative_ingredients\nWITH r, row\nUNWIND coalesce(row.tags, []) AS tagName\nMERGE (t:Tag {name: tagName})\nMERGE (r)-[:TAGGED_AS]->(t)\nWITH r, row\nCALL { WITH r, row\n  WITH r, row UNWIND coalesce(row.ingredients, []) AS ing\n  MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})\n  MERGE (r)-[rel:HAS_INGREDIENT]->(i)\n  SET rel.qty = ing.qty, rel.unit = ing.unit, rel.optional = coalesce(ing.optional_flag,false), rel.prep = ing.prep\n  RETURN count(*) AS _\n}\nWITH r, row\nFOREACH (c IN CASE WHEN row.props.cuisine IS NOT NULL AND row.props.cuisine <> '' THEN [1] ELSE [] END | \n  MERGE (cui:Cuisine {name: row.props.cuisine}) MERGE (r)-[:OF_CUISINE]->(cui)\n)"

API Quản lý User Profile
Thiếu:
API để lấy thông tin user profile
API để cập nhật user preferences onboarding
API để quản lý allergies và dislikes
API để quản lý favorite cuisines
Cần thêm:
3. API Quản lý Recipes
Thiếu:
API để lấy chi tiết recipe
API để tìm kiếm recipes
API để lấy recipes theo cuisine
API để lấy recipes theo tags
Cần thêm:
4. API Quản lý Ingredients
Thiếu:
API để lấy chi tiết ingredient
API để tìm kiếm ingredients
API để lấy ingredients theo category
API để lấy ingredient synonyms
Cần thêm:
5. API Quản lý Interactions
Thiếu:
API để ghi nhận user interactions (cook, like, save)
API để lấy lịch sử interactions của user
API để cập nhật user vector từ interactions
Cần thêm:
6. API Quản lý Data (Admin)
Thiếu:
API để import recipes
API để import users
API để compute features
API để seed data
Cần thêm:
7. API Analytics & Monitoring
Thiếu:
API để lấy thống kê hệ thống
API để monitor performance
API để lấy recommendation metrics
Cần thêm:
8. API Profile Presets
Thiếu:
API để áp dụng profile presets (new, history, explore)
API để tạo custom profiles
Cần thêm:
9. API Batch Operations
Thiếu:
API để recommend cho nhiều users cùng lúc
API để bulk update user preferences
Cần thêm:
10. API Export/Import
Thiếu:
API để export recommendations
API để export user data
API để backup/restore


# 1. Activate environment
cd recommend-service
.venv\Scripts\activate

# 2. Start API server
python -m uvicorn api:app --host 0.0.0.0 --port 8001 --reload