DEFAULT_URI = "bolt://localhost:7687"
DEFAULT_USER = "neo4j"
DEFAULT_PASS = "Admin123!"
DEFAULT_DB   = "test"
DEFAULT_BATCH = 5000
TOP_TERMS_PER_RECIPE = 512
NON_ING_WORDS = {
    "about", "above", "and", "approx", "approximately", "as", "at", "bag", "baked", "baking", "beaten", "below", "boiled",
"boneles", "brand", "bottle", "bowl", "by", "choice", "chopped", "chunk", "cleaned", "coarsely", "cooked", "container",
"cored", "crushed", "crumb", "crumbled", "cub", "cubed", "cut", "desired", "direction", "discarded", "divided", "diced",
"drained", "each", "etc", "finely", "flake", "floret", "for", "form", "from", "fried", "fri", "frying", "garnish", "grated",
"ground", "half", "halved", "it", "in", "into", "instruction", "juiced", "kind", "kit", "large", "leaf", "leav", "like", "long",
"medium", "melted", "mix", "more", "needed", "not", "note", "on", "or", "out", "package", "packet", "pan", "peeled", "per",
"piece", "pitted", "pkg", "portion", "preferred", "prepared", "prepar", "quarter", "quartered", "reserved", "rinsed",
"removed", "roasted", "roughly", "roughlychopped", "rounded", "seed", "seeded", "serving", "sheet", "shredded",
"sliced", "size", "skinles", "small", "so", "spray", "sprinkled", "strip", "style", "table", "temperature", "thin",
"thinly", "thick", "thawed", "to", "toasted", "trimmed", "used", "use", "up", "wedg", "wedge", "well", "whole",
"widthwise", "with", "within", "without", "of", "approximate", "alongside", "asia", "asvelveeta", "ball", "bar", "base",
"beauty", "bella", "bia", "bit", "blend", "block", "boneless", "bought", "brine", "brown", "bruschettini", "bunch",
"butte", "cap", "capicola", "capocollo", "casserole", "cheeto", "chuck", "clasico", "coin", "cola", "coleslaw",
"color", "combination", "combo", "comte", "concentrate", "consistency", "crown", "crystal", "cube", "dak", "diagonal",
"diameter", "dice", "dinner", "dip", "dish", "ditalini", "dorito", "drizzle", "dry", "ear", "edg", "eighth", "elbow",
"end", "envelope", "eye", "fage", "file", "firm", "flat", "foil", "fong", "food", "free", "fresco", "frito", "frond",
"frontera", "frozen", "grand", "granul", "grater", "grease", "grill", "grillo", "gs", "halv", "head", "heart", "heat",
"hock", "homemade", "house", "inch", "instant", "italian", "jack", "jam", "jar", "jicama", "jiffy", "jugo", "knorr",
"lady", "larger", "leg", "length", "lengthway", "lengthwise", "les", "light", "link", "liquid", "loaf", "loin", "ma",
"matchstick", "mccormick", "mezzetta", "microplane", "mild", "mincedsalt", "moisture", "normandy", "nugget",
"original", "os", "own", "pace", "paper", "parchment", "part", "past", "paste", "patti", "pearl", "perlini",
"petal", "pickl", "pillsbury", "pod", "potsticker", "preserv", "processor", "provence", "pulp", "puree", "recipe",
"rectangl", "ribbon", "roast", "root", "round", "rub", "sal", "scant", "schubert", "scoop", "segment", "separate",
"serve", "shank", "shap", "shape", "shell", "siciliani", "similar", "skewer", "skillet", "skin", "slaw", "sliver",
"smith", "smithfield", "soda", "sopressata", "spear", "spiral", "split", "spread", "sprig", "sprinkle", "sprout",
"stacker", "stalk", "stem", "stick", "stonefire", "store", "substitute", "swanson", "tail", "taquito", "tartar",
"taste", "temp", "third", "thread", "tin", "tip", "toast", "toothpick", "top", "topper", "torn", "tot", "total", "towel",
"type", "umm", "valentina", "valley", "vre", "whiz", "wieser", "work", "wrapper", "young","extract","black", "green",
"amino", "chip", "chop", "crisp", "crossway", "crosswise","dat", "filet", "flavor", "gallo","zest", "garden",
"glutamate", "greek", "gallo", "kikkoman", "mama", "mandoline","mexicorn", "salata", "twine","clov","white","smoke","chees","baguett"

}

FIX_MAP = {
    "noodl": "noodle",
    "chil": "chili",
    "oliv": "olive",
    "appl": "apple",
    "leav": "leaf",
    "boneles": "boneless",
    "skinles": "skinless",
    "piec": "piece",
    "flak": "flake",
    "wedg": "wedge",
    "crumb": "crumbs",
    "beaten": "egg",
    "thicknes": "thickness",
    "orang": "orange",
    "lim": "lime",
    "veg": "vegetable",
    "whit": "white",
    "chiv": "chive",
    "sausag": "sausage",
    "asparagu": "asparagus",
    "cauce": "sauce",
    "asparsley": "parsley",
    "madra": "madras",
    "crumbl": "crumb",
    "fri": "fried",
    "hotdog": "hot dog",
    "hotdogs": "hot dog",
    "hot_dog": "hot dog",
}

ALT_MAP = {
    "tomato": ["tomatoes"],
    "potato": ["potatoes"],
    "eggplant": ["aubergine"],
    "bell pepper": ["capsicum", "sweet pepper"],
    "green onion": ["scallion", "spring onion"],
    "chili": ["chilli", "chile"],
    "shrimp": ["prawn"],
    "yogurt": ["yoghurt"],
    "soy": ["soya"],
    "coriander": ["cilantro"],
    "olive": ["olives"],
    "bean": ["beans"],
    "fish": ["fishes"],
    "hot dog": ["hotdog", "hotdogs"],
}


PACKING_PATTERNS = [
    r"\bwell\s+drained\b",
    r"\bdrained\b",
    r"\brinsed?\b",
    r"\bpacked\s+in\s+(?:oil|water|brine|juice|syrup)\b",
    r"\bin\s+(?:oil|water|brine|juice|syrup)\b",
]
COMPOUND_INGREDIENTS = [
    "hot dog",
    "baking soda",
    "soy sauce",
    "bread crumbs"

    
]