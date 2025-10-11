# merge_all_final.py
import os, re, html, glob
import pandas as pd
from pathlib import Path
from typing import List

# ===== CONFIG =====
FINAL_DIR = r"D:\Recommend_System\pre_data\final"  # đổi nếu khác
OUTPUT_NAME = "all_recipes_merged.csv"

# Thứ tự cột chuẩn
CANON_COLS = [
    "title","description","url",
    "prep_time","cook_time","total_time","servings",
    "ingredients","instructions","image_url",
    "recipe_category","recipe_cuisine","keywords",
    "calories","rating_value","rating_count","review_count"
]

# Cột số để ép kiểu (không dùng chuỗi rỗng)
NUM_INT_COLS = {"rating_count", "review_count"}
NUM_FLOAT_COLS = {"calories", "rating_value"}

# ===== Helpers =====
def unescape_multistep(x: str, max_steps: int = 3) -> str:
    prev = x
    for _ in range(max_steps):
        cur = html.unescape(prev)
        if cur == prev:
            break
        prev = cur
    return cur

def flatten_text_series(s: pd.Series, mode: str = "decode") -> pd.Series:
    """
    mode:
      - 'decode': &amp; -> & (giữ &)
      - 'and':    &amp;/& -> ' and '
    """
    s = s.fillna("").astype(str).map(unescape_multistep)
    s = s.str.replace(r"[\r\n\t]+", " ", regex=True)
    if mode == "and":
        s = s.str.replace(r"\s*&\s*", " and ", regex=True)
    s = s.str.replace(r"\s+", " ", regex=True).str.strip()
    return s

def read_csv_any(path: str) -> pd.DataFrame:
    for enc in ("utf-8-sig", "utf-8", "cp1252"):
        try:
            return pd.read_csv(path, encoding=enc)
        except Exception:
            continue
    return pd.read_csv(path)

def to_num(s: pd.Series):
    return pd.to_numeric(s, errors="coerce")

def coalesce_first_non_na(df: pd.DataFrame, names: List[str]) -> pd.Series:
    cands = []
    for n in names:
        if n in df.columns:
            cands.append(to_num(df[n]))
    if not cands:
        return pd.Series(dtype="float64")
    stack = pd.concat(cands, axis=1)
    out = stack.bfill(axis=1).iloc[:, 0]
    return out

# ===== Main =====
def merge_all_final_csv(final_dir: str, output_name: str):
    p = Path(final_dir)
    assert p.exists(), f"Không tìm thấy thư mục: {final_dir}"

    files = sorted(glob.glob(str(p / "*_final.csv")))
    if not files:
        print("⚠️ Không tìm thấy file *_final.csv nào."); return

    print("🔎 Sẽ gộp:")
    for f in files:
        print(" •", os.path.basename(f))

    dfs: List[pd.DataFrame] = []
    for f in files:
        try:
            df = read_csv_any(f)
            df.columns = [c.strip() for c in df.columns]
            dfs.append(df)
            print(f"✅ Đã đọc {os.path.basename(f)} ({len(df)} dòng)")
        except Exception as e:
            print(f"❌ Lỗi đọc {f}: {e}")

    if not dfs:
        print("⚠️ Không có DataFrame hợp lệ để gộp."); return

    merged = pd.concat(dfs, ignore_index=True, sort=False)

    # ---- Hợp nhất biến thể đếm review/rating trước khi reorder
    # review_count <= review_count | review_total | reviews | comment_count
    merged["review_count"] = coalesce_first_non_na(
        merged, ["review_count", "review_total", "reviews", "comment_count"]
    )

    # rating_count <= rating_count | ratings | rating_total
    merged["rating_count"] = coalesce_first_non_na(
        merged, ["rating_count", "ratings", "rating_total"]
    )

    # ---- Chuẩn hóa numeric phụ (nếu có)
    if "rating_value" in merged.columns:
        merged["rating_value"] = to_num(merged["rating_value"])
    if "calories" in merged.columns:
        merged["calories"] = to_num(merged["calories"])

    # ---- Làm phẳng & chuẩn hoá văn bản
    if "title" in merged.columns:
        merged["title"] = flatten_text_series(merged["title"], mode="and")
    if "description" in merged.columns:
        merged["description"] = flatten_text_series(merged["description"], mode="and")
    if "keywords" in merged.columns:
        merged["keywords"] = flatten_text_series(merged["keywords"], mode="and")
    if "ingredients" in merged.columns:
        merged["ingredients"] = flatten_text_series(merged["ingredients"], mode="decode")
    if "instructions" in merged.columns:
        merged["instructions"] = flatten_text_series(merged["instructions"], mode="decode")

    # ---- Bỏ dòng thiếu dữ liệu quan trọng
    required = [c for c in ["title","description","url","ingredients","instructions"] if c in merged.columns]
    before = len(merged)
    merged = merged.dropna(subset=required)
    merged = merged[(merged["title"].str.strip() != "") & (merged["url"].str.strip() != "")]
    print(f"🧹 Loại {before - len(merged)} dòng thiếu dữ liệu.")

    # ---- Khử trùng lặp theo title+url
    before = len(merged)
    if all(c in merged.columns for c in ["title","url"]):
        merged = merged.drop_duplicates(subset=["title","url"], keep="first")
    print(f"🧽 Bỏ trùng: {before - len(merged)} dòng.")

    # ---- Bổ sung cột thiếu & sắp xếp
    for c in CANON_COLS:
        if c not in merged.columns:
            if c in NUM_INT_COLS:
                merged[c] = pd.Series([pd.NA] * len(merged), dtype="Int64")
            elif c in NUM_FLOAT_COLS:
                merged[c] = pd.Series([pd.NA] * len(merged), dtype="Float64")
            else:
                merged[c] = ""
    merged = merged[CANON_COLS]

    # Ép kiểu đúng cho cột số (nếu đã tồn tại)
    for c in NUM_INT_COLS:
        if c in merged.columns:
            merged[c] = to_num(merged[c]).astype("Int64")
    for c in NUM_FLOAT_COLS:
        if c in merged.columns:
            merged[c] = to_num(merged[c]).astype("Float64")

    out_path = Path(final_dir) / output_name
    merged.to_csv(out_path, index=False, encoding="utf-8-sig")
    print(f"\n🎉 DONE! Đã lưu: {out_path}")
    print(f"📊 Tổng số dòng sau khi gộp: {len(merged)}")

if __name__ == "__main__":
    merge_all_final_csv(FINAL_DIR, OUTPUT_NAME)
