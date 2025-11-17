#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Process ingredients from in.txt and create JSON with categories, base names, and variations.

Usage:
  python process_ingredients_from_intxt.py \
    --input data/process/in.txt \
    --output data/process/ingredients_from_intxt.json
"""

import re
import json
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Optional, Tuple
import sys
import os

# Add backend directory to path to import config
backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

from config import NON_ING_WORDS, FIX_MAP, ALT_MAP

# Import from import_ingredients.py
import importlib.util
# import_ingredients.py is in backend/scripts/
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
# 1️⃣ Normalize và Clean Text
# ====================================================
def normalize_text(value: str) -> str:
    """Normalize text: lowercase, remove non-alphanumeric chars, collapse spaces."""
    if value is None:
        return ""
    lowered = value.strip().lower()
    normalized = re.sub(r"[^a-z0-9_]+", " ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def build_canonical(name: str) -> str:
    """
    Build canonical name from raw ingredient name.
    - Remove brand names (heuristic: words with ®, ™, or capitalized words at start)
    - Remove packing phrases
    - Normalize and clean
    """
    # Brand names to remove (same as in filter_ingredients_from_uni.py)
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
        "cool whip", "miracle whip", "crisco", "bisquick", "pam", "jello", "breakstone","knorr",
        "baileys", "bertolli"  # Additional brand names
    ]
    
    # Remove brand markers
    name = re.sub(r'\s*[®™©]\s*', ' ', name, flags=re.IGNORECASE)
    
    # Normalize first
    name = name.strip().lower()
    
    # Remove brand names (check multi-word first, then single-word)
    multi_word_brands = [brand for brand in BRAND_LIST if ' ' in brand]
    multi_word_brands.sort(key=len, reverse=True)  # Longest first
    
    for brand in multi_word_brands:
        # Remove brand name as whole phrase
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        name = re.sub(pattern, '', name, flags=re.IGNORECASE)
    
    # Remove single-word brand names
    words = name.split()
    cleaned_words = []
    for word in words:
        # Skip if it's a brand name
        is_brand = False
        for brand in BRAND_LIST:
            if ' ' not in brand and word == brand.lower():
                is_brand = True
                break
        if not is_brand:
            # Also skip if it's all caps and short (likely brand)
            if word.isupper() and len(word) <= 3:
                continue
            # Skip if contains ® or ™
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
    
    # Normalize plural to singular (for the last word)
    # This helps normalize "amarena cherries" -> "amarena cherry"
    # But only if the word is not already in category base words (to avoid normalizing "rice", "cheese", etc.)
    category_base_words = get_category_base_words()
    words = name.split()
    if words:
        last_word = words[-1]
        # Only normalize if the word is not already in category base words
        # and it looks like a plural form
        if last_word not in category_base_words:
            original_last = last_word
            # Heuristic plural→singular
            # Check special cases first (longest patterns first)
            if last_word.endswith("ies") and len(last_word) > 3:
                # cherries -> cherry, berries -> berry
                last_word = last_word[:-3] + "y"
            elif last_word.endswith("oes") and len(last_word) > 3:
                # tomatoes -> tomato, potatoes -> potato
                last_word = last_word[:-2]
            elif last_word.endswith("ches") or last_word.endswith("shes") or last_word.endswith("xes"):
                # peaches -> peach, dishes -> dish, boxes -> box
                last_word = last_word[:-2]
            elif last_word.endswith("ses") and len(last_word) > 3:
                # cases -> case, bases -> base
                last_word = last_word[:-2]
            elif last_word.endswith("les") and len(last_word) > 3:
                # apples -> apple, tables -> table
                # For words ending in "les", just remove "s" not "es"
                last_word = last_word[:-1]
            elif last_word.endswith("ves") and len(last_word) > 3:
                # leaves -> leaf, knives -> knife (but we'll just remove "s" for simplicity)
                last_word = last_word[:-1]
            elif last_word.endswith("es") and len(last_word) > 3:
                # For other "es" endings, check if removing "es" makes sense
                # oranges -> orange, but be careful with words like "apples"
                # Try removing "es" first, but if result is too short, try just "s"
                singular_es = last_word[:-2]
                if len(singular_es) >= 3:
                    last_word = singular_es
                else:
                    # Fallback: just remove "s"
                    last_word = last_word[:-1]
            elif last_word.endswith("s") and len(last_word) > 1:
                # Simple plural: eggs -> egg, beans -> bean
                singular = last_word[:-1]
                # Skip if removing 's' results in very short word
                if len(singular) >= 2:
                    last_word = singular
            
            # Only use normalized version if it's different and makes sense
            if last_word != original_last:
                words[-1] = last_word
                name = ' '.join(words)
    
    return name


# ====================================================
# 2️⃣ Extract Base Name
# ====================================================
def extract_base_name(name: str) -> str:
    """
    Extract base ingredient name by removing modifiers.
    Priority: 
    1. If contains characteristic/attribute word (juice, pepper, sauce, oil, etc.) → return that word
       (e.g., "apple juice" -> "juice", "black pepper" -> "pepper")
    2. If category is "meat" or "seafood" → return category name
       (e.g., "chicken breast" -> "meat", "salmon fillet" -> "seafood")
    3. Find multi-word phrases from category base words (e.g., "king crab", "cream cheese")
    4. Find single words from category base words (e.g., "chicken", "beef")
    5. Use first non-modifier word as fallback
    Example: "apple juice" -> "juice"
    Example: "black pepper" -> "pepper"
    Example: "chicken breast" -> "meat" (if category is meat)
    Example: "salmon fillet" -> "seafood" (if category is seafood)
    Example: "alaskan king crab legs" -> "king crab" (because "king crab" is in category base words)
    """
    # Get category base words
    category_base_words = get_category_base_words()
    
    # Common modifiers to remove
    modifiers = {
        "boneless", "skinless", "bone-in", "bone in", "bonein",
        "fresh", "dried", "frozen", "canned", "jarred", "pickled",
        "chopped", "sliced", "diced", "minced", "ground", "grated",
        "whole", "halves", "halved", "fillets", "strips", "cubes", "cubed",
        "shredded", "crushed", "peeled", "seeded", "pitted", "cored",
        "unsalted", "salted", "raw", "cooked", "roasted", "toasted",
        "all-purpose", "all purpose", "ap", "plain", "unflavored",
        "low-fat", "low fat", "fat-free", "fat free", "reduced-fat",
        "full-fat", "full fat", "non-fat", "non fat",
        "organic", "conventional",
        "large", "medium", "small", "extra-large", "extra large",
        "whole", "half", "quarter", "quartered",
    }
    
    name_lower = name.lower()
    words = name_lower.split()
    base_words = [w for w in words if w not in modifiers]
    
    # Get characteristic words
    characteristic_words = get_characteristic_words()
    
    # Priority 1: Check for characteristic/attribute words (đặc điểm/tính chất)
    # Check last word first (most common case: "apple juice" -> "juice")
    if words and words[-1] in characteristic_words:
        return words[-1]
    
    # Check all words for characteristic words
    for word in base_words:
        if word in characteristic_words:
            return word
    
    # Priority 2: Find multi-word phrases from category base words (longest first)
    multi_word_phrases = [w for w in category_base_words if ' ' in w]
    multi_word_phrases.sort(key=len, reverse=True)  # Longest first
    
    for phrase in multi_word_phrases:
        # Check if phrase appears in name (as whole phrase with word boundaries)
        pattern = r'\b' + re.escape(phrase) + r'\b'
        if re.search(pattern, name_lower):
            return phrase
    
    # Priority 3: Find single words from category base words
    # Check from right to left (last word first) to prioritize main ingredient over variety names
    # e.g., "braeburn apple" -> "apple" (not "braeburn")
    # e.g., "chicken drumstick" -> "chicken" (not "drumstick" or "meat")
    # e.g., "chocolate milk" -> "milk" (not "chocolate") - prioritize last word if it's in category base words
    # This will find "chicken", "beef", "salmon" etc. from CATEGORY_MEATS or CATEGORY_SEAFOOD
    # But also prioritize last word if it's a valid category word (e.g., "milk", "cookie", "mousse")
    if base_words and base_words[-1] in category_base_words:
        return base_words[-1]
    
    # Then check other words from right to left
    for word in reversed(base_words[:-1] if base_words else []):
        if word in category_base_words:
            return word
    
    # Priority 4: If no category word found, prioritize last word (usually main ingredient)
    # e.g., "castelvetrano olive" -> "olive" (not "castelvetrano")
    # This handles cases where variety names are not in category base words
    if len(base_words) >= 1:
        return base_words[-1]  # Return last word (main ingredient) instead of first
    
    return name  # fallback


# ====================================================
# 3️⃣ Find Parent Ingredient (for variations)
# ====================================================
def get_characteristic_words() -> set:
    """
    Get set of characteristic/attribute words (đặc điểm/tính chất).
    These words should not be grouped as variations when they are base_group.
    """
    return {
        "sauce", "flour", "oil", "juice", "broth", "stock", "soup",
        "vinegar", "syrup", "honey", "molasses", "cream", "milk",
        "butter", "yogurt", "mayonnaise", "dressing", "marinade",
        "paste", "puree", "concentrate", "extract", "essence",
        "liqueur", "wine", "beer", "vodka", "whiskey", "bourbon", "sake",
        "vermouth", "cider", "coffee", "espresso", "tea",
        "pepper", "salt", "paprika", "cumin", "chili", "cayenne", 
        "turmeric", "cinnamon", "nutmeg", "allspice", "curry", "masala",
        "anise", "cardamom", "sumac", "seasoning", "spice", "chile",
        "chipotle", "clove", "coriander", "ginger", "peppercorn",
        "ketchup", "mustard", "salsa", "pesto", "guacamole", "chutney",
        "tahini", "harissa", "sriracha", "tabasco", "gochujang",
        "worcestershire", "tamari", "miso", "dijon", "horseradish",
        "relish", "glaze", "gravy", "bouillon", "pickle", "sauerkraut",
        "furikake", "dashi", "caper", "cornichon", "cereal","candy"
    }


def find_parent_ingredient(name: str, existing_ingredients: Dict[str, dict], current_base_group: str) -> Optional[str]:
    """
    Tìm ingredient chính mà variation này thuộc về.
    Returns: canonical_name của ingredient chính, hoặc None nếu không tìm thấy
    
    Strategy: Tìm ingredient có tên là substring của name hiện tại
    "boneless chicken breast" -> tìm "chicken breast"
    
    But skip if:
    - Current ingredient has a characteristic word as base_group (e.g., "chocolate sauce" -> base_group: "sauce")
      should NOT be variation of "chocolate"
    - Parent's base_group is different from current base_group
    """
    name_lower = name.lower()
    characteristic_words = get_characteristic_words()
    
    # If current base_group is a characteristic word, don't group as variation
    # e.g., "chocolate sauce" has base_group "sauce" -> should NOT be variation of "chocolate"
    if current_base_group in characteristic_words:
        return None
    
    # Sort by length (longest first) để match chính xác nhất
    sorted_ings = sorted(existing_ingredients.keys(), key=len, reverse=True)
    
    for ing in sorted_ings:
        ing_lower = ing.lower()
        # Check if existing ingredient is a substring of current name
        # But not equal to current name
        if ing_lower != name_lower and ing_lower in name_lower:
            # Make sure it's a word boundary match (not just substring)
            # e.g., "chicken" should match "chicken breast" but not "chickens"
            pattern = r'\b' + re.escape(ing_lower) + r'\b'
            if re.search(pattern, name_lower):
                # Check if parent's base_group matches current base_group
                parent_base_group = existing_ingredients[ing]["base_group"]
                # Only group as variation if base_groups match or parent's base_group is not a characteristic word
                if parent_base_group == current_base_group or parent_base_group not in characteristic_words:
                    return ing
    
    return None  # Không tìm thấy parent


# ====================================================
# 4️⃣ Process Ingredients from in.txt
# ====================================================
def process_ingredients_from_file(input_path: Path) -> List[dict]:
    """
    Process ingredients from in.txt file.
    Returns list of ingredient objects with categories, base names, and variations.
    """
    # Read all lines
    lines = [l.strip() for l in input_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    
    # Step 1: Build canonical names and count frequencies
    canonical_to_raw = defaultdict(list)
    for raw_name in lines:
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
    
    # Step 2: Build ingredient objects (first pass - no variations yet)
    ingredients_dict: Dict[str, dict] = {}  # canonical_name -> ingredient object
    
    # Get mapping from base_group to category from import_ingredients.py
    base_group_to_category = get_base_group_to_category()
    
    for canonical, raw_names in canonical_to_raw.items():
        base_name = extract_base_name(canonical)
        category = guess_category(canonical)
        
        # If base_group is a characteristic word, update category to match
        if base_name in base_group_to_category:
            category = base_group_to_category[base_name]
        
        # Generate ingredient_id
        clean = re.sub(r"[^a-z0-9]+", "_", canonical)
        ingredient_id = f"ing_{clean}"
        
        # Generate alt names
        alt_names = generate_alt(canonical)
        
        ingredients_dict[canonical] = {
            "ingredient_id": ingredient_id,
            "canonical_name": canonical,
            "base_group": base_name,
            "category": category,
            "alt_names": alt_names,
            "variations": [],  # Will be populated in next pass
        }
    
    # Step 3: Group variations
    # Sort by length (shortest first) to process base ingredients before variations
    sorted_canonicals = sorted(ingredients_dict.keys(), key=len)
    
    for canonical in sorted_canonicals:
        # Get current ingredient's base_group
        current_base_group = ingredients_dict[canonical]["base_group"]
        
        # Try to find parent
        parent = find_parent_ingredient(canonical, ingredients_dict, current_base_group)
        
        if parent:
            # This is a variation - add to parent's variations list
            ingredients_dict[parent]["variations"].append(canonical)
        # else: it's a base ingredient
    
    # Step 4: Convert to list
    ingredients_list = list(ingredients_dict.values())
    
    return ingredients_list


# ====================================================
# 🚀 MAIN
# ====================================================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Process ingredients from in.txt and create JSON with categories"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/process/ingredients.txt",
        help="Path to input file (in.txt)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/process/ingredients_filter.json",
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
    print(f"Processed {len(ingredients)} unique ingredients")
    
    # Count statistics
    # Base ingredients are those that have variations or are not in any variation list
    all_variations = set()
    for ing in ingredients:
        all_variations.update(ing["variations"])
    
    base_count = sum(1 for ing in ingredients if ing["canonical_name"] not in all_variations)
    variation_count = len(all_variations)
    with_variations = sum(1 for ing in ingredients if len(ing["variations"]) > 0)
    
    print(f"Statistics:")
    print(f"   - Base ingredients: {base_count}")
    print(f"   - Variations: {variation_count}")
    print(f"   - Ingredients with variations: {with_variations}")
    
    # Category distribution
    category_counts = defaultdict(int)
    for ing in ingredients:
        category_counts[ing["category"]] += 1
    print(f"Category distribution:")
    for cat, count in sorted(category_counts.items(), key=lambda x: -x[1]):
        print(f"   - {cat}: {count}")
    
    # Save JSON
    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(ingredients, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"Saved {len(ingredients)} ingredients to {output_path}")
    
    # Preview
    if args.verbose:
        print("\nSample ingredients (first 10):")
        for ing in ingredients[:10]:
            print(f"  - {ing['canonical_name']} ({ing['category']}, base_group: {ing['base_group']})")
            if ing['variations']:
                print(f"    Variations: {ing['variations'][:3]}...")
        
        print("\nSample ingredients with variations:")
        with_variations = [ing for ing in ingredients if len(ing['variations']) > 0][:5]
        for ing in with_variations:
            print(f"  - {ing['canonical_name']} has {len(ing['variations'])} variations")

