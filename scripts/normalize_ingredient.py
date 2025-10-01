import json
import re
from pathlib import Path
from typing import Dict, List


NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")


def normalize_text(value: str) -> str:
    if value is None:
        return ""
    lowered = value.strip().lower()
    normalized = NON_ALNUM_PATTERN.sub(" ", lowered)
    return re.sub(r"\s+", " ", normalized).strip()


def load_synonyms(path: Path) -> Dict[str, List[str]]:
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    # ensure keys and values are normalized
    normalized_map: Dict[str, List[str]] = {}
    for key, values in data.items():
        k = normalize_text(key)
        normalized_values = [normalize_text(v) for v in values]
        normalized_map[k] = [v for v in normalized_values if v]
    return normalized_map


def build_canonical_lookup(synonyms: Dict[str, List[str]]) -> Dict[str, str]:
    lookup: Dict[str, str] = {}
    for canonical, alts in synonyms.items():
        lookup[canonical] = canonical
        for alt in alts:
            # prefer first-seen mapping; avoid overwriting
            lookup.setdefault(alt, canonical)
    return lookup


def canonicalize_ingredient_name(name: str, lookup: Dict[str, str]) -> str:
    norm = normalize_text(name)
    if not norm:
        return ""
    return lookup.get(norm, norm)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Normalize ingredient names using synonyms map")
    parser.add_argument("--synonyms", type=str, default=str(Path(__file__).parents[1] / "data" / "ingredients" / "synonyms.json"))
    parser.add_argument("names", nargs="*", help="Ingredient names to normalize")
    args = parser.parse_args()

    synonyms_path = Path(args.synonyms)
    synonyms = load_synonyms(synonyms_path)
    lookup = build_canonical_lookup(synonyms)

    if not args.names:
        print("No names provided. Example: python scripts/normalize_ingredient.py 'Green Onions' 'Icing sugar'")
        return

    for raw in args.names:
        print(f"{raw} -> {canonicalize_ingredient_name(raw, lookup)}")


if __name__ == "__main__":
    main()


