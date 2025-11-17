#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tạo file JSON ingredients với canonical và variations theo 6 nhóm.

🎯 Mục tiêu:
- Gom các tên nguyên liệu về 1 canonical duy nhất
- Các biến thể được phân loại theo 6 nhóm: nutrition, cut_or_form, product, grade_style, variety, other
- Output JSON đơn giản, dễ sử dụng

Usage:
  python create_canonical_ingredients.py \
    --input data/process/ingredients.txt \
    --output data/process/canonical_ingredients.json
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Set
import sys
import os
import argparse

# Add backend directory to path to import config
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from config import NON_ING_WORDS, FIX_MAP, ALT_MAP

# Import from import_ingredients.py
import importlib.util
scripts_dir = os.path.join(backend_dir, 'scripts')
import_ingredients_path = os.path.join(scripts_dir, 'import_ingredients.py')
spec = importlib.util.spec_from_file_location("import_ingredients", import_ingredients_path)
import_ingredients = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_ingredients)
guess_category = import_ingredients.guess_category
generate_alt = import_ingredients.generate_alt
get_category_base_words = import_ingredients.get_category_base_words
get_base_group_to_category = import_ingredients.get_base_group_to_category


# ====================================================
# 1️⃣ Normalize & Clean - Build Canonical
# ====================================================
def contains_brand_name(name: str) -> bool:
    """
    Check if name contains any brand name.
    If it contains a brand name, the entire ingredient should be excluded.
    """
    # Brand names to check
    BRAND_LIST = [
        "argo", "mccormick", "hershey", "hershey's", "nestle", "ghirardelli", "domino",
        "c&h", "kikkoman", "lee kum kee", "mae ploy", "huy fong", "lao gan ma",
        "campbell", "campbell's", "swanson", "better than bouillon",
        "kraft", "philadelphia", "land o'lakes", "sargento", "tillamook", "darigold", "borden",
        "barilla", "hunt's", "del monte", "heinz", "progresso", "bush's",
        "quaker", "bob's red mill", "uncle ben's", "kellogg", "kellogg's",
        "skippy", "jif", "nutella", "smucker", "smucker's",
        "hellmann's", "best foods", "hidden valley", "wish-bone",
        "tabasco", "frank's redhot", "cholula", "texas pete",
        "bragg", "red star", "king arthur", "clorox",
        "betty crocker", "duncan hines", "eagle brand", "royal",
        "rotel", "old el paso", "pace", "ortega", "la victoria",
        "cabot", "président", "boursin",
        "sir kensington", "sir kensington's", "annie's", "soy vay", "valentina",
        "thai kitchen", "aroy-d", "squid", "pantai", "ajinomoto",
        "ocean spray", "libby", "libby's",
        "cool whip", "miracle whip", "crisco", "bisquick", "pam", "jello", "breakstone", "knorr",
        "baileys", "bertolli","cox's"
    ]
    
    name_lower = name.strip().lower()
    
    # Check for brand markers (®™©) - if present, likely a brand
    if re.search(r'[®™©]', name, flags=re.IGNORECASE):
        return True
    
    # Check multi-word brands first (longest first)
    multi_word_brands = [brand for brand in BRAND_LIST if ' ' in brand]
    multi_word_brands.sort(key=len, reverse=True)
    
    for brand in multi_word_brands:
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        if re.search(pattern, name_lower, flags=re.IGNORECASE):
            return True
    
    # Check single-word brands
    words = name_lower.split()
    for word in words:
        # Check exact match
        for brand in BRAND_LIST:
            if ' ' not in brand and word == brand.lower():
                return True
        # Check if word is likely a brand (all caps, short)
        if word.isupper() and len(word) <= 3:
            return True
    
    return False


def build_canonical(name: str) -> str:
    """
    Build canonical name from raw ingredient name.
    - Remove brand names
    - Remove packing phrases
    - Normalize and clean
    - Normalize plural to singular
    """
    # Brand names to remove
    BRAND_LIST = [
        "argo", "mccormick", "hershey", "hershey's", "nestle", "ghirardelli", "domino",
        "c&h", "kikkoman", "lee kum kee", "mae ploy", "huy fong", "lao gan ma",
        "campbell", "campbell's", "swanson", "better than bouillon",
        "kraft", "philadelphia", "land o'lakes", "sargento", "tillamook", "darigold", "borden",
        "barilla", "hunt's", "del monte", "heinz", "progresso", "bush's",
        "quaker", "bob's red mill", "uncle ben's", "kellogg", "kellogg's",
        "skippy", "jif", "nutella", "smucker", "smucker's",
        "hellmann's", "best foods", "hidden valley", "wish-bone",
        "tabasco", "frank's redhot", "cholula", "texas pete",
        "bragg", "red star", "king arthur", "clorox",
        "betty crocker", "duncan hines", "eagle brand", "royal",
        "rotel", "old el paso", "pace", "ortega", "la victoria",
        "cabot", "président", "boursin",
        "sir kensington", "sir kensington's", "annie's", "soy vay", "valentina",
        "thai kitchen", "aroy-d", "squid", "pantai", "ajinomoto",
        "ocean spray", "libby", "libby's",
        "cool whip", "miracle whip", "crisco", "bisquick", "pam", "jello", "breakstone", "knorr",
        "baileys", "bertolli"
    ]
    
    # Remove brand markers
    name = re.sub(r'\s*[®™©]\s*', ' ', name, flags=re.IGNORECASE)
    
    # Normalize first
    name = name.strip().lower()
    
    # Remove brand names (check multi-word first, then single-word)
    multi_word_brands = [brand for brand in BRAND_LIST if ' ' in brand]
    multi_word_brands.sort(key=len, reverse=True)  # Longest first
    
    for brand in multi_word_brands:
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove single-word brand names
    words = name.split()
    cleaned_words = []
    for word in words:
        is_brand = False
        for brand in BRAND_LIST:
            if ' ' not in brand and word == brand.lower():
                is_brand = True
                break
        if not is_brand:
            if word.isupper() and len(word) <= 3:
                continue
            if '®' in word or '™' in word or '©' in word:
                continue
            cleaned_words.append(word)
    
    name = ' '.join(cleaned_words)
    
    # Apply FIX_MAP
    if name in FIX_MAP:
        name = FIX_MAP[name]
    
    # Remove common packing/preparation phrases
    packing_patterns = [
        r'\bwell\s+drained\b',
        r'\bdrained\b',
        r'\brinsed?\b',
        r'\bpacked\s+in\s+(?:oil|water|brine|juice|syrup)\b',
        r'\bin\s+(?:oil|water|brine|juice|syrup)\b',
    ]
    for pattern in packing_patterns:
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Clean up spaces
    name = re.sub(r'\s+', ' ', name).strip()
    
    # Normalize common spelling mistakes
    # "leave" -> "leaf" (common typo)
    name = re.sub(r'\bleave\b', 'leaf', name, flags=re.IGNORECASE)
    
    # Normalize plural to singular (for the last word)
    category_base_words = get_category_base_words()
    words = name.split()
    if words:
        last_word = words[-1]
        if last_word not in category_base_words:
            original_last = last_word
            # Heuristic plural→singular
            if last_word.endswith("ies") and len(last_word) > 3:
                last_word = last_word[:-3] + "y"
            elif last_word.endswith("oes") and len(last_word) > 3:
                last_word = last_word[:-2]
            elif last_word.endswith(("ches", "shes", "xes")):
                last_word = last_word[:-2]
            elif last_word.endswith("ses") and len(last_word) > 3:
                last_word = last_word[:-2]
            elif last_word.endswith("les") and len(last_word) > 3:
                last_word = last_word[:-1]
            elif last_word.endswith("ves") and len(last_word) > 3:
                last_word = last_word[:-1]
            elif last_word.endswith("ges") and len(last_word) > 3:
                # Words ending in "ges" → "ge" (keep the "e")
                # Examples: "oranges" → "orange", "ranges" → "range", "changes" → "change"
                last_word = last_word[:-1]  # Remove only "s", keep "ge"
            elif last_word.endswith("ces") and len(last_word) > 3:
                # Words ending in "ces" → "ce" (keep the "e")
                # Examples: "faces" → "face", "places" → "place", "spaces" → "space"
                last_word = last_word[:-1]  # Remove only "s", keep "ce"
            elif last_word.endswith("es") and len(last_word) > 3:
                singular_es = last_word[:-2]
                if len(singular_es) >= 3:
                    last_word = singular_es
                else:
                    last_word = last_word[:-1]
            elif last_word.endswith("s") and len(last_word) > 1:
                singular = last_word[:-1]
                if len(singular) >= 2:
                    last_word = singular
            
            if last_word != original_last:
                words[-1] = last_word
                name = ' '.join(words)
    
    return name


# ====================================================
# 2️⃣ Extract Canonical Base Name
# ====================================================
def get_characteristic_words() -> Set[str]:
    """
    Get set of characteristic/attribute words (đặc điểm/tính chất).
    
    ✅ Những từ quyết định base canonical khi xuất hiện Ở CUỐI chuỗi.
    Ví dụ: chicken broth → broth, garlic oil → oil, apple juice → juice
    Ví dụ: bay leaf → leaf, curry leaf → leaf, mint leaf → leaf
    
    📌 Nhóm này không bao gồm spices riêng lẻ như pepper, cumin, paprika
    — vì nếu có "bell pepper" → canonical đúng là pepper, không phải "bell".
    """
    return {
        # Liquids / sauces / condiments
        "sauce", "paste", "puree", "marinade", "dressing", "gravy", "glaze",
        "oil", "juice", "broth", "stock", "soup", "milk", "cream",
        "butter", "yogurt", "mayonnaise", "ketchup", "mustard", "salsa",
        "chutney", "tahini", "pesto", "vinegar", "syrup", "molasses",
        
        # Extracts / concentrates
        "extract", "essence", "concentrate", "bouillon",
        
        # Dry powders / milled / baking base
        "flour", "starch", "meal", "powder",
        
        # Bread/cookie crumbs (vụn bánh mì, vụn bánh quy)
        "crumb", "crumbs",
        
        # Spices & seasoning blends (chỉ khi ở cuối)
        "seasoning", "spice", "rub", "masala", "curry",
        
        # Herbs (leaf form)
        "leaf", "leaves",
        
        # Herbs/flowers (blossom form)
        "blossom", "blossoms",
        
        # Beverages
        "wine", "beer", "cider", "coffee", "tea", "espresso", "liqueur", "vodka",
        "whiskey", "bourbon", "sake", "vermouth",
        
        # Misc categories
        "spread", "dip", "jam", "jelly", "marmalade"
    }


def extract_base_headword(name: str) -> str:
    """
    Extract base_headword (head ingredient) from name.
    
    📌 Luật cơ bản:
    - Nếu từ cuối = characteristic word (broth, sauce, oil, juice, etc.) 
      → base_headword = từ cuối
    - Ngược lại → base_headword = ingredient chính (meat, fruit, vegetable)
    
    Examples:
    - "chicken broth" → "broth" (characteristic word ở cuối)
    - "chicken breast" → "chicken" (không có characteristic word ở cuối)
    - "lemon juice" → "juice" (characteristic word ở cuối)
    - "fuji apple" → "apple" (fruit variety)
    - "dried cloud ear" → "cloud ear" or "ear" (skip "dried" preparation method)
    - "dried hibiscus blossom" → "hibiscus" or "blossom" (skip "dried")
    """
    characteristic_words = get_characteristic_words()
    category_base_words = get_category_base_words()
    
    name_lower = name.lower()
    words = name_lower.split()
    
    if not words:
        return name
    
    # Special handling: Skip preparation methods (CUT_OR_FORM_WORDS) at the beginning
    # Example: "dried cloud ear" → skip "dried", process "cloud ear"
    # Example: "fresh basil" → skip "fresh", process "basil"
    effective_words = words
    effective_name = name_lower
    
    if len(words) >= 2 and words[0] in CUT_OR_FORM_WORDS:
        # Skip first word if it's a preparation method
        effective_words = words[1:]
        effective_name = ' '.join(effective_words)
    
    if not effective_words:
        # If all words were preparation methods, return original last word
        return words[-1]
    
    # Priority 1: Check if last word is characteristic word
    # If so, canonical = last word (broth, sauce, oil, etc.)
    if effective_words[-1] in characteristic_words:
        return effective_words[-1]
    
    # Priority 2: Check if any word is characteristic word
    # (Handle cases where characteristic word is not last)
    for word in reversed(effective_words):
        if word in characteristic_words:
            return word
    
    # Priority 3: Multi-word phrases from category base words
    multi_word_phrases = [w for w in category_base_words if ' ' in w]
    multi_word_phrases.sort(key=len, reverse=True)
    
    for phrase in multi_word_phrases:
        pattern = r'\b' + re.escape(phrase) + r'\b'
        if re.search(pattern, effective_name):
            return phrase
    
    # Priority 4: Single words from category base words (meat, fruit, vegetable)
    # Special case: If "cheese" appears in the name, prioritize it as base_headword
    # This ensures "cheese ravioli" → "cheese" (not "ravioli")
    # This ensures "cheese pizza" → "cheese" (not "pizza")
    # This ensures "cheese dumpling" → "cheese" (not "dumpling")
    if "cheese" in effective_words:
        return "cheese"
    
    # Check last word first (most common case: "fuji apple" → "apple")
    if effective_words[-1] in category_base_words:
        return effective_words[-1]
    
    # Check other words from right to left
    for word in reversed(effective_words[:-1] if effective_words else []):
        if word in category_base_words:
            return word
    
    # Priority 5: For multi-word phrases (after skipping preparation method),
    # first try the full phrase, but if it doesn't exist, use first word as fallback
    # Example: "cloud ear" → try "cloud ear", if not exists → "cloud"
    # Example: "hibiscus blossom" → try "hibiscus blossom", if not exists → "hibiscus"
    if len(effective_words) >= 2:
        # Return the full phrase as base (e.g., "cloud ear", "hibiscus blossom")
        # This allows "dried cloud ear" to group under "cloud ear" if it exists
        # But if "cloud ear" doesn't exist, the logic will fall back to first word "cloud"
        return ' '.join(effective_words)
    
    # Priority 6: Last word as fallback (usually main ingredient)
    return effective_words[-1]


# ====================================================
# 3️⃣ Variation Classification - 7 Groups
# ====================================================
def normalize_variation(text: str) -> str:
    """Normalize variation text for matching."""
    t = text.lower().replace("-", " ").strip()
    return re.sub(r"\s+", " ", t)


# Nutrition patterns
NUTRITION_PATTERNS = [
    "skim", "nonfat", "no fat", "fat free", "low fat", "reduced fat",
    "low sodium", "no salt", "salt free", "sodium free", "reduced sodium",
    "low sugar", "no sugar", "sugar free", "reduced sugar",
    "unsalted", "light", "diet", "reduced", "low", "non", "no-", "no "
]

# Cut or form patterns
CUT_OR_FORM_WORDS = {
    "chop", "strip", "strips", "fillet", "filet", "ground", "minced",
    "boneless", "skinless", "drumstick", "drumette", "leg", "loin", "rib",
    "thigh", "breast", "tenderloin", "wing", "rack", "shank", "shoulder",
    "brisket", "cutlet", "roast", "sliced", "diced", "cubed", "shredded",
    "grated", "crushed", "whole", "halves", "halved", "fillets", "cubes",
    "cracked",  # preparation method: cracked pepper, cracked wheat
    "dried", "fresh", "frozen", "smoked", "roasted", "pickled", "canned"  # preparation methods/state indicators
}

# Flavor source patterns (for broth, stock, sauce with flavor source)
# These are ingredients that modify flavor: chicken broth, beef stock, mushroom stock
FLAVOR_SOURCE_INDICATORS = {
    "chicken", "beef", "pork", "lamb", "turkey", "duck", "fish",
    "vegetable", "mushroom", "bone", "demi-glace", "demi glace"
}

# Product patterns (processed products)
PRODUCT_WORDS = {
    "sausage", "ham", "nugget", "jerky", "bacon", "stock cube", "bouillon cube",
    "nuggets", "pastrami", "salami", "chorizo", "hotdog", "hot dog",
    # Cheese-based products
    "ravioli", "dumpling", "dumplings", "wonton", "wontons", "pizza", "quesadilla",
    "enchilada", "enchiladas", "taco", "tacos", "burrito", "burritos"
}

# Grade/style patterns
GRADE_STYLE_PATTERNS = [
    "extra virgin", "virgin", "refined", "cold pressed", "first press",
    "pure", "light", "whole", "organic", "conventional",
    "dark", "semisweet", "bittersweet", "sweet", "milk chocolate", "white chocolate",
    "unsweetened", "all-purpose", "all purpose", "ap"
]

# Variety patterns (specific varieties)
# Những từ giúp nhận biết biến thể theo giống / loại / đặc tính (không phải canonical riêng)
VARIETY_WORDS = {
    # Fruit varieties
    "fuji", "gala", "granny smith", "braeburn", "braeburn apple",
    "roma", "honeycrisp", "jonagold", "castelvetrano",
    "amarena", "bing", "morello",
    
    # Pepper & spice varieties - Hotness / heat level
    "hot", "mild", "sweet", "extra hot",
    
    # Pepper & spice varieties - Color
    "green", "red", "yellow", "orange", "purple", "black", "white",
    
    # Pepper varieties / cultivars
    "poblano", "serrano", "habanero", "jalapeno", "jalapeño", "fresno",
    "anaheim", "pasilla", "ghost", "carolina reaper", "thai", "scotch bonnet",
    "aleppo", "padron", "piquillo", "bird's eye", "birds eye", "bell",
    
    # Countries / origin-based spice naming
    "sichuan", "korean", "mexican", "spanish", "turkish", "indian",
    
    # Spice state type
    "smoked", "roasted", "pickled", "dried", "fresh", "ground"
}

# Characteristic words that can have flavor_source variations
FLAVOR_ACCEPTING_WORDS = {
    "broth", "stock", "sauce", "gravy", "juice", "milk", "cream",
    "demi-glace", "demi glace", "consommé", "consomme", "bouillon"
}


def classify_variation(variation: str, canonical_base: str, category: str) -> Optional[str]:
    """
    Classify variation into one of 7 groups:
    - flavor_source: chicken broth, beef broth, mushroom stock (flavor modifier)
    - nutrition: skim, nonfat, low sodium, etc.
    - cut_or_form: chop, strip, fillet, ground, etc.
    - product: sausage, ham, nugget, etc.
    - grade_style: extra virgin, refined, organic, etc.
    - variety: fuji apple, gala apple, etc.
    - other: everything else (returns None to be put in "other")
    
    Important: If canonical_base is a characteristic word (broth, sauce, etc.),
    and variation contains a flavor source (chicken, beef, vegetable, etc.),
    classify as "flavor_source".
    """
    n = normalize_variation(variation)
    n_lower = n.lower()
    tokens = set(n.split())
    
    # 1. Check flavor_source FIRST (highest priority for characteristic words)
    # If canonical_base is a characteristic word (broth, sauce, etc.)
    # and variation contains flavor source indicator, classify as flavor_source
    if canonical_base in FLAVOR_ACCEPTING_WORDS:
        for flavor_word in FLAVOR_SOURCE_INDICATORS:
            pattern = r'\b' + re.escape(flavor_word.lower()) + r'\b'
            if re.search(pattern, n_lower):
                return "flavor_source"
    
    # 2. Check nutrition patterns
    for pattern in NUTRITION_PATTERNS:
        pattern_lower = pattern.lower().strip()
        if ' ' in pattern_lower:
            if pattern_lower in n_lower:
                return "nutrition"
        elif '-' in pattern_lower:
            pattern_escaped = re.escape(pattern_lower)
            if re.search(r'\b' + pattern_escaped + r'|' + pattern_escaped, n_lower):
                return "nutrition"
        else:
            pattern_escaped = re.escape(pattern_lower)
            if re.search(r'\b' + pattern_escaped + r'\b', n_lower):
                return "nutrition"
    
    # 3. Check cut_or_form
    if any(word in tokens for word in CUT_OR_FORM_WORDS):
        return "cut_or_form"
    
    # Also check if variation contains cut words as phrases
    for word in CUT_OR_FORM_WORDS:
        if ' ' not in word:
            pattern = r'\b' + re.escape(word) + r'\b'
            if re.search(pattern, n_lower):
                return "cut_or_form"
    
    # 4. Check product
    if any(word in tokens for word in PRODUCT_WORDS):
        return "product"
    
    for word in PRODUCT_WORDS:
        pattern = r'\b' + re.escape(word) + r'\b'
        if re.search(pattern, n_lower):
            return "product"
    
    # 5. Check grade_style
    for pattern in GRADE_STYLE_PATTERNS:
        pattern_lower = pattern.lower().strip()
        if ' ' in pattern_lower:
            if pattern_lower in n_lower:
                return "grade_style"
        else:
            pattern_escaped = re.escape(pattern_lower)
            if re.search(r'\b' + pattern_escaped + r'\b', n_lower):
                return "grade_style"
    
    # 6. Check variety (specific variety names)
    # Color words that indicate variety
    color_words = {"green", "red", "yellow", "orange", "purple", "black", "white", "blue", "pink", "brown"}
    
    # Check for fruit/vegetable/herb varieties
    # Colors are common variety indicators for vegetables, fruits, and herbs
    if category in ("fruit", "vegetable", "herb") or canonical_base in ("apple", "cherry", "olive", "tomato", "onion", "squash", "chive", "pepper", "bell pepper"):
        for variety in VARIETY_WORDS:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(variety.lower()) + r'\b'
            if re.search(pattern, n_lower):
                return "variety"
        
        # Also check for color words as variety indicators
        for color in color_words:
            pattern = r'\b' + re.escape(color.lower()) + r'\b'
            if re.search(pattern, n_lower):
                return "variety"
    
    # Check for pepper/spice varieties
    # Variety words for pepper & spices: bell, green, red, jalapeno, poblano, etc.
    pepper_spice_base_words = {"pepper", "chili", "chile", "spice", "cumin", "paprika", "cayenne"}
    if canonical_base in pepper_spice_base_words or category == "seasoning" or "pepper" in n_lower or "chili" in n_lower or "chile" in n_lower:
        for variety in VARIETY_WORDS:
            # Use word boundary matching for better accuracy
            pattern = r'\b' + re.escape(variety.lower()) + r'\b'
            if re.search(pattern, n_lower):
                return "variety"
        
        # Also check for color words as variety indicators for spices/seasonings
        for color in color_words:
            pattern = r'\b' + re.escape(color.lower()) + r'\b'
            if re.search(pattern, n_lower):
                return "variety"
    
    # General check: If variation contains a color word, likely a variety
    # This catches cases where category might not be detected correctly
    for color in color_words:
        pattern = r'\b' + re.escape(color.lower()) + r'\b'
        if re.search(pattern, n_lower):
            # But only if it's not already classified and base is a common ingredient
            common_ingredients = {"onion", "squash", "chive", "pepper", "bell pepper", "apple", "cherry", 
                                 "tomato", "potato", "carrot", "celery", "lettuce", "cabbage", "miso"}
            if canonical_base in common_ingredients or category in ("fruit", "vegetable", "herb", "condiment"):
                return "variety"
    
    # 7. Return None for "other" (will be handled by caller)
    return None


# ====================================================
# 4️⃣ Find Parent (Group Variations)
# ====================================================
# Blacklist: Ingredients that should NOT be treated as variations of base ingredients
# These are special cases that should remain as separate ingredients
FALSE_VARIATION_EXCEPTIONS = {
    # Synonym mappings (MUST KEEP - map to different canonical)
    "spring onion": "green onion",
    "scallion": "green onion",
    "pepper jack": "cheese",  # canonical khác (cheese, not pepper)
    
    # Target canonicals for synonyms (KEEP as targets)
    "green onion": "green onion",
    
    # Multi-word ingredients (MUST KEEP to prevent wrong grouping during JSON creation)
    "sweet potato": "sweet potato",  # prevent grouping as variation of "potato"
    "water chestnut": "water chestnut",  # prevent grouping as variation of "chestnut"
    "horse chestnut": "horse chestnut",  # prevent grouping as variation of "chestnut"
    "soy sauce": "soy sauce",  # prevent grouping as variation of "sauce"
    
    # Special single-word cases
    "pumpkin": "pumpkin",
    "galangal": "galangal",
    
    # NOTE: Don't add "bell pepper", "black pepper", "cayenne pepper" here
    # → They are properly created as canonicals AND runtime matching uses should_skip_single_word_for_multiword()
}

# Color words that, when appearing as the first word, indicate a separate ingredient
# (not a variation of the base ingredient)
COLOR_FIRST_EXCEPTIONS = {"green", "red", "yellow", "orange", "purple", "black", "white", "brown", "pink"}

def find_parent_canonical(name: str, existing_canonicals: Dict[str, dict], current_category: Optional[str] = None) -> Optional[str]:
    """
    Improved parent detection:
    - For modifier-before-ingredient patterns (e.g., "sea salt", "kosher salt"):
      Check if last word is base ingredient and exists as canonical → use as parent
    - For modifier-after-ingredient patterns (e.g., "chicken breast", "chicken thigh"):
      Check if first word exists as canonical → use as parent
    - Avoid false matches like:
        pepper sauce → parent = sauce (not pepper)
        pepper jack → parent = cheese (not pepper)
        curry leaf (herb) → parent = curry (seasoning) → NO MATCH (category mismatch)
        sweet potato → NO MATCH (blacklist - should be separate ingredient)
        bell pepper → NO MATCH (blacklist - should be separate ingredient)
    
    Returns: canonical_name của parent, hoặc None nếu không tìm thấy.
    """
    name_lower = name.lower().strip()
    
    # Check blacklist FIRST - these should NOT be variations of base ingredients
    # Example: "sweet potato" should NOT be variation of "potato"
    if name_lower in FALSE_VARIATION_EXCEPTIONS:
        # If in blacklist, check if it should map to a different canonical
        target_canonical = FALSE_VARIATION_EXCEPTIONS[name_lower]
        if target_canonical != name_lower and target_canonical in existing_canonicals:
            # Special case: map to different canonical (e.g., "pepper jack" → "cheese")
            return target_canonical
        # Otherwise, don't match with any parent (will be separate ingredient)
        return None
    
    words = name.lower().split()
    if not words:
        return None
    
    # Check if first word is a color - if so, don't group as variation
    # Example: "green onion" should NOT be variation of "onion"
    # Example: "red pepper" should NOT be variation of "pepper"
    first_word = words[0]
    if first_word in COLOR_FIRST_EXCEPTIONS:
        return None  # Không gom làm variation → giữ canonical riêng
    
    characteristic_words = get_characteristic_words()
    category_base_words = get_category_base_words()
    
    # Herb indicators (words that indicate an herb, not a spice/seasoning)
    herb_indicators = {"leaf", "leaves", "blossom", "blossoms", "herb"}
    
    # Helper function to check if categories are compatible
    def are_categories_compatible(cat1: str, cat2: str) -> bool:
        """Check if two categories are compatible (can be variations of each other)"""
        if cat1 == cat2:
            return True
        
        # Incompatible categories (should not be variations)
        incompatible_pairs = [
            ("herb", "seasoning"),
            ("herb", "spice"),
            ("vegetable", "seasoning"),
            ("fruit", "seasoning"),
        ]
        
        for pair in incompatible_pairs:
            if (cat1 in pair and cat2 in pair):
                return False
        
        return True
    
    # Case 1: If second word is characteristic → do NOT match parent
    # Example: "pepper sauce" → words[1] = "sauce" (characteristic) → return None
    # This prevents "pepper sauce" from matching parent "pepper"
    if len(words) >= 2 and words[1] in characteristic_words:
        return None
    
    # Case 2: If last word is a base ingredient AND exists as canonical → likely parent
    # Example: "sea salt" → words[-1] = "salt" (base ingredient) → if "salt" in existing_canonicals → return "salt"
    # Example: "kosher salt" → words[-1] = "salt" → return "salt"
    # Example: "black pepper" → words[-1] = "pepper" (base ingredient) → return "pepper"
    # Example: "dried chive" → words[-1] = "chive" → if "chive" in existing_canonicals → return "chive"
    # Example: "dried wheat" → words[-1] = "wheat" → if "wheat" in existing_canonicals → return "wheat"
    if len(words) >= 2:  # Only check last word if there are multiple words
        last_word = words[-1]
        
        # Check if last word exists as canonical (preferred method)
        # This works even if last_word is not in category_base_words
        if last_word in existing_canonicals:
            # Skip if last word is a cut/form word (e.g., "ground", "sliced", "dried", "cracked")
            # These are preparation methods, not base ingredients
            if last_word in CUT_OR_FORM_WORDS:
                pass  # Don't use cut/form words as parent, continue to next case
            else:
                parent_ing = existing_canonicals[last_word]
                parent_category = parent_ing.get("category", "other")
                # Check category compatibility
                if current_category and not are_categories_compatible(current_category, parent_category):
                    return None
                return last_word
        
        # Fallback: Also check if last word is in category_base_words
        # (for known base ingredients that might not be in existing_canonicals yet)
        if last_word in category_base_words and last_word in existing_canonicals:
            parent_ing = existing_canonicals[last_word]
            parent_category = parent_ing.get("category", "other")
            # Check category compatibility
            if current_category and not are_categories_compatible(current_category, parent_category):
                return None
            return last_word
    
    # Case 3: If first word exists as canonical → likely parent
    # Example: "chicken breast" → words[0] = "chicken" → if "chicken" in existing_canonicals → return "chicken"
    # BUT: If last word is herb indicator (leaf, leaves), do NOT match with seasoning/spice
    # Example: "curry leaf" → words[-1] = "leaf" (herb indicator) → do NOT match "curry" (seasoning)
    # Special handling: Skip ALL preparation methods at the start (e.g., "skinless boneless chicken leg")
    # Example: "dried coconut flak" → words[0] = "dried" (CUT_OR_FORM_WORDS) → check "coconut flak" or "coconut"
    # Example: "dried cloud ear" → words[0] = "dried" → check "cloud ear" (multi-word phrase)
    # Example: "skinless boneless chicken leg" → skip "skinless", "boneless" → check "chicken" or "chicken leg"
    
    # Skip ALL preparation methods at the start (can have multiple: "skinless boneless chicken")
    skip_count = 0
    for word in words:
        if word in CUT_OR_FORM_WORDS:
            skip_count += 1
        else:
            break  # Stop at first non-prep word
    
    # Determine ingredient core after skipping preparation methods
    if skip_count > 0 and skip_count < len(words):
        # After skipping prep methods, check remaining phrase
        remaining_words = words[skip_count:]
        if remaining_words:
            ingredient_core = remaining_words[0]  # e.g., "chicken" in "skinless boneless chicken leg"
            # Also try multi-word phrase after prep (e.g., "chicken leg")
            if len(remaining_words) >= 2:
                phrase_after_prep = ' '.join(remaining_words)  # e.g., "chicken leg"
            else:
                phrase_after_prep = None
        else:
            ingredient_core = words[0]  # Fallback: use first word
            phrase_after_prep = None
    else:
        # No prep methods to skip
        ingredient_core = words[0]  # first word e.g., "chicken" in "chicken breast"
        phrase_after_prep = None  # multi-word phrase after skipping preparation method
    
    # Also check original first word if it's a canonical (before skipping prep methods)
    # This handles cases like "chicken breast" where first word is already the ingredient
    if words[0] in existing_canonicals and words[0] not in CUT_OR_FORM_WORDS:
        parent_ing = existing_canonicals[words[0]]
        parent_category = parent_ing.get("category", "other")
        
        # Skip herb/seasoning mismatch check for now, will check in final return
        
        # Check category compatibility
        if not current_category or are_categories_compatible(current_category, parent_category):
            # Additional check: make sure it's not a false match
            # For example, "pepper sauce" should not match "pepper" if "sauce" is characteristic
            if len(words) >= 2 and words[1] in characteristic_words:
                pass  # Skip this match, continue to check phrase_after_prep
            else:
                # Check herb/seasoning mismatch
                is_current_herb = False
                if current_category == "herb":
                    is_current_herb = True
                elif len(words) >= 2 and words[-1] in herb_indicators:
                    is_current_herb = True
                
                if not (is_current_herb and parent_category in ("seasoning", "spice")):
                    if len(words) >= 2 and words[-1] not in herb_indicators or parent_category not in ("seasoning", "spice"):
                        return words[0]
    
    # First try multi-word phrase if exists (after skipping preparation method)
    if phrase_after_prep and phrase_after_prep in existing_canonicals:
        parent_ing = existing_canonicals[phrase_after_prep]
        parent_category = parent_ing.get("category", "other")
        
        # Check category compatibility
        if current_category and not are_categories_compatible(current_category, parent_category):
            return None
        return phrase_after_prep
    
    # Then try single word (ingredient_core)
    if ingredient_core in existing_canonicals:
        parent_ing = existing_canonicals[ingredient_core]
        parent_category = parent_ing.get("category", "other")
        
        # Special check 1: If current is herb (by category or by herb indicator), avoid matching with seasoning/spice
        is_current_herb = False
        if current_category == "herb":
            is_current_herb = True
        elif len(words) >= 2 and words[-1] in herb_indicators:
            is_current_herb = True
        
        if is_current_herb and parent_category in ("seasoning", "spice"):
            return None  # Do NOT match herb with seasoning/spice
        
        # Special check 2: If last word is herb indicator, avoid matching with seasoning/spice
        if len(words) >= 2 and words[-1] in herb_indicators:
            if parent_category in ("seasoning", "spice"):
                return None
        
        # Check category compatibility
        if current_category and not are_categories_compatible(current_category, parent_category):
            return None
        return ingredient_core
    
    # Case 3.5: Find ANY word in the name that is a canonical (after skipping prep methods)
    # This handles cases like "skinless boneless chicken leg" → find "chicken"
    # Check each word in the name (after skipping prep methods) to see if it's a canonical
    non_prep_words = [w for w in words if w not in CUT_OR_FORM_WORDS]
    
    # Also exclude cut/form words that are likely at the end (like "leg", "breast", "thigh")
    # But keep base ingredients (like "chicken", "beef", "pork")
    for word in non_prep_words:
        # Skip if it's a cut/form word at the end (like "leg" in "chicken leg")
        # But only if it's at the end and not a known base ingredient
        if word == words[-1] and word in CUT_OR_FORM_WORDS and word not in category_base_words:
            continue
        
        # If this word is a canonical, it's likely the parent
        if word in existing_canonicals:
            parent_ing = existing_canonicals[word]
            parent_category = parent_ing.get("category", "other")
            
            # Check category compatibility
            if current_category and not are_categories_compatible(current_category, parent_category):
                continue
            
            # Check herb/seasoning mismatch
            is_current_herb = False
            if current_category == "herb":
                is_current_herb = True
            elif len(words) >= 2 and words[-1] in herb_indicators:
                is_current_herb = True
            
            if is_current_herb and parent_category in ("seasoning", "spice"):
                continue
            
            if len(words) >= 2 and words[-1] in herb_indicators:
                if parent_category in ("seasoning", "spice"):
                    continue
            
            # Found a match!
            return word
    
    # Case 4 fallback: find substring canonical only if at start AND followed by shape/cut word
    # Sort by length (longest first) để match chính xác nhất
    sorted_canonicals = sorted(existing_canonicals.keys(), key=len, reverse=True)
    name_lower = name.lower()
    
    for canonical in sorted_canonicals:
        canonical_lower = canonical.lower()
        # Check if canonical appears at the start of the name (word boundary)
        pattern = r'^' + re.escape(canonical_lower) + r'\b'
        if re.search(pattern, name_lower):
            parent_ing = existing_canonicals[canonical]
            parent_category = parent_ing.get("category", "other")
            
            # Special check 1: If current is herb (by category or by herb indicator), avoid matching with seasoning/spice
            is_current_herb = False
            if current_category == "herb":
                is_current_herb = True
            elif len(words) >= 2 and words[-1] in herb_indicators:
                is_current_herb = True
            
            if is_current_herb and parent_category in ("seasoning", "spice"):
                continue  # Do NOT match herb with seasoning/spice
            
            # Special check 2: If last word is herb indicator, avoid matching with seasoning/spice
            if len(words) >= 2 and words[-1] in herb_indicators:
                if parent_category in ("seasoning", "spice"):
                    continue  # Try next canonical
            
            # Check category compatibility
            if current_category and not are_categories_compatible(current_category, parent_category):
                continue  # Try next canonical
            return canonical
    
    return None


# ====================================================
# 4.5️⃣ Generate Alt Names
# ====================================================
def generate_alt_names(canonical_name: str) -> List[str]:
    """
    Generate alternative names for an ingredient.
    Includes:
    1. Plural/singular forms
    2. Synonyms from ALT_MAP
    3. Variants with/without spaces (e.g., "breadcrumb" vs "bread crumb")
    
    Examples:
    - "bread crumb" → ["breadcrumbs", "breadcrumb", "bread crumbs", "breadcrumb"]
    - "egg" → ["eggs"]
    - "tomato" → ["tomatoes"] + ALT_MAP synonyms
    """
    alt_names = set()  # Use set to avoid duplicates
    name_lower = canonical_name.lower().strip()
    
    # 1. Check ALT_MAP first for synonyms
    if name_lower in ALT_MAP:
        for synonym in ALT_MAP[name_lower]:
            if synonym and synonym.lower() != name_lower:
                alt_names.add(synonym.lower())
    
    # 2. Generate plural/singular forms
    words = name_lower.split()
    
    # Handle single word
    if len(words) == 1:
        word = words[0]
        
        # Detect compound words and generate space variants
        # Common compound words: breadcrumb, cookiecrumb, hotdog, etc.
        # Try to split compound words into two parts
        common_first_parts = {
            "bread", "cookie", "hot", "bell", "sweet", "black", "white", "green", 
            "red", "yellow", "water", "horse", "cayenne", "sea", "kosher", "table",
            "bay", "curry", "mint", "basil", "hibiscus", "cloud", "bamboo", "soybean",
            "alfalfa", "brussels", "turnip", "collard", "dandelion", "spring"
        }
        
        # Try to split compound word (e.g., "breadcrumb" → "bread" + "crumb")
        for first_part in sorted(common_first_parts, key=len, reverse=True):  # Longest first
            if word.startswith(first_part) and len(word) > len(first_part):
                # Potential compound word found
                remaining = word[len(first_part):]
                if len(remaining) >= 3:  # Make sure remaining part is meaningful
                    # Create spaced variant: "breadcrumb" → "bread crumb"
                    spaced_variant = first_part + " " + remaining
                    alt_names.add(spaced_variant)
                    
                    # Also generate plural forms for spaced variant
                    # Helper to pluralize last word
                    def quick_pluralize(w: str) -> str:
                        if w.endswith("y") and len(w) > 1:
                            return w[:-1] + "ies"
                        elif w.endswith(("x", "ch", "sh", "s", "z")):
                            return w + "es"
                        elif w.endswith("f"):
                            return w[:-1] + "ves"
                        elif w.endswith("fe"):
                            return w[:-2] + "ves"
                        elif not w.endswith("s"):
                            return w + "s"
                        return w
                    
                    # Pluralize last word in spaced variant
                    spaced_words = spaced_variant.split()
                    if len(spaced_words) >= 2:
                        plural_last = quick_pluralize(spaced_words[-1])
                        if plural_last != spaced_words[-1]:
                            spaced_plural = " ".join(spaced_words[:-1] + [plural_last])
                            alt_names.add(spaced_plural)
                    
                    break  # Only match once (longest match)
        
        # Generate plural form
        if word.endswith("y") and len(word) > 1:
            plural = word[:-1] + "ies"
            alt_names.add(plural)
        elif word.endswith(("x", "ch", "sh", "s", "z")):
            # Words ending in x, ch, sh, s, z → add "es"
            plural = word + "es"
            alt_names.add(plural)
        elif word.endswith("f"):
            # Words ending in f → replace with "ves" (e.g., "leaf" → "leaves")
            # NOT "leafs" or "leafes" - this is a special rule in English
            plural = word[:-1] + "ves"
            alt_names.add(plural)
            # Also add common misspellings: "leafs", "leafes" for better matching
            # (Some people might write "leafs" incorrectly)
            alt_names.add(word + "s")  # "leafs" (common misspelling)
            alt_names.add(word + "es")  # "leafes" (less common misspelling)
        elif word.endswith("fe"):
            # Words ending in fe → replace with "ves" (e.g., "knife" → "knives")
            # NOT "knifes" or "knifes"
            plural = word[:-2] + "ves"
            alt_names.add(plural)
            # Also add common misspelling: "knifes" for better matching
            alt_names.add(word + "s")  # "knifes" (common misspelling)
        elif not word.endswith("s"):
            # Regular plural: just add "s"
            plural = word + "s"
            alt_names.add(plural)
        else:
            # Already plural, generate singular
            if word.endswith("ies"):
                singular = word[:-3] + "y"
                alt_names.add(singular)
            elif word.endswith("ches") or word.endswith("shes") or word.endswith("xes"):
                singular = word[:-2]
                alt_names.add(singular)
            elif word.endswith("ges") and len(word) > 3:
                # Words ending in "ges" → "ge" (keep the "e")
                # Examples: "oranges" → "orange"
                singular = word[:-1]  # Remove only "s", keep "ge"
                alt_names.add(singular)
            elif word.endswith("ces") and len(word) > 3:
                # Words ending in "ces" → "ce" (keep the "e")
                # Examples: "faces" → "face"
                singular = word[:-1]  # Remove only "s", keep "ce"
                alt_names.add(singular)
            elif word.endswith("ves"):
                # Words ending in "ves" can come from "f" or "fe" endings
                # e.g., "leaves" → "leaf", "knives" → "knife"
                singular_f = word[:-3] + "f"
                singular_fe = word[:-3] + "fe"
                alt_names.add(singular_f)  # "leaves" → "leaf"
                alt_names.add(singular_fe)  # "knives" → "knife"
                # Note: Most "ves" words come from "f" (leaf → leaves, wolf → wolves)
                # But some come from "fe" (knife → knives, life → lives)
                # We add both to catch all cases
            elif word.endswith("es") and len(word) > 2:
                singular = word[:-2]
                alt_names.add(singular)
            elif word.endswith("s") and len(word) > 1:
                singular = word[:-1]
                alt_names.add(singular)
    
    # 3. Handle multi-word phrases: generate space/no-space variants
    # Example: "bread crumb" → "breadcrumb", "breadcrumbs", "bread crumbs"
    # Example: "cookie crumb" → "cookiecrumb", "cookiecrumbs", "cookie crumbs"
    if len(words) >= 2:
        # Helper function to pluralize a word
        def pluralize_word(word: str) -> str:
            """Pluralize a word based on common rules."""
            if word.endswith("y") and len(word) > 1:
                return word[:-1] + "ies"
            elif word.endswith(("x", "ch", "sh", "s", "z")):
                return word + "es"
            elif word.endswith("f"):
                # Words ending in "f" → "ves" (e.g., "leaf" → "leaves")
                # NOT "leafs" or "leafes"
                return word[:-1] + "ves"
            elif word.endswith("fe"):
                # Words ending in "fe" → "ves" (e.g., "knife" → "knives")
                # NOT "knifes"
                return word[:-2] + "ves"
            elif not word.endswith("s"):
                return word + "s"
            else:
                return word  # Already plural
        
        # Helper function to singularize a word
        def singularize_word(word: str) -> str:
            """Singularize a word based on common rules."""
            if word.endswith("ies") and len(word) > 3:
                return word[:-3] + "y"
            elif word.endswith(("ches", "shes", "xes")):
                return word[:-2]
            elif word.endswith("ges") and len(word) > 3:
                # Words ending in "ges" → "ge" (keep the "e")
                # Examples: "oranges" → "orange"
                return word[:-1]  # Remove only "s", keep "ge"
            elif word.endswith("ces") and len(word) > 3:
                # Words ending in "ces" → "ce" (keep the "e")
                # Examples: "faces" → "face"
                return word[:-1]  # Remove only "s", keep "ce"
            elif word.endswith("ves") and len(word) > 3:
                # Try both "f" and "fe" endings
                return word[:-3] + "f"  # Default to "f"
            elif word.endswith("es") and len(word) > 2:
                return word[:-2]
            elif word.endswith("s") and len(word) > 1:
                return word[:-1]
            else:
                return word  # Already singular or can't determine
        
        last_word = words[-1]
        
        # Variant without spaces (compound word)
        no_space = "".join(words)
        alt_names.add(no_space)
        
        # Pluralize last word for both spaced and no-space versions
        plural_last = pluralize_word(last_word)
        
        # Spaced plural (e.g., "bread crumbs")
        if plural_last != last_word:
            plural_spaced = " ".join(words[:-1] + [plural_last])
            alt_names.add(plural_spaced)
        
        # No-space plural (e.g., "breadcrumbs")
        if plural_last != last_word:
            plural_no_space = "".join(words[:-1] + [plural_last])
            alt_names.add(plural_no_space)
        
        # If last word is already plural, also generate singular variants
        if last_word.endswith("s"):
            singular_last = singularize_word(last_word)
            if singular_last != last_word:
                # Spaced singular (e.g., "bread crumb" from "bread crumbs")
                singular_spaced = " ".join(words[:-1] + [singular_last])
                alt_names.add(singular_spaced)
                
                # No-space singular (e.g., "breadcrumb" from "breadcrumbs")
                singular_no_space = "".join(words[:-1] + [singular_last])
                alt_names.add(singular_no_space)
    
    # 4. For words with spaces, also try removing spaces and pluralizing
    # Example: "bread crumb" → "breadcrumb", then plural → "breadcrumbs"
    # (Already handled above in step 3)
    
    # Remove the original name from alt_names (shouldn't be in alt_names)
    alt_names.discard(name_lower)
    alt_names.discard(canonical_name.lower().strip())
    
    # Filter out invalid names
    valid_alt_names = []
    for alt in alt_names:
        alt_clean = alt.strip()
        if alt_clean and len(alt_clean) >= 2:
            # Skip if it's just a number or very short
            if not re.fullmatch(r"[0-9\.]+", alt_clean):
                valid_alt_names.append(alt_clean)
    
    return sorted(valid_alt_names)  # Return sorted list for consistency


# ====================================================
# 5️⃣ Main Processing
# ====================================================
def process_ingredients_from_file(input_path: Path) -> List[dict]:
    """
    Process ingredients from input file.
    Returns list of ingredient objects with canonical names and variations grouped.
    """
    # Read all lines
    lines = [l.strip() for l in input_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    
    # Step 1: Build canonical names
    canonical_to_raw = defaultdict(list)
    for raw_name in lines:
        # Skip if ingredient contains brand name - exclude completely
        if contains_brand_name(raw_name):
            continue
        
        canonical = build_canonical(raw_name)
        if not canonical or len(canonical) < 2:
            continue
        if canonical in NON_ING_WORDS:
            continue
        if re.fullmatch(r"[0-9\.]+", canonical):
            continue
        if canonical.endswith(("ed", "ing", "ly", "ness")):
            continue
        canonical_to_raw[canonical].append(raw_name)
    
    # Additional cleanup: Ensure "leave" is normalized to "leaf" in all canonicals
    # This handles any edge cases where normalization might have been missed
    normalized_canonical_to_raw = defaultdict(list)
    for canonical, raw_names in canonical_to_raw.items():
        # Normalize "leave" to "leaf" if present
        normalized_canonical = re.sub(r'\bleave\b', 'leaf', canonical, flags=re.IGNORECASE)
        normalized_canonical_to_raw[normalized_canonical].extend(raw_names)
    
    canonical_to_raw = normalized_canonical_to_raw
    
    # Step 2: Build canonical ingredient objects (first pass - no variations yet)
    # Key logic: Determine canonical name based on base_headword
    # - If base_headword is characteristic word → canonical = base_headword
    # - Otherwise → canonical = full canonical name (with modifiers removed)
    ingredients_dict: Dict[str, dict] = {}  # canonical_name -> ingredient object
    
    base_group_to_category = get_base_group_to_category()
    characteristic_words = get_characteristic_words()
    
    # First, determine base_headword for each canonical
    canonical_to_headword = {}
    for canonical in canonical_to_raw.keys():
        base_headword = extract_base_headword(canonical)
        canonical_to_headword[canonical] = base_headword
    
    # Group canonicals by their base_headword
    # If base_headword is characteristic word, canonical = base_headword
    # Otherwise, canonical = the canonical name itself
    # IMPORTANT: Check FALSE_VARIATION_EXCEPTIONS FIRST - these should NOT be grouped
    headword_to_canonicals = defaultdict(list)
    for canonical, base_headword in canonical_to_headword.items():
        # Check if this canonical is in FALSE_VARIATION_EXCEPTIONS
        # If so, keep it as its own canonical (don't group with characteristic word)
        canonical_lower = canonical.lower().strip()
        if canonical_lower in FALSE_VARIATION_EXCEPTIONS:
            # Keep as separate canonical (e.g., "soy sauce" → canonical = "soy sauce", not "sauce")
            headword_to_canonicals[canonical].append(canonical)
        elif base_headword in characteristic_words:
            # If base_headword is characteristic word, canonical = base_headword
            # Example: "chicken broth" → base_headword = "broth" → canonical = "broth"
            headword_to_canonicals[base_headword].append(canonical)
        else:
            # Otherwise, canonical = canonical name itself
            # Example: "chicken" → base_headword = "chicken" → canonical = "chicken"
            headword_to_canonicals[canonical].append(canonical)
    
    # Build ingredients_dict with correct canonical names
    # Herb indicators (for detecting herbs vs spices)
    herb_indicators_for_category = {"leaf", "leaves", "blossom", "blossoms", "herb"}
    
    for final_canonical, canonicals in headword_to_canonicals.items():
        # Determine category from base_headword or canonical
        base_headword = canonical_to_headword.get(final_canonical, final_canonical)
        category = guess_category(final_canonical)
        
        # Special case: If ingredient ends with herb indicator (leaf, leaves, blossom, blossoms), force category to "herb"
        # This prevents "curry leaf" from being classified as "seasoning" (because of "curry")
        # This also ensures "hibiscus blossom" is classified as "herb" instead of "other"
        words = final_canonical.lower().split()
        if words and words[-1] in herb_indicators_for_category:
            category = "herb"
        
        # If base_headword is in base_group_to_category, use that category
        if base_headword in base_group_to_category:
            category = base_group_to_category[base_headword]
        
        # Generate ingredient_id
        clean = re.sub(r"[^a-z0-9]+", "_", final_canonical)
        ingredient_id = f"ing_{clean}"
        
        ingredients_dict[final_canonical] = {
            "ingredient_id": ingredient_id,
            "canonical_name": final_canonical,
            "category": category,
            "variations": {},  # Will be populated: { "flavor_source": [...], "nutrition": [...], etc. }
            "_all_canonicals": canonicals,  # Track all canonicals that map to this final canonical
        }
    
    # Step 3: Group variations
    # Process each canonical and determine if it's a variation of another canonical
    # Logic:
    # 1. Canonicals with characteristic word as base_headword are already grouped in Step 2
    #    (e.g., "chicken broth" → "broth" with "chicken broth" in _all_canonicals)
    # 2. For canonicals without characteristic word base_headword, check if they are variations
    #    (e.g., "chicken breast" might be variation of "chicken")
    
    # Build mapping: canonical -> final_canonical (for characteristic word cases)
    canonical_to_final = {}
    for final_canonical, ing in ingredients_dict.items():
        all_canonicals = ing.get("_all_canonicals", [final_canonical])
        for canonical in all_canonicals:
            canonical_to_final[canonical] = final_canonical
    
    # Helper function to check if categories are compatible
    def are_categories_compatible(cat1: str, cat2: str) -> bool:
        """Check if two categories are compatible (can be variations of each other)"""
        if cat1 == cat2:
            return True
        
        # Incompatible categories (should not be variations)
        incompatible_pairs = [
            ("herb", "seasoning"),
            ("herb", "spice"),
            ("vegetable", "seasoning"),
            ("fruit", "seasoning"),
        ]
        
        for pair in incompatible_pairs:
            if (cat1 in pair and cat2 in pair):
                return False
        
        return True
    
    # Now classify and group variations
    # Case 1: Canonicals that map to characteristic word (already handled in Step 2)
    for original_canonical, raw_names in canonical_to_raw.items():
        # Check blacklist - these should NOT be variations of base ingredients
        original_lower = original_canonical.lower().strip()
        if original_lower in FALSE_VARIATION_EXCEPTIONS:
            # Skip - these should remain as separate ingredients
            continue
        
        final_canonical = canonical_to_final.get(original_canonical, original_canonical)
        
        # Skip if this is already the final canonical
        if original_canonical == final_canonical:
            continue
        
        # This canonical maps to a final canonical (characteristic word case)
        # Check category compatibility before adding as variation
        parent_ing = ingredients_dict[final_canonical]
        parent_category = parent_ing["category"]
        
        # Get current canonical's category (may need to check from ingredients_dict)
        current_category = None
        herb_indicators_check = {"leaf", "leaves", "blossom", "blossoms", "herb"}
        words = original_canonical.lower().split()
        
        # Special case: If ends with herb indicator, it's herb (highest priority)
        if words and words[-1] in herb_indicators_check:
            current_category = "herb"
        elif original_canonical in ingredients_dict:
            current_category = ingredients_dict[original_canonical].get("category", "other")
        else:
            # If not in ingredients_dict, guess category
            current_category = guess_category(original_canonical)
        
        # Check category compatibility - skip if incompatible
        # IMPORTANT: Always check if current has herb indicator, even if category was guessed
        if words and words[-1] in herb_indicators_check and parent_category in ("seasoning", "spice"):
            continue  # Do NOT add herb indicators to seasoning/spice variations
        
        if current_category and not are_categories_compatible(current_category, parent_category):
            continue  # Do not add as variation if categories are incompatible
        
        # Classify it as a variation and add to parent
        parent_base = extract_base_headword(final_canonical)
        variation_type = classify_variation(original_canonical, parent_base, parent_category)
        if variation_type is None:
            variation_type = "other"
        
        if variation_type not in parent_ing["variations"]:
            parent_ing["variations"][variation_type] = []
        
        # Only add if not already in list
        if original_canonical not in parent_ing["variations"][variation_type]:
            parent_ing["variations"][variation_type].append(original_canonical)
    
    # Case 2: Check if non-characteristic canonicals are variations of others
    # (e.g., "chicken breast" might be variation of "chicken")
    # Sort by length (shortest first) to process base ingredients before variations
    sorted_canonicals = sorted(ingredients_dict.keys(), key=len)
    
    # First pass: Collect potential base ingredients that need to be created
    # Example: "egg whites", "egg yolks" → need to create "egg" as base
    potential_base_ingredients = defaultdict(set)  # base_word -> {canonicals that need this base}
    
    for canonical in sorted_canonicals:
        # Check blacklist FIRST - don't create base for blacklisted ingredients
        canonical_lower = canonical.lower().strip()
        if canonical_lower in FALSE_VARIATION_EXCEPTIONS:
            continue
        
        current_ing = ingredients_dict[canonical]
        current_base = extract_base_headword(canonical)
        
        # Skip if base is characteristic word (already handled)
        if current_base in characteristic_words:
            continue
        
        # Check blacklist for base word too - don't create base if base is blacklisted
        if current_base.lower().strip() in FALSE_VARIATION_EXCEPTIONS:
            continue
        
        # If base_headword is a single word and different from canonical, it might need to be created
        # Example: "egg whites" → base = "egg", canonical = "egg whites"
        # Example: "dried barberry" → base = "barberry", canonical = "dried barberry"
        # Example: "dried cloud ear" → base = "cloud ear", canonical = "dried cloud ear"
        # Check if base doesn't exist but should be created
        if current_base != canonical and current_base not in ingredients_dict:
            words = canonical.lower().split()
            canonical_starts_with_prep = len(words) >= 2 and words[0] in CUT_OR_FORM_WORDS
            
            # Case 1: Base is a single word
            if ' ' not in current_base and len(current_base) >= 2:
                # Skip if base is a preparation method (cut/form word)
                if current_base in CUT_OR_FORM_WORDS:
                    continue
                
                # Check if base is in category_base_words (likely a valid ingredient)
                category_base_words = get_category_base_words()
                if current_base in category_base_words:
                    potential_base_ingredients[current_base].add(canonical)
                elif canonical_starts_with_prep:
                    # Even if not in category_base_words, still consider creating base
                    # if canonical starts with a preparation method (e.g., "dried", "fresh", "frozen")
                    # Example: "dried barberry" → base = "barberry" (should be created)
                    # First word is a preparation method, second word should be base
                    # Only create if second word matches current_base
                    if len(words) >= 2 and words[1] == current_base:
                        potential_base_ingredients[current_base].add(canonical)
            
            # Case 2: Base is a multi-word phrase (e.g., "cloud ear", "hibiscus blossom")
            # Only create if canonical starts with a preparation method
            # Example: "dried cloud ear" → base = "cloud ear" (should be created)
            elif ' ' in current_base and canonical_starts_with_prep:
                # Extract the phrase after skipping preparation method
                # Example: "dried cloud ear" → "cloud ear"
                if len(words) >= 2:
                    phrase_after_prep = ' '.join(words[1:])
                    if phrase_after_prep == current_base:
                        # Only create if phrase is not too long (max 3 words) and makes sense
                        phrase_words = phrase_after_prep.split()
                        if len(phrase_words) <= 3 and len(phrase_words) >= 2:
                            # Check if first word of phrase is not a preparation method
                            if phrase_words[0] not in CUT_OR_FORM_WORDS:
                                potential_base_ingredients[current_base].add(canonical)
    
    # Create missing base ingredients
    for base_word, variations_set in potential_base_ingredients.items():
        if base_word not in ingredients_dict:
            # Determine category for base ingredient
            base_category = guess_category(base_word)
            if base_word in base_group_to_category:
                base_category = base_group_to_category[base_word]
            
            # Generate ingredient_id for base
            clean = re.sub(r"[^a-z0-9]+", "_", base_word)
            base_ingredient_id = f"ing_{clean}"
            
            # Create base ingredient
            ingredients_dict[base_word] = {
                "ingredient_id": base_ingredient_id,
                "canonical_name": base_word,
                "category": base_category,
                "variations": {},
                "_all_canonicals": [base_word],
            }
            # Add to sorted_canonicals so it gets processed
            sorted_canonicals.append(base_word)
    
    # Sort again after adding new base ingredients
    sorted_canonicals = sorted(set(sorted_canonicals), key=len)
    
    for canonical in sorted_canonicals:
        # Check blacklist - these should NOT be variations of base ingredients
        canonical_lower = canonical.lower().strip()
        if canonical_lower in FALSE_VARIATION_EXCEPTIONS:
            # Skip - these should remain as separate ingredients
            continue
        
        current_ing = ingredients_dict[canonical]
        current_base = extract_base_headword(canonical)
        
        # Skip if base is characteristic word (already handled)
        if current_base in characteristic_words:
            continue
        
        # Try to find parent (longer canonical that contains this canonical)
        current_category = current_ing.get("category", "other")
        parent = find_parent_canonical(canonical, ingredients_dict, current_category)
        if parent:
            # Double check: parent should not be in blacklist either
            parent_lower = parent.lower().strip()
            if parent_lower in FALSE_VARIATION_EXCEPTIONS:
                # Don't add to blacklisted parent
                continue
            
            # This is a variation, classify it and add to parent
            parent_ing = ingredients_dict[parent]
            parent_base = extract_base_headword(parent)
            parent_category = parent_ing["category"]
            
            variation_type = classify_variation(canonical, parent_base, parent_category)
            if variation_type is None:
                variation_type = "other"
            
            if variation_type not in parent_ing["variations"]:
                parent_ing["variations"][variation_type] = []
            
            # Only add if not already in list
            if canonical not in parent_ing["variations"][variation_type]:
                parent_ing["variations"][variation_type].append(canonical)
    
    # Step 4: Build final output
    # Remove internal tracking fields and build clean output
    # Filter out ingredients that are variations of others
    
    # Collect all variations
    all_variations = set()
    for ing in ingredients_dict.values():
        for var_list in ing["variations"].values():
            all_variations.update(var_list)
    
    final_ingredients = []
    for canonical, ing in ingredients_dict.items():
        # Skip if this canonical is a variation of another ingredient
        # Only keep the final canonical (parent), not the variations
        # Exception: if canonical is its own final canonical (e.g., "sauce" with variations)
        # and is NOT in any other ingredient's variations, keep it
        if canonical in all_variations:
            # Check if this canonical is a variation of another canonical
            # (i.e., exists in another ingredient's variations)
            is_variation_of_other = False
            for other_canonical, other_ing in ingredients_dict.items():
                if other_canonical == canonical:
                    continue  # Skip self
                for var_list in other_ing["variations"].values():
                    if canonical in var_list:
                        is_variation_of_other = True
                        break
                if is_variation_of_other:
                    break
            
            # If this canonical is a variation of another, skip it
            # (it should only appear in the parent's variations list, not as a separate entry)
            if is_variation_of_other:
                continue
        
        # Generate alt_names for this canonical ingredient
        alt_names = generate_alt_names(ing["canonical_name"])
        
        # Build output object
        output_ing = {
            "ingredient_id": ing["ingredient_id"],
            "canonical_name": ing["canonical_name"],
            "category": ing["category"],
        }
        
        # Add alt_names if any
        if alt_names:
            output_ing["alt_names"] = alt_names
        
        # Add variations if any (only non-empty groups)
        if ing["variations"]:
            variations_dict = {}
            for var_type, var_list in ing["variations"].items():
                if var_list:  # Only add non-empty lists
                    variations_dict[var_type] = sorted(set(var_list))
            
            if variations_dict:
                output_ing["variations"] = variations_dict
        
        final_ingredients.append(output_ing)
    
    return final_ingredients


# ====================================================
# 🚀 MAIN
# ====================================================
if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create canonical ingredients JSON with variations grouped into 6 categories"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/process/ingredients.txt",
        help="Path to input file"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/process/canonical_ingredients.json",
        help="Path to output JSON file"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print debug logs"
    )
    
    args = parser.parse_args()
    
    # Process ingredients
    input_path = Path(args.input)
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        sys.exit(1)
    
    print(f"Reading ingredients from {input_path}...")
    ingredients = process_ingredients_from_file(input_path)
    print(f"Processed {len(ingredients)} unique canonical ingredients")
    
    # Statistics
    total_variations = 0
    ingredients_with_variations = 0
    variation_type_counts = defaultdict(int)
    
    for ing in ingredients:
        if "variations" in ing:
            ingredients_with_variations += 1
            for var_type, var_list in ing["variations"].items():
                count = len(var_list)
                total_variations += count
                variation_type_counts[var_type] += count
    
    print(f"\nStatistics:")
    print(f"  - Canonical ingredients: {len(ingredients)}")
    print(f"  - Ingredients with variations: {ingredients_with_variations}")
    print(f"  - Total variations: {total_variations}")
    print(f"\nVariation type distribution:")
    for var_type, count in sorted(variation_type_counts.items(), key=lambda x: -x[1]):
        print(f"  - {var_type}: {count}")
    
    # Category distribution
    category_counts = defaultdict(int)
    for ing in ingredients:
        category_counts[ing["category"]] += 1
    print(f"\nCategory distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"  - {cat}: {count}")
    
    # Save JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(ingredients, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\nSaved {len(ingredients)} ingredients to {output_path}")
    
    # Save separate file for category "other"
    other_ingredients = [ing for ing in ingredients if ing.get("category") == "other"]
    if other_ingredients:
        # Generate output path for "other" category
        output_dir = output_path.parent
        output_name = output_path.stem  # e.g., "canonical_ingredients"
        other_output_path = output_dir / f"{output_name}_other.json"
        
        other_output_path.write_text(
            json.dumps(other_ingredients, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )
        print(f"Saved {len(other_ingredients)} 'other' category ingredients to {other_output_path}")
    
    # Preview
    if args.verbose:
        print("\nSample ingredients (first 5):")
        for ing in ingredients[:5]:
            print(f"  - {ing['canonical_name']} ({ing['category']})")
            if "variations" in ing:
                for var_type, var_list in ing["variations"].items():
                    print(f"    {var_type}: {var_list[:3]}...")  # Show first 3
        
        print("\nSample ingredients with variations:")
        with_variations = [ing for ing in ingredients if "variations" in ing][:5]
        for ing in with_variations:
            total_vars = sum(len(v) for v in ing["variations"].values())
            print(f"  - {ing['canonical_name']} has {total_vars} variations")

