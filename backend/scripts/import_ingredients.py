import re
import json
from pathlib import Path
import sys, os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from config import NON_ING_WORDS, FIX_MAP, ALT_MAP, DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB



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
    n = name.lower().strip()

    # 🌿 Herbs
    if n in {"basil", "parsley", "cilantro", "thyme", "rosemary", "oregano", "dill", "mint", "tarragon", "sage","marjoram"}:
        return "herb"

    # 🥩 Meats
    if n in {
        "beef", "pork", "chicken", "bacon", "turkey", "ham", "sausage", "lamb", "breast", "thigh",
        "tenderloin", "cutlet", "sirloin", "ribeye", "prosciutto", "pancetta", "brisket", "oxtail",
        "drumstick", "meatball", "steak","bologna", "chorizo", "frankfurter", "mortadella",
        "pepperoni", "poultry",  "rib", "salami", "tender", "wiener","hotdog "
        }:
        return "meat"

    # 🐟 Seafood
    if n in {"fish", "shrimp", "salmon", "tuna", "crab", "mussel", "scallop", "crawfish", "fillet","bronzino", "crapmeat","katsuobushi"
}:
        return "seafood"

    # 🧀 Dairy
    if n in {
        "milk", "cheese", "butter", "yogurt", "cream", "buttermilk", "cheddar", "mozzarella", "parmesan",
        "ricotta", "feta", "brie", "gorgonzola", "cream cheese", "sour cream", "creme fraiche",
        "almondmilk", "boursin", "cheese", "fontina", "fraiche", "galbani",
        "ghee", "gruyere", "margarine", "pecorino", "provolone", "reggiano"
    }:
        return "dairy"

    # 🍞 Grain & starch
    if n in {
        "rice", "flour", "bread", "pasta", "noodle", "macaroni", "couscous", "quinoa", "grain", "tortilla",
        "breadcrumb", "cornmeal", "corn", "spaghetti", "penne", "fettuccine", "linguine", "orzo", "rigatoni",
        "ziti", "gnocchi", "farfalle", "rotini", "pita", "naan", "bagel", "biscuit", "roll", "polenta",
        "pastry", "crust", "cracker", "dough", "tortellini", "ravioli", "baguette", "biscotti",  "brioche" "ciabatta",
         "crouton", "corn kernel", "cavatappi", "bucatini", "cornstarch","couscous","flatbread","fusilli","baguette","cereal"
    }:
        return "grain"

    # 🥚 Baking
    if n in {"egg", "yolk", "baking", "yeast", "muffin", "cake", "pie", "pancake", "waffle", "pastry"}:
        return "baking"

    # 🥦 Vegetables
    if n in {
        "tomato", "onion", "garlic", "carrot", "cabbage", "broccoli", "zucchini", "mushroom", "spinach",
        "pepper", "shallot", "celery", "lettuce", "pea", "cucumber", "potato", "radish", "leek", "kale",
        "cauliflower", "asparagus", "bell", "eggplant", "artichok", "okra", "choy", "beet", "scallion", "arugula",
        "aril", "avocado", "bay", "caper", "chard", "chive", "cob", "cornichon", "lemongras", "parsnip", "pumpkin",
        "romaine", "squash", "tomatillo", "vegetable","yam","pimento"

    }:
        return "vegetable"

    # 🍊 Fruits
    if n in {
        "apple", "banana", "lemon", "orange", "mango", "lime", "pineapple", "peach", "pear", "plum", "fig",
        "avocado", "strawberry", "raisin", "cranberry", "apricot", "nectarine", "melon", "grape", "blueberry", "cherry", "coconut",
        "applesauce", "braeburn", "craisin", "fuji", "gala", "hawaiian"

    }:
        return "fruit"

    # 🫘 Plant proteins
    if n in {"tofu", "bean", "kidney bean", "chickpea", "blackbean", "black bean", "lentil", "edamame", "pinto", "black bean", "kidney bean"}:
        return "plant_protein"

    # 🍯 Condiments 
    if n in {
        "soy", "ketchup", "mustard", "mayonnaise", "salsa", "pesto", "guacamole", "chutney", "tahini",
        "harissa", "sriracha", "tabasco", "gochujang", "worcestershire", "tamari", "miso", "dijon",
        "horseradish", "relish", "marinade", "glaze", "dressing", "gravy", "broth", "stock", "bouillon",
        "ale", "canola", "cholula", "crema", "giardiniera", "heinz", "kraut", "kimchi", "kraft", "labneh", "marmalade", "mirin", "oil",
        "olive", "ranch", "pickle","rotel", "sauerkraut", "soup", "truffle", "furikake", "dashi", "pepper"

    }:
        return "condiment"

    # 🍲 Sauces
    if n in {
        "sauce", "soy sauce", "fish sauce", "tomato sauce", "bbq sauce", "chili sauce", "hoisin sauce",
        "oyster sauce", "teriyaki", "alfredo", "bolognese","adobo", "marinara", "oelek", "tzatziki", "sherry", "vinegar", "verde"

    }:
        return "sauce"

    # 🧂 Seasonings 
    if n in {
        "salt", "pepper", "paprika", "cumin", "chili", "cayenne", "turmeric", "cinnamon", "nutmeg",
        "allspice", "curry", "masala", "anise", "cardamom", "sumac", "seasoning", "spice","accent",  "chile", "chilli", "chipotle", "clove", "coriander",
        "ginger", "hanout", "jalapeno","pepperoncini", "herb", "madras", "peppercorn", "redhot", "season", "sugar"

    }:
        return "seasoning"

    # 🌰 Nuts & seeds
    if n in {"peanut", "walnut", "pepita","almond", "cashew", "pistachio", "pecan", "pine nut", "sesame", "chia", "flax", "sunflower", "nut"}:
        return "nut_or_seed"

    # 🍷 Beverages
    if n in {"wine", "beer", "merlot", "limoncello" ,"juice", "grigio", "vodka", "whiskey", "bourbon", "sake", "vermouth", "cider", "coffee", "espresso", "tea", "water"}:
        return "beverage"

    # 🍬 Sweeteners / flavor bases
    if n in { "molass", "marshmallow", "caramel", "vanilla", "honey", "syrup"}:
        return "sweetener"

    return "other"

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