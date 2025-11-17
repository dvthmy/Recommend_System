#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Migrate variations trong canonical_ingredients.json → thành Ingredient độc lập.

❗ Chỉ migrate variants THẬT SỰ cần thiết:
- ✅ Tạo ingredients riêng cho: "cheddar cheese", "provolone cheese", "jasmine rice", "yellow onion"
- ❌ KHÔNG tạo cho variants có preparation/modifier words:
  - Preparation: boneless, refined, refrigerated, fresh, frozen, dried, sliced, diced, etc.
  - Grade/style: extra virgin, extra large, large, medium, small
  - Nutrition: low fat, reduced fat, skim, nonfat, low sodium, etc.

Những variants có modifiers sẽ được giữ trong variations của base ingredient.

Usage:
  python add_variant_ingredients.py \
    --input  data/process/canonical_ingredients.json \
    --output data/process/canonical_ingredients_migrated.json
"""

import json
import re
import argparse
import sys
import os
from pathlib import Path
from typing import Dict, List, Set, Tuple

# ==========================
#  CONFIG & IMPORT HELPERS
# ==========================

backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_dir)

# Import from import_ingredients.py
import importlib.util
scripts_dir = os.path.join(backend_dir, 'scripts')
import_ingredients_path = os.path.join(scripts_dir, 'import_ingredients.py')
spec = importlib.util.spec_from_file_location("import_ingredients", import_ingredients_path)
import_ingredients = importlib.util.module_from_spec(spec)
spec.loader.exec_module(import_ingredients)
guess_category = import_ingredients.guess_category
generate_alt = import_ingredients.generate_alt

# Import FALSE_VARIATION_EXCEPTIONS from create_canonical_ingredients.py
create_canonical_path = os.path.join(os.path.dirname(__file__), 'create_canonical_ingredients.py')
spec_canonical = importlib.util.spec_from_file_location("create_canonical_ingredients", create_canonical_path)
create_canonical_module = importlib.util.module_from_spec(spec_canonical)
spec_canonical.loader.exec_module(create_canonical_module)
FALSE_VARIATION_EXCEPTIONS = create_canonical_module.FALSE_VARIATION_EXCEPTIONS

# Patterns để xác định variant KHÔNG nên tạo thành ingredient riêng
# Chỉ giữ trong variations của base ingredient

# Brand names - KHÔNG tạo ingredients riêng
BRAND_NAMES = [
    "dreamfields", "stonefire", "splenda", "argo", "mccormick", "hershey", "hershey's", 
    "nestle", "ghirardelli", "domino", "c&h", "kikkoman", "lee kum kee", "mae ploy", 
    "huy fong", "lao gan ma", "campbell", "campbell's", "swanson", "better than bouillon",
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
    "baileys", "bertolli", "cox's",
    "foster farms", "tyson","crumbled",
    "lea & perrins", "lea and perrins","ic","country",
    "st germain", "st. germain", "colman's", "colmans",
    "knox", "knudsen", "kroger","purée","creamed","soften",
    "saigon", "challenge", "islands","on","on the vine","on the cob","on the",
    "dr pepper", "dr. pepper","virgin"
]

# Preparation/modifier words - KHÔNG tạo ingredients riêng
PREPARATION_MODIFIERS = [
    "boneless", "skinless", "bone-in", "bone in", "refined", "refrigerated",
    "fresh", "frozen", "dried", "canned", "jarred", "pickled", "smoked",
    "roasted", "toasted", "cooked", "uncooked", "raw", "organic", "conventional",
    "sliced", "diced", "minced", "chopped", "ground", "grated", "crushed","purée"
    "shredded", "flaked", "peeled", "seeded", "pitted", "cored", "whole", "halves",
    "halved", "fillets", "strips", "cubes", "cubed", "unsalted", "salted",
    "all-purpose", "all purpose", "ap", "plain", "unflavored","cube","ume"
    "gluten", "glutend", "powdered", "cracked", "dry", "sweet", "unsweet", "unsweetened", "sweetened",
    "andouille", "angel", "breaded", "broiler-fryer", "broiler","unbaked",
    "free range", "free-range", "fried", "refried", "homemade", "instant", "imitation",
    "brine-cured", "brine cured", "niçoise", "nicoise","urad","unsulphured","tree",
    "rich", "round", "rotisserie", "round sourdough", "spring", "sponge", "crispy",
    "bottled", "golden", "prepared", "prepar", "traditional", "stir fry", "vegan",
    "self-rising", "self rising", "seasoned", "steamed", "strong", "unbleached", "sparkling",
    "southern", "five-spice", "five spice", "file", "malted","spray"
    "glucose", "pure", "distilled", "agar", "string","-filled","filled","fat"
    "texas", "graham", "store-bought", "store bought", "baby", "aged","ground",
    "bittersweet", "mini", "chocolatecovered", "chocolate covered", "sundried", "sun-dried", "true",
    "smooth", "softened", "stick", "grass-fed", "grass fed", "clarified","free-range","fresh-squeezed","frozen-squeezed",
    "whipped", "root", "pimento stuffed", "pimento-stuffed", "shucked", "bow-tie", "bow tie",
    "solid", "unseasoned", "flax", "wide","shaved","shell-on","shelled","unsalted","salted","on","on the vine","on the cob","on the",
    "unpeeled","peeled","uncooked","cooked","unbaked","baked","unfried","fried","unroasted","roasted",
    "ungrilled","grilled","unbroiled","broiled","unsteamed","steamed","unboiled","boiled","unpoached","poached",
]

# Grade/style modifiers - KHÔNG tạo ingredients riêng
GRADE_STYLE_MODIFIERS = [
    "extra virgin", "extra fine", "extra large", "extra small",
    "large", "medium", "small","extra medium", "extra medium","extra large", "extra small",
    "long", "extra", "superfine", "wide","extra small", "extra large","sharp"
]

# Nutrition patterns - KHÔNG tạo ingredients riêng
NUTRITION_PATTERNS = [
    "skim", "nonfat", "no fat", "fat free", "fatfree", "low fat", "lowfat", "reduced fat",
    "low sodium", "lowsodium", "lower sodium", "less sodium", "no salt", "salt free", "sodium free", "reduced sodium",
    "low sugar", "no sugar", "sugar free", "reduced sugar",
    "unsalted", "light", "diet", "reduced", "low", "non", "no-", "no ",
    "full-fat", "full fat"
]


def normalize_name_for_key(text: str) -> str:
    """Normalize name để dùng làm key (so sánh duplicate)."""
    return re.sub(r'[^a-z0-9]+', '_', text.strip().lower())


def create_ingredient_id(canonical_name: str) -> str:
    """Tạo ingredient_id từ canonical_name."""
    clean = re.sub(r'[^a-z0-9]+', '_', canonical_name.strip().lower())
    clean = clean.strip('_')
    return f"ing_{clean}"


def has_brand_name(name: str) -> bool:
    """
    Check nếu variant có brand name như dreamfields, stonefire, splenda, etc.
    
    Returns:
        True nếu variant có brand name (không nên tạo ingredient riêng)
    """
    name_lower = name.lower()
    
    # Check brand markers (®™©)
    if re.search(r'[®™©]', name, flags=re.IGNORECASE):
        return True
    
    # Check multi-word brands first (longest first)
    multi_word_brands = [brand for brand in BRAND_NAMES if ' ' in brand]
    multi_word_brands.sort(key=len, reverse=True)
    
    for brand in multi_word_brands:
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        if re.search(pattern, name_lower, flags=re.IGNORECASE):
            return True
    
    # Check single-word brands
    words = name_lower.split()
    for word in words:
        # Check exact match
        for brand in BRAND_NAMES:
            if ' ' not in brand and word == brand.lower():
                return True
        # Check if word is likely a brand (all caps, short)
        if word.isupper() and len(word) <= 3:
            return True
    
    return False


def has_preparation_modifier(name: str) -> bool:
    """
    Check nếu variant có preparation/modifier words như boneless, refined, refrigerated, etc.
    
    Những variants có modifiers này KHÔNG nên tạo thành ingredients riêng,
    mà nên giữ trong variations của base ingredient.
    
    Returns:
        True nếu variant có modifiers (không nên tạo ingredient riêng)
    """
    name_lower = name.lower()
    
    # EXCEPTIONS: Các variants thật sự, không phải modifiers
    # "sweet potato" là một loại thật sự, không phải modifier
    if name_lower == "sweet potato":
        return False
    # "angel hair pasta" là một loại pasta thật sự, không phải modifier
    if "angel hair pasta" in name_lower or name_lower == "angel hair":
        return False
    # "andouille sausage" là một loại sausage thật sự, nhưng "andouille" alone là modifier
    # Chỉ check "andouille" khi nó đứng một mình, không phải part of "andouille sausage"
    
    # Check phrases like "on the vine", "on the cob", etc. - không tạo ingredients riêng
    descriptive_phrases = [
        "on the vine", "on the cob", "on the bone", "on the side",
        "in the shell", "in the can", "in the jar", "in the box",
        "with the", "without the"
    ]
    for phrase in descriptive_phrases:
        if phrase in name_lower:
            return True
    
    # Check preparation modifiers (whole word match)
    for modifier in PREPARATION_MODIFIERS:
        # Skip "sweet" nếu là "sweet potato"
        if modifier == "sweet" and "sweet potato" in name_lower:
            continue
        # Skip "angel" nếu là "angel hair pasta" hoặc "angel hair"
        if modifier == "angel" and ("angel hair pasta" in name_lower or "angel hair" in name_lower):
            continue
        # Skip "andouille" nếu là "andouille sausage" (loại sausage thật sự)
        # Nhưng nếu chỉ có "andouille" thì là modifier
        if modifier == "andouille" and "andouille sausage" in name_lower:
            continue
        pattern = r'\b' + re.escape(modifier) + r'\b'
        if re.search(pattern, name_lower, re.IGNORECASE):
            return True
    
    # Check grade/style modifiers (multi-word first)
    for modifier in sorted(GRADE_STYLE_MODIFIERS, key=len, reverse=True):
        if modifier in name_lower:
            return True
    
    # Check nutrition patterns (whole word match)
    for pat in NUTRITION_PATTERNS:
        if ' ' in pat:
            if pat in name_lower:
                return True
        else:
            pattern = r'\b' + re.escape(pat) + r'\b'
            if re.search(pattern, name_lower, re.IGNORECASE):
                return True
    
    return False


def is_variant_of_false_exception(name: str) -> bool:
    """
    Check nếu variant là variation của một ingredient trong FALSE_VARIATION_EXCEPTIONS.
    
    Ví dụ:
    - "coarse ground black pepper" contains "black pepper" (trong FALSE_VARIATION_EXCEPTIONS)
    - "cracked black pepper" contains "black pepper" (trong FALSE_VARIATION_EXCEPTIONS)
    
    Những variants này KHÔNG nên tạo thành ingredient riêng, mà giữ trong variations
    của FALSE_VARIATION_EXCEPTIONS ingredient.
    
    Returns:
        True nếu variant là variation của FALSE_VARIATION_EXCEPTIONS ingredient
    """
    name_lower = name.lower().strip()
    
    # Check nếu variant contains một ingredient trong FALSE_VARIATION_EXCEPTIONS
    # Sort by length (longest first) để match chính xác nhất
    sorted_exceptions = sorted(FALSE_VARIATION_EXCEPTIONS.keys(), key=len, reverse=True)
    
    for exception_key in sorted_exceptions:
        exception_lower = exception_key.lower().strip()
        
        # Check nếu variant contains exception (nhưng không bằng)
        # Ví dụ: "coarse ground black pepper" contains "black pepper"
        if exception_lower != name_lower and exception_lower in name_lower:
            # Check word boundary để tránh false matches
            # Ví dụ: "black pepper" should match "coarse ground black pepper" nhưng không match "blackpeppercorn"
            pattern = r'\b' + re.escape(exception_lower) + r'\b'
            if re.search(pattern, name_lower, re.IGNORECASE):
                return True
    
    return False


def is_nutrition_variant(name: str, bucket_name: str | None = None) -> bool:
    """
    Trả về True nếu variant có tính nutrition HOẶC có preparation modifiers HOẶC có brand name
    HOẶC là variation của FALSE_VARIATION_EXCEPTIONS ingredient:
    - bucket_name == 'nutrition'
    - hoặc name chứa một trong NUTRITION_PATTERNS
    - hoặc name có preparation/modifier words (boneless, refined, etc.)
    - hoặc name có brand name (dreamfields, stonefire, splenda, etc.)
    - hoặc name là variation của FALSE_VARIATION_EXCEPTIONS (như "coarse ground black pepper")
    
    Những variants này KHÔNG nên tạo thành ingredient riêng.
    """
    if bucket_name and bucket_name.lower() == "nutrition":
        return True
    
    # Check nếu variant là variation của FALSE_VARIATION_EXCEPTIONS ingredient
    if is_variant_of_false_exception(name):
        return True
    
    # Check brand names
    if has_brand_name(name):
        return True
    
    # Check preparation modifiers
    if has_preparation_modifier(name):
        return True
    
    return False


def index_existing_ingredients(ingredients: List[Dict]) -> Dict[str, Dict]:
    """
    Map các key (canonical_name, ingredient_id) đã tồn tại → ingredient.
    Dùng để tránh tạo trùng.
    """
    existing: Dict[str, Dict] = {}
    for ing in ingredients:
        canonical = ing.get("canonical_name") or ing.get("canonical") or ""
        ing_id = ing.get("ingredient_id", "")
        if canonical:
            key = "name:" + normalize_name_for_key(canonical)
            existing[key] = ing
        if ing_id:
            key_id = "id:" + ing_id.strip().lower()
            existing[key_id] = ing
    return existing


def create_variant_ingredient(
    variant_name: str,
    base_canonical: str,
    base_category: str | None,
) -> Dict:
    """
    Tạo ingredient dict cho 1 variation được nâng cấp thành Ingredient riêng.
    - canonical_name = variant_name
    - base = base_canonical (vd: 'flour', 'sauce', 'cheese', ...)
    - category = cùng category với base (hoặc guess nếu thiếu)
    """
    ingredient_id = create_ingredient_id(variant_name)

    # Category: ưu tiên dùng category của base, fallback guess_category
    category = base_category or guess_category(variant_name)

    alt_names = generate_alt(variant_name)

    return {
        "ingredient_id": ingredient_id,
        "canonical_name": variant_name,
        "base": base_canonical,       # 👉 group theo base (vd: cheese, flour, sauce)
        "category": category,
        "alt_names": alt_names,
        # Variations của variant mới: để rỗng cho đơn giản, sau này nếu muốn có thể build thêm
        "variations": {}
    }


def migrate_variations(
    input_path: Path,
    output_path: Path,
    log_file_path: Path | None = None,
) -> None:
    # Tạo log file path nếu chưa có
    if log_file_path is None:
        log_file_path = output_path.with_suffix('.log.txt')
    
    # Mở log file để ghi
    log_file = open(log_file_path, 'w', encoding='utf-8')
    
    def log(msg: str):
        """Ghi log vào file (không in ra console)"""
        log_file.write(msg + '\n')
        log_file.flush()
    
    try:
        log(f"[*] Reading canonical ingredients from: {input_path}")
        ingredients: List[Dict] = json.loads(input_path.read_text(encoding="utf-8"))
        log(f"[*] Total ingredients before migrate: {len(ingredients)}")

        existing = index_existing_ingredients(ingredients)
        log(f"[*] Indexed {len(existing)} existing keys (names + ids)")

        new_ingredients: List[Dict] = []
        migrated_names: Set[str] = set()   # để remove khỏi variations
        skipped_nutrition: List[str] = []  # log cho vui, để biết có gì bị skip
        removed_existing_variants: List[str] = []  # log các ingredient đã tồn tại bị remove
        
        # Pass 1: Filter ingredients đã tồn tại - nếu là variant của FALSE_VARIATION_EXCEPTIONS, 
        # remove nó và thêm vào variations của FALSE_VARIATION_EXCEPTIONS ingredient
        log("\n[*] Pass 1: Filtering existing ingredients that are variants of FALSE_VARIATION_EXCEPTIONS...")
        filtered_ingredients: List[Dict] = []
        false_exception_to_ingredient: Dict[str, Dict] = {}  # Map FALSE_VARIATION_EXCEPTIONS → ingredient
        
        # Build map: FALSE_VARIATION_EXCEPTIONS ingredient → ingredient dict
        for ing in ingredients:
            canonical = ing.get("canonical_name") or ing.get("canonical") or ""
            canonical_lower = canonical.lower().strip()
            if canonical_lower in FALSE_VARIATION_EXCEPTIONS:
                false_exception_to_ingredient[canonical_lower] = ing
        
        # Filter ingredients: remove variants của FALSE_VARIATION_EXCEPTIONS
        for ing in ingredients:
            canonical = ing.get("canonical_name") or ing.get("canonical") or ""
            if not canonical:
                filtered_ingredients.append(ing)
                continue
            
            canonical_lower = canonical.lower().strip()
            
            # Check nếu ingredient này là variant của FALSE_VARIATION_EXCEPTIONS
            if is_variant_of_false_exception(canonical):
                # Tìm FALSE_VARIATION_EXCEPTIONS ingredient cha
                parent_ing = None
                sorted_exceptions = sorted(FALSE_VARIATION_EXCEPTIONS.keys(), key=len, reverse=True)
                for exception_key in sorted_exceptions:
                    exception_lower = exception_key.lower().strip()
                    if exception_lower != canonical_lower and exception_lower in canonical_lower:
                        pattern = r'\b' + re.escape(exception_lower) + r'\b'
                        if re.search(pattern, canonical_lower, re.IGNORECASE):
                            if exception_lower in false_exception_to_ingredient:
                                parent_ing = false_exception_to_ingredient[exception_lower]
                                break
                
                if parent_ing:
                    # Thêm vào variations của parent ingredient
                    parent_variations = parent_ing.get("variations") or {}
                    if "other" not in parent_variations:
                        parent_variations["other"] = []
                    if canonical not in parent_variations["other"]:
                        parent_variations["other"].append(canonical)
                        parent_ing["variations"] = parent_variations
                        log(f"  ⊘ [removed] Remove ingredient: {canonical} (variant của '{parent_ing.get('canonical_name')}')")
                        log(f"    → Added to variations of '{parent_ing.get('canonical_name')}'")
                        removed_existing_variants.append(canonical)
                    else:
                        # Already in variations, just remove ingredient
                        log(f"  ⊘ [removed] Remove ingredient: {canonical} (variant của '{parent_ing.get('canonical_name')}', already in variations)")
                        removed_existing_variants.append(canonical)
                else:
                    # Không tìm thấy parent, giữ nguyên nhưng log warning
                    log(f"  ⚠ [warning] Ingredient '{canonical}' is variant of FALSE_VARIATION_EXCEPTIONS but parent not found, keeping it")
                    filtered_ingredients.append(ing)
            else:
                # Không phải variant của FALSE_VARIATION_EXCEPTIONS, giữ nguyên
                filtered_ingredients.append(ing)
        
        log(f"[*] Pass 1 done: Removed {len(removed_existing_variants)} existing ingredients that are variants of FALSE_VARIATION_EXCEPTIONS")
        log(f"    Remaining ingredients: {len(filtered_ingredients)}/{len(ingredients)}")
        
        # Update ingredients list và existing index
        ingredients = filtered_ingredients
        existing = index_existing_ingredients(ingredients)
        log(f"[*] Re-indexed {len(existing)} existing keys (names + ids)")

        # Pass 2: Duyệt qua từng ingredient base để migrate variations
        for base_ing in ingredients:
            base_canonical = base_ing.get("canonical_name") or base_ing.get("canonical")
            if not base_canonical:
                continue

            base_category = base_ing.get("category")
            variations = base_ing.get("variations") or {}

            if not variations:
                continue

            log(f"\n[*] Base: {base_canonical} (category={base_category})")

            # Ta sẽ build lại variations sau khi remove những cái đã migrate
            new_variations: Dict[str, List[str]] = {}
            for bucket_name, names in variations.items():
                if not isinstance(names, list):
                    continue

                kept_names: List[str] = []

                for name in names:
                    if not isinstance(name, str) or not name.strip():
                        continue

                    name_stripped = name.strip()
                    name_key = "name:" + normalize_name_for_key(name_stripped)

                    # 1) Kiểm tra nếu có preparation/modifier words HOẶC brand name 
                    # HOẶC là variation của FALSE_VARIATION_EXCEPTIONS → KHÔNG tạo ingredient mới
                    # Chỉ tạo ingredients riêng cho variants THẬT SỰ cần thiết
                    if is_nutrition_variant(name_stripped, bucket_name):
                        skipped_nutrition.append(name_stripped)
                        kept_names.append(name_stripped)   # vẫn giữ trong variations
                        if bucket_name and bucket_name.lower() == "nutrition":
                            log(f"  ⊘ [nutrition] Skip migrate: {name_stripped}")
                        elif is_variant_of_false_exception(name_stripped):
                            log(f"  ⊘ [false_exception] Skip migrate: {name_stripped} (variation của FALSE_VARIATION_EXCEPTIONS ingredient)")
                        elif has_brand_name(name_stripped):
                            log(f"  ⊘ [brand] Skip migrate: {name_stripped} (có brand name)")
                        elif has_preparation_modifier(name_stripped):
                            log(f"  ⊘ [modifier] Skip migrate: {name_stripped} (có preparation/modifier words)")
                        else:
                            log(f"  ⊘ [nutrition] Skip migrate: {name_stripped}")
                        continue

                    # 2) Nếu ingredient này đã tồn tại rồi (do bạn add trước đó) → chỉ giữ trong variations
                    if name_key in existing:
                        kept_names.append(name_stripped)
                        log(f"  ✓ Already exists as ingredient: {name_stripped}")
                        continue

                    # 3) Tạo ingredient mới
                    variant_ing = create_variant_ingredient(
                        variant_name=name_stripped,
                        base_canonical=base_canonical,
                        base_category=base_category,
                    )

                    new_ing_id = variant_ing["ingredient_id"]
                    key_new_name = "name:" + normalize_name_for_key(name_stripped)
                    key_new_id = "id:" + new_ing_id.lower()

                    # Update index để không tạo trùng nếu variant lặp lại ở base khác
                    existing[key_new_name] = variant_ing
                    existing[key_new_id] = variant_ing

                    new_ingredients.append(variant_ing)
                    migrated_names.add(name_stripped)

                    log(f"  + Migrate variation → Ingredient: {name_stripped} -> {new_ing_id}")

                    # Vì variant đã thành ingredient riêng, thường ta không cần giữ lại trong variations
                    # nên KHÔNG cho vào kept_names

                if kept_names:
                    new_variations[bucket_name] = kept_names

            # Cập nhật variations sau khi migrate
            base_ing["variations"] = new_variations

        # Gộp ingredients cũ + mới
        if new_ingredients:
            log(f"\n[*] Total new ingredients created: {len(new_ingredients)}")
            ingredients.extend(new_ingredients)
        else:
            log("\n[*] No new ingredients created.")

        # Sort lại cho dễ đọc
        ingredients.sort(key=lambda x: (x.get("canonical_name") or "").lower())

        # Ghi file
        log(f"[*] Writing migrated ingredients to: {output_path}")
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(
            json.dumps(ingredients, ensure_ascii=False, indent=2),
            encoding="utf-8"
        )

        log("\n[OK] Migration done!")
        log(f"    Total ingredients after migrate: {len(ingredients)}")
        log(f"    Existing ingredients removed (FALSE_VARIATION_EXCEPTIONS variants): {len(removed_existing_variants)}")
        log(f"    New ingredients created: {len(new_ingredients)}")
        log(f"    Nutrition variants skipped: {len(skipped_nutrition)}")
        log(f"\n[*] Log file saved to: {log_file_path}")
        
        # Chỉ print summary cuối cùng ra console
        print(f"\n[OK] Migration done!")
        print(f"    Total ingredients after migrate: {len(ingredients)}")
        print(f"    Existing ingredients removed (FALSE_VARIATION_EXCEPTIONS variants): {len(removed_existing_variants)}")
        print(f"    New ingredients created: {len(new_ingredients)}")
        print(f"    Nutrition variants skipped: {len(skipped_nutrition)}")
        print(f"    Log file saved to: {log_file_path}")
    finally:
        log_file.close()


def main():
    parser = argparse.ArgumentParser(
        description="Migrate variations trong canonical_ingredients.json → Ingredient riêng (skip nutrition variants)."
    )
    parser.add_argument(
        "--input",
        type=str,
        default="canonical_ingredients.json",
        help="Path đến canonical_ingredients.json (có thể relative hoặc absolute)"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="canonical_ingredients_migrated.json",
        help="Path output sau khi migrate (khuyên không ghi đè lúc test lần đầu)"
    )
    args = parser.parse_args()

    script_dir = Path(__file__).parent

    # Resolve input
    if os.path.isabs(args.input):
        input_path = Path(args.input)
    elif args.input.startswith("data/"):
        backend_root = Path(backend_dir)
        input_path = backend_root / args.input
    else:
        input_path = script_dir / args.input

    # Resolve output
    if os.path.isabs(args.output):
        output_path = Path(args.output)
    elif args.output.startswith("data/"):
        backend_root = Path(backend_dir)
        output_path = backend_root / args.output
    else:
        output_path = script_dir / args.output

    if not input_path.exists():
        print(f"[ERROR] Input file not found: {input_path}")
        sys.exit(1)

    # Tạo log file path (cùng thư mục với output, tên file .log.txt)
    log_file_path = output_path.with_suffix('.log.txt')

    migrate_variations(input_path, output_path, log_file_path)


if __name__ == "__main__":
    main()
