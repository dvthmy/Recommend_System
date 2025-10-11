"""
📘 Compute mean rating (C) for each dataset, calculate weighted_rating (IMDb-style),
and merge all recipes into a single file.

Author: Jovana Golubovic
"""

import pandas as pd
import numpy as np
import json
from pathlib import Path


# ==========================
# CONFIG
# ==========================
DATA_DIR = Path(r"D:\Recommend_System\pre_data\final")  # Thư mục chứa các file nguồn
OUTPUT_C_PATH = Path(r"D:\Recommend_System\pre_data\dataset_C.json")
OUTPUT_MERGED_PATH = Path(r"D:\Recommend_System\pre_data\all_recipes_weighted.csv")

DATASETS = {
    "foodcom": DATA_DIR / "foodcom_final.csv",
    "hungryhuy": DATA_DIR / "hungryhuy_final.csv",
    "recipetineats": DATA_DIR / "recipetineats_final.csv",
    "redhousespice": DATA_DIR / "redhousespice_final.csv",
    "vickypham": DATA_DIR / "vickypham_final.csv",
    "koreanbapsang": DATA_DIR / "koreanbapsang_final.csv",
}

M = 10         # minimum votes threshold (IMDb-style)
DEFAULT_C = 4.2


# ==========================
# FUNCTIONS
# ==========================

def compute_mean_rating(csv_path: Path) -> float:
    """Tính mean rating (C) cho một dataset."""
    if not csv_path.exists():
        print(f"⚠️ File not found: {csv_path}")
        return None

    try:
        df = pd.read_csv(csv_path, encoding="utf-8")
    except Exception as e:
        print(f"❌ Error reading {csv_path.name}: {e}")
        return None

    rating_cols = [c for c in df.columns if "rating" in c.lower()]
    if not rating_cols:
        print(f"⚠️ No rating column found in {csv_path.name}")
        return None

    rating_col = next((c for c in rating_cols if "value" in c.lower()), rating_cols[0])
    df[rating_col] = pd.to_numeric(df[rating_col], errors="coerce")
    df = df[df[rating_col].notna()]

    if df.empty:
        print(f"⚠️ No valid rating values in {csv_path.name}")
        return None

    mean_rating = round(df[rating_col].mean(), 3)
    print(f"✅ {csv_path.name:<35} → Mean Rating (C) = {mean_rating:.3f} (n={len(df)})")
    return mean_rating


def compute_weighted_rating(R, v, C, m=M):
    """Tính IMDb-style weighted rating."""
    try:
        R = float(R)
        v = float(v)
        if np.isnan(R) or v < 0:
            return np.nan
        return (v / (v + m)) * R + (m / (v + m)) * C
    except Exception:
        return np.nan


# ==========================
# STEP 1️⃣: TÍNH MEAN RATING (C)
# ==========================

dataset_C = {}
for name, path in DATASETS.items():
    mean_val = compute_mean_rating(path)
    dataset_C[name] = mean_val

# Lưu lại file JSON
with open(OUTPUT_C_PATH, "w", encoding="utf-8") as f:
    json.dump(dataset_C, f, indent=2, ensure_ascii=False)

print("\n📂 Saved mean ratings to:", OUTPUT_C_PATH)
print(json.dumps(dataset_C, indent=2, ensure_ascii=False))


# ==========================
# STEP 2️⃣: TÍNH WEIGHTED RATING VÀ GỘP DỮ LIỆU
# ==========================

merged_dfs = []

for name, path in DATASETS.items():
    if not path.exists():
        print(f"⚠️ Skipping {path.name} (not found)")
        continue

    C = dataset_C.get(name) or DEFAULT_C

    try:
        df = pd.read_csv(path, encoding="utf-8")
    except Exception as e:
        print(f"❌ Cannot read {path.name}: {e}")
        continue

    if "rating_value" not in df.columns:
        print(f"⚠️ {path.name} has no 'rating_value' column, skipping.")
        continue

    if "rating_count" not in df.columns:
        df["rating_count"] = 0

    df["rating_value"] = pd.to_numeric(df["rating_value"], errors="coerce")
    df["rating_count"] = pd.to_numeric(df["rating_count"], errors="coerce").fillna(0)

    df["weighted_rating"] = df.apply(
        lambda r: compute_weighted_rating(r["rating_value"], r["rating_count"], C),
        axis=1,
    )

    merged_dfs.append(df)

# Gộp tất cả dataset
if merged_dfs:
    merged = pd.concat(merged_dfs, ignore_index=True)
    merged.to_csv(OUTPUT_MERGED_PATH, index=False, encoding="utf-8-sig")
    print(f"\n✅ Merged {len(merged_dfs)} datasets, total recipes: {len(merged)}")
    print(f"📁 Saved merged file to: {OUTPUT_MERGED_PATH}")
else:
    print("\n⚠️ No datasets were merged (no valid files found).")
