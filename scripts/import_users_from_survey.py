import argparse
import csv
import unicodedata
from typing import Dict, List, Optional, Tuple

from neo4j import GraphDatabase

# ============================================================
#  DISH MAPPING: Liên kết tên món trong survey với keyword Recipe
# ============================================================
DISH_MAP: Dict[str, List[str]] = {
    "Pho": ["Pho", "Phở"],
    "Banh Mi": ["Banh Mi", "Bánh Mì"],
    "Bun Cha": ["Bun Cha", "Bún Chả"],
    "Spring Rolls": ["Spring Roll", "Gỏi Cuốn"],
    "Banh Xeo": ["Banh Xeo", "Bánh Xèo"],
    "Pad Thai": ["Pad Thai"],
    "Tom Yum": ["Tom Yum"],
    "Green Curry": ["Green Curry"],
    "Som Tum": ["Papaya Salad", "Gỏi Đu Đủ"],
    "Mango Sticky Rice": ["Mango Sticky Rice", "Xôi Xoài"],
    "Dim Sum": ["Dim Sum"],
    "Peking Duck": ["Peking Duck", "Vịt Quay"],
    "Mapo Tofu": ["Mapo Tofu", "Đậu Hũ Tứ Xuyên"],
    "Kung Pao Chicken": ["Kung Pao", "Gà Cung Bảo"],
    "Chow Mein": ["Chow Mein", "Mì Xào"],
    "Croissant": ["Croissant"],
    "Baguette": ["Baguette"],
    "Creme Brulee": ["Creme Brulee", "Crème Brûlée"],
    "Ratatouille": ["Ratatouille"],
    "Biryani": ["Biryani"],
    "Butter Chicken": ["Butter Chicken", "Gà Bơ"],
    "Tikka Masala": ["Tikka Masala", "Cà Ri Tikka Masala"],
    "Samosa": ["Samosa"],
    "Pizza": ["Pizza"],
    "Spaghetti": ["Spaghetti", "Carbonara"],
    "Lasagna": ["Lasagna"],
    "Tiramisu": ["Tiramisu"],
    "Sushi": ["Sushi"],
    "Ramen": ["Ramen"],
    "Tempura": ["Tempura"],
    "Okonomiyaki": ["Okonomiyaki"],
    "Udon": ["Udon"],
    "Kimchi": ["Kimchi"],
    "Bibimbap": ["Bibimbap", "Cơm Trộn"],
    "Bulgogi": ["Bulgogi"],
    "Tteokbokki": ["Tteokbokki", "Bánh Gạo Cay"],
    "Korean Fried Chicken": ["Korean Fried Chicken", "Gà Rán Hàn Quốc"],
    "Hamburger": ["Hamburger", "Burger"],
    "Hot Dog": ["Hot Dog"],
    "Barbecue Ribs": ["BBQ", "Ribs", "Sườn Nướng"]
}

VN_TO_EN_CUISINE = {
    "Việt Nam": "Vietnamese",
    "Trung Quốc": "Chinese",
    "Ý": "Italian",
    "Nhật Bản": "Japanese",
    "Hàn Quốc": "Korean",
    "Pháp": "French",
    "Ấn Độ": "Indian",
    "Thái Lan": "Thai",
    "Mỹ": "American",
}

# ============================================================
#  UTILITIES
# ============================================================

def _normalize_col(s: str) -> str:
    """Chuẩn hóa tiêu đề cột."""
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).replace(" ", "").lower()

def _strip_accents(s: str) -> str:
    """Xóa dấu tiếng Việt để dễ so khớp."""
    return "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c)).lower()

def _split_multi(value: Optional[str]) -> List[str]:
    if not value:
        return []
    parts = [p.strip() for p in value.split(",") if p.strip()]
    return list(dict.fromkeys(parts))

def _norm_skill(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.lower()
    if "beginner" in v or "người mới" in v:
        return "beginner"
    if "intermediate" in v or "trung bình" in v:
        return "intermediate"
    if "advanced" in v or "thành thạo" in v or "nâng cao" in v:
        return "advanced"
    return None

def _norm_time(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    v = value.replace("–", "-").lower()
    if "<" in v:
        for tok in v.replace("<", "").split():
            try:
                return int(tok)
            except Exception:
                continue
        return 15
    if "-" in v:
        try:
            parts = [int(x) for x in v.replace("minutes", "").replace("phút", "").split("-")]
            if parts:
                return max(parts)
        except Exception:
            return None
    for tok in v.split():
        try:
            return int(tok)
        except Exception:
            continue
    return None

def _extract_cuisines(value: Optional[str]) -> List[str]:
    out: List[str] = []
    for raw in _split_multi(value):
        en = None
        if "(" in raw and ")" in raw:
            try:
                en = raw.split("(")[-1].split(")")[0].strip()
            except Exception:
                en = None
        if not en:
            for vn, eng in VN_TO_EN_CUISINE.items():
                if vn in raw:
                    en = eng
                    break
        if en:
            out.append(en)
    return list(dict.fromkeys(out))

def _extract_allergy_categories(value: Optional[str]) -> List[str]:
    if not value:
        return []
    v = value.lower()
    cats: List[str] = []
    if "hải sản" in v or "seafood" in v:
        cats.append("seafood")
    if "hạt" in v or "nut" in v or "peanut" in v:
        cats.append("nut")
    if "sữa" in v or "milk" in v or "dairy" in v:
        cats.append("dairy")
    if "trứng" in v or "egg" in v:
        cats.append("dairy")
    return list(dict.fromkeys(cats))

# ============================================================
#  COLUMN FINDER
# ============================================================

def _find_cols(header: List[str]) -> Dict[str, int]:
    norm_headers = [_normalize_col(h) for h in header]

    def find_one(keywords):
        for i, h in enumerate(norm_headers):
            if any(k in h for k in keywords):
                return i
        return -1

    idx_name = find_one(["hovaten", "fullname"])
    idx_email = find_one(["email"])
    idx_skill = find_one(["kynang", "skill"])
    idx_time = find_one(["baonhieuthoigian", "howmuchtimedo"])
    idx_cuisine = find_one(["quocgia", "cuisine"])
    idx_allergy = find_one(["diung", "allergy"])
    idx_diet = find_one(["hanche", "dietary"])

    # 🔹 Tìm tất cả các cột món ăn (mỗi quốc gia 1 cột)
    dish_cols = [
        i for i, h in enumerate(norm_headers)
        if "monan" in h or "dish" in h or "dishes" in h
    ]

    return {
        "name": idx_name,
        "email": idx_email,
        "skill": idx_skill,
        "time": idx_time,
        "cuisine": idx_cuisine,
        "allergy": idx_allergy,
        "diet": idx_diet,
        "dish_cols": dish_cols,
    }

def _row_get(row: List[str], idx: int) -> Optional[str]:
    if idx < 0 or idx >= len(row):
        return None
    v = row[idx]
    return v.strip() if v and v.strip() else None

# ============================================================
#  MAIN IMPORT FUNCTION
# ============================================================

def import_survey(csv_path: str, uri: str, user: str, password: str, database: Optional[str]):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    created_users = linked_allergies = linked_fav_cuisines = linked_recipes = 0

    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            cols = _find_cols(header)

            session_kwargs = {"database": database} if database else {}
            with driver.session(**session_kwargs) as session:
                for idx, row in enumerate(reader, start=1):
                    name = _row_get(row, cols["name"]) or f"user_{idx}"
                    email = (_row_get(row, cols["email"]) or f"user{idx}@example.com").lower()
                    user_id = f"survey_{idx}"

                    skill = _norm_skill(_row_get(row, cols["skill"]))
                    max_time = _norm_time(_row_get(row, cols["time"]))
                    fav_cuisines = _extract_cuisines(_row_get(row, cols["cuisine"]))
                    allergy_cats = _extract_allergy_categories(_row_get(row, cols["allergy"]))

                    diet_raw = _row_get(row, cols["diet"]) or ""
                    dietary_prefs: List[str] = []
                    v = diet_raw.lower()
                    if "vegan" in v:
                        dietary_prefs.append("vegan")
                    if "vegetarian" in v or "chay" in v:
                        dietary_prefs.append("vegetarian")
                    if "ít đường" in v or "low sugar" in v:
                        dietary_prefs.append("low_sugar")

                    # --- Tạo user node ---
                    session.run(
                        """
                        MERGE (u:User {user_id: $uid})
                        SET u.name = $name,
                            u.email = $email,
                            u.skill_level = coalesce($skill, u.skill_level),
                            u.max_cook_time = coalesce($max_time, u.max_cook_time),
                            u.dietary_preferences = CASE WHEN size($diet) > 0 THEN $diet ELSE coalesce(u.dietary_preferences, []) END,
                            u.locale = coalesce(u.locale, 'vi-VN')
                        """,
                        uid=user_id,
                        name=name,
                        email=email,
                        skill=skill,
                        max_time=max_time,
                        diet=dietary_prefs,
                    )
                    created_users += 1

                    # --- Link allergy ---
                    if allergy_cats:
                        session.run(
                            """
                            MATCH (u:User {user_id: $uid})
                            MATCH (i:Ingredient)
                            WHERE i.category IN $cats
                            MERGE (u)-[:ALLERGIC_TO]->(i)
                            """,
                            uid=user_id,
                            cats=allergy_cats,
                        )
                        linked_allergies += 1

                    # --- Link favorite cuisines ---
                    for c in fav_cuisines:
                        session.run(
                            """
                            MERGE (cu:Cuisine {name: $name})
                            WITH cu
                            MATCH (u:User {user_id: $uid})
                            MERGE (u)-[:FAVORS_CUISINE]->(cu)
                            """,
                            uid=user_id,
                            name=c,
                        )
                        linked_fav_cuisines += 1

                    # --- Link favorite dishes (gộp nhiều cột) ---
                    fav_dishes: List[str] = []
                    for col_idx in cols["dish_cols"]:
                        cell = _row_get(row, col_idx)
                        if cell:
                            fav_dishes.extend(_split_multi(cell))
                    fav_dishes = list(dict.fromkeys(fav_dishes))

                    for dish in fav_dishes:
                        dish_nodot = _strip_accents(dish)
                        for key, keywords in DISH_MAP.items():
                            for kw in keywords:
                                if _strip_accents(kw) in dish_nodot:
                                    session.run(
                                        """
                                        MATCH (u:User {user_id:$uid})
                                        MATCH (r:Recipe)
                                        WHERE toLower(r.title) CONTAINS toLower($kw)
                                        MERGE (u)-[:INTERACTED_WITH {event_type:'like', timestamp:datetime()}]->(r)
                                        """,
                                        uid=user_id,
                                        kw=kw,
                                    )
                                    linked_recipes += 1
    finally:
        driver.close()

    print(f"✅ Imported users={created_users}, allergy_links={linked_allergies}, "
          f"fav_cuisine_links={linked_fav_cuisines}, recipe_links={linked_recipes}")

# ============================================================
#  ENTRY POINT
# ============================================================

def main():
    parser = argparse.ArgumentParser(description="Import users from survey CSV and map to Neo4j profile")
    parser.add_argument("--csv", required=True, help="Path to survey CSV (UTF-8)")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="neo4j")
    parser.add_argument("--db", dest="database", default="food")
    args = parser.parse_args()

    import_survey(args.csv, args.uri, args.user, args.password, args.database)

if __name__ == "__main__":
    main()
