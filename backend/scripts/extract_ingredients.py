import pandas as pd
import re
from pathlib import Path

# ======================================
# ⚙️ CONFIGURATION
# ======================================
CSV_PATH = Path("data/recipes/full_data_ing.csv")
OUTPUT_PATH = Path("data/ingredients/clean_final_ingredients.txt")

# ======================================
# 🔍 REGEX PATTERNS
# ======================================
BRACKETS = re.compile(r"[\(\[\{].*?[\)\]\}]")               # remove (5g), [optional]
NUMBERS = re.compile(r"\b\d+[\/\d\.xX]*\b")                 # remove 1, 1/2, 12x12, etc.
UNITS = re.compile(
    r"\b(tablespoons?|teaspoons?|cups?|cup|grams?|g|kg|ml|l|oz|ounces?|lb|pounds?|pinch|dash)\b"
)
QUANTIFIERS = re.compile(r"\b(half|quarter|one|two|three|four|five|six|seven|eight|nine|ten)\b")
STOPWORDS = re.compile(
    r"\b(of|and|or|as|to|for|each|optional|needed|prepared|divided|more|from|the|a|an)\b"
)
PREP_WORDS = re.compile(r"\b(in|with|on|into|at|over|under|along|between|within)\b")  # drop text after
NON_ALPHA = re.compile(r"[^a-z\s-]")

# ✅ inch patterns
INCH_PHRASES = re.compile(
    r"\b\d*[\- ]?inch(\s*(thick|wide|dice[ds]?|slice[sd]?|piece[sd]?|strip[sd]?))?\b"
)

# ✅ if phrase contains any of these words → remove whole phrase'tsp
REMOVE_IF_CONTAINS = {"very", "vietnamese", "swanson", "such", "vidalia","thick","then","thawed","that","thai","teaspoons","tablespoons","tsp","tbsp",
                      "young","yukon","zesty","you","x"}
DESCRIPTORS = {
    "fresh","dried","chopped","sliced","minced","ground","powdered","boiled",
    "roasted","cooked","raw","frozen","softened","grated","peeled","crushed",
    "firmly","packed","large","small","medium","unsalted","divided","thinly",
    "beaten","ripe","whole","cold","hot"
}

# ======================================
# 🧹 CLEAN ONE INGREDIENT PHRASE
# ======================================
def clean_phrase(text: str) -> str:
    text = text.lower().strip()

    # Remove everything after 'in', 'with', etc.
    text = re.split(PREP_WORDS, text)[0]

    # Remove (inch...), brackets, numbers, units, quantifiers, stopwords
    text = INCH_PHRASES.sub(" ", text)
    text = BRACKETS.sub(" ", text)
    text = NUMBERS.sub(" ", text)
    text = UNITS.sub(" ", text)
    text = QUANTIFIERS.sub(" ", text)
    text = STOPWORDS.sub(" ", text)
    text = NON_ALPHA.sub(" ", text)
    text = re.sub(r"\s+", " ", text).strip()

    # Skip descriptors
    words = [w for w in text.split() if w not in DESCRIPTORS]
    phrase = " ".join(words).strip()

    # ❌ remove phrase if contains forbidden words (unless "vidalia onion")
    if any(bad in phrase for bad in REMOVE_IF_CONTAINS) and phrase != "vidalia onion":
        return ""

    return phrase


# ======================================
# 🍳 SPLIT A ROW INTO INDIVIDUAL INGREDIENTS
# ======================================
def split_and_clean_ingredients(row: str):
    if not isinstance(row, str) or not row.strip():
        return []
    parts = re.split(r"[,;]| and ", row)
    cleaned = []
    for p in parts:
        phrase = clean_phrase(p)
        if phrase:
            cleaned.append(phrase)
    return cleaned


# ======================================
# 🚀 MAIN PIPELINE
# ======================================
def main():
    df = pd.read_csv(CSV_PATH, encoding="utf-8", usecols=["ingredients"])
    all_cleaned = []

    for val in df["ingredients"]:
        phrases = split_and_clean_ingredients(str(val))
        all_cleaned.extend(phrases)

    # Deduplicate and sort
    unique = sorted(set(all_cleaned))
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text("\n".join(unique), encoding="utf-8")

    print(f"[DONE] Saved {len(unique)} cleaned ingredients → {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
