import argparse
import csv
from typing import Dict, List, Optional, Tuple

from neo4j import GraphDatabase


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


def _split_multi(value: Optional[str]) -> List[str]:
    if not value:
        return []
    # Values look like: "A (English), B (English), ..."
    parts = [p.strip() for p in value.split(",") if p.strip()]
    # Collapse duplicates and trailing parentheses pieces
    out: List[str] = []
    for p in parts:
        # Keep inside text before last ')', drop trailing punctuation
        out.append(p.strip())
    return list(dict.fromkeys(out))


def _norm_skill(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.lower()
    if "beginner" in v or "người mới" in v:
        return "beginner"
    if "intermediate" in v or "trung bình" in v:
        return "intermediate"
    if "advanced" in v or "nâng cao" in v:
        return "advanced"
    return None


def _norm_time(value: Optional[str]) -> Optional[int]:
    if not value:
        return None
    v = value.replace("–", "-").lower()
    if "<" in v:
        # "< 15 minutes"
        for tok in v.replace("<", "").split():
            try:
                return int(tok)
            except Exception:
                continue
        return 15
    if "-" in v:
        # "30 - 60 minutes" -> upper bound
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
        # Expect patterns like "Việt Nam (Vietnamese)"
        en = None
        if "(" in raw and ")" in raw:
            try:
                en = raw.split("(")[-1].split(")")[0].strip()
            except Exception:
                en = None
        if not en:
            # Try map by Vietnamese name
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
        cats.append("dairy")  # in ingredient list, egg marked dairy
    return list(dict.fromkeys(cats))


def _find_cols(header: List[str]) -> Dict[str, int]:
    # Fuzzy match key columns by Vietnamese/English prompts
    def find(pred) -> Optional[int]:
        for i, h in enumerate(header):
            if pred(h):
                return i
        return None

    idx_name = find(lambda h: "Họ và tên" in h or "Full Name" in h)
    idx_email = find(lambda h: "Email" in h)
    idx_skill = find(lambda h: "kỹ năng" in h.lower() or "skill" in h.lower())
    idx_time = find(lambda h: "bao nhiêu thời gian" in h.lower() or "how much time" in h.lower())
    idx_cuisine = find(lambda h: "quốc gia" in h.lower() or "which country’s cuisine" in h.lower())
    idx_allergy = find(lambda h: "dị ứng" in h.lower() and "thực phẩm" in h.lower())
    idx_diet = find(lambda h: "hạn chế" in h.lower() or "dietary" in h.lower())

    return {
        "name": idx_name if idx_name is not None else -1,
        "email": idx_email if idx_email is not None else -1,
        "skill": idx_skill if idx_skill is not None else -1,
        "time": idx_time if idx_time is not None else -1,
        "cuisine": idx_cuisine if idx_cuisine is not None else -1,
        "allergy": idx_allergy if idx_allergy is not None else -1,
        "diet": idx_diet if idx_diet is not None else -1,
    }


def _row_get(row: List[str], idx: int) -> Optional[str]:
    if idx < 0 or idx >= len(row):
        return None
    v = row[idx]
    return v if v and v.strip() else None


def import_survey(csv_path: str, uri: str, user: str, password: str, database: Optional[str]) -> Tuple[int, int, int]:
    driver = GraphDatabase.driver(uri, auth=(user, password))
    created_users = 0
    linked_allergies = 0
    linked_fav_cuisines = 0
    try:
        with open(csv_path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.reader(f)
            header = next(reader)
            cols = _find_cols(header)

            session_kwargs = {"database": database} if database else {}
            with driver.session(**session_kwargs) as session:
                for idx, row in enumerate(reader, start=1):
                    name = _row_get(row, cols["name"]) or f"survey_user_{idx}"
                    email = (_row_get(row, cols["email"]) or f"survey{idx}@example.com").lower()
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

                    # Create/Update User basic props
                    session.run(
                        """
                        MERGE (u:User {user_id: $uid})
                        SET u.name = $name,
                            u.email = $email,
                            u.skill_level = coalesce($skill, u.skill_level),
                            u.max_cook_time = coalesce($max_time, u.max_cook_time),
                            u.dietary_preferences = CASE WHEN size($diet) > 0 THEN $diet ELSE coalesce(u.dietary_preferences, []) END,
                            u.locale = coalesce(u.locale, 'vi-VN')
                        RETURN u.user_id AS uid
                        """,
                        uid=user_id,
                        name=name,
                        email=email,
                        skill=skill,
                        max_time=max_time,
                        diet=dietary_prefs,
                    )
                    created_users += 1

                    # Link allergies by category to all matching ingredients
                    if allergy_cats:
                        session.run(
                            """
                            MATCH (u:User {user_id: $uid})
                            MATCH (i:Ingredient)
                            WHERE i.category IN $cats OR (i.allergen_flag = true AND i.category IN $cats)
                            MERGE (u)-[:ALLERGIC_TO]->(i)
                            """,
                            uid=user_id,
                            cats=allergy_cats,
                        )
                        linked_allergies += 1

                    # Link favorite cuisines
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

    finally:
        driver.close()
    return created_users, linked_allergies, linked_fav_cuisines


def main() -> None:
    parser = argparse.ArgumentParser(description="Import users from survey CSV and map to Neo4j profile")
    parser.add_argument("--csv", required=True, help="Path to survey CSV (UTF-8)")
    parser.add_argument("--uri", default="bolt://localhost:7687")
    parser.add_argument("--user", default="neo4j")
    parser.add_argument("--password", default="neo4j")
    parser.add_argument("--db", dest="database", default="food")
    args = parser.parse_args()

    created, allerg, fav = import_survey(args.csv, args.uri, args.user, args.password, args.database)
    print(f"Imported users={created}, allergy_links={allerg}, fav_cuisine_links={fav}")


if __name__ == "__main__":
    main()


