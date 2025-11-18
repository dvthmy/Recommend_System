# Hướng dẫn chạy recommend_graph.py

## Cách chạy script gợi ý công thức nấu ăn

### 1. Chạy với ingredient IDs (không có user)

```bash
cd backend
python scripts/recommend_graph.py \
  --ingredients "ing_001,ing_002,ing_003" \
  --limit 10
```

### 2. Chạy với tên nguyên liệu (tự động map sang IDs)

```bash
python scripts/recommend_graph.py \
  --ingredient-names "thịt heo,gạo,rau cải" \
  --limit 10
```

### 3. Chạy với user ID (có profile, allergies, preferences)

```bash
python scripts/recommend_graph.py \
  --user-id "user_001" \
  --ingredient-names "thịt gà,ớt,rau thơm" \
  --limit 20
```

### 4. Chạy với filter thời gian nấu

```bash
python scripts/recommend_graph.py \
  --ingredient-names "trứng,cà chua" \
  --max-cook-time 30 \
  --limit 15
```

### 5. Chạy với filter loại món ăn

```bash
python scripts/recommend_graph.py \
  --ingredient-names "thịt bò,khoai tây" \
  --recipe-category "Dinner" \
  --limit 10
```

### 6. Chạy với ưu tiên ẩm thực

```bash
python scripts/recommend_graph.py \
  --user-id "user_001" \
  --ingredient-names "thịt heo,rau cải" \
  --preferred-cuisines "Vietnamese,Korean" \
  --limit 15
```

### 7. Chạy đầy đủ tham số

```bash
python scripts/recommend_graph.py \
  --uri "bolt://localhost:7687" \
  --user "neo4j" \
  --password "Admin123!" \
  --db "neo4j" \
  --user-id "user_001" \
  --ingredient-names "thịt gà,ớt,rau thơm" \
  --limit 20 \
  --min-match 0.3 \
  --max-cook-time 60 \
  --recipe-category "Dinner" \
  --preferred-cuisines "Vietnamese,Chinese" \
  --json
```

### 8. Xuất kết quả dạng JSON

```bash
python scripts/recommend_graph.py \
  --ingredient-names "thịt heo,gạo" \
  --json > results.json
```

### 9. Chạy với database khác

```bash
python scripts/recommend_graph.py \
  --db "production" \
  --ingredient-names "cá,tôm" \
  --limit 10
```

## Các tham số chi tiết

| Tham số | Mô tả | Mặc định | Ví dụ |
|---------|-------|----------|-------|
| `--uri` | Neo4j connection URI | `bolt://localhost:7687` | `bolt://localhost:7687` |
| `--user` | Neo4j username | `neo4j` | `neo4j` |
| `--password` | Neo4j password | `Admin123!` | `your_password` |
| `--db` | Database name | `test` | `neo4j`, `production` |
| `--user-id` | User ID (optional) | `None` | `user_001` |
| `--ingredients` | Ingredient IDs (comma-separated) | `None` | `ing_001,ing_002` |
| `--ingredient-names` | Ingredient names (comma-separated) | `None` | `thịt heo,gạo` |
| `--limit` | Số lượng kết quả | `30` | `10`, `50` |
| `--min-match` | Tỷ lệ match tối thiểu | `0.4` | `0.3`, `0.5` |
| `--max-cook-time` | Thời gian nấu tối đa (phút) | `None` | `30`, `60` |
| `--recipe-category` | Loại món ăn | `None` | `Dinner`, `Breakfast` |
| `--preferred-cuisines` | Ưu tiên ẩm thực (comma-separated) | `None` | `Vietnamese,Korean` |
| `--json` | Xuất JSON format | `False` | (flag) |

## Lưu ý

1. **Ingredient IDs vs Names**: 
   - Dùng `--ingredients` nếu bạn đã biết ingredient IDs
   - Dùng `--ingredient-names` nếu bạn chỉ biết tên (script sẽ tự map)

2. **User ID**: 
   - Nếu có `--user-id`, script sẽ dùng profile, allergies, và preferences của user
   - Nếu không có, chỉ dựa vào ingredients

3. **Recipe Category**: 
   - Có thể dùng: `"no preference"`, `"none"`, `"all"` để bỏ filter
   - Hoặc: `"Dinner"`, `"Breakfast"`, `"Lunch"`, etc.

4. **Preferred Cuisines**: 
   - Script sẽ ưu tiên recipes có cuisine khớp
   - Có thể chỉ định nhiều cuisines: `"Vietnamese,Korean,Chinese"`

5. **Output Format**:
   - Mặc định: Text format với emoji và formatting
   - Với `--json`: JSON format để xử lý programmatically

## Ví dụ kết quả

### Text format (mặc định):
```
#1. Phở Bò (recipe_001)
   🍳 Match: 85.5%
   • ✅ Shares most of your given ingredients
   • 🍜 Matches your favorite cuisine
   • ⭐ Top-rated recipe
   ✅ Matched: ing_001, ing_002, ing_003
   📝 Missing: ing_004, ing_005
   ⏱️  Cook time: 45 min
   🍽️  Category: Dinner
```

### JSON format (với --json):
```json
{
  "results": [
    {
      "recipe_id": "recipe_001",
      "title": "Phở Bò",
      "match_percent": 85.5,
      "matched_ing": ["ing_001", "ing_002"],
      "missing_ing": ["ing_004", "ing_005"],
      "reasoning": [
        "✅ Shares most of your given ingredients",
        "🍜 Matches your favorite cuisine"
      ],
      "cook_time_min": 45,
      "recipe_category": "Dinner"
    }
  ]
}
```

