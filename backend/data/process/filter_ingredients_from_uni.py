 #!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Filter ingredients from in.txt based on uni_ingredients.csv

Usage:
  python filter_ingredients_from_uni.py \
    --input data/process/filtered_in.txt \
    --uni data/process/uni_ingredients.csv \
    --output data/process/filtered_in.txt
"""

import re
import csv
from pathlib import Path
from typing import Set, List
import argparse

processing_words = [
        'mix', 'extract', 'sliced', 'slice', 'diced', 'dice',"breakfast","extra","regular",
        'chopped', 'chop', 'minced', 'mince', 'grind',"mission","style","grits","or",
        'grated', 'grate', 'shredded', 'shred', 'crushed', 'crush',"cut","grilled",
        'peeled', 'peel''pitted', 'pit',"baked","baking","base","for","bass","homestyl",
        'cored', 'core', 'halved', 'halves', 'quartered', 'quarters', 'pickled',"lo bok",
        'unsalted', 'salted', 'plain', 'unflavored',"condensed","topping","fat","salad"
        'low-fat', 'low fat', 'fat-free', 'fat free', 'reduced-fat',"style","flavored","flavor","flavors",
        'full-fat', 'full fat', 'non-fat', 'non fat', 'conventional',"cooked","cooking","urad dal split",
        'large', 'medium', 'small', 'extra-large', 'extra large', 'ap',"spread","double","v 8 juice",
        'well', 'rinsed', 'packed', 'in',"mixture","mixed","of","with","and","dark","dr.","long","substitute"
    ]

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
    "cool whip", "miracle whip", "crisco", "bisquick", "pam", "jello","breakstone","knorr"
]

# Common country names to remove
country_names = [
    'vietnam', 'vietnamese', 'viet', 'viet nam',
    'thailand', 'thai',"asia","asian","european","europe",
    'china', 'chinese',
    'japan', 'japanese',
    'korea', 'korean',"english",
    'india', 'indian',
    'italy', 'italian',
    'france', 'french',
    'spain', 'spanish',
    'mexico', 'mexican',
    'germany', 'german',
    'greece', 'greek',
    'turkey', 'turkish',
    'philippines', 'filipino', 'philippine',
    'indonesia', 'indonesian',
    'malaysia', 'malaysian',
    'singapore', 'singaporean',
    'cambodia', 'cambodian',
    'laos', 'laotian',
    'myanmar', 'burmese',
    'usa', 'american', 'us',
    'britain', 'british', 'uk',
    'australia', 'australian',
    'canada', 'canadian',
    'brazil', 'brazilian',
    'argentina', 'argentinian',
    'peru', 'peruvian',
    'chile', 'chilean',
    'colombia', 'colombian',
    'morocco', 'moroccan',
    'egypt', 'egyptian',
    'lebanon', 'lebanese',
    'israel', 'israeli',
    'russia', 'russian',
    'poland', 'polish',
    'czech', 'czech republic',
    'hungary', 'hungarian',
    'romania', 'romanian',
    'portugal', 'portuguese',
    'netherlands', 'dutch',
    'belgium', 'belgian',
    'switzerland', 'swiss',
    'austria', 'austrian',
    'sweden', 'swedish',
    'norway', 'norwegian',
    'denmark', 'danish',
    'finland', 'finnish'
]
def load_ingredients_from_uni(csv_path: Path) -> Set[str]:
    """
    Load all ingredient words from uni_ingredients.csv
    Returns a set of normalized ingredient words
    """
    ingredients_set = set()
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            ingredients_str = row.get('ingredients', '')
            # Split by comma and clean each ingredient
            for ingredient in ingredients_str.split(','):
                ingredient = ingredient.strip().lower()
                if ingredient:
                    # Add the full ingredient name
                    ingredients_set.add(ingredient)
                    # Also add individual words from the ingredient
                    words = re.findall(r'\b\w+\b', ingredient)
                    for word in words:
                        if len(word) > 2:  # Skip very short words
                            ingredients_set.add(word)
    
    return ingredients_set


def has_common_suffix(text: str) -> bool:
    """
    Check if text contains common ingredient suffixes
    """
    common_suffixes = [
        'oil', 'flour', 'seed', 'powder', 'broth', 'breast',
        'sauce', 'paste', 'juice', 'vinegar', 'butter', 'cheese',
        'cream', 'milk', 'yogurt', 'sugar', 'salt', 'pepper',
        'spice', 'herb', 'seasoning', 'base', 'stock',
        'noodle', 'pasta', 'rice', 'bean', 'lentil', 'pea',
        'chicken', 'beef', 'pork', 'fish', 'shrimp', 'crab',
        'tomato', 'onion', 'garlic', 'ginger', 'pepper',
        'apple', 'banana', 'orange', 'lemon', 'lime',
        'bread', 'roll', 'tortilla', 'wrap', 'cracker',
        'cookie', 'cake', 'pie', 'pastry', 'dough',
        'soup', 'stew', 'curry', 'marinade', 'dressing',
        'mayonnaise', 'mustard', 'ketchup', 'relish',
        'pickle', 'olive', 'capers', 'anchovy',
        'flakes', 'cereal', 'granola', 'oats',
        'chips', 'crackers', 'pretzels',
        'wine', 'beer', 'liqueur', 'spirits',
        'chocolate', 'vanilla',
        'honey', 'syrup', 'molasses',
        'flakes', 'crumbs', 'breadcrumbs','cheese','meat','leaves','leaf','leave'
    ]
    
    text_lower = text.lower()
    for suffix in common_suffixes:
        # Check if suffix appears as a whole word
        pattern = r'\b' + re.escape(suffix) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    return False


def is_processing_word_only(text: str) -> bool:
    """
    Check if text contains ONLY processing/preparation words (no actual ingredient)
    Returns True if line should be removed (only processing words, no ingredient)
    """
    
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # If no words, return False (don't remove empty lines here)
    if not words:
        return False
    
    # Check if ALL words are processing words
    all_processing = True
    for word in words:
        # Check if this word is a processing word
        is_processing = False
        for proc_word in processing_words:
            # Match as whole word (exact match, case insensitive)
            if word == proc_word.lower():
                is_processing = True
                break
        if not is_processing:
            all_processing = False
            break
    
    return all_processing


def contains_processing_word(text: str) -> bool:
    """
    Check if text contains ANY processing/preparation word
    Returns True if line should be removed (contains processing words)
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Check if ANY word is a processing word
    for word in words:
        for proc_word in processing_words:
            # Match as whole word (exact match, case insensitive)
            if word == proc_word.lower():
                return True
    
    return False


def has_parentheses(text: str) -> bool:
    """
    Check if text contains parentheses ( )
    Returns True if line should be removed (contains parentheses)
    """
    return '(' in text or ')' in text


def contains_country_name(text: str) -> bool:
    """
    Check if text contains any country name
    Returns True if line should be removed (contains country name)
    """
    text_lower = text.lower()
    words = re.findall(r'\b\w+\b', text_lower)
    
    # Check if ANY word is a country name
    for word in words:
        for country in country_names:
            # Match as whole word (exact match, case insensitive)
            if word == country.lower():
                return True
    
    return False


def contains_brand_name(text: str) -> bool:
    """
    Check if text contains any brand name
    Returns True if line should be removed (contains brand name)
    """
    text_lower = text.lower()
    
    # Check for multi-word brand names first (longest first)
    multi_word_brands = [brand for brand in BRAND_LIST if ' ' in brand]
    multi_word_brands.sort(key=len, reverse=True)
    
    for brand in multi_word_brands:
        # Match as whole phrase (case insensitive)
        pattern = r'\b' + re.escape(brand.lower()) + r'\b'
        if re.search(pattern, text_lower):
            return True
    
    # Check for single-word brand names
    words = re.findall(r'\b\w+\b', text_lower)
    for word in words:
        for brand in BRAND_LIST:
            # Match as whole word (exact match, case insensitive)
            if ' ' not in brand and word == brand.lower():
                return True
    
    return False


def contains_number(text: str) -> bool:
    """
    Check if text contains any number (digit)
    Returns True if line should be removed (contains number)
    """
    return bool(re.search(r'\d', text))


def should_keep_line(line: str, ingredients_set: Set[str]) -> bool:
    """
    Check if a line should be kept based on:
    1. Contains any word from uni_ingredients.csv
    2. Contains common ingredient suffixes
    3. NOT contains any processing/preparation words (remove if contains processing words)
    4. NOT has more than 4 words (remove if > 4 words)
    5. NOT contains parentheses (remove if has parentheses)
    6. NOT contains country names (remove if has country names)
    7. NOT contains brand names (remove if has brand names)
    8. NOT contains numbers (remove if has numbers)
    """
    # Check 1: if line contains parentheses, remove it
    if has_parentheses(line):
        return False
    
    # Check 2: if line contains country name, remove it
    if contains_country_name(line):
        return False
    
    # Check 3: if line contains brand name, remove it
    if contains_brand_name(line):
        return False
    
    # Check 4: if line contains number, remove it
    if contains_number(line):
        return False
    
    line_lower = line.lower()
    
    # Extract all words from the line
    words = re.findall(r'\b\w+\b', line_lower)
    
    # Check 5: if line has more than 4 words, remove it
    if len(words) > 4:
        return False
    
    # Check 6: if line contains ANY processing word, remove it
    if contains_processing_word(line):
        return False
    
    # Check 7: if any word matches ingredients from uni_ingredients.csv
    for word in words:
        if word in ingredients_set:
            return True
    
    # Check 8: if line contains common suffixes
    if has_common_suffix(line):
        return True
    
    return False


def filter_ingredients(
    input_path: Path,
    uni_path: Path,
    output_path: Path
) -> tuple[int, int]:
    """
    Filter ingredients from in.txt based on uni_ingredients.csv
    Returns: (total_lines, kept_lines)
    """
    print(f"Loading ingredients from {uni_path}...")
    ingredients_set = load_ingredients_from_uni(uni_path)
    print(f"Loaded {len(ingredients_set)} ingredient words from uni_ingredients.csv")
    
    print(f"Reading lines from {input_path}...")
    with open(input_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f if line.strip()]
    
    total_lines = len(lines)
    print(f"Total lines: {total_lines}")
    
    print("Filtering lines...")
    kept_lines = []
    for line in lines:
        if should_keep_line(line, ingredients_set):
            kept_lines.append(line)
    
    print(f"Kept {len(kept_lines)} lines (removed {total_lines - len(kept_lines)})")
    
    # Write filtered results
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, 'w', encoding='utf-8') as f:
        for line in kept_lines:
            f.write(line + '\n')
    
    print(f"Saved filtered results to {output_path}")
    
    return total_lines, len(kept_lines)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Filter ingredients from in.txt based on uni_ingredients.csv"
    )
    parser.add_argument(
        "--input",
        type=str,
        default="data/process/filtered_in.txt",
        help="Path to input file (in.txt)"
    )
    parser.add_argument(
        "--uni",
        type=str,
        default="data/process/uni_ingredients.csv",
        help="Path to uni_ingredients.csv"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/process/ingredients.txt",
        help="Path to output file"
    )
    
    args = parser.parse_args()
    
    input_path = Path(args.input)
    uni_path = Path(args.uni)
    output_path = Path(args.output)
    
    if not input_path.exists():
        print(f"Error: Input file not found: {input_path}")
        exit(1)
    
    if not uni_path.exists():
        print(f"Error: Uni ingredients file not found: {uni_path}")
        exit(1)
    
    total, kept = filter_ingredients(input_path, uni_path, output_path)
    
    print(f"\nSummary:")
    print(f"  Total lines: {total}")
    print(f"  Kept lines: {kept}")
    print(f"  Removed lines: {total - kept}")
    print(f"  Kept percentage: {kept/total*100:.2f}%")

