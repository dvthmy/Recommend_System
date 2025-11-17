#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import survey data → create User nodes in Neo4j
Link:
 - ALLERGIC_TO (handle 'No allergies')
 - FAVORS_CUISINE
 - INTERACTED_WITH Recipes (3 for DISH_MAP, 1 for DISH_MAP_EXTRA)

Usage:
  python import_users_from_survey.py \
    --csv data/users/users-survey.csv \
    --uri bolt://localhost:7687 \
    --user neo4j \
    --password Admin123! \
    --db test \
    --verbose
"""

import argparse
import csv
import json
import unicodedata
import time
import traceback
from pathlib import Path
from typing import Dict, List, Optional

from neo4j import GraphDatabase

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from config import DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

# ============================================================
#  DISH MAPS
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

# Gộp toàn bộ dish extra vào
DISH_MAP_EXTRA = {
    # 🇻🇳 Vietnamese dishes
    "Bun Dau Mam Tom": ["Bun Dau Mam Tom", "Bún Đậu Mắm Tôm", "Fermented Shrimp Noodle"],
    "Bun Bo Hue": ["Bun Bo Hue", "Bún Bò Huế", "Hue Beef Noodle Soup"],
    "Bun Thang": ["Bun Thang", "Bún Thang", "Vietnamese Chicken Vermicelli Soup"],
    "Bun Rieu": ["Bun Rieu", "Bún Riêu", "Crab Noodle Soup"],
    "Bun Oc Nguoi": ["Bun Oc", "Bún Ốc", "Snail Noodle Soup"],
    "Hu Tieu": ["Hu Tieu", "Hủ Tiếu", "Pork Noodle Soup"],
    "Banh Canh": ["Banh Canh", "Vietnamese Thick Noodle Soup"],
    "Bot Chien": ["Bot Chien", "Bột Chiên", "Vietnamese Fried Rice Cake"],
    "Banh Khot": ["Banh Khot", "Bánh Khọt", "Mini Savory Pancake"],
    "Banh Duc Nong": ["Banh Duc Nong", "Bánh Đúc Nóng", "Vietnamese Rice Cake Soup"],
    "Bun Cha": ["Bun Cha", "Bún Chả", "Grilled Pork Noodle"],
    "Banh Trang Tron": ["Banh Trang Tron", "Bánh Tráng Trộn", "Rice Paper Salad"],
    "Com Tam": ["Com Tam", "Cơm Tấm", "Broken Rice with Pork"],
    "Com Suon": ["Com Suon", "Cơm Sườn", "Grilled Pork Rice"],
    "Com Chien": ["Com Chien ", "Cơm Chiên ", "Fried Rice"],
    "Thit Kho Hot Vit": ["Thit Kho Hot Vit", "Thịt Kho Hột Vịt", "Braised Pork with Eggs"],
    "Canh Chua": ["Canh Chua", "Vietnamese Sour Soup"],
    "Mi Quang": ["Mi Quang", "Mì Quảng", "Quang Style Turmeric Noodles"],
    "Sup Cua": ["Sup Cua", "Súp Cua", "Crab Soup"],
    "Pia": ["Pia", "Pịa", "Pịa Bò", "Fermented Beef Soup"],
    "Ga Ran": ["Ga Ran", "Gà Rán", "Fried Chicken"],
    "Ga Nuong": ["Ga Nuong", "Gà Nướng", "Grilled Chicken"],
    "Thit Xao Chua Ngot": ["Suon Xao Chua Ngot", "Sườn Xào Chua Ngọt", "Sweet and Sour Pork Ribs"],
    "Bun Quay": ["Bun Quay", "Quay Noodle Soup"],
    "Bo Luc Lac": ["Bo Luc Lac", "Bò Lúc Lắc", "Shaking Beef"],
    "Bun Bo": ["Bun Bo", "Bún Bò", "Beef Vermicelli"],
    "Com Ca Ri": ["Com Ca Ri", "Cơm Cà Ri", "Vietnamese Curry Rice"],
    "Mi Cay": ["Mi Cay", "Mì Cay", "Spicy Noodles"],
    "Mi Kho Xa Xiu": ["Mì Khô Xá Xíu", "Mì Trộn Xá Xíu", "Char Siu Noodles"],
    "Nam Kim Cham": ["Nam Kim Cham", "Nấm Kim Châm", "Enoki Mushrooms"],
    "Nam Dui Ga": ["Nam Dui Ga", "Nấm Đùi Gà", "King Oyster Mushrooms"],


    # 🇯🇵 Japanese dishes
    "Takoyaki": ["Takoyaki", "Octopus Balls"],
    "Curry Japan": ["Ca Ri Nhat", "Cà Ri Nhật", "Japanese Curry"],

    # 🇮🇳 Indian dishes
    "Masala": ["Masala", "Bột Masala", "Cà Ri Ấn Độ", "Masala Ấn Độ", "Indian Masala"],
    "Biryani India": ["Biryani Ấn Độ", "Cơm Biryani", "Indian Biryani"],

    # 🇰🇷 Korean
    "Kimbap": ["Com Cuon Han Quoc", "Cơm Cuộn Hàn Quốc", "Kimbap"],

    # 🇲🇽 Mexican
    "Tacos": ["Tacos", "Bánh Tacos", "Bánh Tacos Pháp", "Burito", "Burrito", "Mexican Tacos"],

    # 🇫🇷 French
    "Panna Cotta": ["Panna Cotta", "Italian Pudding"],  # thường gốc Ý nhưng hay được nhóm cùng nhóm châu Âu
    "Creme Brulee": ["Creme Brulee", "Crème Brûlée", "French Custard"],

    # 🇷🇺 Russian
    "Chocolate Nga": ["Socola Nga", "Sô-cô-la Nga", "Russian Chocolate"],

    # 🌍 Other / International
    "Lobster": ["Lobster", "Grilled Lobster", "Butter Lobster"],
    "Hamburger Cheese": ["Hamburger", "Burger", "Phô Mai", "Cheeseburger"],
    "Lechona": ["Lechona", "Colombian Roasted Pork"],
}


# ============================================================
#  RULES
# ============================================================

DISH_RULES = {
    "Pho": {"cuisine": "Vietnamese", "must_have": ["pho"], "must_not": []},
    "Banh Mi": {"cuisine": "Vietnamese", "must_have": ["banh", "mi"], "must_not": []},
    "Spring Rolls": {"cuisine": "Vietnamese", "must_have": ["spring", "roll"], "must_not": []},
    "Pad Thai": {"cuisine": "Thai", "must_have": ["pad", "thai"], "must_not": []},
    "Tom Yum": {"cuisine": "Thai", "must_have": ["tom", "yum"], "must_not": []},
    "Green Curry": {"cuisine": "Thai", "must_have": ["green", "curry"], "must_not": []},
    "Chicken Tikka Masala": {"cuisine": "Indian", "must_have": ["tikka", "masala"], "must_not": []},
    "Butter Chicken": {"cuisine": "Indian", "must_have": ["butter", "chicken"], "must_not": []},
    "Biryani": {"cuisine": "Indian", "must_have": ["biryani"], "must_not": []},
    "Pizza": {"cuisine": "Italian", "must_have": ["pizza"], "must_not": ["fruit", "dessert"]},
    "Lasagna": {"cuisine": "Italian", "must_have": ["lasagna"], "must_not": []},
    "Spaghetti Carbonara": {"cuisine": "Italian", "must_have": ["carbonara"], "must_not": ["sauce"]},
    "Sushi": {"cuisine": "Japanese", "must_have": ["sushi"], "must_not": ["rice"]},
    "Ramen": {"cuisine": "Japanese", "must_have": ["ramen"], "must_not": []},
    "Udon": {"cuisine": "Japanese", "must_have": ["udon"], "must_not": []},
    "Tempura": {"cuisine": "Japanese", "must_have": ["tempura"], "must_not": []},
    "Kimchi": {"cuisine": "Korean", "must_have": ["kimchi"], "must_not": []},
    "Bibimbap": {"cuisine": "Korean", "must_have": ["bibimbap"], "must_not": []},
    "Bulgogi": {"cuisine": "Korean", "must_have": ["bulgogi"], "must_not": []},
    "Tteokbokki": {"cuisine": "Korean", "must_have": ["tteokbokki"], "must_not": []},
    "Peking Duck": {"cuisine": "Chinese", "must_have": ["peking", "duck"], "must_not": []},
    "Mapo Tofu": {"cuisine": "Chinese", "must_have": ["mapo", "tofu"], "must_not": []},
    "Chow Mein": {"cuisine": "Chinese", "must_have": ["chow", "mein"], "must_not": []},
    "Baguette": {"cuisine": "French", "must_have": ["baguette"], "must_not": []},
    "Creme Brulee": {"cuisine": "French", "must_have": ["creme", "brulee"], "must_not": []},
    "Ratatouille": {"cuisine": "French", "must_have": ["ratatouille"], "must_not": []},
}


DISH_RULES_EXTRA = {
    # 🇻🇳 Vietnamese
    "Bun Dau Mam Tom": {"cuisine": "Vietnamese", "must_have": ["bun", "mam", "tom"], "must_not": []},
    "Bun Bo Hue": {"cuisine": "Vietnamese", "must_have": ["bun", "bo", "hue"], "must_not": []},
    "Bun Thang": {"cuisine": "Vietnamese", "must_have": ["bun", "thang"], "must_not": []},
    "Bun Rieu": {"cuisine": "Vietnamese", "must_have": ["bun", "rieu"], "must_not": []},
    "Bun Oc Nguoi": {"cuisine": "Vietnamese", "must_have": ["bun", "oc"], "must_not": []},
    "Hu Tieu": {"cuisine": "Vietnamese", "must_have": ["hu", "tieu"], "must_not": []},
    "Banh Canh": {"cuisine": "Vietnamese", "must_have": ["banh", "canh"], "must_not": []},
    "Banh Xeo": {"cuisine": "Vietnamese", "must_have": ["banh", "xeo"], "must_not": []},
    "Banh Khot": {"cuisine": "Vietnamese", "must_have": ["banh", "khot"], "must_not": []},
    "Banh Duc Nong": {"cuisine": "Vietnamese", "must_have": ["banh", "duc"], "must_not": []},
    "Bun Cha": {"cuisine": "Vietnamese", "must_have": ["bun", "cha"], "must_not": []},
    "Banh Trang Tron": {"cuisine": "Vietnamese", "must_have": ["banh", "trang"], "must_not": []},
    "Com Tam": {"cuisine": "Vietnamese", "must_have": [], "must_not": []},
    "Com Suon": {"cuisine": "Vietnamese", "must_have": [], "must_not": []},
    "Com Chien": {"cuisine": "Vietnamese", "must_have": ["com", "chien"], "must_not": []},
    "Thit Kho Hot Vit": {"cuisine": "Vietnamese", "must_have": ["thit", "kho", "vit"], "must_not": []},
    "Canh Chua": {"cuisine": "Vietnamese", "must_have": ["canh", "chua"], "must_not": []},
    "Mi Quang": {"cuisine": "Vietnamese", "must_have": ["mi", "quang"], "must_not": []},
    "Sup Cua": {"cuisine": "Vietnamese", "must_have": ["sup", "cua"], "must_not": []},
    "Pia": {"cuisine": "Vietnamese", "must_have": ["pia"], "must_not": []},
    "Ga Ran": {"cuisine": "Vietnamese", "must_have": [], "must_not": []},
    "Ga Nuong": {"cuisine": "Vietnamese", "must_have": ["ga", "nuong"], "must_not": []},
    "Thit Xao Chua Ngot": {"cuisine": "Vietnamese", "must_have": ["xao", "chua", "ngot"], "must_not": []},
    "Bun Quay": {"cuisine": "Vietnamese", "must_have": ["bun", "quay"], "must_not": []},
    "Bo Luc Lac": {"cuisine": "Vietnamese", "must_have": ["bo", "luc", "lac"], "must_not": []},
    "Bun Bo": {"cuisine": "Vietnamese", "must_have": ["bun", "bo"], "must_not": []},
    "Com Ca Ri": {"cuisine": "Vietnamese", "must_have": ["com", "ca", "ri"], "must_not": []},
    "Com Nha": {"cuisine": "Vietnamese", "must_have": ["com", "nha"], "must_not": []},
    "Mi Cay": {"cuisine": "Vietnamese", "must_have": ["mi", "cay"], "must_not": []},
    "Mi Tron Xa Xiu": {"cuisine": "Vietnamese", "must_have": ["mi", "xa", "xiu"], "must_not": []},
    "Nam Kim Cham": {"cuisine": "Vietnamese", "must_have": ["nam", "kim", "cham"], "must_not": []},
    "Nam Dui Ga": {"cuisine": "Vietnamese", "must_have": ["nam", "dui", "ga"], "must_not": []},
    "Bot Chien": {"cuisine": "Vietnamese", "must_have": ["bot", "chien"], "must_not": []},

    # 🇯🇵 Japanese
    "Takoyaki": {"cuisine": "Japanese", "must_have": ["takoyaki"], "must_not": []},
    "Curry Japan": {"cuisine": "Japanese", "must_have": ["curry"], "must_not": []},

    # 🇮🇳 Indian
    "Masala": {"cuisine": "Indian", "must_have": ["masala"], "must_not": []},
    "Biryani India": {"cuisine": "Indian", "must_have": ["biryani"], "must_not": []},

    # 🇰🇷 Korean
    "Kimbap": {"cuisine": "Korean", "must_have": ["kimbap", "rice", "roll"], "must_not": []},

    # 🇲🇽 Mexican
    "Tacos": {"cuisine": "Mexican", "must_have": ["taco", "burrito"], "must_not": []},

    # 🇫🇷 French
    "Panna Cotta": {"cuisine": "French", "must_have": ["panna", "cotta"], "must_not": []},
    "Creme Brulee": {"cuisine": "French", "must_have": ["creme", "brulee"], "must_not": []},

    # 🇷🇺 Russian
    "Chocolate Nga": {"cuisine": "Russian", "must_have": ["chocolate"], "must_not": []},

    # 🌍 Other
    "Hamburger Cheese": {"cuisine": "American", "must_have": ["hamburger", "cheese"], "must_not": []},
    "Lobster": {"cuisine": "International", "must_have": ["lobster"], "must_not": []},
    "Lechona": {"cuisine": "Colombian", "must_have": ["lechona"], "must_not": []},
}

VN_TO_EN_CUISINE = { "Việt Nam": "Vietnamese", "Trung Quốc": "Chinese", "Ý": "Italian", "Nhật Bản": "Japanese", "Hàn Quốc": "Korean", "Pháp": "French", "Ấn Độ": "Indian", "Thái Lan": "Thai", "Mỹ": "American" }
# ============================================================

def _normalize_col(s: str) -> str:
    s = unicodedata.normalize("NFKD", s)
    return "".join(c for c in s if not unicodedata.combining(c)).replace(" ", "").lower()

def _strip_accents(s: str) -> str:
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
    v = value.lower().strip()
    cats: List[str] = []
    if "không dị ứng" in v or "no allergy" in v or "none" in v:
        cats.append("none")
    if "hải sản" in v or "seafood" in v:
        cats.append("seafood")
    if "đậu phộng" in v or "peanut" in v:
        cats.append("peanut")
    if "hạt" in v or "nut" in v or "tree nut" in v:
        cats.append("nut")
    if "sữa" in v or "milk" in v or "dairy" in v:
        cats.append("dairy")
    if "trứng" in v or "egg" in v:
        cats.append("egg")
    if "gluten" in v or "lúa mì" in v or "wheat" in v:
        cats.append("gluten")
    if "đậu nành" in v or "soy" in v or "tofu" in v:
        cats.append("soy")
    return list(dict.fromkeys(cats))


    
def _find_cols(header: List[str]) -> Dict[str, int | List[int]]:
    norm_headers = [_normalize_col(h) for h in header]

    def find_one(keys): 
        return next((i for i, h in enumerate(norm_headers) if any(k in h for k in keys)), -1)

    def find_many(keys):
        return [i for i, h in enumerate(norm_headers) if any(k in h for k in keys)]

    # ---- Các cột cơ bản
    name_idx   = find_one(["hovaten", "fullname"])
    email_idx1 = find_one(["diachiemail", "emailaddress", "email"])
    skill_idx  = find_one(["kynang", "cookingskill"])
    time_idx   = find_one(["baonhieuthoigian", "howmuchtimedo", "howmuchtimedoyouusuallyhaveto"])
    cuisine_idx= find_one(["quocgia", "whichcountryscuisine"])
    allergy_idx= find_one(["diung", "foodallerg", "doyouhaveanyfoodallerg"])
    diet_idx   = find_one(["hanche", "dietaryrestrict", "doyouhaveanydietaryrestrict"])
    gender_idx    = find_one(["gioitinh", "gender"])
    age_idx       = find_one(["tuoi", "age", "dotuoi"])

    # ---- Cột món ăn theo từng quốc gia (MAIN)
    vn_cols    = find_many(["vietnamm", "monanvietnam", "whichvietnamesedish"])
    thai_cols  = find_many(["thailan", "whichthaidish"])
    cn_cols    = find_many(["trungquoc", "whichchinesedish"])
    fr_cols    = find_many(["phap", "whichfrenchdish"])
    in_cols    = find_many(["an_do", "an_do", "whichindiandish", "andodish", "indiandish"])
    it_cols    = find_many(["y", "italy", "whichitaliandish", "y_nao", "monany"])
    jp_cols    = find_many(["nhatban", "whichjapanesedish", "nhatban_nao"])
    kr_cols    = find_many(["hanquoc", "whichkoreandish"])
    us_cols    = find_many(["my", "whichamericandish"])

    # ---- Cột EXTRA (món khác chưa liệt kê)
    extra_idx  = find_one(["comonanaobanchuaduocdecap", "isthereanydishyoulike", "monankhac"])

    # ---- Cột meal-type (không dùng trong chọn recipe, nhưng có thể lưu)
    mealtype_idx = find_one(["banthuongquantamdenloaibua", "whichtypeofmeal"])

    return {
        "name": name_idx,
        "email": email_idx1,
        "skill": skill_idx,
        "time": time_idx,
        "cuisine": cuisine_idx,
        "allergy": allergy_idx,
        "diet": diet_idx,
        "mealtype": mealtype_idx,
        "gender": gender_idx,
        "age": age_idx,

        # nhóm MAIN: gộp hết vào một list lớn (để duyệt đồng nhất)
        "dish_cols_main": list(dict.fromkeys(
            vn_cols + thai_cols + cn_cols + fr_cols + in_cols + it_cols + jp_cols + kr_cols + us_cols
        )),

        # nhóm EXTRA: chỉ 1 cột
        "dish_col_extra": extra_idx,
    }


def _row_get(row: List[str], idx: int) -> Optional[str]:
    return row[idx].strip() if 0 <= idx < len(row) and row[idx].strip() else None

def _norm_gender(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.lower()
    if "nam" in v or "male" in v:
        return "male"
    if "nữ" in v or "female" in v:
        return "female"
    return "other"
def _norm_age(value: Optional[str]) -> Optional[str]:
    if not value:
        return None
    v = value.lower().replace("–", "-").strip()

    if "under" in v or "<18" in v or "dưới" in v:
        return "<18"
    if "18" in v and ("30" in v or "24" in v):
        return "18-30"
    if "30" in v and "34" in v:
        return "30-34"
    if "45" in v and "54" in v:
        return "45-54"
    if "55" in v or "trở lên" in v or "+" in v:
        return "55+"
    return v

# ============================================================
#  Recipe Query
# ============================================================
def _top_k_recipes_for_keyword(session, kw: str, k: int = 3, method: str = "hybrid",
                               C: float = None, m: int = None,
                               cuisine: str | None = None,
                               must_have: list[str] | None = None,
                               must_not: list[str] | None = None):
    """
    Tìm top-k recipes khớp keyword theo tiêu đề (không cần title_tokens)
    Có thể lọc theo cuisine, must_have, must_not.
    method ∈ {"bayes", "wilson", "hybrid"}
    """
    if method not in {"bayes", "wilson", "hybrid"}:
        method = "bayes"

    # Lấy giá trị trung bình toàn cục nếu chưa có
    if C is None or m is None:
        rec = session.run("""
            MATCH (r:Recipe) WHERE r.rating_avg IS NOT NULL
            RETURN avg(r.rating_avg) AS C, percentileCont(coalesce(r.review_count,0),0.5) AS p50
        """).single()
        C = rec["C"]
        m = rec["p50"]

    # ===== Tạo điều kiện động =====
    where_parts = ["r.rating_avg IS NOT NULL"]
    params = {"kw": kw, "C": C, "m": float(m)}

    # 🔍 Tìm trong tiêu đề
    where_parts.append("toLower(r.title) CONTAINS toLower($kw)")

    # 🔍 Lọc theo cuisine
    if cuisine:
        where_parts.append("$cuisine IN coalesce(r.cuisine, [])")
        params["cuisine"] = cuisine

    # 🔍 must_have = tất cả token phải có trong title
    if must_have:
        where_parts.append("all(x IN $must_have WHERE toLower(r.title) CONTAINS toLower(x))")
        params["must_have"] = [x.lower() for x in must_have]

    # 🔍 must_not = không chứa token cấm
    if must_not:
        where_parts.append("none(x IN $must_not WHERE toLower(r.title) CONTAINS toLower(x))")
        params["must_not"] = [x.lower() for x in must_not]

    where_clause = " AND ".join(where_parts)

    # ===== Chọn công thức tính điểm =====
    if method == "bayes":
        q = f"""
        WITH $C AS C, toFloat($m) AS m
        MATCH (r:Recipe)
        WHERE {where_clause}
        WITH r, coalesce(r.rating_avg,0.0) AS R, toFloat(coalesce(r.review_count,0)) AS v, C, m
        WITH r, R, v, ((v/(v+m))*R + (m/(v+m))*C) AS score
        RETURN r.recipe_id AS id, r.title AS title, R AS rating, toInteger(v) AS reviews, score
        ORDER BY score DESC, reviews DESC
        LIMIT 10
        """

    elif method == "wilson":
        q = f"""
        MATCH (r:Recipe)
        WHERE {where_clause}
        WITH r, coalesce(r.rating_avg,0.0) AS R, toFloat(coalesce(r.review_count,0)) AS v
        WITH r, R, v,
             ((R/5.0) + (1.96^2)/(2*v) - 1.96*sqrt(((R/5.0)*(1 - R/5.0) + (1.96^2)/(4*v))/v)) /
             (1 + (1.96^2)/v) * 5 AS score
        RETURN r.recipe_id AS id, r.title AS title, R AS rating, toInteger(v) AS reviews, score
        ORDER BY score DESC
        LIMIT 10
        """

    else:  # method == "hybrid"
        q = f"""
        WITH $C AS C, toFloat($m) AS m
        MATCH (r:Recipe)
        WHERE {where_clause}
        WITH r,
            coalesce(r.rating_avg,0.0) AS R,
            toFloat(coalesce(r.review_count,0)) AS v, C, m
        WITH r, R, v, C, m,
            ((v/(v+m))*R + (m/(v+m))*C) AS bayes,
            CASE 
                WHEN v > 0 THEN
                    ((R/5.0) + (1.96^2)/(2*v) - 1.96*sqrt(((R/5.0)*(1-R/5.0) + (1.96^2)/(4*v))/v)) /
                    (1 + (1.96^2)/v) * 5
                ELSE 0
            END AS wilson
        WITH r, R, v, bayes, wilson,
            (0.7 * bayes + 0.3 * wilson) AS score
        RETURN r.recipe_id AS id, r.title AS title, R AS rating, toInteger(v) AS reviews,
            bayes, wilson, score
        ORDER BY score DESC
        LIMIT 10
        """


    # ===== Thực thi & chọn top-k =====
    results = session.run(q, **params).data()

    # 🟢 Sort thủ công để đảm bảo chính xác
    results_sorted = sorted(results, key=lambda r: (r["score"], r.get("reviews", 0)), reverse=True)
    return results_sorted[:k]


# ============================================================
#  Pick Recipes (Survey + Extra)
# ============================================================

def pick_recipes(session, user_id: str, dish_name: str, C: float, m: int,
                 mode: str = "main", seen_global: set[str] | None = None):
    """
    mode = 'main'  -> dùng DISH_RULES + DISH_MAP, mỗi món k=3
    mode = 'extra' -> dùng DISH_RULES_EXTRA + DISH_MAP_EXTRA, mỗi món k=1
    """
    dish_clean = _strip_accents(dish_name).strip()
    dish_tokens = set(dish_clean.split())
    all_results = []
    seen_aliases, seen_keys = set(), set()

    if seen_global is None:
        seen_global = set()

    if mode not in {"main", "extra"}:
        mode = "main"
    
    NOISE_WORDS = {"no", "none", "hong", "hông", "yes", "không", "ok", "none","Hog","ko","Ko","Có"}
    if dish_clean in NOISE_WORDS or dish_clean.strip() == "":
        return []


    # ============================================================
    #  MAIN MODE
    # ============================================================
    if mode == "main":
        for key, rule in DISH_RULES.items():
            if key in seen_keys or key in seen_global:
                continue

            for alias in DISH_MAP.get(key, []):
                alias_norm = _strip_accents(alias).strip()
                alias_tokens = set(alias_norm.split())

                # tránh alias quá ngắn (vd: "banh")
                if len(alias_tokens) == 1 and list(alias_tokens)[0] in {"banh", "com", "bun", "mi"}:
                    continue

                # nếu alias nằm nguyên cụm trong dish_clean
                if alias_norm in dish_clean or dish_tokens.issuperset(alias_tokens):
                    seen_aliases.add(alias_norm)
                    seen_keys.add(key)
                    seen_global.add(key)

                    recipes = _top_k_recipes_for_keyword(
                        session, key.lower(), k=3, C=C, m=m,
                        cuisine=rule["cuisine"],
                        must_have=rule.get("must_have"),
                        must_not=rule.get("must_not")
                    )
                    if recipes:
                        all_results.append((key, recipes))
                        for r in recipes:
                            session.run("""
                                MATCH (u:User {user_id:$uid}), (rec:Recipe {recipe_id:$rid})
                                MERGE (u)-[rel:INTERACTED_WITH]->(rec)
                                ON CREATE SET rel.event_type='like', rel.timestamp=datetime()
                            """, uid=user_id, rid=r["id"])
                    break
        return all_results

    # ============================================================
    #  EXTRA MODE
    # ============================================================
    else:
        # 🧹 Kiểm tra tránh pick lại các món đã được main chọn
        for key_main, aliases in DISH_MAP.items():
            for alias in aliases:
                alias_norm = _strip_accents(alias).strip()
                if alias_norm and (
                     alias_norm == dish_clean or dish_tokens.issuperset(set(alias_norm.split()))):
                    return []


        for key, rule in DISH_RULES_EXTRA.items():
            if key in seen_keys or key in seen_global:
                continue

            for alias in DISH_MAP_EXTRA.get(key, []):
                alias_norm = _strip_accents(alias).strip()
                alias_tokens = set(alias_norm.split())
                if alias_norm in seen_aliases or alias_norm in seen_global:
                    continue

                # alias phải khớp toàn bộ token hoặc nguyên cụm
                if alias_norm in dish_clean or dish_tokens.issuperset(alias_tokens):
                    seen_aliases.add(alias_norm)
                    seen_keys.add(key)
                    seen_global.add(key)

                    recipes = _top_k_recipes_for_keyword(
                        session, key.lower(), k=1, C=C, m=m,
                        cuisine=rule["cuisine"],
                        must_have=rule.get("must_have"),
                        must_not=rule.get("must_not")
                    )
                    if recipes:
                        # ✅ thêm nhãn [EXTRA] vào key trực tiếp tại đây
                        all_results.append((f"{key} [EXTRA]", recipes))
                        for r in recipes:
                            session.run("""
                                MATCH (u:User {user_id:$uid}), (rec:Recipe {recipe_id:$rid})
                                MERGE (u)-[rel:INTERACTED_WITH]->(rec)
                                ON CREATE SET rel.event_type='like', rel.timestamp=datetime()
                            """, uid=user_id, rid=r["id"])
                    break

        # fallback cho món lạ chưa có rule
        if not all_results and dish_name not in seen_global:
            recipes = _top_k_recipes_for_keyword(session, dish_clean, k=1, C=C, m=m)
            if recipes:
                all_results.append((f"{dish_name} [EXTRA]", recipes))
                seen_global.add(dish_name)
                for r in recipes:
                    session.run("""
                        MATCH (u:User {user_id:$uid}), (rec:Recipe {recipe_id:$rid})
                        MERGE (u)-[rel:INTERACTED_WITH]->(rec)
                        ON CREATE SET rel.event_type='like', rel.timestamp=datetime()
                    """, uid=user_id, rid=r["id"])
        return all_results





def import_survey(
    csv_path: str,
    uri: str,
    user: str,
    password: str,
    database: Optional[str],
    verbose: bool = False,
    out_cypher: Optional[str] = None
):
    """
    Import survey data from CSV into Neo4j.
    
    Args:
        csv_path: Path to CSV file
        uri: Neo4j URI
        user: Neo4j username
        password: Neo4j password
        database: Neo4j database name
        verbose: Print verbose output
        out_cypher: Optional path to generate Cypher file instead of direct import
    """
    csv_file = Path(csv_path)
    if not csv_file.exists():
        print(f"[ERROR] CSV file not found: {csv_path}")
        sys.exit(1)
    
    start_time = time.time()
    driver = None
    created_users = linked_allergies = linked_fav_cuisines = linked_recipes = 0
    errors = 0
    
    if out_cypher:
        print(f"[*] Generating Cypher file: {out_cypher}")
        cypher_lines = []
    else:
        print(f"[*] Importing users from {csv_path}")
        print(f"   URI: {uri}")
        print(f"   Database: {database or 'default'}")
        print(f"   User: {user}")
        driver = GraphDatabase.driver(uri, auth=(user, password))

    try:
        with open(csv_file, "r", encoding="utf-8-sig") as f:
            reader = csv.reader(f)
            header = next(reader)
            cols = _find_cols(header)
            
            if verbose:
                print(f"[*] Detected columns:")
                for key, val in cols.items():
                    if isinstance(val, list):
                        print(f"   {key}: {len(val)} columns")
                    elif val != -1:
                        print(f"   {key}: column {val}")
            
            session_kwargs = {"database": database} if database else {}
            
            if out_cypher:
                # Generate Cypher mode
                cypher_lines.append("// Import users from survey")
                cypher_lines.append("// Generated by import_users_from_survey.py")
                cypher_lines.append("")
                session = None
            else:
                session = driver.session(**session_kwargs)
            
            try:
                for idx, row in enumerate(reader, start=1):
                    try:
                        name = _row_get(row, cols["name"]) or f"user_{idx}"
                        email = (_row_get(row, cols["email"]) or f"user{idx}@example.com").lower()
                        user_id = f"survey_{idx}"

                        skill = _norm_skill(_row_get(row, cols["skill"]))
                        max_time = _norm_time(_row_get(row, cols["time"]))
                        fav_cuisines = _extract_cuisines(_row_get(row, cols["cuisine"]))
                        allergy_cats = _extract_allergy_categories(_row_get(row, cols["allergy"]))
                        
                        gender = _norm_gender(_row_get(row, cols["gender"]))
                        age_group = _norm_age(_row_get(row, cols["age"]))

                        diet_raw = _row_get(row, cols["diet"]) or ""
                        dietary_prefs: List[str] = []
                        v = diet_raw.lower()
                        if "vegan" in v: dietary_prefs.append("vegan")
                        if "vegetarian" in v or "chay" in v: dietary_prefs.append("vegetarian")
                        if "ít đường" in v or "low sugar" in v: dietary_prefs.append("low_sugar")

                        log_lines = [f"[{user_id}] {name}"]
                        
                        if out_cypher:
                            # Generate Cypher for user creation
                            name_escaped = name.replace("'", "\\'")
                            email_escaped = email.replace("'", "\\'")
                            skill_str = f"'{skill}'" if skill else "null"
                            max_time_str = str(max_time) if max_time else "null"
                            gender_str = f"'{gender}'" if gender else "null"
                            age_group_str = f"'{age_group}'" if age_group else "null"
                            diet_json = json.dumps(dietary_prefs, ensure_ascii=False)
                            
                            cypher_lines.append(f"// User {idx}: {name}")
                            cypher_lines.append(f"MERGE (u{idx}:User {{user_id: '{user_id}'}})")
                            cypher_lines.append(f"SET u{idx}.name = '{name_escaped}',")
                            cypher_lines.append(f"    u{idx}.email = '{email_escaped}',")
                            if skill:
                                cypher_lines.append(f"    u{idx}.skill_level = {skill_str},")
                            if max_time:
                                cypher_lines.append(f"    u{idx}.max_cook_time = {max_time_str},")
                            if gender:
                                cypher_lines.append(f"    u{idx}.gender = {gender_str},")
                            if age_group:
                                cypher_lines.append(f"    u{idx}.age_group = {age_group_str},")
                            cypher_lines.append(f"    u{idx}.dietary_preferences = {diet_json},")
                            cypher_lines.append(f"    u{idx}.locale = 'vi-VN';")
                            cypher_lines.append("")
                        else:
                            # Direct import
                            session.run(
                                """
                                MERGE (u:User {user_id:$uid})
                                SET u.name=$name, u.email=$email,
                                    u.skill_level=coalesce($skill,u.skill_level),
                                    u.max_cook_time=coalesce($max_time,u.max_cook_time),
                                    u.gender=coalesce($gender,u.gender),
                                    u.age_group=coalesce($age_group,u.age_group),
                                    u.dietary_preferences=CASE WHEN size($diet)>0 THEN $diet ELSE coalesce(u.dietary_preferences,[]) END,
                                    u.locale=coalesce(u.locale,'vi-VN')
                                """,
                                uid=user_id, name=name, email=email, skill=skill, max_time=max_time, diet=dietary_prefs,
                                gender=gender, age_group=age_group
                            )

                        created_users += 1

                        # --- Allergies ---
                        if allergy_cats:
                            if "none" in allergy_cats:
                                log_lines.append("  Selected 'No allergies' → skip all other allergy links.")
                            else:
                                allergy_examples = {
                                    "seafood": ["shrimp", "fish", "crab", "salmon", "tuna"],
                                    "peanut": ["peanut"],
                                    "nut": ["almond", "walnut", "cashew"],
                                    "dairy": ["milk", "cheese", "butter"],
                                    "egg": ["egg"],
                                    "gluten": ["wheat", "flour", "bread"],
                                    "soy": ["tofu", "soy sauce"]
                                }
                                linked_ing = []
                                for cat in allergy_cats:
                                    examples = allergy_examples.get(cat, [])
                                    if not examples:
                                        continue
                                    for ing in examples[:2]:
                                        if out_cypher:
                                            ing_escaped = ing.replace("'", "\\'")
                                            cat_escaped = cat.replace("'", "\\'")
                                            cypher_lines.append(f"MATCH (u{idx}:User {{user_id: '{user_id}'}})")
                                            cypher_lines.append(f"MATCH (i:Ingredient)")
                                            cypher_lines.append(f"WHERE toLower(i.canonical_name) = toLower('{ing_escaped}')")
                                            cypher_lines.append(f"MERGE (u{idx})-[:ALLERGIC_TO {{reason: '{cat_escaped}'}}]->(i);")
                                        else:
                                            session.run("""
                                                MATCH (u:User {user_id:$uid})
                                                MATCH (i:Ingredient)
                                                WHERE toLower(i.canonical_name)=toLower($ing)
                                                MERGE (u)-[:ALLERGIC_TO {reason:$cat}]->(i)
                                            """, uid=user_id, ing=ing, cat=cat)
                                        linked_ing.append(ing)
                                if linked_ing:
                                    log_lines.append(f"  ALLERGIC_TO {allergy_cats} → {', '.join(linked_ing)}")
                                    linked_allergies += 1
                        else:
                            log_lines.append("  No allergy info provided.")

                        # --- Favorite cuisines ---
                        if fav_cuisines:
                            for c in fav_cuisines:
                                if out_cypher:
                                    c_escaped = c.replace("'", "\\'")
                                    cypher_lines.append(f"MERGE (cu:Cuisine {{name: '{c_escaped}'}})")
                                    cypher_lines.append(f"WITH cu MATCH (u{idx}:User {{user_id: '{user_id}'}})")
                                    cypher_lines.append(f"MERGE (u{idx})-[:FAVORS_CUISINE]->(cu);")
                                else:
                                    session.run("""
                                        MERGE (cu:Cuisine {name:$name})
                                        WITH cu MATCH (u:User {user_id:$uid})
                                        MERGE (u)-[:FAVORS_CUISINE]->(cu)
                                    """, uid=user_id, name=c)
                                linked_fav_cuisines += 1
                            log_lines.append(f"  FAVORS_CUISINE → {', '.join(fav_cuisines)}")

                        # --- Favorite dishes (MAIN + EXTRA) ---
                        dish_logs = []
                        picked_total = 0
                        seen_global = set()

                        # (1) MAIN dishes
                        fav_dishes_main: List[str] = []
                        for col_idx in cols["dish_cols_main"]:
                            cell = _row_get(row, col_idx)
                            if cell:
                                fav_dishes_main.extend(_split_multi(cell))
                        fav_dishes_main = list(dict.fromkeys(fav_dishes_main))

                        if not out_cypher:
                            rec_stat = session.run("""
                                MATCH (r:Recipe) WHERE r.rating_avg IS NOT NULL
                                RETURN avg(r.rating_avg) AS C, percentileCont(coalesce(r.review_count,0),0.5) AS p50
                            """).single()
                            C_global = rec_stat["C"]
                            m_global = rec_stat["p50"]
                        else:
                            # For Cypher generation, we'll skip recipe matching (too complex)
                            C_global = None
                            m_global = None

                        if not out_cypher:
                            for dish in fav_dishes_main:
                                results = pick_recipes(session, user_id, dish, C_global, m_global, mode="main", seen_global=seen_global)
                                for key, recipes in results:
                                    if recipes:
                                        pretty = "; ".join([f"{r['title']} (★ {r['rating']:.2f}, {r['reviews']} reviews)" for r in recipes])
                                        dish_logs.append(f"    - {dish}: {pretty}")
                                        picked_total += len(recipes)

                            # (2) EXTRA dishes
                            if cols["dish_col_extra"] != -1:
                                extra_cell = _row_get(row, cols["dish_col_extra"])
                                if extra_cell:
                                    for raw_dish in _split_multi(extra_cell):
                                        results = pick_recipes(session, user_id, raw_dish, C_global, m_global, mode="extra")
                                        for key, recipes in results:
                                            if recipes:
                                                pretty = "; ".join([f"{r['title']} (★ {r['rating']:.2f}, {r['reviews']} reviews)" for r in recipes])
                                                dish_logs.append(f"    - {key}: {pretty}")
                                                picked_total += len(recipes)

                            if dish_logs:
                                log_lines.append("  INTERACTED_WITH (auto-picked):")
                                log_lines.extend(dish_logs)
                                linked_recipes += picked_total
                            else:
                                log_lines.append("  (no valid dishes found)")
                        else:
                            # For Cypher generation, just log the dishes
                            if fav_dishes_main:
                                log_lines.append(f"  Favorite dishes (MAIN): {', '.join(fav_dishes_main)}")
                            if cols["dish_col_extra"] != -1:
                                extra_cell = _row_get(row, cols["dish_col_extra"])
                                if extra_cell:
                                    extra_dishes = _split_multi(extra_cell)
                                    if extra_dishes:
                                        log_lines.append(f"  Favorite dishes (EXTRA): {', '.join(extra_dishes)}")
                            
                        if verbose or idx % 10 == 0:
                            print("\n".join(log_lines))
                        
                    except Exception as e:
                        errors += 1
                        error_msg = str(e)
                        try:
                            error_msg_safe = error_msg.encode('ascii', errors='replace').decode('ascii')
                        except Exception:
                            error_msg_safe = error_msg
                        print(f"[ERROR] Row #{idx}: {error_msg_safe}")
                        if verbose:
                            traceback.print_exc()
            finally:
                if session:
                    session.close()
                        
    except Exception as e:
        print(f"[ERROR] Failed to process CSV: {e}")
        if verbose:
            traceback.print_exc()
        sys.exit(1)
    finally:
        if driver:
            driver.close()
        
        # Write Cypher file if requested
        if out_cypher:
            output_path = Path(out_cypher)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            output_path.write_text("\n".join(cypher_lines), encoding="utf-8")
            print(f"[OK] Generated Cypher file with {created_users} users")
            print(f"   File size: {output_path.stat().st_size / 1024:.1f} KB")
            print(f"   To import: Run this file in Neo4j Browser or use cypher-shell")
            print(f"   Example: cypher-shell.bat -a {uri} -u {user} -p 'password' -d {database or 'neo4j'} --file {output_path}")

    # Summary statistics
    total_time = time.time() - start_time
    print(f"\n[*] Import Summary:")
    print(f"  [OK] Successfully imported: {created_users} users")
    print(f"  [OK] Linked allergies: {linked_allergies}")
    print(f"  [OK] Linked cuisines: {linked_fav_cuisines}")
    print(f"  [OK] Linked recipes: {linked_recipes}")
    if errors > 0:
        print(f"  [ERROR] Errors: {errors}")
    print(f"  [*] Total processed: {created_users + errors} rows")
    print(f"  [*] Time taken: {total_time:.1f}s")
    if total_time > 0:
        print(f"  [*] Speed: {(created_users + errors) / total_time:.1f} rows/sec")
    
    if not out_cypher:
        # Verify import
        try:
            driver = GraphDatabase.driver(uri, auth=(user, password))
            with driver.session(database=database) as session:
                verify_query = "MATCH (u:User) WHERE u.user_id STARTS WITH 'survey_' RETURN count(u) AS count"
                result = session.run(verify_query)
                count = result.single()["count"]
                print(f"\n[*] Verification: {count} survey users in Neo4j database")
            driver.close()
        except Exception as e:
            if verbose:
                print(f"[WARNING] Could not verify import: {e}")



# ============================================================
#  ENTRY POINT
# ============================================================

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Import survey data from CSV into Neo4j"
    )
    parser.add_argument(
        "--csv",
        type=str,
        required=True,
        help="Path to CSV file containing survey data"
    )
    parser.add_argument(
        "--uri",
        type=str,
        default=DEFAULT_URI,
        help="Neo4j URI (default: %(default)s)"
    )
    parser.add_argument(
        "--user",
        type=str,
        default=DEFAULT_USER,
        help="Neo4j username (default: %(default)s)"
    )
    parser.add_argument(
        "--password",
        type=str,
        default=DEFAULT_PASS,
        help="Neo4j password (default: %(default)s)"
    )
    parser.add_argument(
        "--db",
        dest="database",
        type=str,
        default=DEFAULT_DB,
        help="Neo4j database name (default: %(default)s)"
    )
    parser.add_argument(
        "--out-cypher",
        type=str,
        default=None,
        help="Optional: Generate Cypher file instead of direct import"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print verbose output"
    )
    
    args = parser.parse_args()

    import_survey(
        args.csv,
        args.uri,
        args.user,
        args.password,
        args.database,
        verbose=args.verbose,
        out_cypher=args.out_cypher
    )
