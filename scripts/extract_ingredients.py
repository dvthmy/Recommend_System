import csv
import json
import re
from collections import Counter
from pathlib import Path
from typing import Dict, List, Set


# Basic text utils
NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    lowered = value.strip().lower()
    normalized = NON_ALNUM_PATTERN.sub(" ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def _simplify_token(token: str) -> str:
    # Remove common adjectives/modifiers and keep core noun
    token = re.sub(r"\b(green|red|white|yellow|fresh|dried|ground|powder|powdered|canned|chopped|diced|sliced|minced|softened)\b", " ", token)
    token = re.sub(r"\s+", " ", token).strip()
    # Take last word as head noun if multi-word
    parts = token.split(" ")
    head = parts[-1] if parts else token
    # Plural to singular heuristics
    if head.endswith("ies"):
        # chilies -> chili
        head = head[:-3] + "i"
    elif head.endswith("oes"):
        head = head[:-2]  # potatoes -> potato
    elif head.endswith("es"):
        head = head[:-2]
    elif head.endswith("s") and len(head) > 3:
        head = head[:-1]
    return head


def tokenize_ingredients(raw: str) -> List[str]:
    if not raw:
        return []
    # Common separators: comma, semicolon, line breaks, bullets
    parts = re.split(r"[\n\r;,•|]+", raw)
    tokens: List[str] = []
    for p in parts:
        t = normalize_text(p)
        if not t:
            continue
        # Remove common stopwords and qty/units heuristically
        t = re.sub(r"\b(grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|ounce|ounces|oz|lb|pounds?)\b", " ", t)
        t = re.sub(r"\b(of|and|or|optional|can|cans|slice|slices|teaspoon|teaspoons|tablespoon|tablespoons)\b", " ", t)
        t = re.sub(r"\d+[\./\d]*", " ", t)
        t = re.sub(r"\s+", " ", t).strip()
        if t:
            head = _simplify_token(t)
            if head:
                tokens.append(head)
    return tokens


def read_csv_rows(csv_path: Path, limit: int = None):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    
    encodings = ["utf-8", "utf-8-sig", "latin-1"]
    last_err: Exception | None = None
    for enc in encodings:
        try:
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                count = 0
                for row in reader:
                    yield row
                    count += 1
                    if limit and count >= limit:
                        break
            return
        except UnicodeDecodeError as e:
            last_err = e
            continue
    # If we get here, all encodings failed
    if last_err:
        raise last_err


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Extract unique ingredients from CSV recipes")
    parser.add_argument("--csv", type=str, default=str(Path("data/recipes/full_dataset.csv")), help="Path to full_dataset.csv")
    parser.add_argument("--limit", type=int, default=1000, help="Process only the first N rows")
    parser.add_argument("--output", type=str, default=str(Path("data/ingredients/extracted_ingredients.txt")), help="Output file for ingredients")
    parser.add_argument("--min-count", type=int, default=2, help="Minimum occurrence count to include ingredient")
    parser.add_argument("--verbose", action="store_true", help="Print debug logs")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    output_path = Path(args.output)
    
    print(f"[extract] Processing {args.limit} recipes from {csv_path}")
    
    # Collect all ingredient tokens
    all_tokens: List[str] = []
    token_counts = Counter()
    
    for idx, row in enumerate(read_csv_rows(csv_path, args.limit), 1):
        if args.verbose and idx <= 5:
            print(f"[sample] row {idx}: title='{row.get('title', '')[:50]}'")
        
        raw_ing = row.get("ingredients", "")
        tokens = tokenize_ingredients(raw_ing)
        all_tokens.extend(tokens)
        
        for token in tokens:
            token_counts[token] += 1
        
        if args.verbose and idx <= 3:
            print(f"  ingredients_raw='{raw_ing[:100]}...'")
            print(f"  tokens={tokens[:10]}")
    
    print(f"[extract] Total tokens: {len(all_tokens)}, Unique: {len(token_counts)}")
    
    # Filter by minimum count and sort by frequency
    filtered_tokens = [
        (token, count) for token, count in token_counts.items() 
        if count >= args.min_count and len(token) > 1
    ]
    filtered_tokens.sort(key=lambda x: x[1], reverse=True)
    
    print(f"[extract] After filtering (min_count={args.min_count}): {len(filtered_tokens)} ingredients")
    
    # Save to output file
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        for token, count in filtered_tokens:
            f.write(f"{token}\n")
    
    print(f"[extract] Saved {len(filtered_tokens)} ingredients to {output_path}")
    
    # Show top 20 most frequent
    print(f"[extract] Top 20 most frequent ingredients:")
    for i, (token, count) in enumerate(filtered_tokens[:20], 1):
        print(f"  {i:2d}. {token:<20} ({count} times)")
    
    # Show some examples of what was filtered out
    low_freq = [(token, count) for token, count in token_counts.items() if count < args.min_count]
    if low_freq and args.verbose:
        print(f"[extract] Examples of filtered out (count < {args.min_count}):")
        for token, count in sorted(low_freq, key=lambda x: x[1], reverse=True)[:10]:
            print(f"  {token} ({count} times)")


if __name__ == "__main__":
    main()
