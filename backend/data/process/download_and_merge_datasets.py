"""
Script để tải và gộp datasets từ Kaggle và Hugging Face
- Kaggle: kaggle/recipe-ingredients-dataset
- Hugging Face: Scuccorese/food-ingredients-dataset
Gộp tất cả category, sub, ingredient unique và lưu thành CSV
"""

import os
import json
import pandas as pd
import kagglehub
from datasets import load_dataset
from pathlib import Path

# Đường dẫn thư mục
BASE_PATH = Path(__file__).parent.parent.parent.parent
PROCESS_DIR = BASE_PATH / "backend" / "data" / "process"
PROCESS_DIR.mkdir(parents=True, exist_ok=True)

print(f"📁 Thư mục làm việc: {PROCESS_DIR}")


def download_kaggle_dataset():
    """Tải dataset từ Kaggle và trích xuất ingredients vào in.txt"""
    print("\n" + "="*60)
    print("📥 Đang tải dataset từ Kaggle...")
    print("="*60)
    
    try:
        # Download latest version
        path = kagglehub.dataset_download("kaggle/recipe-ingredients-dataset")
        print(f"✅ Path to dataset files: {path}")
        
        # Tìm và xử lý file JSON (test.json, train.json, ...)
        json_files = list(Path(path).rglob("*.json"))
        print(f"📄 Tìm thấy {len(json_files)} file JSON")
        
        all_ingredients = set()
        
        for json_file in json_files:
            print(f"  📖 Đang đọc JSON: {json_file.name}")
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Nếu là list, xử lý từng item
                    if isinstance(data, list):
                        print(f"     ✅ Đã tìm thấy {len(data)} items từ {json_file.name}")
                        # Trích xuất ingredients từ mỗi item
                        for item in data:
                            ingredients = extract_ingredients_from_item(item)
                            all_ingredients.update(ingredients)
                    # Nếu là dict, xử lý trực tiếp
                    elif isinstance(data, dict):
                        print(f"     ✅ Đã tìm thấy 1 item từ {json_file.name}")
                        ingredients = extract_ingredients_from_item(data)
                        all_ingredients.update(ingredients)
            except Exception as e:
                print(f"     ❌ Lỗi khi đọc {json_file.name}: {e}")
        
        # Lưu ingredients vào file in.txt
        if all_ingredients:
            output_file = PROCESS_DIR / "in.txt"
            with open(output_file, 'w', encoding='utf-8') as f:
                for ingredient in sorted(all_ingredients):
                    f.write(f"{ingredient}\n")
            print(f"\n✅ Đã lưu {len(all_ingredients)} ingredients unique vào:")
            print(f"   👉 {output_file}")
        else:
            print("\n⚠️ Không tìm thấy ingredients nào trong JSON files")
        
        return None  # Không trả về DataFrame cho Kaggle
            
    except Exception as e:
        print(f"❌ Lỗi khi tải Kaggle dataset: {e}")
        return None


def extract_ingredients_from_item(item):
    """Trích xuất ingredients từ một item JSON"""
    ingredients = set()
    
    if not isinstance(item, dict):
        return ingredients
    
    # Tìm các key có thể chứa ingredients
    possible_keys = ['ingredients', 'ingredient', 'ing', 'ingredients_list', 
                     'ingredient_list', 'items', 'food_items']
    
    for key in possible_keys:
        if key in item:
            value = item[key]
            if isinstance(value, list):
                for ing in value:
                    if isinstance(ing, str) and ing.strip():
                        ingredients.add(ing.strip())
                    elif isinstance(ing, dict):
                        # Nếu ingredient là dict, tìm name hoặc text
                        if 'name' in ing:
                            ingredients.add(str(ing['name']).strip())
                        elif 'text' in ing:
                            ingredients.add(str(ing['text']).strip())
            elif isinstance(value, str):
                # Nếu là string, có thể là comma-separated
                for ing in value.split(','):
                    if ing.strip():
                        ingredients.add(ing.strip())
    
    # Nếu không tìm thấy, thử tìm trong tất cả các giá trị string
    if not ingredients:
        for key, value in item.items():
            if isinstance(value, list):
                for v in value:
                    if isinstance(v, str) and any(word in key.lower() for word in ['ingredient', 'food', 'item']):
                        ingredients.add(v.strip())
    
    return ingredients


def download_huggingface_dataset():
    """Tải dataset từ Hugging Face và tạo CSV với category, subcategory, ingredients"""
    print("\n" + "="*60)
    print("📥 Đang tải dataset từ Hugging Face...")
    print("="*60)
    
    try:
        ds = load_dataset("Scuccorese/food-ingredients-dataset")
        print(f"✅ Dataset keys: {list(ds.keys())}")
        
        # Chuyển đổi sang DataFrame
        dfs_hf = []
        for split_name, split_data in ds.items():
            print(f"📖 Đang xử lý split: {split_name} ({len(split_data)} dòng)")
            df = split_data.to_pandas()
            dfs_hf.append(df)
        
        if not dfs_hf:
            print("⚠️ Không có dữ liệu từ Hugging Face")
            return None
        
        df_hf = pd.concat(dfs_hf, ignore_index=True)
        print(f"\n✅ Hugging Face dataset: {len(df_hf)} dòng, {len(df_hf.columns)} cột")
        print(f"📋 Các cột có trong dataset: {list(df_hf.columns)}")
        
        # Tạo file CSV với format category, subcategory, ingredients
        create_huggingface_csv(df_hf)
        
        return None  # Không trả về DataFrame cho Hugging Face
            
    except Exception as e:
        print(f"❌ Lỗi khi tải Hugging Face dataset: {e}")
        return None


def create_huggingface_csv(df):
    """Tạo file CSV từ Hugging Face dataset với format category, subcategory, ingredients"""
    print("\n" + "="*60)
    print("🔄 Đang tạo file CSV cho Hugging Face...")
    print("="*60)
    
    # Tìm các cột có thể chứa category, subcategory, ingredients
    category_cols = [col for col in df.columns if 'category' in col.lower() and 'sub' not in col.lower()]
    subcategory_cols = [col for col in df.columns if 'sub' in col.lower() and 'category' in col.lower()]
    # Nếu không tìm thấy subcategory, thử tìm "sub" đơn giản
    if not subcategory_cols:
        subcategory_cols = [col for col in df.columns if 'sub' in col.lower() and col.lower() != 'sub']
    ingredient_cols = [col for col in df.columns if 'ingredient' in col.lower()]
    
    print(f"🔍 Tìm thấy:")
    print(f"  - Category columns: {category_cols}")
    print(f"  - Subcategory columns: {subcategory_cols}")
    print(f"  - Ingredient columns: {ingredient_cols}")
    
    # Nhóm ingredients theo (category, subcategory)
    # Key: (category, subcategory), Value: set of ingredients
    grouped_dict = {}
    
    for idx, row in df.iterrows():
        # Lấy category
        category = None
        for col in category_cols:
            if pd.notna(row[col]) and str(row[col]).strip():
                category = str(row[col]).strip()
                break
        
        # Lấy subcategory
        subcategory = None
        for col in subcategory_cols:
            if pd.notna(row[col]) and str(row[col]).strip():
                subcategory = str(row[col]).strip()
                break
        
        # Lấy ingredients
        ingredients = []
        for col in ingredient_cols:
            if pd.notna(row[col]):
                value = row[col]
                if isinstance(value, list):
                    ingredients.extend([str(item).strip() for item in value if str(item).strip()])
                elif isinstance(value, str):
                    # Nếu là string, có thể là comma-separated hoặc JSON string
                    if ',' in value:
                        ingredients.extend([item.strip() for item in value.split(',') if item.strip()])
                    else:
                        if value.strip():
                            ingredients.append(value.strip())
        
        # Nhóm ingredients theo (category, subcategory)
        for ing in ingredients:
            if ing.strip():
                # Tạo key từ category và subcategory
                cat = category if category else ''
                subcat = subcategory if subcategory else ''
                key = (cat, subcat)
                
                # Khởi tạo set nếu chưa có
                if key not in grouped_dict:
                    grouped_dict[key] = set()
                
                # Thêm ingredient vào set (tự động unique)
                grouped_dict[key].add(ing.strip())
    
    # Tạo danh sách records từ dictionary đã nhóm
    records = []
    for (category, subcategory), ingredients_set in grouped_dict.items():
        # Sắp xếp ingredients và join bằng dấu phẩy
        ingredients_list = sorted(list(ingredients_set))
        records.append({
            'category': category,
            'subcategory': subcategory,
            'ingredients': ', '.join(ingredients_list)
        })
    
    # Tạo DataFrame và lưu
    if records:
        df_output = pd.DataFrame(records)
        # Sắp xếp theo category, sau đó subcategory
        df_output = df_output.sort_values(['category', 'subcategory'])
        output_file = PROCESS_DIR / "huggingface_data.csv"
        df_output.to_csv(output_file, index=False, encoding="utf-8-sig")
        print(f"\n✅ Đã tạo file CSV với {len(df_output)} nhóm (category, subcategory):")
        print(f"   👉 {output_file}")
        print(f"\n📊 Thống kê:")
        print(f"   - Tổng số nhóm: {len(df_output)}")
        total_ingredients = sum(len(record['ingredients'].split(', ')) for record in records)
        print(f"   - Tổng số ingredients unique: {total_ingredients}")
        print(f"   - Số nhóm có category: {df_output['category'].astype(bool).sum()}")
        print(f"   - Số nhóm có subcategory: {df_output['subcategory'].astype(bool).sum()}")
    else:
        print("⚠️ Không tạo được records từ dataset")


def extract_unique_items(df, column_name):
    """Trích xuất các giá trị unique từ một cột"""
    if column_name not in df.columns:
        return set()
    
    unique_items = set()
    for value in df[column_name].dropna():
        if isinstance(value, str):
            # Nếu là list/array dạng string, tách ra
            if ',' in value or '[' in value:
                items = [item.strip().strip('"\'[]') for item in str(value).replace('[', '').replace(']', '').split(',')]
                unique_items.update([item for item in items if item])
            else:
                unique_items.add(value.strip())
        elif pd.notna(value):
            unique_items.add(str(value).strip())
    
    return unique_items


def merge_and_save(df_kaggle, df_hf):
    """Gộp dữ liệu từ cả 2 nguồn và lưu CSV (chỉ dùng cho unique items)"""
    print("\n" + "="*60)
    print("🔄 Đang xử lý unique items...")
    print("="*60)
    
    # Hugging Face đã được xử lý riêng trong download_huggingface_dataset
    # Kaggle đã được xử lý riêng trong download_kaggle_dataset
    # Hàm này chỉ để tương thích với code cũ, không cần làm gì
    print("✅ Kaggle và Hugging Face đã được xử lý riêng")
    return


def main():
    """Hàm chính"""
    print("="*60)
    print("🚀 BẮT ĐẦU TẢI VÀ GỘP DATASETS")
    print("="*60)
    
    # Tải datasets
    df_kaggle = download_kaggle_dataset()
    df_hf = download_huggingface_dataset()
    
    # Gộp và lưu
    merge_and_save(df_kaggle, df_hf)


if __name__ == "__main__":
    main()

