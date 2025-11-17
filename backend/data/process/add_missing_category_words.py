#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Check filtered_in.txt against categories in import_ingredients.py
and add missing words
"""

import re
from pathlib import Path
from typing import Set, List

# Extract all category words from import_ingredients.py
def extract_category_words() -> Set[str]:
    """Extract all words from categories in import_ingredients.py"""
    category_words = set()
    
    # Herbs
    herbs = {"basil", "parsley", "cilantro", "thyme", "rosemary", "oregano", "dill", "mint", "tarragon", "sage", "marjoram", "lemongrass"}
    category_words.update(herbs)
    
    # Meats
    meats = {
        "beef", "pork", "chicken", "bacon", "turkey", "ham", "sausage", "lamb", "breast", "thigh",
        "tenderloin", "cutlet", "sirloin", "ribeye", "prosciutto", "pancetta", "brisket", "oxtail",
        "drumstick", "meatball", "steak", "bologna", "chorizo", "frankfurter", "mortadella",
        "pepperoni", "poultry", "rib", "salami", "tender", "wiener", "hotdog"
    }
    category_words.update(meats)
    
    # Seafood
    seafood = {"fish", "shrimp", "salmon", "tuna", "crab", "mussel", "scallop", "crawfish", "fillet", "bronzino", "crabmeat", "katsuobushi"}
    category_words.update(seafood)
    
    # Dairy
    dairy = {
        "milk", "cheese", "butter", "yogurt", "cream", "buttermilk", "cheddar", "mozzarella", "parmesan",
        "ricotta", "feta", "brie", "gorgonzola", "cream cheese", "sour cream", "creme fraiche",
        "boursin", "fontina", "galbani",
        "ghee", "gruyere", "margarine", "pecorino", "provolone", "reggiano"
    }
    category_words.update(dairy)
    
    # Grain & starch
    grains = {
        "rice", "flour", "bread", "pasta", "noodle", "macaroni", "couscous", "quinoa", "grain", "tortilla",
        "breadcrumb", "cornmeal", "corn", "spaghetti", "penne", "fettuccine", "linguine", "orzo", "rigatoni",
        "ziti", "gnocchi", "farfalle", "rotini", "pita", "naan", "bagel", "biscuit", "roll", "polenta",
        "crust", "cracker", "dough", "tortellini", "ravioli", "baguette", "brioche", "ciabatta",
        "crouton", "corn kernel", "cavatappi", "bucatini", "cornstarch", "flatbread", "fusilli", "cereal"
    }
    category_words.update(grains)
    
    # Baking
    baking = {"egg", "yolk", "yeast", "pastry", "biscotti"}
    category_words.update(baking)
    
    # Vegetables
    vegetables = {
        "tomato", "onion", "garlic", "carrot", "cabbage", "broccoli", "zucchini", "mushroom", "spinach",
        "pepper", "bell pepper", "shallot", "celery", "lettuce", "pea", "cucumber", "potato", "radish", "leek", "kale",
        "cauliflower", "asparagus", "bell", "eggplant", "artichoke", "okra", "choy", "beet", "scallion", "arugula",
        "jalapeno", "pepperoncini",
        "aril", "avocado", "chard", "cob", "parsnip", "pumpkin",
        "romaine", "squash", "tomatillo", "vegetable", "yam", "pimento"
    }
    category_words.update(vegetables)
    
    # Fruits
    fruits = {
        "apple", "banana", "lemon", "orange", "mango", "lime", "pineapple", "peach", "pear", "plum", "fig",
        "avocado", "strawberry", "raisin", "cranberry", "apricot", "nectarine", "melon", "grape", "blueberry", "cherry", "coconut",
        "applesauce", "braeburn", "craisin", "fuji", "gala"
    }
    category_words.update(fruits)
    
    # Plant proteins
    plant_proteins = {"tofu", "bean", "kidney bean", "chickpea", "blackbean", "black bean", "lentil", "edamame", "pinto"}
    category_words.update(plant_proteins)
    
    # Condiments
    condiments = {
        "soy", "ketchup", "mustard", "mayonnaise", "salsa", "pesto", "guacamole", "chutney", "tahini",
        "harissa", "sriracha", "tabasco", "gochujang", "worcestershire", "tamari", "miso", "dijon",
        "horseradish", "relish", "marinade", "glaze", "dressing", "gravy", "broth", "stock", "bouillon",
        "canola oil", "cholula", "crema", "giardiniera", "kraut", "kimchi", "labneh", "marmalade", "mirin",
        "olive oil", "ranch", "pickle", "sauerkraut", "truffle oil", "furikake", "dashi", "caper", "cornichon", "vinegar"
    }
    category_words.update(condiments)
    
    # Sauces
    sauces = {
        "soy sauce", "fish sauce", "tomato sauce", "bbq sauce", "chili sauce", "hoisin sauce",
        "oyster sauce", "teriyaki", "alfredo", "bolognese", "adobo", "marinara", "oelek", "tzatziki", "verde"
    }
    category_words.update(sauces)
    
    # Seasonings
    seasonings = {
        "salt", "black pepper", "white pepper", "paprika", "cumin", "chili", "cayenne", "turmeric", "cinnamon", "nutmeg",
        "allspice", "curry", "masala", "anise", "cardamom", "sumac", "seasoning", "spice", "accent", "chile", "chipotle", "clove", "coriander",
        "ginger", "hanout", "madras", "peppercorn", "redhot"
    }
    category_words.update(seasonings)
    
    # Nuts & seeds
    nuts_seeds = {"peanut", "walnut", "pepita", "almond", "cashew", "pistachio", "pecan", "pine nut", "sesame", "chia", "flax", "sunflower", "nut"}
    category_words.update(nuts_seeds)
    
    # Beverages
    beverages = {"wine", "beer", "merlot", "limoncello", "juice", "grigio", "vodka", "whiskey", "bourbon", "sake", "vermouth", "cider", "coffee", "espresso", "tea", "water", "ale", "sherry"}
    category_words.update(beverages)
    
    # Sweeteners
    sweeteners = {"molass", "caramel", "vanilla", "honey", "syrup", "sugar"}
    category_words.update(sweeteners)
    
    return category_words


def normalize_text(text: str) -> str:
    """Normalize text to lowercase and clean"""
    return text.strip().lower()


def extract_words_from_line(line: str) -> List[str]:
    """Extract all words from a line"""
    line_lower = normalize_text(line)
    words = re.findall(r'\b\w+\b', line_lower)
    return words


def check_and_add_missing(
    filtered_file: Path,
    category_words: Set[str]
) -> tuple[List[str], int]:
    """
    Check filtered_in.txt and find missing category words
    Returns: (missing_words, total_added)
    """
    # Read filtered_in.txt
    with open(filtered_file, 'r', encoding='utf-8') as f:
        lines = [l.strip() for l in f if l.strip()]
    
    # Extract all words from filtered_in.txt
    existing_words = set()
    for line in lines:
        words = extract_words_from_line(line)
        for word in words:
            existing_words.add(word)
        # Also add the full line as a potential match
        existing_words.add(normalize_text(line))
    
    print(f"Total lines in filtered_in.txt: {len(lines)}")
    print(f"Total unique words extracted: {len(existing_words)}")
    print(f"Total category words to check: {len(category_words)}")
    
    # Find missing words
    missing_words = []
    for word in category_words:
        word_lower = normalize_text(word)
        # Check if word exists as a standalone word or in any line
        if word_lower not in existing_words:
            # Check if it's a multi-word phrase
            if ' ' in word_lower:
                # For multi-word phrases, check if all words exist separately
                phrase_words = word_lower.split()
                all_exist = all(w in existing_words for w in phrase_words)
                if not all_exist:
                    missing_words.append(word)
            else:
                missing_words.append(word)
    
    print(f"\nMissing words found: {len(missing_words)}")
    
    # Add missing words to file
    if missing_words:
        # Sort missing words
        missing_words_sorted = sorted(missing_words, key=str.lower)
        
        # Append to file
        with open(filtered_file, 'a', encoding='utf-8') as f:
            for word in missing_words_sorted:
                f.write(word + '\n')
        
        print(f"Added {len(missing_words)} missing words to {filtered_file}")
        print("\nSample missing words (first 30):")
        for i, word in enumerate(missing_words_sorted[:30], 1):
            print(f"  {i}. {word}")
    else:
        print("No missing words found!")
    
    return missing_words, len(missing_words)


if __name__ == "__main__":
    filtered_file = Path("data/process/ingredients.txt")
    
    if not filtered_file.exists():
        print(f"Error: File not found: {filtered_file}")
        exit(1)
    
    print("Extracting category words from import_ingredients.py...")
    category_words = extract_category_words()
    
    print(f"\nChecking {filtered_file}...")
    missing_words, added_count = check_and_add_missing(filtered_file, category_words)
    
    print(f"\nSummary:")
    print(f"  Total category words: {len(category_words)}")
    print(f"  Missing words: {len(missing_words)}")
    print(f"  Added to file: {added_count}")

