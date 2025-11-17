# Thêm Variant Ingredients vào Canonical Ingredients

## Mục đích

Script này thêm các variant ingredients (như "provolone cheese", "havarti cheese") vào `canonical_ingredients.json` dưới dạng ingredients độc lập, không chỉ là variations.

## Tại sao cần?

- **Strategy 0.25** trong `import_recipe_AI.py` cần variants là ingredients độc lập để match chính xác
- Khi có "provolone cheese" và "Havarti cheese" trong recipe, cần match riêng biệt thay vì gộp về "cheese"
- Variants phải có `ingredient_id` riêng để Strategy 0.25 hoạt động

## Cách sử dụng

### 1. Chạy script để thêm variants

```bash
cd backend/data/process
python add_variant_ingredients.py \
  --input canonical_ingredients.json \
  --output canonical_ingredients.json
```

### 2. Kiểm tra kết quả

Script sẽ:
- ✅ Đọc `canonical_ingredients.json` hiện tại
- ✅ Check xem variant đã tồn tại chưa (tránh duplicate)
- ✅ Tạo ingredients mới cho các variants chưa có
- ✅ Thêm vào file JSON (sort theo canonical_name)

### 3. Import vào Neo4j

Sau khi thêm variants, import lại vào Neo4j:

```bash
cd backend/scripts
python import_canonical_ingredients.py \
  --json ../data/process/canonical_ingredients.json \
  --uri bolt://localhost:7687 \
  --user neo4j \
  --password Admin123! \
  --db test
```

## Variants được thêm

Script sẽ thêm variants cho các base ingredients sau:

### Cheese variants:
- cheddar cheese, mozzarella cheese, parmesan cheese, swiss cheese
- pepper jack cheese, cream cheese, feta cheese
- **provolone cheese**, **havarti cheese**, gouda cheese, brie cheese
- camembert cheese, ricotta cheese, mascarpone cheese, gruyere cheese
- blue cheese, gorgonzola cheese, manchego cheese, pecorino cheese
- romano cheese, asiago cheese, fontina cheese, muenster cheese
- colby cheese, jack cheese, monterey jack cheese

### Onion variants:
- yellow onion, green onion, red onion, white onion
- sweet onion, spanish onion, vidalia onion
- scallion, spring onion

### Pepper variants:
- black pepper, white pepper, cayenne pepper, bell pepper
- red pepper, green pepper, jalapeno pepper, serrano pepper

### Potato variants:
- sweet potato, russet potato, red potato, yukon potato
- fingerling potato, new potato

### Rice variants:
- brown rice, white rice, jasmine rice, basmati rice
- arborio rice, wild rice, sticky rice

### Flour variants:
- all purpose flour, bread flour, cake flour, whole wheat flour
- almond flour, coconut flour, rice flour

### Milk variants:
- whole milk, skim milk, 2% milk, almond milk, soy milk
- coconut milk, oat milk

### Sugar variants:
- brown sugar, white sugar, powdered sugar, granulated sugar
- coconut sugar, maple sugar

### Vinegar variants:
- apple cider vinegar, white vinegar, balsamic vinegar, red wine vinegar
- rice vinegar, distilled vinegar

### Salt variants:
- kosher salt, sea salt, table salt, himalayan salt, coarse salt

## Format output

Mỗi variant được tạo như sau:

```json
{
  "ingredient_id": "ing_provolone_cheese",
  "canonical_name": "provolone cheese",
  "base_group": "cheese",
  "category": "dairy",
  "alt_names": [
    "provolone cheeses",
    "provolonecheese",
    "provolonecheeses"
  ],
  "variations": {}
}
```

## Notes

- Script tự động check duplicate, không thêm nếu đã tồn tại
- Ingredients được sort theo `canonical_name` để dễ đọc
- `base_group` được set = base ingredient name (vd: "cheese")
- `category` được guess tự động dựa trên canonical_name
- `alt_names` được generate tự động (plural forms, etc.)

