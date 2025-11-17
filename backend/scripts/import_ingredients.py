import re
import json
from pathlib import Path
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config import NON_ING_WORDS, FIX_MAP, ALT_MAP, DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

# ====================================================
# Category Definitions (shared by guess_category and get_category_base_words)
# ====================================================
CATEGORY_HERBS = {"basil","chive", "parsley", "cilantro", "thyme", "rosemary", "oregano", "dill", "mint", "tarragon", "sage", "marjoram", "lemongrass", "lavender"}

CATEGORY_MEATS = {
    "beef", "pork", "chicken", "bacon", "turkey", "ham", "sausage", "lamb", "breast", "thigh",
    "tenderloin", "cutlet", "sirloin", "ribeye", "prosciutto", "pancetta", "brisket", "oxtail",
    "drumstick", "meatball", "steak", "bologna", "chorizo", "frankfurter", "mortadella",
    "pepperoni", "poultry", "rib", "salami", "tender", "wiener", "hotdog","duck","buffalo",
    "boar", "fowl", "goat", "goose", "guinea hen", "pheasant", "quail", "rabbit", "squirrel",
    "venison", "bison", "mutton", "meat", "hot dog", "kielbasa", "bratwurst", "hog jowl", "rasher"
}

CATEGORY_SEAFOOD = {"fish","anchovy", "shrimp", "salmon", "tuna", "crab", "mussel", "scallop", "crawfish", "fillet", "bronzino", "crabmeat", "katsuobushi", "king crab", "lobster", "anovy", "crayfish", "bluefish",
    "cod", "prawn", "bonito", "haddock", "mackerel", "trout", "snapper", "eel", "kelp", "sardine", "sardin",
    "whitefish", "sea bream", "red mullet", "red sockeye", "red drum", "clam", "caviar", "beluga caviar"}

CATEGORY_DAIRY = {
    "milk", "cheese", "butter", "yogurt", "cream", "buttermilk", "cheddar", "mozzarella", "parmesan",
    "ricotta", "feta", "brie", "gorgonzola", "cream cheese", "sour cream", "creme fraiche",
    "boursin", "fontina", "galbani",
    "ghee", "gruyere", "margarine", "pecorino", "provolone", "reggiano","chocolate", "gouda"
}

CATEGORY_GRAINS = {
    "rice", "flour", "bread", "pasta", "noodle", "macaroni", "couscous", "quinoa", "grain", "tortilla",
    "breadcrumb", "cornmeal", "corn", "spaghetti", "penne", "fettuccine", "linguine", "orzo", "rigatoni",
    "ziti", "gnocchi", "farfalle", "rotini", "pita", "naan", "bagel", "biscuit", "roll", "polenta",
    "crust", "cracker", "dough", "tortellini", "ravioli", "baguette", "brioche", "ciabatta",
    "crouton", "corn kernel", "cavatappi", "bucatini", "cornstarch", "flatbread", "fusilli", "cereal",
    "lasagna", "barley", "wheat", "rye", "oats", "oat", "buckwheat", "bulgur", "farro", "millet",
    "sorghum", "spelt", "teff", "semolina", "amaranth","crumb "
    "starch", "meal", "soba", "udon", "pappardelle", "tagliatelle", "pretzel", "cake", "gluten", "granola"
}

CATEGORY_BAKING = {"egg", "yolk", "yeast", "pastry", "biscotti"}

CATEGORY_VEGETABLES = {
    "tomato", "onion", "garlic", "carrot", "cabbage", "broccoli", "zucchini", "mushroom", "spinach",
    "pepper", "bell pepper", "shallot", "celery", "lettuce", "pea", "cucumber", "potato", "radish", "leek", "kale",
    "cauliflower", "asparagus", "bell", "eggplant", "artichoke", "artichok", "okra", "choy", "beet", "scallion", "arugula",
    "jalapeno", "pepperoncini","cocoa","chestnut","soybean",
    "aril", "avocado", "chard", "cob", "parsnip", "pumpkin",
    "romaine", "squash", "tomatillo", "vegetable", "yam", "pimento","kiwi",
    "daikon", "kohlrabi", "radicchio", "fennel", "rutabaga", "turnip", "turnip green", "collard green",
    "dandelion green", "spring green", "watercress", "watercres", "cloud ear", "bamboo shoot",
    "soybean sprout", "alfalfa sprout", "brussels sprout", "ramp", "lo bok", "baby green"
}

CATEGORY_FRUITS = {
    "apple", "banana", "lemon", "orange", "mango", "lime", "pineapple", "peach", "pear", "plum", "fig",
    "avocado", "strawberry", "raisin", "cranberry", "apricot", "nectarine", "melon", "grape", "blueberry", "cherry", "coconut",
     "craisin", "gala","olive","fruit","grapefruit","guava",
    "currant", "raspberry", "barberry", "papaya", "tangerine", "pomelo", "rhubarb", "soursop", "goji berry",
    "yuzu", "jackfruit", "breadfruit", "date", "pitted date", "medjool date", "mandarin orang",
    "seedless orang", "seville orang", "navel orang", "seedless red grap", "green plantain",
    "kalamata", "manzanilla", "picholine"
}

CATEGORY_PLANT_PROTEINS = {"tofu", "bean", "kidney bean", "chickpea", "blackbean", "black bean", "lentil", "edamame", "pinto"}

CATEGORY_CONDIMENTS = {
    "soy", "ketchup", "mustard", "mayonnaise", "salsa", "pesto", "guacamole", "chutney", "tahini",
    "harissa", "sriracha", "tabasco", "gochujang", "worcestershire", "tamari", "miso", "dijon",
    "horseradish", "relish", "marinade", "glaze", "dressing", "gravy", "broth", "stock", "bouillon",
    "cholula", "crema", "giardiniera", "kraut", "kimchi", "labneh", "marmalade", "mirin",
    "ranch", "pickle", "sauerkraut", "oil", "furikake", "dashi", "caper", "cornichon", "vinegar",
    "concentrate", "puree", "jam", "dip", "soup", "canola", "stew"
}

CATEGORY_SAUCES = {
    "soy sauce", "fish sauce", "tomato sauce", "bbq sauce", "chili sauce", "hoisin sauce",
    "oyster sauce", "teriyaki", "alfredo", "bolognese", "adobo", "marinara", "oelek", "tzatziki", "verde"
}

CATEGORY_SEASONINGS = {
    "salt", "black pepper", "white pepper", "paprika", "cumin", "chili", "cayenne", "turmeric", "cinnamon", "nutmeg",
    "allspice", "curry", "masala", "anise", "cardamom", "sumac", "seasoning", "spice", "accent", "chile", "chipotle", "clove", "coriander",
    "ginger", "hanout", "madras", "peppercorn", "redhot","powder","paste"
}

CATEGORY_NUTS_SEEDS = {"peanut", "walnut", "pepita", "almond", "cashew", "pistachio", "pecan", "pine nut", "sesame", "chia", "flax", "sunflower", "nut"}

CATEGORY_BEVERAGES = {"liqueur","wine", "beer", "merlot", "limoncello", "juice", "grigio", "vodka", "whiskey", "bourbon", "sake", "vermouth", "cider", "coffee", "espresso", "tea", "water", "ale", "sherry", "liqueur"}

CATEGORY_SWEETENERS = {"molass", "molasses", "caramel", "vanilla", "honey", "syrup", "sugar","candy"}
# Category mapping for guess_category
CATEGORY_MAP = [
    (CATEGORY_HERBS, "herb"),
    (CATEGORY_MEATS, "meat"),
    (CATEGORY_SEAFOOD, "seafood"),
    (CATEGORY_DAIRY, "dairy"),
    (CATEGORY_GRAINS, "grain"),
    (CATEGORY_BAKING, "baking"),
    (CATEGORY_VEGETABLES, "vegetable"),
    (CATEGORY_FRUITS, "fruit"),
    (CATEGORY_PLANT_PROTEINS, "plant_protein"),
    (CATEGORY_CONDIMENTS, "condiment"),
    (CATEGORY_SAUCES, "sauce"),
    (CATEGORY_SEASONINGS, "seasoning"),
    (CATEGORY_NUTS_SEEDS, "nut_or_seed"),
    (CATEGORY_BEVERAGES, "beverage"),
    (CATEGORY_SWEETENERS, "sweetener"),
]


def generate_alt(name: str):
    n = name.lower()
    if n in ALT_MAP:
        return ALT_MAP[n]
    if n.endswith("y"):
        return [n[:-1] + "ies"]
    elif n.endswith("s"):
        return []
    elif n.endswith(("x", "ch", "sh")):
        return [n + "es"]
    else:
        return [n + "s"]

# ====================================================
# 4️⃣ Phân loại nguyên liệu (Category tách riêng)
# ====================================================
def guess_category(name: str) -> str:
    """
    Guess ingredient category based on name.
    Checks exact matches first, then checks if category words appear in the name.
    """
    n = name.lower().strip()
    
    # Check exact matches first
    for category_set, category_name in CATEGORY_MAP:
        if n in category_set:
            return category_name
    
    # Check if any category word/phrase appears in the name
    # Check multi-word phrases first (longest first)
    for category_set, category_name in CATEGORY_MAP:
        multi_word = [w for w in category_set if ' ' in w]
        multi_word.sort(key=len, reverse=True)
        for phrase in multi_word:
            pattern = r'\b' + re.escape(phrase) + r'\b'
            if re.search(pattern, n):
                return category_name
    
    # Then check single words
    for category_set, category_name in CATEGORY_MAP:
        for word in category_set:
            if ' ' not in word:
                pattern = r'\b' + re.escape(word) + r'\b'
                if re.search(pattern, n):
                    return category_name
    
    
    
    return "other"


def get_category_base_words() -> set:
    """
    Get all base words from categories.
    These are the main ingredient names that should be used as base_name.
    Returns a set of all category words (including multi-word phrases and individual words).
    """
    category_words = set()
    
    # Extract all words: keep multi-word phrases as-is, and also add individual words
    for category_set, _ in CATEGORY_MAP:
        for item in category_set:
            # Add the full phrase (e.g., "king crab", "cream cheese")
            category_words.add(item)
            # Also add individual words from multi-word phrases (e.g., "king", "crab", "cream", "cheese")
            category_words.update(item.split())
    
    return category_words


def get_base_group_to_category() -> dict:
    """
    Get mapping from characteristic words (base_group) to category names.
    This maps words like "sauce", "juice", "pepper" to their corresponding categories.
    Returns a dictionary: {base_group_word: category_name}
    """
    base_group_to_category = {}
    
    # Map each word in category sets to its category name
    for category_set, category_name in CATEGORY_MAP:
        for item in category_set:
            # For single words, map directly
            if ' ' not in item:
                base_group_to_category[item] = category_name
            # For multi-word phrases, also map individual words
            # But prioritize the category of the phrase
            words = item.split()
            for word in words:
                # Only add if not already mapped (to avoid overwriting more specific mappings)
                if word not in base_group_to_category:
                    base_group_to_category[word] = category_name
    return base_group_to_category

# ====================================================
# 5️⃣ Tạo danh sách đối tượng nguyên liệu
# ====================================================
def build_ingredient_objects(lines):
    out = []
    for name in lines:
        name = name.strip().lower()
        if not name or len(name) < 2:
            continue
        if name in FIX_MAP:
            name = FIX_MAP[name]
        if name in NON_ING_WORDS:
            continue
        if re.fullmatch(r"[0-9\.]+", name):
            continue
        if name.endswith(("ed", "ing", "ly", "ness")):
            continue

        clean = re.sub(r"[^a-z0-9]+", "_", name)
        obj = {
            "id": f"ing_{clean}",
            "canonical": name,
            "category": guess_category(name),
            "alt": generate_alt(name),
        }
        out.append(obj)
    return out

# ====================================================
# 6️⃣ Xuất file Cypher để import vào Neo4j
# ====================================================
def build_cypher(rows):
    cypher = [
        ":param rows => " + json.dumps({"rows": rows}, ensure_ascii=False) + ";",
        "UNWIND $rows AS ing",
        "MERGE (i:Ingredient {ingredient_id: ing.id})",
        "SET i.canonical_name = ing.canonical,",
        "    i.category = ing.category,",
        "    i.alt_names = coalesce(ing.alt, [])"
    ]
    return "\n".join(cypher)

# ====================================================
# 🚀 MAIN
# ====================================================
if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Build Ingredient JSON and Cypher import for Neo4j")
    parser.add_argument("--input", type=str, default="data/ingredients/data.txt", help="Path to ingredient text file (one name per line)")
    parser.add_argument("--out-json", type=str, default="data/ingredients/ingredients.json", help="Path to export JSON output")
    parser.add_argument("--out-cypher", type=str, default="data/ingredients/ingredients_import.cypher", help="Path to export Cypher file")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASS)
    parser.add_argument("--db", dest="database", default=DEFAULT_DB)
    parser.add_argument("--use-driver", action="store_true", help="Send data directly to Neo4j via Python driver instead of writing file")
    
    parser.add_argument("--verbose", action="store_true", help="Print debug logs")
    args = parser.parse_args()

    # Đọc file text nguyên liệu
    txt_path = Path(args.input)
    lines = [l.strip() for l in txt_path.read_text(encoding="utf-8").splitlines() if l.strip()]
    ingredients = build_ingredient_objects(lines)
    print(f"✅ Loaded {len(ingredients)} valid ingredients from {txt_path}")

    # Xuất JSON
    json_path = Path(args.out_json)
    json_path.parent.mkdir(parents=True, exist_ok=True)
    json_path.write_text(json.dumps(ingredients, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"💾 Exported {len(ingredients)} ingredients to {json_path}")

    # Xuất Cypher
    cypher = build_cypher(ingredients)
    cypher_path = Path(args.out_cypher)
    cypher_path.write_text(cypher, encoding="utf-8")
    print(f"📄 Wrote Cypher import file to {cypher_path}")

    # (Optional) nhập trực tiếp lên Neo4j bằng Python driver
    if args.use_driver:
        from neo4j import GraphDatabase
        driver = GraphDatabase.driver(args.uri, auth=(args.user, args.password))
        with driver.session(database=args.database) as session:
            query = """
            UNWIND $rows AS ing
            MERGE (i:Ingredient {ingredient_id: ing.id})
            SET i.canonical_name = ing.canonical,
                i.category = ing.category,
                i.alt_names = coalesce(ing.alt, [])
            """
            session.run(query, {"rows": ingredients}).consume()
        driver.close()
        print(f"🚀 Imported {len(ingredients)} ingredients directly into Neo4j")

    # Preview 10 dòng đầu
    if args.verbose:
        for i in ingredients[:10]:
            print(i)