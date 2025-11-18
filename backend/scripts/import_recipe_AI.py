#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import recipes from CSV into Neo4j, with smart ingredient mapping:
- Exact/fuzzy (Levenshtein) match first
- Semantic fallback (SentenceTransformer "paraphrase-MiniLM-L6-v2") for tokens not matched

Usage (ví dụ):
  python import_recipes_neo4j.py \
    --csv data/recipes/full_data_ing.csv \
    --labels data/ingredients/ingredients.json \
    --use-driver \
    --semantic \
    --threshold 0.80 \
    --semantic-threshold 0.78 \
    --verbose

Yêu cầu:
  pip install sentence-transformers torch neo4j
"""

import csv
import json
import re
import os
import subprocess
import time
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from neo4j import GraphDatabase
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from config import NON_ING_WORDS, FIX_MAP,ALT_MAP, PACKING_PATTERNS, COMPOUND_INGREDIENTS, DEFAULT_URI, DEFAULT_USER, DEFAULT_PASS, DEFAULT_DB

_HAS_SEMANTIC = True
try:
    from sentence_transformers import SentenceTransformer, util
    import torch
except Exception:
    _HAS_SEMANTIC = False
try:
    import importlib.util
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    create_canonical_path = os.path.join(backend_dir, 'data', 'process', 'create_canonical_ingredients.py')
    spec = importlib.util.spec_from_file_location("create_canonical_ingredients", create_canonical_path)
    create_canonical_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(create_canonical_module)
    build_canonical = create_canonical_module.build_canonical
    CUT_OR_FORM_WORDS = create_canonical_module.CUT_OR_FORM_WORDS
    VARIETY_WORDS = create_canonical_module.VARIETY_WORDS
    FALSE_VARIATION_EXCEPTIONS = create_canonical_module.FALSE_VARIATION_EXCEPTIONS
    get_characteristic_words = create_canonical_module.get_characteristic_words
    _HAS_BUILD_CANONICAL = True
except Exception as e:
    _HAS_BUILD_CANONICAL = False
    CUT_OR_FORM_WORDS = {
        "chop", "strip", "strips", "fillet", "filet", "ground", "minced",
        "boneless", "skinless", "drumstick", "drumette", "leg", "loin", "rib",
        "thigh", "breast", "tenderloin", "wing", "rack", "shank", "shoulder",
        "brisket", "cutlet", "roast", "sliced", "diced", "cubed", "shredded",
        "grated", "crushed", "whole", "halves", "halved", "fillets", "cubes",
        "cracked", "dried", "fresh", "frozen", "smoked", "roasted", "pickled", "canned"
    }
    VARIETY_WORDS = {
        "green", "red", "yellow", "orange", "purple", "black", "white",
        "hot", "mild", "sweet", "extra hot", "fuji", "gala", "roma", "honeycrisp"
    }
    FALSE_VARIATION_EXCEPTIONS = {
        "sweet potato": "sweet potato",
        "water chestnut": "water chestnut",
        "horse chestnut": "horse chestnut",
        "pumpkin": "pumpkin",
        "bell pepper": "bell pepper",
        "black pepper": "black pepper",
        "cayenne pepper": "cayenne pepper",
        "green onion": "green onion",
        "spring onion": "green onion",
        "scallion": "green onion",
        "pepper jack": "cheese",
        "soy sauce": "soy sauce",
    }
    def get_characteristic_words():
        """Fallback characteristic words if import fails."""
        return {
            "sauce", "paste", "puree", "marinade", "dressing", "gravy", "glaze",
            "oil", "juice", "broth", "stock", "soup", "milk", "cream",
            "butter", "yogurt", "mayonnaise", "ketchup", "mustard", "salsa",
            "chutney", "tahini", "pesto", "vinegar", "syrup", "molasses",
            "extract", "essence", "concentrate", "bouillon",
            "flour", "starch", "meal", "powder",
            "crumb", "crumbs",
            "seasoning", "spice", "rub", "masala", "curry",
            "leaf", "leaves",
            "blossom", "blossoms",
            "wine", "beer", "cider", "coffee", "tea", "espresso", "liqueur", "vodka",
            "whiskey", "bourbon", "sake", "vermouth",
            "spread", "dip", "jam", "jelly", "marmalade"
        }
    def build_canonical(name: str) -> str:
        """Fallback build_canonical if import fails."""
        name = name.strip().lower()
        name = REGEX_LEAVE_TO_LEAF.sub('leaf', name)
        if name in FIX_MAP:
            name = FIX_MAP[name]
        for pattern in REGEX_PACKING_PATTERNS:
            name = pattern.sub('', name)
        name = REGEX_WHITESPACE.sub(' ', name).strip()
        return name


NON_ALNUM_PATTERN = re.compile(r"[^a-z0-9]+")
TOKEN_MAP_CACHE: Dict[str, Optional[str]] = {}

# Precompiled regex patterns for performance
REGEX_ENCODING_FIX_1 = re.compile(r'á([a-z]+)á', re.IGNORECASE)
REGEX_ENCODING_FIX_2 = re.compile(r'á([a-z]+)', re.IGNORECASE)
REGEX_ENCODING_FIX_3 = re.compile(r'([a-z]+)á', re.IGNORECASE)
REGEX_LEAVE_TO_LEAF = re.compile(r'\bleave\b', re.IGNORECASE)
REGEX_WHITESPACE = re.compile(r'\s+')
REGEX_NON_ALNUM_SPACE = re.compile(r"[^a-z0-9_]+")
REGEX_LEADING_NUMBER = re.compile(r'^\d+\s+', re.IGNORECASE)
REGEX_OPTIONAL_PAREN = re.compile(r"\(\s*optional\s*\)", re.IGNORECASE)
REGEX_OPTIONAL_END = re.compile(r"\s*\(optional\)", re.IGNORECASE)
REGEX_QUANTITY_PAREN = re.compile(r"\(\s*\d+\s*[a-z]*\s*\)", re.IGNORECASE)
REGEX_QUANTITY_UNIT = re.compile(r"\d+[\./\d]*(?:grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|oz|lb|pounds?|packages?)", re.IGNORECASE)
REGEX_STANDALONE_NUMBER = re.compile(r"\b\d+[\./\d]*\b")
REGEX_UNIT_WORDS = re.compile(r"\b(grams?|g|kg|ml|l|tbsp|tablespoons?|tsp|teaspoons?|cup|cups|oz|lb|pounds?|packages?)\b", re.IGNORECASE)
REGEX_NUMBER_ONLY = re.compile(r"\b\d+\b")
REGEX_COMMA_SPACE = re.compile(r"\s*,\s*")
REGEX_PACKING_PHRASE = re.compile(r"^(.*?)(?:\s+packed\s+in\s+|\s+in\s+)(?:oil|water|brine|juice|syrup)\b.*$", re.IGNORECASE)
REGEX_INGREDIENT_SEPARATORS = re.compile(r"[\n\r;,•|]+")
REGEX_CUISINE_SEPARATORS = re.compile(r"[,;/|]+")
REGEX_COOKING_METHOD_WORDS = re.compile(r"\b(edge|edges|dipping|char|to\s+char|dry|towel|towels|minced|chopped|diced|grated|squeezed|drained|paper|sliced|garnish|serving)\b", re.IGNORECASE)
REGEX_SALT_AND_PEPPER = re.compile(r"\bsalt\s*(?:and|,)\s+.*?pepper", re.IGNORECASE)
REGEX_PEPPER_EXTRACT = re.compile(r"\bsalt\s*(?:and|,)\s+(.*?pepper)", re.IGNORECASE)
REGEX_PEPPER_CLEAN = re.compile(r"\b(freshly|ground|to\s+taste|and)\b", re.IGNORECASE)
REGEX_SALT_STANDALONE = re.compile(r"\b(\w+\s+)?salt\b", re.IGNORECASE)
REGEX_FRESHLY_GROUND_PEPPER = re.compile(r"\bfreshly\s+ground\s+(black|white)\s+pepper\b", re.IGNORECASE)
REGEX_BLACK_WHITE_PEPPER = re.compile(r"\b(black|white)\s+pepper\b", re.IGNORECASE)
REGEX_WITH_AND = re.compile(r"\bwith\b|\band\b|,|&")
REGEX_PARENTHETICAL = re.compile(r"\s*\([^)]*\)\s*", re.IGNORECASE)
REGEX_GREEN_ONIONS = re.compile(r"\bgreen\s+onions\b", re.IGNORECASE)
REGEX_BREAD_CRUMB = re.compile(r"\bbread\s+crumb(s?)\b", re.IGNORECASE)
REGEX_SESAME_SEEDS = re.compile(r"\bsesame\s+seeds\b", re.IGNORECASE)
REGEX_TOMATO_PREP = re.compile(r"\b(diced|chopped|sliced|minced|grated|crushed|whole|halved|quartered)\b", re.IGNORECASE)
REGEX_TO_TASTE = re.compile(r"\b(to\s+taste|or\s+to\s+taste)\b", re.IGNORECASE)
REGEX_POWDER_NAME = re.compile(r"(\w+(?:\s+\w+)*)\s+powder", re.IGNORECASE)
REGEX_POWDERED_NAME = re.compile(r"(\w+(?:\s+\w+)*)\s+powdered", re.IGNORECASE)
REGEX_POWDER_WORDS = re.compile(r"\b(powder|powdered|ground|crushed|freshly)\b", re.IGNORECASE)
REGEX_SEASONING_WORDS = re.compile(r"\b(seasoning|spice|mix|rub|blend|masala|curry|salt|pepper)\b", re.IGNORECASE)
REGEX_SOUP_WORDS = re.compile(r"\b(soup|soups)\b", re.IGNORECASE)
REGEX_LOW_SODIUM = re.compile(r"\b(lower|low)\s+sodium\b", re.IGNORECASE)
REGEX_GREEN_ONION_PREP = re.compile(r"\b(sliced|chopped|diced|minced|grated|shredded|to\s+garnish|garnish|optional)\b", re.IGNORECASE)
REGEX_LEAVES_TO_LEAF = re.compile(r"\s+leaves\b", re.IGNORECASE)
REGEX_DRY_MIX = re.compile(r"\b(dry|mix)\b", re.IGNORECASE)
REGEX_SALAD = re.compile(r"\s+salad\s+", re.IGNORECASE)
REGEX_DRESSING = re.compile(r"\s+dressing\s*(?:mix)?\b", re.IGNORECASE)
REGEX_GROUND_CRUSHED = re.compile(r"\b(ground|crushed|freshly)\b", re.IGNORECASE)

# Precompiled patterns for pepper matching
REGEX_PEPPER_COLOR = re.compile(r"\b(black|white|red|green|yellow|orange|pink)\s+pepper\b", re.IGNORECASE)
REGEX_CAYENNE_PEPPER = re.compile(r"\bcayenne\s+pepper\b", re.IGNORECASE)
REGEX_BELL_PEPPER = re.compile(r"\bbell\s+pepper\b", re.IGNORECASE)
REGEX_CHILI_PEPPER = re.compile(r"\bchili\s+pepper\b", re.IGNORECASE)
REGEX_CHILE_PEPPER = re.compile(r"\bchile\s+pepper\b", re.IGNORECASE)

# Precompiled patterns for powder matching
REGEX_GARLIC_POWDER = re.compile(r"\bgarlic\s+powder\b", re.IGNORECASE)
REGEX_ONION_POWDER = re.compile(r"\bonion\s+powder\b", re.IGNORECASE)
REGEX_CHILI_POWDER = re.compile(r"\bchili\s+powder\b", re.IGNORECASE)
REGEX_CHILLI_POWDER = re.compile(r"\bchilli\s+powder\b", re.IGNORECASE)
REGEX_CURRY_POWDER = re.compile(r"\bcurry\s+powder\b", re.IGNORECASE)
REGEX_GINGER_POWDER = re.compile(r"\bginger\s+powder\b", re.IGNORECASE)
REGEX_MUSTARD_POWDER = re.compile(r"\bmustard\s+powder\b", re.IGNORECASE)
REGEX_VANILLA_POWDER = re.compile(r"\bvanilla\s+powder\b", re.IGNORECASE)
REGEX_COCOA_POWDER = re.compile(r"\bcocoa\s+powder\b", re.IGNORECASE)
REGEX_CHOCOLATE_POWDER = re.compile(r"\bchocolate\s+powder\b", re.IGNORECASE)
REGEX_CINNAMON_POWDER = re.compile(r"\bcinnamon\s+powder\b", re.IGNORECASE)
REGEX_PAPRIKA_POWDER = re.compile(r"\bpaprika\s+powder\b", re.IGNORECASE)
REGEX_CAYENNE_POWDER = re.compile(r"\bcayenne\s+powder\b", re.IGNORECASE)
REGEX_TUMERIC_POWDER = re.compile(r"\btumeric\s+powder\b", re.IGNORECASE)
REGEX_TURMERIC_POWDER = re.compile(r"\bturmeric\s+powder\b", re.IGNORECASE)

# Precompiled cooking method phrases
REGEX_COOKING_METHOD_PHRASES = [
    re.compile(r"\bchar\s+the\s+edges?\b", re.IGNORECASE),
    re.compile(r"\bcook(?:ed)?\s+to\s+char\s+(?:the\s+)?edges?\b", re.IGNORECASE),
    re.compile(r"\bfor\s+dipping\b", re.IGNORECASE),
    re.compile(r"\bfor\s+garnish(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bto\s+garnish(?:ing)?\b", re.IGNORECASE),
    re.compile(r"\bfor\s+serving\b", re.IGNORECASE),
    re.compile(r"\bdiced\s+and\s+cooked\s+to\s+char\s+(?:the\s+)?edges?\b", re.IGNORECASE),
    re.compile(r"\bsqueezed\s+dry\s+(?:with\s+)?(?:paper\s+)?towels?\b", re.IGNORECASE),
    re.compile(r"\b(?:squeezed|drained)\s+dry\b", re.IGNORECASE),
    re.compile(r"\bwith\s+paper\s+towels?\b", re.IGNORECASE),
    re.compile(r",\s*minced\b", re.IGNORECASE),
    re.compile(r",\s*chopped\b", re.IGNORECASE),
    re.compile(r",\s*diced\b", re.IGNORECASE),
    re.compile(r",\s*grated\b", re.IGNORECASE),
    re.compile(r"\d+\s*\(\s*\d+\s*inch\s*\)\s*skewers?\b", re.IGNORECASE),
    re.compile(r"skewers?\b", re.IGNORECASE),
]

# Precompiled packing phrase patterns
REGEX_PACKING_PATTERNS = [
    re.compile(r'\bwell\s+drained\b', re.IGNORECASE),
    re.compile(r'\bdrained\b', re.IGNORECASE),
    re.compile(r'\brinsed?\b', re.IGNORECASE),
    re.compile(r'\bpacked\s+in\s+(?:oil|water|brine|juice|syrup)\b', re.IGNORECASE),
    re.compile(r'\bin\s+(?:oil|water|brine|juice|syrup)\b', re.IGNORECASE),
]

def preprocess_compound_phrases(text: str) -> str:
    """Giữ nguyên các cụm đặc biệt trước khi tokenize."""
    for phrase in COMPOUND_INGREDIENTS:
        safe = phrase.replace(" ", "_")
        pattern = rf"\b{re.escape(phrase)}s?\b"
        text = re.sub(pattern, safe, text, flags=re.IGNORECASE)
    return text

FIX_MAP_TOKEN = {

}

@lru_cache(maxsize=10000)
def normalize_text(value: str) -> str:
    """
    Normalize text using build_canonical for consistency with canonical_ingredients.json.
    This ensures the same normalization logic is used for matching.
    Cached for performance.
    """
    if value is None:
        return ""
    
    value = REGEX_ENCODING_FIX_1.sub(r'a \1 a', value)
    value = REGEX_ENCODING_FIX_2.sub(r'a \1', value)
    value = REGEX_ENCODING_FIX_3.sub(r'\1 a', value)
    
    if _HAS_BUILD_CANONICAL:
        normalized = build_canonical(value)
    else:
        normalized = value.strip().lower()
        normalized = REGEX_LEAVE_TO_LEAF.sub('leaf', normalized)
        if normalized in FIX_MAP:
            normalized = FIX_MAP[normalized]
        for pattern in REGEX_PACKING_PATTERNS:
            normalized = pattern.sub('', normalized)
        normalized = REGEX_WHITESPACE.sub(' ', normalized).strip()
    
    normalized = REGEX_NON_ALNUM_SPACE.sub(" ", normalized)
    return REGEX_WHITESPACE.sub(" ", normalized).strip()


@lru_cache(maxsize=5000)
def _simplify_token_no_lookup(token: str) -> str:
    """
    Cached version of _simplify_token when exact_lookup is None (most common case).
    """
    return _simplify_token_impl(token, None)

def _simplify_token(token: str, exact_lookup: Optional[Dict[str, str]] = None) -> str:
    """
    Simplify ingredient tokens to a core noun form.
    Uses CUT_OR_FORM_WORDS and VARIETY_WORDS from create_canonical_ingredients.py for consistency.
    
    Args:
        token: Token to simplify
        exact_lookup: Optional exact lookup map to check if variety word + base exists as a canonical ingredient.
                     If provided, will keep variety words if the full token exists in the lookup.
    """
    if exact_lookup is None:
        return _simplify_token_no_lookup(token)
    return _simplify_token_impl(token, exact_lookup)

def _simplify_token_impl(token: str, exact_lookup: Optional[Dict[str, str]] = None) -> str:
    """
    Simplify ingredient tokens to a core noun form.
    Uses CUT_OR_FORM_WORDS and VARIETY_WORDS from create_canonical_ingredients.py for consistency.
    
    Args:
        token: Token to simplify
        exact_lookup: Optional exact lookup map to check if variety word + base exists as a canonical ingredient.
                     If provided, will keep variety words if the full token exists in the lookup.
    """
    # First normalize using build_canonical for consistency
    token = normalize_text(token)
    
    # Special pepper types that should keep their modifier (black, white, bell, cayenne, etc.)
    # These are distinct ingredients, not just color modifiers
    SPECIAL_PEPPER_TYPES = {"black pepper", "white pepper", "bell pepper", "cayenne pepper", 
                           "chili pepper", "red pepper", "green pepper", "yellow pepper"}
    token_lower = token.lower()
    for pepper_type in SPECIAL_PEPPER_TYPES:
        if pepper_type in token_lower:
            # Keep the full pepper type name
            # Remove only preparation methods, not the pepper type modifier
            cut_form_pattern = r"\b(" + "|".join(re.escape(w) for w in CUT_OR_FORM_WORDS) + r")\b"
            cut_form_regex = re.compile(cut_form_pattern, re.IGNORECASE)
            token = cut_form_regex.sub(" ", token)
            token = REGEX_WHITESPACE.sub(" ", token).strip()
            return token
    
    cut_form_pattern = r"\b(" + "|".join(re.escape(w) for w in CUT_OR_FORM_WORDS) + r")\b"
    cut_form_regex = re.compile(cut_form_pattern, re.IGNORECASE)
    token = cut_form_regex.sub(" ", token)
    token = REGEX_WHITESPACE.sub(" ", token).strip()
    
    # Remove variety words (color, type indicators) - but keep the base ingredient
    # IMPORTANT: Check if variety word + base exists in exact_lookup before removing
    # This prevents "red onion" → "onion" when "red onion" is a distinct canonical ingredient
    words = token.split()
    if len(words) > 1 and exact_lookup is not None:
        # Check if the current token (with variety word) exists in exact_lookup
        if token in exact_lookup:
            # Token exists as-is, keep it (don't remove variety word)
            # Only remove preparation methods
            return token
        
        # If first word is a variety word, check if "variety base" exists in lookup
        if words[0].lower() in VARIETY_WORDS:
            variety_base = " ".join(words[1:])
            # Check if full token exists
            if token not in exact_lookup:
                # Full token doesn't exist, try removing variety word
                # But only if variety_base also exists (to avoid breaking things)
                if variety_base in exact_lookup:
                    token = variety_base
        # Also check middle words
        else:
            filtered_words = []
            for i, word in enumerate(words):
                # Keep variety words if they're at the end (might be part of name)
                if i < len(words) - 1 and word.lower() in VARIETY_WORDS:
                    # Check if removing this variety word breaks an existing canonical
                    test_token = " ".join(filtered_words + words[i+1:])
                    if test_token not in exact_lookup:
                        # Removing variety word breaks canonical, keep it
                        filtered_words.append(word)
                    # Otherwise, skip variety word in middle
                    continue
                filtered_words.append(word)
            token = " ".join(filtered_words)
    elif len(words) > 1:
        # No exact_lookup provided, use original logic (less safe)
        # If first word is a variety word, remove it
        if words[0].lower() in VARIETY_WORDS:
            token = " ".join(words[1:])
        # Also check middle words
        else:
            filtered_words = []
            for i, word in enumerate(words):
                # Keep variety words if they're at the end (might be part of name)
                if i < len(words) - 1 and word.lower() in VARIETY_WORDS:
                    continue  # Skip variety word in middle
                filtered_words.append(word)
            token = " ".join(filtered_words)
    
    token = REGEX_WHITESPACE.sub(" ", token).strip()
    
    if not token:
        token = normalize_text(token)
    
    # Split token and get head word
    parts = token.split(" ")
    head = parts[-1] if parts else token

    # Heuristic plural→singular (more comprehensive)
    if head.endswith("ies") and len(head) > 3:
        head = head[:-3] + "y"
    elif head.endswith("oes") and len(head) > 3:
        head = head[:-2]
    elif head.endswith(("ches", "shes", "xes")):
        head = head[:-2]
    elif head.endswith("ses") and len(head) > 3:
        head = head[:-2]
    elif head.endswith("ves") and len(head) > 3:
        head = head[:-1]
    elif head.endswith("es") and len(head) > 3:
        singular_es = head[:-2]
        if len(singular_es) >= 3:
            head = singular_es
        else:
            head = head[:-1]
    elif head.endswith("s") and len(head) > 1:
        singular = head[:-1]
        if len(singular) >= 2:
            head = singular

    head = FIX_MAP_TOKEN.get(head, head)
    head = head.replace("_", " ")
    return head.strip()

def strip_packing_phrases(s: str) -> str:
    s = REGEX_COMMA_SPACE.sub(" ", s)
    for pat in PACKING_PATTERNS:
        s = re.sub(pat, "", s)
    m = REGEX_PACKING_PHRASE.search(s)
    if m:
        s = m.group(1).strip()
    return REGEX_WHITESPACE.sub(" ", s).strip()


def tokenize_ingredients(raw: str) -> List[str]:
    """Tokenize & normalize ingredients with general rules."""
    if not raw:
        return []
    raw = preprocess_compound_phrases(raw) 
    
    for pattern in REGEX_COOKING_METHOD_PHRASES:
        raw = pattern.sub("", raw)
    
    raw = REGEX_COOKING_METHOD_WORDS.sub("", raw)
    
    parts = REGEX_INGREDIENT_SEPARATORS.split(raw)
    tokens: List[str] = []

    MEAT_FISH = {
        "beef","pork","chicken","duck","lamb","turkey","bacon","ham","sausage","prosciutto","pancetta",
        "brisket","meatball","steak","salami","rib","tenderloin","cutlet","sirloin",
        "fish","salmon","tuna","shrimp","crab","mussel","scallop","crawfish","fillet","bronzino","crabmeat","katsuobushi"
    }
    POWDER_ENDINGS = {"powder","powdered","ground","crushed"}
    SEASONING_ENDINGS = {"seasoning","spice","mix","rub","blend","masala","curry","salt","pepper"}

    for p in parts:
        if _HAS_BUILD_CANONICAL:
            t = build_canonical(p)
        else:
            t = normalize_text(p)
        
        if not t:
            continue

        t = REGEX_OPTIONAL_PAREN.sub(" ", t)
        t = REGEX_OPTIONAL_END.sub(" ", t)
        t = REGEX_QUANTITY_PAREN.sub(" ", t)
        t = REGEX_QUANTITY_UNIT.sub(" ", t)
        t = REGEX_STANDALONE_NUMBER.sub(" ", t)
        t = REGEX_UNIT_WORDS.sub(" ", t)
        t = REGEX_NUMBER_ONLY.sub(" ", t)
        t = REGEX_WHITESPACE.sub(" ", t).strip()
        if not t:
            continue

        t = strip_packing_phrases(t)
        if not t:
            continue
        
        lower = f" {t} "
        
        if REGEX_SALT_AND_PEPPER.search(lower):
            tokens.append("salt")
            pepper_match = REGEX_PEPPER_EXTRACT.search(lower)
            if pepper_match:
                pepper_part = pepper_match.group(1).strip()
                pepper_part = REGEX_PEPPER_CLEAN.sub("", pepper_part)
                pepper_part = REGEX_WHITESPACE.sub(" ", pepper_part).strip()
                if pepper_part:
                    pepper_normalized = normalize_text(pepper_part)
                    if pepper_normalized and pepper_normalized not in NON_ING_WORDS:
                        tokens.append(pepper_normalized)
            continue
        
        if REGEX_SALT_STANDALONE.search(lower) and "pepper" not in lower:
            tokens.append("salt")
            continue
        
        if REGEX_FRESHLY_GROUND_PEPPER.search(lower):
            pepper_match = REGEX_BLACK_WHITE_PEPPER.search(lower)
            if pepper_match:
                pepper_type = pepper_match.group(1).lower()
                tokens.append(f"{pepper_type} pepper")
                continue
            
        if "cooking spray" in t.lower():
            continue
        
        if " with " in t or " and " in t:
            sub_parts = REGEX_WITH_AND.split(t)
            sub_tokens = []
            for sub in sub_parts:
                sub = sub.strip()
                if not sub:
                    continue
                sub = REGEX_PARENTHETICAL.sub(" ", sub)
                sub = REGEX_WHITESPACE.sub(" ", sub).strip()
                if not sub:
                    continue
                sub_tokens.append(sub)
            if len(sub_tokens) > 1:
                for sub in sub_tokens:
                    sub_lower = f" {sub} "
                    mapped = None
                    if any(x in sub_lower for x in [" oil ", "olive oil", "sesame oil"]):
                        tokens.append("oil")
                    elif "soy sauce" in sub_lower:
                        tokens.append(normalize_text(sub))
                    elif "green onion" in sub_lower or "green onions" in sub_lower or "scallion" in sub_lower:
                        sub_normalized = REGEX_GREEN_ONIONS.sub("green onion", sub)
                        tokens.append(normalize_text(sub_normalized))
                    elif "bread crumb" in sub_lower or "bread crumbs" in sub_lower or "breadcrumb" in sub_lower or "breadcrumbs" in sub_lower:
                        sub_normalized = REGEX_BREAD_CRUMB.sub("breadcrumb", sub)
                        sub_normalized = normalize_text(sub_normalized)
                        tokens.append(sub_normalized)
                    elif "sesame seed" in sub_lower or "sesame seeds" in sub_lower:
                        sub_normalized = normalize_text(sub)
                        sub_normalized = REGEX_SESAME_SEEDS.sub("sesame seed", sub_normalized)
                        tokens.append(sub_normalized)
                    elif "tomato" in sub_lower:
                        tomato_clean = REGEX_TOMATO_PREP.sub("", sub).strip()
                        tomato_clean = REGEX_WHITESPACE.sub(" ", tomato_clean)
                        tomato_normalized = normalize_text(tomato_clean)
                        if tomato_normalized:
                            if tomato_normalized.endswith("es"):
                                tomato_normalized = tomato_normalized[:-2]
                            elif tomato_normalized.endswith("s"):
                                tomato_normalized = tomato_normalized[:-1]
                            tokens.append(tomato_normalized if tomato_normalized else "tomato")
                        else:
                            tokens.append("tomato")
                    elif "salt" in sub_lower:
                        tokens.append("salt")
                    elif "pepper" in sub_lower and "black pepper" not in sub_lower and "white pepper" not in sub_lower:
                        pepper_clean = REGEX_TO_TASTE.sub("", sub).strip()
                        pepper_clean = REGEX_WHITESPACE.sub(" ", pepper_clean)
                        pepper_normalized = normalize_text(pepper_clean)
                        if pepper_normalized:
                            tokens.append(pepper_normalized)
                        else:
                            tokens.append("pepper")
                    elif any(x in sub_lower for x in ["basil", "garlic", "onion"]):
                        tokens.append(_simplify_token(sub))
                    else:
                        tokens.append(_simplify_token(sub))
                continue


        lower = f" {t} "

        if t in NON_ING_WORDS:
            continue

        mapped = None

        for k in MEAT_FISH:
            if f" {k} " in lower:
                specific = [x for x in ("salmon","tuna","shrimp","crab","mussel","scallop","fish","chicken","beef","pork","duck","lamb","turkey") if f" {x} " in lower]
                mapped = specific[0] if specific else k
                break

        if not mapped and " oil " in lower:
                mapped = "oil"

        if not mapped:
            multi_word_powder_patterns_compiled = [
                REGEX_GARLIC_POWDER, REGEX_ONION_POWDER, REGEX_CHILI_POWDER, REGEX_CHILLI_POWDER,
                REGEX_CURRY_POWDER, REGEX_GINGER_POWDER, REGEX_MUSTARD_POWDER, REGEX_VANILLA_POWDER,
                REGEX_COCOA_POWDER, REGEX_CHOCOLATE_POWDER, REGEX_CINNAMON_POWDER, REGEX_PAPRIKA_POWDER,
                REGEX_CAYENNE_POWDER, REGEX_TUMERIC_POWDER, REGEX_TURMERIC_POWDER
            ]
            for pattern in multi_word_powder_patterns_compiled:
                match = pattern.search(lower)
                if match:
                    powder_match = REGEX_POWDER_NAME.search(lower)
                    if powder_match:
                        powder_name = powder_match.group(1).strip()
                        prep_words = ["ground", "crushed", "freshly"]
                        powder_words = [w for w in powder_name.split() if w.lower() not in prep_words]
                        if powder_words:
                            mapped = normalize_text(" ".join(powder_words + ["powder"]))
                        else:
                            mapped = normalize_text(f"{powder_name} powder")
                    break
        
        if not mapped and any(f" {end} " in lower or lower.endswith(f" {end}") for end in POWDER_ENDINGS):
            if " black pepper" in lower or lower.endswith(" black pepper"):
                mapped = REGEX_POWDER_WORDS.sub("", t).strip()
                mapped = REGEX_WHITESPACE.sub(" ", mapped)
                mapped = normalize_text(mapped)
            elif " white pepper" in lower or lower.endswith(" white pepper"):
                mapped = REGEX_POWDER_WORDS.sub("", t).strip()
                mapped = REGEX_WHITESPACE.sub(" ", mapped)
                mapped = normalize_text(mapped)
            else:
                words = t.split()
                if words and words[-1].lower() in ("powder", "powdered"):
                    if len(words) >= 2:
                        prep_words = ["ground", "crushed", "freshly"]
                        cleaned_words = [w for w in words if w.lower() not in prep_words]
                        if len(cleaned_words) >= 2:
                            mapped = normalize_text(" ".join(cleaned_words))
                        else:
                            mapped = "powder"
                    else:
                        mapped = "powder"
                elif " powder" in lower or lower.endswith(" powder"):
                    powder_match = REGEX_POWDER_NAME.search(lower)
                    if powder_match:
                        powder_name = powder_match.group(1).strip()
                        prep_words = ["ground", "crushed", "freshly"]
                        powder_words = [w for w in powder_name.split() if w.lower() not in prep_words]
                        if powder_words:
                            mapped = normalize_text(" ".join(powder_words + ["powder"]))
                        else:
                            mapped = "powder"
                    else:
                        mapped = "powder"
                elif " powdered" in lower or lower.endswith(" powdered"):
                    powdered_match = REGEX_POWDERED_NAME.search(lower)
                    if powdered_match:
                        powdered_name = powdered_match.group(1).strip()
                        prep_words = ["ground", "crushed", "freshly"]
                        powdered_words = [w for w in powdered_name.split() if w.lower() not in prep_words]
                        if powdered_words:
                            mapped = normalize_text(" ".join(powdered_words + ["powder"]))
                        else:
                            mapped = "powder"
                    else:
                        mapped = "powder"
                else:
                    main = REGEX_GROUND_CRUSHED.sub("", t).strip()
                    main = REGEX_WHITESPACE.sub(" ", main)
                    mapped = _simplify_token(main)
        if not mapped and any(f" {end} " in lower or lower.endswith(f" {end}") for end in SEASONING_ENDINGS):
            main = REGEX_SEASONING_WORDS.sub("", t).strip()
            main = REGEX_WHITESPACE.sub(" ", main)
            mapped = _simplify_token(main)

        if not mapped and " soup" in lower:
            main = REGEX_SOUP_WORDS.sub("", t).strip()
            if main:
                mapped = _simplify_token(main)
            else:
                mapped = "soup"
        if not mapped:
            if "soy sauce" in lower:
                mapped = REGEX_LOW_SODIUM.sub("", t).strip()
                mapped = REGEX_WHITESPACE.sub(" ", mapped)
                mapped = normalize_text(mapped)
            elif "green onion" in lower or "green onions" in lower or "scallion" in lower:
                mapped = REGEX_GREEN_ONION_PREP.sub("", t).strip()
                mapped = REGEX_WHITESPACE.sub(" ", mapped)
                mapped = REGEX_GREEN_ONIONS.sub("green onion", mapped)
                mapped = normalize_text(mapped)
            elif "bread crumb" in lower or "bread crumbs" in lower or "breadcrumb" in lower or "breadcrumbs" in lower:
                mapped = REGEX_BREAD_CRUMB.sub("breadcrumb", t)
                mapped = normalize_text(mapped)
            elif "sesame seed" in lower or "sesame seeds" in lower:
                mapped = normalize_text(t)
                mapped = REGEX_SESAME_SEEDS.sub("sesame seed", mapped)
            elif " olive " in lower and " oil " in lower:
                mapped = "oil"
            elif " chicken " in lower and any(w in lower for w in [" breast "," thigh "," tenderloin "," drumstick "]):
                mapped = "chicken"
            elif " french fry" in lower or " french fries" in lower:
                mapped = "potato"
            elif lower.endswith(" fries") or lower.endswith(" fry"):
                if " potato " in lower or lower.startswith("potato "):
                    if " sweet potato " in lower or lower.startswith("sweet potato "):
                        mapped = "sweet potato"
                    else:
                        mapped = "potato"
                else:
                    mapped = "potato"
            elif " dressing " in lower or lower.endswith(" dressing"):
                main = REGEX_DRY_MIX.sub("", t).strip()
                if " ranch " in lower or lower.startswith("ranch "):
                    mapped = REGEX_SALAD.sub(" ", main).strip()
                    mapped = REGEX_DRESSING.sub(" dressing", mapped).strip()
                    mapped = normalize_text(mapped)
                else:
                    main = REGEX_DRESSING.sub(" dressing", main).strip()
                    if main and len(main) > 3:
                        mapped = normalize_text(main)
                    else:
                        mapped = "dressing"
            elif " leaves" in lower or lower.endswith(" leaves"):
                mapped = REGEX_LEAVES_TO_LEAF.sub(" leaf", t).strip()
                mapped = normalize_text(mapped)
            elif " leaf" in lower or lower.endswith(" leaf"):
                mapped = normalize_text(t)

        if not mapped:
            mapped = _simplify_token(t)
            if not mapped or len(mapped) < 2:
                mapped = t

        if not mapped or mapped in NON_ING_WORDS:
            continue
        
        cooking_method_words = {
            "edge", "edges", "dipping", "char", "garnish", "serving",
            "dry", "towel", "towels", "minced", "chopped", "diced", "grated",
            "squeezed", "drained", "paper", "skewer", "skewers", "optional",
            "sliced", "freshly", "spray", "cooking"
        }
        if mapped.lower() in cooking_method_words:
            continue
        
        if "cooking spray" in lower or ("cooking" in lower and "spray" in lower):
            continue

        mapped = normalize_text(mapped)
        if mapped:
            tokens.append(mapped)

    return list(dict.fromkeys(tokens))


def normalize_cuisine_name(name: Optional[str]) -> Optional[str]:
    """Standardize cuisine names for consistency."""
    if not name:
        return None
    name = normalize_text(name)
    replacements = {
        "modern thai": "Thai",
        "portuguese inspired": "portuguese",
        "vietnam": "vietnamese",
        "viet nam": "vietnamese",
        "usa": "american",
        "us": "american",
        "latin america": "latin american",
        "western": "western",
        "asian": "asian",
    }
    return replacements.get(name, name.title())


def parse_cuisines(raw: Optional[str]) -> List[str]:
    """Split and normalize multiple cuisines from CSV field.
    
    Handles formats like:
    - "Korean, Vietnamese" -> ["Korean", "Vietnamese"]
    - "Korean;Vietnamese" -> ["Korean", "Vietnamese"]
    - "Korean/Vietnamese" -> ["Korean", "Vietnamese"]
    - "Korean" -> ["Korean"]
    """
    if not raw:
        return []
    # Split by common separators: comma, semicolon, slash, pipe
    parts = REGEX_CUISINE_SEPARATORS.split(str(raw))
    cuisines: List[str] = []
    for c in parts:
        c = c.strip()  # Remove whitespace
        if not c:  # Skip empty strings
            continue
        cname = normalize_cuisine_name(c)
        if cname and cname not in cuisines:
            cuisines.append(cname)
    return cuisines


def levenshtein_distance(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            insert_cost = cur[j - 1] + 1
            delete_cost = prev[j] + 1
            replace_cost = prev[j - 1] + (0 if ca == cb else 1)
            cur.append(min(insert_cost, delete_cost, replace_cost))
        prev = cur
    return prev[-1]


def similarity_ratio(a: str, b: str) -> float:
    if not a and not b:
        return 1.0
    dist = levenshtein_distance(a, b)
    denom = max(len(a), len(b))
    if denom == 0:
        return 0.0
    return 1.0 - (dist / denom)


@dataclass
class IngredientLabel:
    ingredient_id: str
    canonical_name: str
    synonyms: List[str]


def load_label_set(path: Path) -> List[IngredientLabel]:
    """Load canonical ingredient names from a text file (one name per line)."""
    labels: List[IngredientLabel] = []
    with path.open("r", encoding="utf-8") as f:
        for line in f:
            name = normalize_text(line)
            if not name:
                continue
            slug = NON_ALNUM_PATTERN.sub("_", name).strip("_")
            labels.append(IngredientLabel(ingredient_id=f"ing_{slug}", canonical_name=name, synonyms=[]))
    return labels


def load_label_json(path: Path) -> List[IngredientLabel]:
    """
    Load canonical ingredient names from a JSON list with fields id, canonical, alt, and variations.
    Enhanced to better index all variations for exact matching.
    Filters out invalid single-word color ingredients (red, green, black, white, blue, yellow).
    """
    data = json.loads(path.read_text(encoding="utf-8"))
    labels: List[IngredientLabel] = []
    
    INVALID_COLOR_WORDS = {"red", "green", "black", "white", "blue", "yellow"}
    
    for obj in data:
        canonical = obj.get("canonical_name") or obj.get("canonical") or ""
        if not canonical:
            continue
        
        canonical_norm = normalize_text(canonical)
        if not canonical_norm:
            continue
        
        canonical_words = canonical_norm.lower().split()
        if len(canonical_words) == 1 and canonical_words[0] in INVALID_COLOR_WORDS:
            continue
            
        iid = obj.get("ingredient_id") or obj.get("id") or f"ing_{NON_ALNUM_PATTERN.sub('_', canonical_norm).strip('_')}"
        
        synonyms = obj.get("alt") or obj.get("alt_names") or []
        syn_norm = set()
        
        for s in synonyms:
            if s:
                s_norm = normalize_text(s)
                if s_norm and s_norm != canonical_norm:
                    syn_norm.add(s_norm)
        
        variations = obj.get("variations", {})
        if isinstance(variations, dict):
            for var_type, var_list in variations.items():
                if isinstance(var_list, list):
                    for variation in var_list:
                        if variation and isinstance(variation, str):
                            var_norm = normalize_text(variation)
                            if var_norm and var_norm != canonical_norm:
                                syn_norm.add(var_norm)
                            
                            var_simplified = _simplify_token(variation)
                            if var_simplified and var_simplified != canonical_norm and var_simplified != var_norm:
                                syn_norm.add(var_simplified)
        
        syn_list = sorted(list(syn_norm))
        
        labels.append(IngredientLabel(ingredient_id=iid, canonical_name=canonical_norm, synonyms=syn_list))
    return labels


def build_lookup(labels: List[IngredientLabel]) -> Tuple[Dict[str, str], List[IngredientLabel]]:
    """
    Build exact and synonym lookup maps.
    Enhanced to include multiple normalization strategies for better matching.
    """
    exact: Dict[str, str] = {}
    # First pass: build basic exact map (without simplified versions)
    for lab in labels:
        # Add canonical name (already normalized in load_label_json)
        canonical_norm = normalize_text(lab.canonical_name)
        if canonical_norm:
            exact[canonical_norm] = lab.ingredient_id
        
        # Add all synonyms (already normalized in load_label_json)
        for s in lab.synonyms:
            s_norm = normalize_text(s)
            if s_norm and s_norm not in exact:
                exact[s_norm] = lab.ingredient_id
    
    # Second pass: add simplified versions (using exact_lookup to avoid breaking canonical ingredients)
    for lab in labels:
        # Add simplified canonical (without preparation methods)
        canonical_norm = normalize_text(lab.canonical_name)
        canonical_simplified = _simplify_token(lab.canonical_name, exact_lookup=exact)
        if canonical_simplified and canonical_simplified != canonical_norm:
            # Only add if it doesn't conflict with existing canonical
            if canonical_simplified not in exact:
                exact[canonical_simplified] = lab.ingredient_id
        
        # Add simplified versions of synonyms
        for s in lab.synonyms:
            s_norm = normalize_text(s)
            s_simplified = _simplify_token(s, exact_lookup=exact)
            if s_simplified and s_simplified != s_norm and s_simplified not in exact:
                exact[s_simplified] = lab.ingredient_id
    
    return exact, labels


def build_base_to_variants_map(labels: List[IngredientLabel]) -> Dict[str, List[str]]:
    """
    Build a mapping from base ingredient names to their specific variants.
    This helps prevent matching base ingredients (e.g., "onion", "pepper") 
    when specific variants (e.g., "yellow onion", "black pepper") are already present.
    
    Returns:
        Dict mapping base ingredient name -> list of variant ingredient_ids
        Example: {"onion": ["ing_yellow_onion", "ing_green_onion", "ing_red_onion"], ...}
    """
    base_to_variants: Dict[str, List[str]] = {}
    
    base_patterns = {
        "onion": [
            "yellow onion", "green onion", "red onion", "white onion", 
            "sweet onion", "spanish onion", "vidalia onion", 
            "scallion", "spring onion"
        ],
        "pepper": [
            "black pepper", "white pepper", "cayenne pepper", "bell pepper",
            "red pepper", "green pepper", "jalapeno pepper", "serrano pepper"
        ],
        "potato": [
            "sweet potato", "russet potato", "red potato", "yukon potato",
            "fingerling potato", "new potato"
        ],
        "rice": [
            "brown rice", "white rice", "jasmine rice", "basmati rice",
            "arborio rice", "wild rice", "sticky rice"
        ],
        "flour": [
            "all purpose flour", "bread flour", "cake flour", "whole wheat flour",
            "almond flour", "coconut flour", "rice flour"
        ],
        "cheese": [
            "cheddar cheese", "mozzarella cheese", "parmesan cheese", "swiss cheese",
            "pepper jack cheese", "cream cheese", "feta cheese"
        ],
        "milk": [
            "whole milk", "skim milk", "2% milk", "almond milk", "soy milk",
            "coconut milk", "oat milk"
        ],
        "sugar": [
            "brown sugar", "white sugar", "powdered sugar", "granulated sugar",
            "coconut sugar", "maple sugar"
        ],
        "vinegar": [
            "apple cider vinegar", "white vinegar", "balsamic vinegar", "red wine vinegar",
            "rice vinegar", "distilled vinegar"
        ],
        "salt": [
            "kosher salt", "sea salt", "table salt", "himalayan salt", "coarse salt"
        ]
    }
    
    variant_to_base: Dict[str, str] = {}
    for base, variants in base_patterns.items():
        for variant in variants:
            variant_to_base[variant.lower()] = base
    
    if _HAS_BUILD_CANONICAL:
        for exception_key, exception_target in FALSE_VARIATION_EXCEPTIONS.items():
            exception_key_lower = normalize_text(exception_key).lower()
            exception_target_lower = normalize_text(exception_target).lower()
            
            words = exception_target_lower.split()
            if len(words) > 1:
                last_word = words[-1]
                if last_word in base_patterns:
                    variant_to_base[exception_key_lower] = last_word
                    variant_to_base[exception_target_lower] = last_word
    
    for lab in labels:
        canonical_lower = normalize_text(lab.canonical_name).lower()
        
        if canonical_lower in variant_to_base:
            base = variant_to_base[canonical_lower]
            if base not in base_to_variants:
                base_to_variants[base] = []
            base_to_variants[base].append(lab.ingredient_id)
        
        for base, variants in base_patterns.items():
            if canonical_lower == base:
                if base not in base_to_variants:
                    base_to_variants[base] = []
                continue
            
            for variant_pattern in variants:
                if variant_pattern.lower() in canonical_lower or canonical_lower in variant_pattern.lower():
                    if base not in base_to_variants:
                        base_to_variants[base] = []
                    if lab.ingredient_id not in base_to_variants[base]:
                        base_to_variants[base].append(lab.ingredient_id)
    
    return base_to_variants


def should_skip_single_word_for_multiword(
    single_word_name: str,
    text_for_canonical: str,
    normalized_raw_lower: str,
    inverted_index: Dict[str, List[str]],
    additional_index: Dict[str, List[str]] = None
) -> bool:
    """
    Check if a single-word canonical should be skipped because a multi-word canonical 
    containing it exists in the text.
    
    Examples:
    - Skip "powder" if "garlic powder" is in text
    - Skip "onion" if "green onion" is in text  
    - Skip "pepper" if "black pepper" is in text
    - Skip "cheese" if "cheddar cheese" is in text
    - Skip "soy" if "soy sauce" or "low sodium soy sauce" is in text
    
    This is a general solution for all single-word base ingredients.
    Checks both primary inverted_index and optional additional_index (for synonyms).
    """
    name_words = single_word_name.split()
    if len(name_words) != 1:
        return False
    
    single_word = name_words[0]
    
    # Check both primary index and additional index (if provided)
    indexes_to_check = [inverted_index]
    if additional_index is not None:
        indexes_to_check.append(additional_index)
    
    for index in indexes_to_check:
        if single_word not in index:
            continue
        
        longer_names_with_word = index[single_word]
        for longer_name in longer_names_with_word:
            if longer_name == single_word_name:
                continue
            longer_words = longer_name.split()
            if len(longer_words) > 1:
                # Check if this multi-word canonical exists in text
                longer_pattern = re.compile(r'\b' + re.escape(longer_name) + r'\b', re.IGNORECASE)
                if longer_pattern.search(text_for_canonical) or longer_pattern.search(normalized_raw_lower):
                    return True
    
    return False


def precompute_matching_maps(labels: List[IngredientLabel]) -> Tuple[Dict[str, str], Dict[str, str], Dict[str, str], List[Tuple[str, str]], List[str], List[str], Dict[str, List[str]], Dict[str, List[str]], Dict[str, List[str]]]:
    """
    Precompute all matching maps once to avoid rebuilding them for every row.
    Returns: (exception_to_id, canonical_to_id, all_synonyms_to_id, characteristic_canonicals, 
              canonical_sorted, synonyms_sorted, base_to_variants, canonical_inverted_index, synonyms_inverted_index)
    """
    exception_to_id: Dict[str, str] = {}
    for lab in labels:
        canonical_norm = normalize_text(lab.canonical_name).lower()
        for exception_key, exception_target in FALSE_VARIATION_EXCEPTIONS.items():
            exception_key_norm = normalize_text(exception_key).lower()
            exception_target_norm = normalize_text(exception_target).lower()
            if canonical_norm == exception_target_norm:
                exception_to_id[exception_key_norm] = lab.ingredient_id
            if canonical_norm == exception_key_norm:
                exception_to_id[exception_key_norm] = lab.ingredient_id
        for syn in lab.synonyms:
            syn_norm = normalize_text(syn).lower()
            for exception_key, exception_target in FALSE_VARIATION_EXCEPTIONS.items():
                exception_key_norm = normalize_text(exception_key).lower()
                exception_target_norm = normalize_text(exception_target).lower()
                if syn_norm == exception_key_norm and canonical_norm == exception_target_norm:
                    exception_to_id[exception_key_norm] = lab.ingredient_id
    
    canonical_to_id: Dict[str, str] = {}
    for lab in labels:
        canonical_norm = normalize_text(lab.canonical_name)
        if canonical_norm:
            canonical_norm_lower = canonical_norm.lower()
            if canonical_norm_lower not in exception_to_id:
                canonical_to_id[canonical_norm_lower] = lab.ingredient_id
    
    all_synonyms_to_id: Dict[str, str] = {}
    for lab in labels:
        canonical_norm = normalize_text(lab.canonical_name)
        for syn in lab.synonyms:
            syn_norm = normalize_text(syn)
            if syn_norm:
                syn_norm_lower = syn_norm.lower()
                if syn_norm_lower != canonical_norm.lower() and syn_norm_lower not in exception_to_id:
                    all_synonyms_to_id[syn_norm_lower] = lab.ingredient_id
    
    characteristic_words = get_characteristic_words()
    characteristic_canonicals = []
    for name, ing_id in canonical_to_id.items():
        if name in characteristic_words:
            characteristic_canonicals.append((name, ing_id))
    characteristic_canonicals.sort(key=lambda x: len(x[0]), reverse=True)
    
    canonical_sorted = sorted(canonical_to_id.keys(), key=len, reverse=True)
    synonyms_sorted = sorted(all_synonyms_to_id.keys(), key=len, reverse=True)
    
    base_to_variants = build_base_to_variants_map(labels)
    
    canonical_inverted_index: Dict[str, List[str]] = {}
    for name in canonical_to_id.keys():
        words = name.lower().split()
        for word in words:
            if word not in canonical_inverted_index:
                canonical_inverted_index[word] = []
            if name not in canonical_inverted_index[word]:
                canonical_inverted_index[word].append(name)
    
    synonyms_inverted_index: Dict[str, List[str]] = {}
    for name in all_synonyms_to_id.keys():
        words = name.lower().split()
        for word in words:
            if word not in synonyms_inverted_index:
                synonyms_inverted_index[word] = []
            if name not in synonyms_inverted_index[word]:
                synonyms_inverted_index[word].append(name)
    
    return exception_to_id, canonical_to_id, all_synonyms_to_id, characteristic_canonicals, canonical_sorted, synonyms_sorted, base_to_variants, canonical_inverted_index, synonyms_inverted_index


def match_ingredient_from_raw_text(raw_text: str, labels: List[IngredientLabel], exact: Dict[str, str], 
                                   precomputed_maps: Optional[Tuple[Dict[str, str], Dict[str, str], Dict[str, str], List[Tuple[str, str]], List[str], List[str], Dict[str, List[str]], Dict[str, List[str]], Dict[str, List[str]]]] = None,
                                   seen_ingredient_ids: Optional[set] = None) -> Optional[str]:
    """
    Match raw ingredient text directly against canonical ingredients.
    Strategy: 
    0. First check FALSE_VARIATION_EXCEPTIONS (highest priority) - these must match exactly
    1. Then try canonical names - after removing preparation words
    2. Then try alt_names
    3. Finally try variations
    This ensures we match "black pepper" (canonical) before "ground black pepper" (variation),
    and "black pepper" (from FALSE_VARIATION_EXCEPTIONS) before "pepper" (base ingredient).
    
    Examples:
    - "2 cups chicken broth" → matches "broth" (canonical) or "chicken broth" (variation)
    - "sliced green onions" → matches "green onion" (FALSE_VARIATION_EXCEPTIONS), not "onion"
    - "freshly ground black pepper" → matches "black pepper" (FALSE_VARIATION_EXCEPTIONS), not "pepper" or "ground black pepper"
    """
    if not raw_text:
        return None
    
    # Filter out "cooking spray" early - it's a cooking tool, not an ingredient
    if "cooking spray" in raw_text.lower():
        return None
    
    text_for_normalize = raw_text.strip()
    text_for_normalize = REGEX_LEADING_NUMBER.sub('', text_for_normalize).strip()
    
    if _HAS_BUILD_CANONICAL:
        normalized_raw = build_canonical(text_for_normalize)
    else:
        normalized_raw = normalize_text(text_for_normalize)
    normalized_raw_lower = normalized_raw.lower()
    
    if "cooking spray" in normalized_raw_lower:
        return None
    
    if "french fry" in normalized_raw_lower or "french fries" in normalized_raw_lower:
        if precomputed_maps is not None:
            _, canonical_to_id, _, _, _, _, _, _, _ = precomputed_maps
            if "potato" in canonical_to_id:
                return canonical_to_id["potato"]
        potato_norm = normalize_text("potato")
        if potato_norm in exact:
            return exact[potato_norm]
        return None
    pepper_patterns_compiled = [
        (REGEX_PEPPER_COLOR, "{} pepper"),
        (REGEX_CAYENNE_PEPPER, "cayenne pepper"),
        (REGEX_BELL_PEPPER, "bell pepper"),
        (REGEX_CHILI_PEPPER, "chili pepper"),
        (REGEX_CHILE_PEPPER, "chili pepper"),
    ]
    for pattern, template in pepper_patterns_compiled:
        match = pattern.search(normalized_raw_lower)
        if match:
            if "{}" in template:
                color = match.group(1).lower()
                pepper_type = template.format(color)
            else:
                pepper_type = template
            pepper_norm = normalize_text(pepper_type).lower()
            if precomputed_maps is not None:
                _, canonical_to_id, all_synonyms_to_id, _, _, _, _, _, _ = precomputed_maps
                if pepper_norm in canonical_to_id:
                    return canonical_to_id[pepper_norm]
                if pepper_norm in all_synonyms_to_id:
                    return all_synonyms_to_id[pepper_norm]
            if pepper_norm in exact:
                return exact[pepper_norm]
    powder_patterns_compiled = [
        (REGEX_GARLIC_POWDER, "garlic powder"),
        (REGEX_ONION_POWDER, "onion powder"),
        (REGEX_CHILI_POWDER, "chili powder"),
        (REGEX_CHILLI_POWDER, "chili powder"),
        (REGEX_CURRY_POWDER, "curry powder"),
        (REGEX_GINGER_POWDER, "ginger powder"),
        (REGEX_MUSTARD_POWDER, "mustard powder"),
        (REGEX_VANILLA_POWDER, "vanilla powder"),
        (REGEX_COCOA_POWDER, "cocoa powder"),
        (REGEX_CHOCOLATE_POWDER, "chocolate powder"),
        (REGEX_CINNAMON_POWDER, "cinnamon powder"),
        (REGEX_PAPRIKA_POWDER, "paprika powder"),
        (REGEX_CAYENNE_POWDER, "cayenne powder"),
        (REGEX_TUMERIC_POWDER, "tumeric powder"),
        (REGEX_TURMERIC_POWDER, "turmeric powder"),
    ]
    for pattern, powder_type in powder_patterns_compiled:
        match = pattern.search(normalized_raw_lower)
        if match:
            powder_norm_variants = [
                normalize_text(powder_type).lower(),
                powder_type.lower().strip(),
                REGEX_WHITESPACE.sub(' ', powder_type.lower().strip()),
            ]
            
            for powder_norm in powder_norm_variants:
                if precomputed_maps is not None:
                    _, canonical_to_id, all_synonyms_to_id, _, _, _, _, _, _ = precomputed_maps
                    if powder_norm in canonical_to_id:
                        return canonical_to_id[powder_norm]
                    if powder_norm in all_synonyms_to_id:
                        return all_synonyms_to_id[powder_norm]
                if powder_norm in exact:
                    return exact[powder_norm]
            
            if precomputed_maps is not None:
                _, canonical_to_id, all_synonyms_to_id, _, canonical_sorted, _, _, _, _ = precomputed_maps
                for name in canonical_sorted:
                    if powder_type.lower() in name.lower() or name.lower() in powder_type.lower():
                        name_norm = normalize_text(name).lower()
                        powder_norm_check = normalize_text(powder_type).lower()
                        if name_norm == powder_norm_check or name.lower() == powder_type.lower():
                            return canonical_to_id[name]
    
    if "dressing" in normalized_raw_lower:
        if precomputed_maps is not None:
            _, canonical_to_id, all_synonyms_to_id, _, _, _, _, _, _ = precomputed_maps
            if "sauce" in canonical_to_id:
                return canonical_to_id["sauce"]
            if "sauce" in all_synonyms_to_id:
                return all_synonyms_to_id["sauce"]
        sauce_norm = normalize_text("sauce")
        if sauce_norm in exact:
            return exact[sauce_norm]
    
    if " and " in normalized_raw_lower or " & " in normalized_raw_lower:
        return None
    
    if precomputed_maps is not None:
        exception_to_id, canonical_to_id, all_synonyms_to_id, characteristic_canonicals, canonical_sorted, synonyms_sorted, base_to_variants, canonical_inverted_index, synonyms_inverted_index = precomputed_maps
    else:
        exception_to_id, canonical_to_id, all_synonyms_to_id, characteristic_canonicals, canonical_sorted, synonyms_sorted, base_to_variants, canonical_inverted_index, synonyms_inverted_index = precompute_matching_maps(labels)
    
    exception_sorted = sorted(exception_to_id.keys(), key=len, reverse=True)
    
    for exception_name in exception_sorted:
        pattern = re.compile(r'\b' + re.escape(exception_name) + r'\b', re.IGNORECASE)
        if pattern.search(normalized_raw_lower):
            return exception_to_id[exception_name]
        
        exception_plural = exception_name + "s"
        pattern_plural = re.compile(r'\b' + re.escape(exception_plural) + r'\b', re.IGNORECASE)
        if pattern_plural.search(normalized_raw_lower):
            return exception_to_id[exception_name]
        
        pattern_flexible = re.compile(r'\b' + re.escape(exception_name) + r'(?:s)?\b', re.IGNORECASE)
        if pattern_flexible.search(normalized_raw_lower):
            return exception_to_id[exception_name]
    
    variant_matches = []
    for base_name, variant_ids in base_to_variants.items():
        if not variant_ids:
            continue
        
        variants_info = []
        for variant_id in variant_ids:
            for lab in labels:
                if lab.ingredient_id == variant_id:
                    variant_name = lab.canonical_name.lower()
                    variant_normalized = normalize_text(variant_name).lower()
                    variants_info.append((variant_id, variant_name, variant_normalized, base_name))
                    break
        
        variants_info.sort(key=lambda x: len(x[2]), reverse=True)
        
        for variant_id, variant_name, variant_normalized, base_name in variants_info:
            if seen_ingredient_ids is not None and variant_id in seen_ingredient_ids:
                continue
            
            pattern = re.compile(r'\b' + re.escape(variant_normalized) + r'\b', re.IGNORECASE)
            if pattern.search(normalized_raw_lower):
                variant_matches.append((variant_id, variant_name, base_name, len(variant_normalized)))
                continue
            
            variant_plural = variant_normalized + "s"
            pattern_plural = re.compile(r'\b' + re.escape(variant_plural) + r'\b', re.IGNORECASE)
            if pattern_plural.search(normalized_raw_lower):
                variant_matches.append((variant_id, variant_name, base_name, len(variant_normalized)))
                continue
            
            pattern_flexible = re.compile(r'\b' + re.escape(variant_normalized) + r'(?:s)?\b', re.IGNORECASE)
            if pattern_flexible.search(normalized_raw_lower):
                variant_matches.append((variant_id, variant_name, base_name, len(variant_normalized)))
                continue
            
            if len(variant_normalized.split()) > 1 or len(variant_normalized) > 5:
                if variant_normalized in normalized_raw_lower:
                    variant_matches.append((variant_id, variant_name, base_name, len(variant_normalized)))
                    continue
    
    if variant_matches:
        variant_matches.sort(key=lambda x: x[3], reverse=True)
        best_match = variant_matches[0]
        return best_match[0]
    characteristic_words_set = get_characteristic_words()
    
    if _HAS_BUILD_CANONICAL:
        preparation_words = list(CUT_OR_FORM_WORDS) + ["freshly", "extra", "virgin", "extra-virgin"]
    else:
        preparation_words = ["ground", "freshly", "dried", "fresh", "frozen", "sliced", "chopped", 
                            "diced", "minced", "grated", "crushed", "whole", "cracked", "extra", "virgin", "extra-virgin"]
    
    text_for_canonical = normalized_raw_lower
    for prep_word in preparation_words:
        prep_pattern = re.compile(r'\b' + re.escape(prep_word.lower()) + r'\b', re.IGNORECASE)
        text_for_canonical = prep_pattern.sub(' ', text_for_canonical)
    text_for_canonical = REGEX_WHITESPACE.sub(' ', text_for_canonical).strip()
    
    text_words = text_for_canonical.lower().split()
    candidates_set = set()
    for word in text_words:
        if word in canonical_inverted_index:
            candidates_set.update(canonical_inverted_index[word])
    
    candidates = sorted(candidates_set, key=len, reverse=True)
    if not candidates:
        candidates = canonical_sorted
    
    for name in candidates:
        if name in characteristic_words_set:
            continue
        
        # Skip single-word canonicals that are part of multi-word canonicals/synonyms in text
        # (e.g., skip "powder" if "garlic powder" is in text, skip "soy" if "soy sauce" is in text)
        # IMPORTANT: Check BOTH canonical and synonym indexes because "low sodium soy sauce" is a synonym!
        if should_skip_single_word_for_multiword(name, text_for_canonical, normalized_raw_lower, canonical_inverted_index, synonyms_inverted_index):
            continue
        
        if name in base_to_variants:
            if seen_ingredient_ids is not None:
                variants = base_to_variants[name]
                if any(variant_id in seen_ingredient_ids for variant_id in variants):
                    continue
        
        pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
        if pattern.search(text_for_canonical):
            return canonical_to_id[name]
        if pattern.search(normalized_raw_lower):
            return canonical_to_id[name]
    
    # Strategy 0.6: Check characteristic words (only if no specific canonical matched)
    characteristic_words = get_characteristic_words()
    words_in_text = normalized_raw_lower.split()
    
    if len(words_in_text) >= 2:
        multi_word_matches = []
        text_words_set = set(words_in_text)
        candidates_set = set()
        for word in text_words_set:
            if word in canonical_inverted_index:
                candidates_set.update(canonical_inverted_index[word])
        
        candidates = sorted(candidates_set, key=len, reverse=True) if candidates_set else canonical_sorted
        
        for name in candidates:
            if name in characteristic_words_set:
                continue
            name_words = name.split()
            if len(name_words) >= 2 and name_words[-1] in characteristic_words:
                # Try exact pattern match first
                pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                matched = False
                if pattern.search(normalized_raw_lower):
                    multi_word_matches.append((name, canonical_to_id[name], len(name)))
                    matched = True
                if not matched:
                    try:
                        if 'text_for_canonical' in locals() and pattern.search(text_for_canonical):
                            multi_word_matches.append((name, canonical_to_id[name], len(name)))
                            matched = True
                    except NameError:
                        pass
                # Fallback: check if all words from name are in the text consecutively
                # (for cases like "garlic powder" in "1/4teaspoon (5g) garlic powder")
                if not matched:
                    name_words_lower = [w.lower() for w in name_words]
                    text_words_lower = normalized_raw_lower.lower().split()
                    # Check if all words from name appear consecutively in text
                    for i in range(len(text_words_lower) - len(name_words_lower) + 1):
                        if text_words_lower[i:i+len(name_words_lower)] == name_words_lower:
                            multi_word_matches.append((name, canonical_to_id[name], len(name)))
                            matched = True
                            break
        
        if multi_word_matches:
            # Sort by length (longest first) and return most specific match
            multi_word_matches.sort(key=lambda x: x[2], reverse=True)
            return multi_word_matches[0][1]
    
    # Fallback to single characteristic words
    if "spray" in normalized_raw_lower and "oil" not in normalized_raw_lower:
        pass
    else:
        if words_in_text and words_in_text[-1] in characteristic_words:
            char_word = words_in_text[-1]
            if char_word in canonical_to_id:
                return canonical_to_id[char_word]
            if char_word in all_synonyms_to_id:
                return all_synonyms_to_id[char_word]
        
        for char_name, char_id in characteristic_canonicals:
            if char_name == "oil" and "spray" in normalized_raw_lower and "oil" not in normalized_raw_lower:
                continue
            pattern = re.compile(r'\b' + re.escape(char_name) + r'\b', re.IGNORECASE)
            if pattern.search(normalized_raw_lower):
                return char_id
    
    fallback_words = normalized_raw_lower.split()
    fallback_candidates_set = set()
    for word in fallback_words:
        if word in canonical_inverted_index:
            fallback_candidates_set.update(canonical_inverted_index[word])
    
    fallback_candidates = sorted(fallback_candidates_set, key=len, reverse=True) if fallback_candidates_set else canonical_sorted
    
    for name in fallback_candidates:
        if name in characteristic_words_set:
            continue
        
        # Skip single-word if multi-word exists (check both canonical and synonym indexes)
        if should_skip_single_word_for_multiword(name, text_for_canonical, normalized_raw_lower, canonical_inverted_index, synonyms_inverted_index):
            continue
        
        if name in base_to_variants:
            if seen_ingredient_ids is not None:
                variants = base_to_variants[name]
                if any(variant_id in seen_ingredient_ids for variant_id in variants):
                    continue
        
        pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
        if pattern.search(text_for_canonical):
            return canonical_to_id[name]
        if pattern.search(normalized_raw_lower):
            return canonical_to_id[name]
    
    if precomputed_maps is not None:
        text_words_for_synonyms = normalized_raw_lower.split()
        synonyms_candidates_set = set()
        for word in text_words_for_synonyms:
            if word in synonyms_inverted_index:
                synonyms_candidates_set.update(synonyms_inverted_index[word])
        
        synonyms_candidates = sorted(synonyms_candidates_set, key=len, reverse=True) if synonyms_candidates_set else sorted(all_synonyms_to_id.keys(), key=len, reverse=True)
        
        for syn_name in synonyms_candidates:
            if syn_name in characteristic_words_set:
                continue
            
            # Skip single-word synonyms if multi-word exists (check both synonym and canonical indexes)
            if should_skip_single_word_for_multiword(syn_name, text_for_canonical, normalized_raw_lower, synonyms_inverted_index, canonical_inverted_index):
                continue
            
            pattern = re.compile(r'\b' + re.escape(syn_name) + r'\b', re.IGNORECASE)
            if pattern.search(normalized_raw_lower):
                # Check if this synonym belongs to a base ingredient
                syn_id = all_synonyms_to_id[syn_name]
                # Find the base ingredient for this synonym
                for base_name, variant_ids in base_to_variants.items():
                    if syn_id in variant_ids:
                        # This is a variation of a base ingredient
                        # Check if base ingredient is a characteristic word
                        if base_name in characteristic_words_set:
                            # This is a variation of a characteristic word (e.g., "all-purpose flour" → "flour")
                            # Match with the variation, not the base
                            return syn_id
                        break
                # If not a variation of a characteristic word, continue to check if it's a variation
                # For now, return the synonym ID (it might be a variation)
                return syn_id
    
    words_for_synonyms = normalized_raw_lower.split()
    synonyms_final_candidates_set = set()
    for word in words_for_synonyms:
        if word in synonyms_inverted_index:
            synonyms_final_candidates_set.update(synonyms_inverted_index[word])
    
    synonyms_final_candidates = sorted(synonyms_final_candidates_set, key=len, reverse=True) if synonyms_final_candidates_set else synonyms_sorted
    
    for name in synonyms_final_candidates:
        # Skip single-word synonyms if multi-word exists (check both synonym and canonical indexes)
        if should_skip_single_word_for_multiword(name, text_for_canonical, normalized_raw_lower, synonyms_inverted_index, canonical_inverted_index):
            continue
        
        pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
        if pattern.search(normalized_raw_lower):
            return all_synonyms_to_id[name]
    
    words_for_compound = text_for_canonical.split()
    compound_candidates_set = set()
    for word in words_for_compound:
        if word in canonical_inverted_index:
            compound_candidates_set.update(canonical_inverted_index[word])
    
    compound_candidates = sorted(compound_candidates_set, key=len, reverse=True) if compound_candidates_set else canonical_sorted
    
    for name in compound_candidates:
        # Skip single-word if multi-word exists (check both canonical and synonym indexes)
        if should_skip_single_word_for_multiword(name, text_for_canonical, normalized_raw_lower, canonical_inverted_index, synonyms_inverted_index):
            continue
        # Skip base ingredient if specific variants are present in text
        if name in base_to_variants:
            variants = base_to_variants[name]
            variant_patterns = []
            for variant_id in variants:
                for lab in labels:
                    if lab.ingredient_id == variant_id:
                        variant_name = lab.canonical_name.lower().replace(' ', '')
                        variant_patterns.append(variant_name)
                        break
            # Check if any variant pattern matches in text (no space version)
            raw_no_space = normalized_raw_lower.replace(' ', '')
            has_variant_in_text = False
            for variant_pattern in variant_patterns:
                if variant_pattern in raw_no_space:
                    has_variant_in_text = True
                    break
            
            if has_variant_in_text:
                continue  # Skip matching base ingredient if variant is present in text
        
        name_no_space = name.replace(' ', '')
        raw_no_space = text_for_canonical.replace(' ', '')
        if name_no_space in raw_no_space and len(name_no_space) >= 3:
            return canonical_to_id[name]
        # Also try original
        raw_no_space_orig = normalized_raw_lower.replace(' ', '')
        if name_no_space in raw_no_space_orig and len(name_no_space) >= 3:
            return canonical_to_id[name]
    
    for name in synonyms_sorted:
        name_no_space = name.replace(' ', '')
        raw_no_space = normalized_raw_lower.replace(' ', '')
        if name_no_space in raw_no_space and len(name_no_space) >= 3:
            return all_synonyms_to_id[name]
    
    return None


def map_ingredient(token: str, exact: Dict[str, str], labels: List[IngredientLabel], threshold: float) -> Optional[str]:
    """
    Map ingredient token to ingredient_id.
    Enhanced to prioritize exact matches from variations before fuzzy matching.
    Uses TOKEN_MAP_CACHE for performance optimization.
    """
    if not token:
        return None
    
    # Check cache first (cache key includes threshold for correctness)
    cache_key = f"{token}::{threshold}"
    if cache_key in TOKEN_MAP_CACHE:
        return TOKEN_MAP_CACHE[cache_key]
    
    # Strategy 1: Exact match with normalized token
    tok = normalize_text(token)
    if tok in exact:
        result = exact[tok]
        TOKEN_MAP_CACHE[cache_key] = result
        return result
    
    # Strategy 2: Exact match with simplified token (without preparation methods)
    # Use exact_lookup to prevent breaking canonical ingredients like "red onion", "green onion"
    tok_simplified = _simplify_token(token, exact_lookup=exact)
    if tok_simplified and tok_simplified != tok and tok_simplified in exact:
        result = exact[tok_simplified]
        TOKEN_MAP_CACHE[cache_key] = result
        return result
    
    # Strategy 3: Try matching against original token (before normalization)
    # This helps with edge cases
    if token.lower() in exact:
        result = exact[token.lower()]
        TOKEN_MAP_CACHE[cache_key] = result
        return result
    
    # Strategy 4: Fuzzy match against canonical and synonyms
    # Only do fuzzy if exact match failed
    best_id: Optional[str] = None
    best_score: float = 0.0
    
    # First try against canonical names
    for lab in labels:
        score = similarity_ratio(tok, lab.canonical_name)
        if score > best_score:
            best_score = score
            best_id = lab.ingredient_id
        
        # Also try simplified versions
        canonical_simplified = _simplify_token(lab.canonical_name, exact_lookup=exact)
        if canonical_simplified != lab.canonical_name:
            score_simplified = similarity_ratio(tok_simplified, canonical_simplified)
            if score_simplified > best_score:
                best_score = score_simplified
                best_id = lab.ingredient_id
        
        # Try against all synonyms
        for syn in lab.synonyms:
            syn_norm = normalize_text(syn)
            sscore = similarity_ratio(tok, syn_norm)
            if sscore > best_score:
                best_score = sscore
                best_id = lab.ingredient_id
            
            # Also try simplified synonym
            syn_simplified = _simplify_token(syn, exact_lookup=exact)
            if syn_simplified != syn_norm:
                sscore_simplified = similarity_ratio(tok_simplified, syn_simplified)
                if sscore_simplified > best_score:
                    best_score = sscore_simplified
                    best_id = lab.ingredient_id
    
    result = best_id if (best_id and best_score >= threshold) else None
    TOKEN_MAP_CACHE[cache_key] = result
    return result


# ==========================================
# 🔤 SEMANTIC FALLBACK (optional)
# ==========================================
def semantic_prepare(label_list: List[IngredientLabel], device: Optional[str] = None):
    if not _HAS_SEMANTIC:
        raise RuntimeError("sentence-transformers/torch not installed.")
    model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    if device is None:
        device = "cuda" if torch.cuda.is_available() else "cpu"
    model = model.to(torch.device(device))
    label_names = [lab.canonical_name for lab in label_list]
    label_embeds = model.encode(label_names, convert_to_tensor=True, normalize_embeddings=True, batch_size=256)
    if device == "cuda":
        label_embeds = label_embeds.to(torch.device("cuda"))
    return model, label_embeds


def semantic_fallback_batch(tokens: List[str],
                            model: "SentenceTransformer",
                            label_embeds: "torch.Tensor",
                            label_list: List[IngredientLabel],
                            threshold: float = 0.78) -> Dict[str, Optional[str]]:
    """Return map token → ingredient_id (or None) using embeddings."""
    if not tokens:
        return {}
    qs = [normalize_text(t) for t in tokens]
    q_embs = model.encode(qs, convert_to_tensor=True, normalize_embeddings=True, batch_size=128)
    if label_embeds.is_cuda:
        q_embs = q_embs.to(torch.device("cuda"))
    cos = util.cos_sim(q_embs, label_embeds)  # B x N
    best_idx = torch.argmax(cos, dim=1)       # B
    best_scores = torch.gather(cos, 1, best_idx.unsqueeze(1)).squeeze(1)  # B
    out: Dict[str, Optional[str]] = {}
    for i, tok in enumerate(tokens):
        score = float(best_scores[i].item())
        idx = int(best_idx[i].item())
        out[tok] = label_list[idx].ingredient_id if score >= threshold else None
    return out


# ==========================================
# 📂 CSV READER
# ==========================================
def read_csv_rows(csv_path: Path, verbose: bool = False):
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")
    try:
        size_mb = round(csv_path.stat().st_size / (1024*1024), 2)
    except Exception:
        size_mb = None
    if verbose:
        print(f"[csv] opening {csv_path} size={size_mb}MB")

    encodings = ["utf-8-sig", "utf-8", "latin-1"]
    last_err: Exception | None = None
    for enc in encodings:
        try:
            if verbose:
                print(f"[csv] try encoding={enc}")
            with csv_path.open("r", encoding=enc, newline="") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    yield row
            return
        except UnicodeDecodeError as e:
            last_err = e
            if verbose:
                print(f"[csv] decode failed for {enc}: {e}")
            continue
    if last_err:
        raise last_err


# ==========================================
# 🍽️ RECIPE PROPERTY BUILDER
# ==========================================
def build_recipe_props(row: Dict[str, str]) -> Dict:
    """Convert a CSV row into a dictionary of Neo4j node properties."""

    def parse_minutes(x: Optional[str]) -> Optional[int]:
        if not x:
            return None
        s = str(x).strip().lower()
        total = 0
        REGEX_HOURS = re.compile(r"(\d+)\s*h")
        REGEX_MINUTES = re.compile(r"(\d+)\s*m")
        REGEX_NUMBER = re.compile(r"(\d+)")
        h = REGEX_HOURS.findall(s)
        if h:
            total += 60 * int(h[0])
        m = REGEX_MINUTES.findall(s)
        if m:
            total += int(m[0])
        if total == 0:
            m3 = REGEX_NUMBER.search(s)
            return int(m3.group(1)) if m3 else None
        return total

    def to_float(x: str) -> Optional[float]:
        """Parse float from string, handling units like '507 kcal', '14 g', '385 mg'."""
        if not x or x in ("", "N/A", "None"):
            return None
        try:
            # Try direct conversion first
            return float(x)
        except (ValueError, TypeError):
            # Extract number from string with units (e.g., "507 kcal" -> 507.0, "14 g" -> 14.0, "1.5 g" -> 1.5)
            # Match number (with optional decimal) at the start of string
            match = re.match(r'^([0-9]+(?:\.[0-9]+)?)', str(x).strip())
            if match:
                return float(match.group(1))
            return None

    def to_int(x: str) -> Optional[int]:
        try:
            return int(float(x)) if x not in (None, "", "N/A") else None
        except Exception:
            return None

    tags = []
    if row.get("recipe_category"):
        tags = [normalize_text(row["recipe_category"])]

    return {
        # Basic info
        "title": row.get("title") or "",
        "description": row.get("description") or "",
        "instructions": row.get("instructions") or "",
        "tags": tags,

        # Times
        "prep_time_min": parse_minutes(row.get("prep_time")),
        "cook_time_min": parse_minutes(row.get("cook_time")),
        "total_time_min": parse_minutes(row.get("total_time")),

        # Meta
        "servings": to_int(row.get("servings")),
        "yield": row.get("yield"),
        "cuisine": parse_cuisines(row.get("recipe_cuisine")),
        "recipe_category": row.get("recipe_category"),
        "source_url": row.get("url"),

        # Ratings
        "rating_value": to_float(row.get("rating_value")),
        "rating_count": to_int(row.get("rating_count")),
        "review_count": to_int(row.get("review_count")),

        # Popularity counters (default 0)
        "popularity_views": 0,
        "popularity_likes": 0,

        # Nutrition
        "nutrition_calories": to_float(row.get("calories")),
        "nutrition_protein": to_float(row.get("protein")),
        "nutrition_fat": to_float(row.get("fat")),
        "nutrition_carbohydrate": to_float(row.get("carbohydrate")),
        "nutrition_fiber": to_float(row.get("fiber")),
        "nutrition_sugar": to_float(row.get("sugar")),
        "nutrition_sodium": to_float(row.get("sodium")),

        # Media
        "image_urls": [row.get("image_url")] if row.get("image_url") else [],
    }


# ==========================================
# 📝 CYPHER FILE GENERATOR
# ==========================================
def escape_cypher_string(s: Optional[str]) -> str:
    """Escape string for Cypher (escape single quotes and backslashes)."""
    if s is None:
        return "null"
    # Escape backslashes first, then single quotes
    escaped = str(s).replace("\\", "\\\\").replace("'", "\\'")
    return f"'{escaped}'"


def format_cypher_value(val: any) -> str:
    """Format a value for Cypher (handle None, lists, strings, numbers)."""
    if val is None:
        return "null"
    if isinstance(val, list):
        # Format as JSON array string
        json_str = json.dumps(val, ensure_ascii=False)
        return json_str.replace("'", "\\'")
    if isinstance(val, (int, float)):
        return str(val)
    if isinstance(val, bool):
        return "true" if val else "false"
    # String - escape it
    return escape_cypher_string(val)


def generate_cypher_file(recipes: List[Dict], output_path: Path, verbose: bool = False, log_batch_size: int = 100) -> None:
    """
    Generate Cypher import file using UNWIND pattern with parameterized queries.
    This is much more efficient than individual MERGE statements.
    Similar to build_cypher_batch but writes to file with :param rows => {...}
    
    Args:
        recipes: List of recipe dictionaries
        output_path: Path to output Cypher file
        verbose: Print verbose output
        log_batch_size: Log progress every N recipes (default: 100)
    """
    print(f"[*] Generating Cypher file: {output_path}")
    print(f"   Using UNWIND pattern with parameterized queries for {len(recipes)} recipes")
    print(f"   This is much more efficient than individual MERGE statements")
    
    start_time = time.time()
    
    # Prepare data in the format expected by build_cypher_batch
    rows_data = []
    for idx, recipe in enumerate(recipes, 1):
        if idx % log_batch_size == 0:
            elapsed = time.time() - start_time
            rate = idx / elapsed if elapsed > 0 else 0
            remaining = len(recipes) - idx
            eta = remaining / rate if rate > 0 else 0
            print(f"[cypher] Progress: {idx}/{len(recipes)} recipes ({idx*100//len(recipes)}%) - {rate:.1f} recipes/sec - ETA: {eta:.0f}s")
        
        rows_data.append(recipe)
        
    # Build the parameter JSON
    # json.dumps() automatically serializes None to null in JSON
    param_json = json.dumps({"rows": rows_data}, ensure_ascii=False)
    
    # Get the Cypher query template from build_cypher_batch
    cypher_query = build_cypher_batch([])
        
    # Combine parameter definition with query
    cypher_content = f":param rows => {param_json};\n\n{cypher_query}"
    
    output_path.parent.mkdir(parents=True, exist_ok=True)
    print(f"[cypher] Writing file to {output_path}...")
    output_path.write_text(cypher_content, encoding="utf-8")
    
    total_time = time.time() - start_time
    file_size_mb = output_path.stat().st_size / 1024 / 1024
    print(f"[OK] Generated Cypher file with {len(recipes)} recipes")
    print(f"   File size: {file_size_mb:.1f} MB")
    print(f"   Time taken: {total_time:.1f}s ({len(recipes)/total_time:.1f} recipes/sec)")
    print(f"   To import: Run this file in Neo4j Browser or use cypher-shell")
    print(f"   Example: cypher-shell.bat -a bolt://localhost:7687 -u neo4j -p 'password' -d test --file {output_path}")


# ==========================================
# 🧱 CYPHER BUILDER
# ==========================================
def build_cypher_batch(_: List[Dict]) -> str:
    """Construct Cypher query for batch import into Neo4j (params come in $rows)."""
    lines: List[str] = []
    lines.append("UNWIND $rows AS row")
    lines.append("MERGE (r:Recipe {recipe_id: row.recipe_id})")
    lines.append("SET r.title = row.props.title,")
    lines.append("    r.description = row.props.description,")
    lines.append("    r.instructions = row.props.instructions,")
    lines.append("    r.tags = row.props.tags,")
    lines.append("    r.prep_time_min = row.props.prep_time_min,")
    lines.append("    r.cook_time_min = row.props.cook_time_min,")
    lines.append("    r.total_time_min = row.props.total_time_min,")
    lines.append("    r.servings = row.props.servings,")
    lines.append("    r.yield = row.props.yield,")
    lines.append("    r.cuisine = row.props.cuisine,")
    lines.append("    r.recipe_category = row.props.recipe_category,")
    lines.append("    r.source_url = row.props.source_url,")
    lines.append("    r.rating_value = row.props.rating_value,")
    lines.append("    r.rating_count = row.props.rating_count,")
    lines.append("    r.review_count = row.props.review_count,")
    lines.append("    r.popularity_views = coalesce(row.props.popularity_views,0),")
    lines.append("    r.popularity_saves = coalesce(row.props.popularity_saves,0),")
    lines.append("    r.popularity_cooks = coalesce(row.props.popularity_cooks,0),")
    lines.append("    r.popularity_likes = coalesce(row.props.popularity_likes,0),")
    lines.append("    r.nutrition_calories = row.props.nutrition_calories,")
    lines.append("    r.nutrition_protein = row.props.nutrition_protein,")
    lines.append("    r.nutrition_fat = row.props.nutrition_fat,")
    lines.append("    r.nutrition_carbohydrate = row.props.nutrition_carbohydrate,")
    lines.append("    r.nutrition_fiber = row.props.nutrition_fiber,")
    lines.append("    r.nutrition_sugar = row.props.nutrition_sugar,")
    lines.append("    r.nutrition_sodium = row.props.nutrition_sodium,")
    lines.append("    r.image_urls = row.props.image_urls")
    lines.append("WITH r, row")

    # Ingredient relationships
    # Pattern similar to import_canonical_ingredients.py: ensure ingredients exist, then create relationships
    # Note: Ingredients must be imported first using import_canonical_ingredients.py
    # Use CALL (r, row) { ... } syntax (variable scope clause) to avoid deprecation warning
    lines.append("CALL (r, row) {")
    lines.append("  UNWIND coalesce(row.ingredients, []) AS ing")
    lines.append("  // Match existing ingredient (must exist from canonical_ingredients import)")
    lines.append("  // This will fail if ingredient doesn't exist - ensure ingredients are imported first")
    lines.append("  MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})")
    lines.append("  // Create or update HAS_INGREDIENT relationship (similar to MERGE pattern in import_canonical_ingredients.py)")
    lines.append("  MERGE (r)-[rel:HAS_INGREDIENT]->(i)")
    lines.append("  RETURN count(*) AS _")
    lines.append("}")
    lines.append("WITH r, row")

    # Cuisine relationships
    lines.append("UNWIND coalesce(row.props.cuisine, []) AS cuisineName")
    lines.append("MERGE (cu:Cuisine {name: cuisineName})")
    lines.append("MERGE (r)-[:OF_CUISINE]->(cu)")

    return "\n".join(lines)


# ==========================================
# ⚙️ EXECUTION UTILITIES
# ==========================================
def run_cypher_shell(cypher: str, neo4j_uri: str, user: str, password: str) -> None:
    """Run Cypher query via cypher-shell."""
    proc = subprocess.Popen(
        ["cypher-shell.bat" if os.name == "nt" else "cypher-shell", "-a", neo4j_uri, "-u", user, "-p", password],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    out, err = proc.communicate(cypher)
    if proc.returncode != 0:
        raise RuntimeError(f"cypher-shell error: {err}\nOutput: {out}")


def run_via_driver(rows: List[Dict], *, uri: str, user: str, password: str, database: Optional[str]) -> None:
    """
    Send batched queries using the official Neo4j Python driver (with retry).
    Pattern similar to import_canonical_ingredients.py for consistency.
    """
    query = build_cypher_batch(rows)
    driver = GraphDatabase.driver(uri, auth=(user, password))
    session_kwargs = {"database": database} if database else {}
    
    for attempt in range(3):
        try:
            with driver.session(**session_kwargs) as session:
                result = session.run(query, rows=rows)
                result.consume()  # Consume result to ensure execution (like import_canonical_ingredients.py)
            print(f"[neo4j] batch inserted successfully ({len(rows)} rows)")
            break
        except Exception as e:
            if attempt < 2:  # Not last attempt
                print(f"[retry] Neo4j error at batch ({attempt+1}/3): {e}")
                import time
                time.sleep(2)
            else:  # Last attempt failed
                print(f"[error] Neo4j error at batch (final attempt): {e}")
                # Check if error is due to missing ingredients
                error_str = str(e).lower()
                if "ingredient" in error_str or "not found" in error_str or "null" in error_str:
                    print(f"[warning] Some ingredients may not exist. Ensure ingredients are imported first using:")
                    print(f"         python scripts/import_canonical_ingredients.py")
                raise
    driver.close()



# ==========================================
# 🚀 MAIN FUNCTION
# ==========================================
def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Import recipes from CSV into Neo4j with ingredient mapping (fuzzy + semantic fallback)")
    parser.add_argument("--csv", type=str, default=str(Path("data/recipes/full_data_ing.csv")), help="Path to CSV with recipes")
    parser.add_argument("--labels", type=str, default=str(Path("data/process/canonical_ingredients_migrated.json")), help="Path to ingredient labels (.json or .txt, default: canonical_ingredients_migrated.json)")
    parser.add_argument("--threshold", type=float, default=0.85, help="Fuzzy (Levenshtein) match threshold (0-1)")
    parser.add_argument("--semantic", action="store_true", help="Enable semantic fallback with SentenceTransformer")
    parser.add_argument("--semantic-threshold", type=float, default=0.78, help="Cosine threshold for semantic fallback (0-1)")
    parser.add_argument("--uri", default=DEFAULT_URI)
    parser.add_argument("--user", default=DEFAULT_USER)
    parser.add_argument("--password", default=DEFAULT_PASS)
    parser.add_argument("--db", dest="database", default=DEFAULT_DB)
    parser.add_argument("--use-driver", action="store_true", help="Use Neo4j Python driver for import (recommended)")
    parser.add_argument("--batch-size", type=int, default=3000, help="Number of recipes per batch (default: 3000, optimized for performance)")
    parser.add_argument("--dry-run", action="store_true", help="Print Cypher only, do not execute")
    parser.add_argument("--out-cypher", type=str, default=None, help="Optional: Generate Cypher file instead of direct import")
    parser.add_argument("--cypher-log-batch-size", type=int, default=100, help="Log progress every N recipes when generating Cypher file (default: 100)")
    parser.add_argument("--limit", type=int, default=None, help="Process only the first N rows")
    parser.add_argument("--verbose", action="store_true", help="Print debug logs while processing")
    parser.add_argument("--log-every", type=int, default=1000, help="Log progress every N rows")
    args = parser.parse_args()

    csv_path = Path(args.csv)
    labels_path = Path(args.labels)

    # Load labels (json ưu tiên)
    if labels_path.suffix.lower() == ".json":
        label_list = load_label_json(labels_path)
    else:
        label_list = load_label_set(labels_path)
    exact, label_list = build_lookup(label_list)

    # Precompute matching maps once (performance optimization)
    if args.verbose:
        print("[optimization] precomputing matching maps...")
    precomputed_maps = precompute_matching_maps(label_list)
    if args.verbose:
        print(f"[optimization] precomputed maps ready (exceptions={len(precomputed_maps[0])}, canonicals={len(precomputed_maps[1])}, synonyms={len(precomputed_maps[2])})")

    # Semantic init (nếu bật)
    model = None
    label_embeds = None
    if args.semantic:
        if not _HAS_SEMANTIC:
            raise RuntimeError("Bạn bật --semantic nhưng chưa cài sentence-transformers/torch.")
        if args.verbose:
            print("[semantic] initializing model & encoding label embeddings…")
        model, label_embeds = semantic_prepare(label_list)
        if args.verbose:
            device = "cuda" if (hasattr(label_embeds, "is_cuda") and label_embeds.is_cuda) else "cpu"
            print(f"[semantic] ready (device={device}, labels={len(label_list)})")

    iterator = read_csv_rows(csv_path, verbose=args.verbose)
    batch_rows: List[Dict] = []
    cypher_batches: List[str] = []
    all_recipes: List[Dict] = []  # Collect all recipes if generating Cypher file
    
    # Performance tracking for speed logging
    start_time = time.time()
    last_log_time = start_time
    last_log_idx = 0
    
    # Batch semantic fallback optimization: collect unmatched tokens and process in batches
    semantic_batch_tokens: List[str] = []
    semantic_batch_size = 3000
    
    for idx, row in enumerate(iterator, 1):
        try:
            if args.limit and idx > args.limit:
                break

            recipe_id = f"rec_{idx}"
            props = build_recipe_props(row)
            raw_ing = row.get("ingredients", "")
            
            # NEW APPROACH: Direct matching from raw text against canonical ingredients
            # Split by common separators but keep full phrases for matching
            ing_parts = REGEX_INGREDIENT_SEPARATORS.split(raw_ing)
            seen = set()
            mapped_ids: List[str] = []
            
            for part in ing_parts:
                part = part.strip()
                if not part or len(part) < 2:
                    continue
                
                # Filter out non-ingredient parts (like "[Ingredients]", standalone numbers, etc.)
                part_lower = part.lower()
                # Remove "[Ingredients]" marker if present (but keep the rest of the text)
                if part_lower.startswith("[ingredients]") or part_lower.startswith("[ingredient]"):
                    # Remove marker and keep the rest
                    REGEX_INGREDIENTS_MARKER = re.compile(r'^\[ingredients?\]\s*', re.IGNORECASE)
                    part = REGEX_INGREDIENTS_MARKER.sub('', part).strip()
                    part_lower = part.lower()
                    # If after removing marker, part is empty, skip it
                    if not part or len(part) < 2:
                        continue
                # Skip parts that are mostly numbers/units (quantity information)
                # But keep parts that have some text along with numbers
                REGEX_NUMBERS_ONLY = re.compile(r'^[\d\s\/\(\)gmltbspcups]+$')
                REGEX_LETTERS = re.compile(r'[a-z]')
                if REGEX_NUMBERS_ONLY.match(part_lower) and len(REGEX_LETTERS.findall(part_lower)) < 2:
                    continue
                
                # Filter out parts that are ONLY preparation words (like "boneless", "skinless", "patted dry")
                # These are modifiers, not ingredients themselves
                # First, remove numbers and units to check if only preparation words remain
                part_for_check = part_lower
                part_for_check = REGEX_LEADING_NUMBER.sub('', part_for_check).strip()
                part_for_check = REGEX_QUANTITY_PAREN.sub('', part_for_check).strip()
                part_for_check = REGEX_QUANTITY_UNIT.sub('', part_for_check).strip()
                part_for_check = REGEX_STANDALONE_NUMBER.sub('', part_for_check).strip()
                part_for_check = REGEX_UNIT_WORDS.sub('', part_for_check).strip()
                part_for_check = REGEX_WHITESPACE.sub(' ', part_for_check).strip()
                
                # Check if part is ONLY preparation/cut words (from CUT_OR_FORM_WORDS)
                if part_for_check:
                    part_words = part_for_check.lower().split()
                    # If all words are preparation/cut words and no ingredient name, skip it
                    all_prep_words = all(word in CUT_OR_FORM_WORDS for word in part_words)
                    # Also check common preparation phrases
                    prep_phrases = {"patted dry", "patted", "dry", "lightly beaten", "lightly", "beaten", "divided", "optional", "plus more", "for garnish", "for serving"}
                    all_prep_phrases = part_for_check.lower() in prep_phrases or all(word in prep_phrases for word in part_words)
                    # If it's only preparation words/phrases, skip it
                    if all_prep_words or all_prep_phrases:
                        continue
                
                # Special handling for "French fries" - must be handled before direct matching
                # to avoid false matches with "red" or other ingredients
                if "french fry" in part_lower or "french fries" in part_lower:
                    # Directly map to potato
                    potato_id = exact.get("potato") or exact.get(normalize_text("potato"))
                    if potato_id and potato_id not in seen:
                        mapped_ids.append(potato_id)
                        seen.add(potato_id)
                        continue
                
                # Generalized handling: Check variants BEFORE base ingredients
                # This ensures "chicken breast", "cheddar cheese", "yellow onion", etc. 
                # match with specific variants instead of generic base ingredients
                variant_matched = False
                if precomputed_maps is not None:
                    _, canonical_to_id, all_synonyms_to_id, _, _, _, base_to_variants, _, _ = precomputed_maps
                    
                    # Check all variants from all bases (prioritize longer/more specific variants)
                    # IMPORTANT: Only match multi-word variants here - single-word variants will be handled by SPECIAL HANDLING
                    # This prevents "soy" from matching before "soy sauce" is checked
                    all_variants_info = []
                    for base_name, variant_ids in base_to_variants.items():
                        for variant_id in variant_ids:
                            if variant_id in seen:
                                continue  # Skip already matched variants
                            for lab in label_list:
                                if lab.ingredient_id == variant_id:
                                    variant_name = lab.canonical_name.lower()
                                    variant_normalized = normalize_text(variant_name).lower()
                                    
                                    # Skip single-word variants - let SPECIAL HANDLING handle multi-word ingredients first
                                    variant_words = variant_normalized.split()
                                    if len(variant_words) < 2:
                                        break  # Skip single-word variants
                                    
                                    # Check if variant name appears in part
                                    # Try exact match first (most reliable)
                                    pattern = r'\b' + re.escape(variant_normalized) + r'\b'
                                    if re.search(pattern, part_lower, re.IGNORECASE):
                                        all_variants_info.append((variant_id, variant_name, variant_normalized, len(variant_normalized), base_name))
                                    # Also try plural form
                                    variant_plural = variant_normalized + "s"
                                    pattern_plural = r'\b' + re.escape(variant_plural) + r'\b'
                                    if re.search(pattern_plural, part_lower, re.IGNORECASE):
                                        all_variants_info.append((variant_id, variant_name, variant_normalized, len(variant_normalized), base_name))
                                    # Also try partial match (for cases like "boneless skinless chicken breast")
                                    if len(variant_normalized) > 5 and variant_normalized in part_lower:
                                        all_variants_info.append((variant_id, variant_name, variant_normalized, len(variant_normalized), base_name))
                                    break
                    
                    # Sort by length (longest first) to match most specific variants first
                    if all_variants_info:
                        all_variants_info.sort(key=lambda x: x[3], reverse=True)
                        # Use the most specific variant match
                        best_variant_id, _, _, _, _ = all_variants_info[0]
                        if best_variant_id not in seen:
                            mapped_ids.append(best_variant_id)
                            seen.add(best_variant_id)
                            variant_matched = True
                
                if variant_matched:
                    continue
                
                # SPECIAL HANDLING: Check for multi-word ingredients directly in part_lower
                if precomputed_maps is not None:
                    exception_to_id, canonical_to_id, all_synonyms_to_id, _, canonical_sorted, _, base_to_variants, _, _ = precomputed_maps
                    
                    # Strategy: Find all multi-word ingredients that match in part_lower
                    # CRITICAL: Check exact matches first, then longer matches
                    # This ensures "black pepper" matches before "black peppercorn" if both could match
                    # NOTE: Must check BOTH exception_to_id (for FALSE_VARIATION_EXCEPTIONS like "black pepper", "green onion")
                    #       AND canonical_to_id (for regular multi-word ingredients like "garlic powder")
                    multi_word_matches = []
                    # First pass: collect all potential matches from exception_to_id
                    potential_matches = []
                    
                    # Check exception_to_id first (for FALSE_VARIATION_EXCEPTIONS like "black pepper", "green onion")
                    exception_sorted = sorted(exception_to_id.keys(), key=len, reverse=True)
                    for exception_name in exception_sorted:
                        # Only check multi-word ingredients (2+ words)
                        name_words = exception_name.split()
                        if len(name_words) < 2:
                            continue
                        
                        # Check if this exception appears in part
                        pattern = r'\b' + re.escape(exception_name) + r'\b'
                        # Also check plural form
                        exception_plural = exception_name + "s"
                        pattern_plural = r'\b' + re.escape(exception_plural) + r'\b'
                        if re.search(pattern, part_lower, re.IGNORECASE) or re.search(pattern_plural, part_lower, re.IGNORECASE):
                            ing_id = exception_to_id[exception_name]
                            if ing_id not in seen:
                                potential_matches.append((exception_name, ing_id, len(exception_name)))
                    
                    # Second pass: check canonical_to_id (for regular multi-word ingredients)
                    for name in canonical_sorted:
                        # Only check multi-word ingredients (2+ words)
                        name_words = name.split()
                        if len(name_words) < 2:
                            continue
                        
                        # Skip if already matched in exception_to_id
                        name_lower = name.lower()
                        if name_lower in exception_to_id:
                            continue
                        
                        # Skip if this canonical is a base and we already have a variant
                        name_is_base = name in base_to_variants
                        if name_is_base and seen:
                            variants = base_to_variants[name]
                            if any(variant_id in seen for variant_id in variants):
                                continue
                        
                        # Check if this multi-word canonical appears in part
                        # Also check plural form (e.g., "yellow onions" -> "yellow onion")
                        pattern = r'\b' + re.escape(name) + r'\b'
                        name_plural = name + "s"
                        pattern_plural = r'\b' + re.escape(name_plural) + r'\b'
                        if re.search(pattern, part_lower, re.IGNORECASE) or re.search(pattern_plural, part_lower, re.IGNORECASE):
                            ing_id = canonical_to_id[name]
                            if ing_id not in seen:
                                potential_matches.append((name, ing_id, len(name)))
                    
                    # Sort matches: exact word-boundary matches first, then by length (longest first)
                    # This ensures "black pepper" (exact) matches before "black peppercorn" (longer but not exact)
                    exact_matches = []
                    other_matches = []
                    for name, ing_id, name_len in potential_matches:
                        # Check if this is an exact match (name appears as complete words in part)
                        # Extract words from part and check if name matches exactly
                        part_words = part_lower.split()
                        name_words = name.split()
                        # Check if name_words appear consecutively in part_words
                        is_exact = False
                        for i in range(len(part_words) - len(name_words) + 1):
                            if part_words[i:i+len(name_words)] == name_words:
                                is_exact = True
                                break
                        
                        if is_exact:
                            exact_matches.append((name, ing_id, name_len))
                        else:
                            other_matches.append((name, ing_id, name_len))
                    
                    # Sort exact matches by length (longest first) - most specific exact match first
                    exact_matches.sort(key=lambda x: x[2], reverse=True)
                    # Sort other matches by length (longest first)
                    other_matches.sort(key=lambda x: x[2], reverse=True)
                    # Combine: exact matches first, then other matches
                    multi_word_matches = exact_matches + other_matches
                    
                    # Match all multi-word ingredients found in part (not just first one)
                    # This handles cases like "garlic powder and onion powder"
                    matched_any = False
                    for name, ing_id, _ in multi_word_matches:
                        mapped_ids.append(ing_id)
                        seen.add(ing_id)
                        matched_any = True
                    
                    # If any multi-word ingredient matched, skip further processing (avoid duplicate base ingredient)
                    if matched_any:
                        continue
                
                # Try direct matching first (simpler and more accurate) - use precomputed maps
                # This already has Strategy 0.25 to check variants, but we do it here too for extra safety
                ing_id = match_ingredient_from_raw_text(part, label_list, exact, precomputed_maps=precomputed_maps, seen_ingredient_ids=seen)
                if ing_id and ing_id not in seen:
                    mapped_ids.append(ing_id)
                    seen.add(ing_id)
                    continue
                
                # Fallback to tokenize + fuzzy matching if direct match fails
                # Note: If multi-word ingredient was detected above, we already continue (skip tokenization)
                tokens = tokenize_ingredients(part)
                
                # Check if part contains multi-word variants to skip generic base ingredients
                # This prevents duplicate mapping: "garlic powder" (correct) + "powder" (wrong)
                has_multi_word_variants_in_part = False
                if precomputed_maps is not None:
                    _, canonical_to_id, _, _, canonical_sorted, _, base_to_variants, _, _ = precomputed_maps
                    # Check if any multi-word canonical matches in part
                    for name in canonical_sorted:
                        name_words = name.split()
                        if len(name_words) >= 2:
                            pattern = re.compile(r'\b' + re.escape(name) + r'\b', re.IGNORECASE)
                            if pattern.search(part_lower):
                                has_multi_word_variants_in_part = True
                                break
                
                for tok in tokens:
                    tok_lower = tok.lower().strip()
                    
                    # Skip if token is only a preparation word (not a real ingredient)
                    if tok_lower in CUT_OR_FORM_WORDS:
                        continue
                    
                    # Skip base ingredient if specific variants are already present (generalized logic)
                    tok_normalized = normalize_text(tok)
                    if precomputed_maps is not None:
                        _, _, _, _, _, _, base_to_variants, _, _ = precomputed_maps
                        if tok_normalized in base_to_variants:
                            # This token is a base ingredient (e.g., "powder", "pepper", "onion", "sauce")
                            
                            # Strategy 1: Check if any variant of this base is already matched
                            variants = base_to_variants[tok_normalized]
                            has_variant_matched = any(variant_id in seen for variant_id in variants)
                            if has_variant_matched:
                                continue  # Skip matching base ingredient if variant is already present
                            
                            # Strategy 2: Check if part contains multi-word variant (even if not matched yet)
                            if has_multi_word_variants_in_part:
                                # If we detected multi-word variants in part, skip this base
            
                                continue
                    
                    ing_id = map_ingredient(tok, exact, label_list, args.threshold)
                    if ing_id and ing_id not in seen:
                        mapped_ids.append(ing_id)
                        seen.add(ing_id)
                
                # Collect unmatched tokens for batch semantic fallback (if enabled)
                if args.semantic:
                    for t in tokens:
                        # Check if this token was already matched
                        already_matched = False
                        for existing_id in seen:
                            # Quick check: if token was matched, skip
                            if map_ingredient(t, exact, label_list, args.threshold) == existing_id:
                                already_matched = True
                                break
                        if not already_matched and t not in semantic_batch_tokens:
                            semantic_batch_tokens.append(t)

            ingredients_edges = [{"ingredient_id": iid} for iid in mapped_ids]
            recipe_data = {"recipe_id": recipe_id, "props": props, "tags": props.get("tags", []), "ingredients": ingredients_edges}
            batch_rows.append(recipe_data)
            
            # Collect for Cypher file generation
            if args.out_cypher:
                all_recipes.append(recipe_data)

            # Logging - chỉ log ingredients
            # Log first 20 rows, then every log_every rows, or more frequently when generating Cypher
            should_log = False
            if args.verbose:
                if idx <= 20:
                    should_log = True
                elif args.out_cypher:
                    # When generating Cypher file, log more frequently for better visibility
                    cypher_log_interval = getattr(args, 'cypher_log_batch_size', 100)
                    if idx % cypher_log_interval == 0:
                        should_log = True
                elif args.log_every and idx % args.log_every == 0:
                    should_log = True
            
            if should_log:
                # Chỉ log ingredients
                # Handle encoding errors when printing raw_ing (may contain Unicode characters)
                try:
                    raw_ing_safe = raw_ing.encode('ascii', errors='replace').decode('ascii')
                except Exception:
                    raw_ing_safe = raw_ing
                print(f"[row] #{idx} ingredients_raw='{raw_ing_safe}'")
                print(f"      mapped_ids={mapped_ids}")
            
            # Speed logging every 2000 rows
            if idx % 2000 == 0:
                current_time = time.time()
                elapsed = current_time - last_log_time
                rows_processed = idx - last_log_idx
                rows_per_sec = rows_processed / elapsed if elapsed > 0 else 0
                total_elapsed = current_time - start_time
                avg_rows_per_sec = idx / total_elapsed if total_elapsed > 0 else 0
                print(f"[speed] row #{idx}: {rows_per_sec:.1f} rows/sec (last 2000), {avg_rows_per_sec:.1f} rows/sec (avg)")
                last_log_time = current_time
                last_log_idx = idx
            
            # Process semantic batch if it reaches threshold
            if args.semantic and len(semantic_batch_tokens) >= semantic_batch_size:
                if args.verbose:
                    print(f"[semantic] processing batch of {len(semantic_batch_tokens)} unmatched tokens...")
                sem_map = semantic_fallback_batch(semantic_batch_tokens, model, label_embeds, label_list, threshold=args.semantic_threshold)
                # Apply semantic matches back to rows (simplified: just cache results)
                # Note: Cache with semantic threshold for future lookups
                for tok, ing_id in sem_map.items():
                    if ing_id:
                        # Cache the result for future use (use semantic threshold as part of key)
                        cache_key = f"{tok}::semantic::{args.semantic_threshold}"
                        TOKEN_MAP_CACHE[cache_key] = ing_id
                semantic_batch_tokens.clear()

            # Batch flush (skip if generating Cypher file)
            if not args.out_cypher and len(batch_rows) >= args.batch_size:
                print(f"[batch] importing up to row #{idx} (size={len(batch_rows)})")
                if args.use_driver and not args.dry_run:
                    run_via_driver(batch_rows, uri=args.uri, user=args.user, password=args.password, database=args.database)

                else:
                    cypher = build_cypher_batch([])
                    param_json = json.dumps({"rows": batch_rows})
                    full = f":param rows => {param_json};\n{cypher}"
                    cypher_batches.append(full)
                    if not args.dry_run:
                        run_cypher_shell(full, args.uri, args.user, args.password)

                batch_rows = []

        except Exception as e:
            # Handle encoding errors when printing error messages
            try:
                error_msg = str(e)
            except Exception:
                error_msg = repr(e)
            # Encode to ASCII-safe string to avoid Windows console encoding issues
            try:
                error_msg_safe = error_msg.encode('ascii', errors='replace').decode('ascii')
            except Exception:
                error_msg_safe = error_msg
            print(f"[error] row #{idx}: {error_msg_safe}")
            continue

    # Process final semantic batch if any remaining
    if args.semantic and semantic_batch_tokens:
        if args.verbose:
            print(f"[semantic] processing final batch of {len(semantic_batch_tokens)} unmatched tokens...")
        sem_map = semantic_fallback_batch(semantic_batch_tokens, model, label_embeds, label_list, threshold=args.semantic_threshold)
        # Cache results
        for tok, ing_id in sem_map.items():
            if ing_id:
                cache_key = f"{tok}::semantic::{args.semantic_threshold}"
                TOKEN_MAP_CACHE[cache_key] = ing_id
        semantic_batch_tokens.clear()

    # Generate Cypher file if requested
    if args.out_cypher:
        output_path = Path(args.out_cypher)
        generate_cypher_file(all_recipes, output_path, args.verbose, log_batch_size=args.cypher_log_batch_size)
    else:
        # Final leftover batch (only if not generating Cypher file)
        if batch_rows:
            if args.use_driver and not args.dry_run:
                run_via_driver(batch_rows, uri=args.uri, user=args.user, password=args.password, database=args.database)
            else:
                cypher = build_cypher_batch([])
                param_json = json.dumps({"rows": batch_rows})
                full = f":param rows => {param_json};\n{cypher}"
                cypher_batches.append(full)
                if not args.dry_run:
                    run_cypher_shell(full, args.uri, args.user, args.password)

        # Preview file nếu dry-run
        if args.dry_run:
            out_path = Path("data/recipes/recipes_import.cypher")
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text("\n\n".join(cypher_batches), encoding="utf-8")
            print(f"[dry-run] wrote Cypher preview to {out_path} (batches={len(cypher_batches)})")

    # Final speed summary
    total_time = time.time() - start_time
    avg_speed = idx / total_time if total_time > 0 else 0
    print(f"[OK] Import completed! Processed {idx} rows in {total_time:.1f}s ({avg_speed:.1f} rows/sec)")


if __name__ == "__main__":
    main()
