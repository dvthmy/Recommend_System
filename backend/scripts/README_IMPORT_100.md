# 🚀 Quick Guide: Import 100 Recipes với Log File

## Cách Sử Dụng Nhanh

### Windows PowerShell (Khuyến nghị)

```powershell
cd backend\scripts
.\import_100_recipes.ps1
```

### Windows CMD

```cmd
cd backend\scripts
import_100_recipes.bat
```

## Kết Quả

- ✅ Import 100 recipes đầu tiên từ CSV
- ✅ Log file được lưu tại: `backend/scripts/logs/import_100_recipes_YYYYMMDD_HHMMSS.log`
- ✅ Hiển thị 20 dòng log cuối cùng sau khi import xong

## Xem Log File

### PowerShell
```powershell
# Xem toàn bộ log
Get-Content logs\import_100_recipes_*.log

# Xem 20 dòng cuối
Get-Content logs\import_100_recipes_*.log -Tail 20

# Tìm lỗi
Select-String -Path logs\import_100_recipes_*.log -Pattern "error|unmatched|warn"
```

### CMD
```cmd
type logs\import_100_recipes_*.log
```

## Tham Số Đã Cấu Hình

- `--limit 100`: Chỉ import 100 recipes
- `--verbose`: Log chi tiết
- `--log-every 10`: Log mỗi 10 recipes
- `--batch-size 50`: Batch size nhỏ để dễ theo dõi
- `--use-driver`: Dùng Neo4j Python driver (nhanh hơn)

## Tùy Chỉnh

Nếu muốn thay đổi số lượng recipes hoặc tham số khác, chỉnh sửa file script hoặc chạy manual:

```powershell
python import_recipe_AI.py `
  --csv data/recipes/full_data_ing.csv `
  --labels data/process/canonical_ingredients.json `
  --use-driver `
  --limit 100 `
  --verbose `
  --log-every 10 `
  --batch-size 50 *> "logs\import_100_recipes_$(Get-Date -Format 'yyyyMMdd_HHmmss').log"
```

## Troubleshooting

1. **Lỗi "python not found"**: Đảm bảo Python đã được cài và trong PATH
2. **Lỗi Neo4j connection**: Kiểm tra Neo4j đang chạy và credentials trong `config.py`
3. **Log file không tạo**: Kiểm tra quyền ghi file trong thư mục `logs`

