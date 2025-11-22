#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Import recipes from Spoonacular API into Neo4j.

Usage:
    python import_spoonacular_to_neo4j.py \
        --query "pasta" \
        --cuisine "italian" \
        --number 50 \
        --include-nutrition

Requirements:
    pip install httpx neo4j python-dotenv
"""

import os
import sys
import asyncio
import httpx
from typing import Dict, List, Optional, Set
from neo4j import GraphDatabase
from dotenv import load_dotenv
import argparse
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Load environment variables
load_dotenv()

# Neo4j connection
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "Admin123!")
NEO4J_DB = os.getenv("NEO4J_DB", "test")

# Spoonacular API
SPOONACULAR_API_KEY = os.getenv("SPOONACULAR_API_KEY")
SPOONACULAR_BASE_URL = "https://api.spoonacular.com"


class SpoonacularImporter:
    def __init__(self):
        if not SPOONACULAR_API_KEY:
            raise ValueError("SPOONACULAR_API_KEY not found in environment variables")
        
        self.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
        self.ingredient_cache = {}  # Cache ingredient mappings
        self.cuisine_cache = {}  # Cache cuisine nodes
    
    def close(self):
        self.driver.close()
    
    async def fetch_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        max_ready_time: Optional[int] = None,
        number: int = 10,
        offset: int = 0
    ) -> List[Dict]:
        """Fetch recipes from Spoonacular API."""
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "number": min(number, 100),  # Max 100 per request
            "offset": offset,
            "addRecipeInformation": "true",
            "fillIngredients": "true"
        }
        
        if query:
            params["query"] = query
        if cuisine:
            params["cuisine"] = cuisine
        if diet:
            params["diet"] = diet
        if intolerances:
            params["intolerances"] = ",".join(intolerances)
        if max_ready_time:
            params["maxReadyTime"] = max_ready_time
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{SPOONACULAR_BASE_URL}/recipes/complexSearch",
                    params=params
                )
                response.raise_for_status()
                data = response.json()
                return data.get("results", [])
            except httpx.HTTPStatusError as e:
                print(f"❌ Error fetching recipes: {e.response.text}")
                return []
    
    async def fetch_recipe_details(self, recipe_id: int) -> Optional[Dict]:
        """Fetch detailed recipe information including nutrition."""
        params = {
            "apiKey": SPOONACULAR_API_KEY,
            "includeNutrition": "true"
        }
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.get(
                    f"{SPOONACULAR_BASE_URL}/recipes/{recipe_id}/information",
                    params=params
                )
                response.raise_for_status()
                return response.json()
            except httpx.HTTPStatusError as e:
                print(f"❌ Error fetching recipe {recipe_id}: {e.response.text}")
                return None
    
    def get_or_create_ingredient(
        self,
        session,
        spoonacular_ingredient: Dict
    ) -> Optional[str]:
        """
        Map Spoonacular ingredient to Neo4j ingredient.
        Returns ingredient_id if found/created, None otherwise.
        """
        ing_name = spoonacular_ingredient.get("name", "").lower().strip()
        ing_id_spoonacular = spoonacular_ingredient.get("id")
        
        # Check cache first
        cache_key = f"{ing_name}_{ing_id_spoonacular}"
        if cache_key in self.ingredient_cache:
            return self.ingredient_cache[cache_key]
        
        # Try to find existing ingredient by name (exact match)
        q_find = """
        MATCH (i:Ingredient)
        WHERE toLower(i.canonical_name) = $name
           OR toLower(i.name) = $name
           OR any(alt IN coalesce(i.alt_names, []) WHERE toLower(alt) = $name)
        RETURN i.ingredient_id AS ingredient_id
        LIMIT 1
        """
        result = session.run(q_find, name=ing_name).single()
        
        if result:
            ingredient_id = result["ingredient_id"]
            self.ingredient_cache[cache_key] = ingredient_id
            return ingredient_id
        
        # Try fuzzy match (contains)
        q_fuzzy = """
        MATCH (i:Ingredient)
        WHERE toLower(i.canonical_name) CONTAINS $name
           OR toLower(i.name) CONTAINS $name
        RETURN i.ingredient_id AS ingredient_id, i.canonical_name AS name
        ORDER BY size(i.canonical_name) ASC
        LIMIT 5
        """
        fuzzy_results = list(session.run(q_fuzzy, name=ing_name))
        
        if fuzzy_results:
            # Use the shortest match (most likely)
            ingredient_id = fuzzy_results[0]["ingredient_id"]
            self.ingredient_cache[cache_key] = ingredient_id
            print(f"  ⚠️  Fuzzy matched '{ing_name}' -> {fuzzy_results[0]['name']}")
            return ingredient_id
        
        # If not found, create new ingredient
        # Generate ingredient_id from name
        ingredient_id = f"ing_{ing_name.replace(' ', '_').replace('-', '_').replace(',', '')}"
        
        q_create = """
        MERGE (i:Ingredient {ingredient_id: $ing_id})
        SET i.canonical_name = $name,
            i.name = $name,
            i.category = coalesce($category, 'other'),
            i.spoonacular_id = $spoonacular_id,
            i.created_at = datetime()
        RETURN i.ingredient_id AS ingredient_id
        """
        
        category = self._infer_category(spoonacular_ingredient)
        result = session.run(
            q_create,
            ing_id=ingredient_id,
            name=spoonacular_ingredient.get("name", ""),
            category=category,
            spoonacular_id=ing_id_spoonacular
        ).single()
        
        if result:
            self.ingredient_cache[cache_key] = ingredient_id
            print(f"  ✅ Created new ingredient: {ingredient_id} ({spoonacular_ingredient.get('name')})")
            return ingredient_id
        
        return None
    
    def _infer_category(self, ingredient: Dict) -> str:
        """Infer ingredient category from Spoonacular data."""
        # Spoonacular provides 'aisle' which can help categorize
        aisle = ingredient.get("aisle", "").lower()
        
        category_map = {
            "meat": "protein",
            "seafood": "protein",
            "poultry": "protein",
            "dairy": "dairy",
            "cheese": "dairy",
            "produce": "vegetable",
            "vegetables": "vegetable",
            "fruits": "fruit",
            "bakery": "grain",
            "bread": "grain",
            "pasta": "grain",
            "rice": "grain",
            "spices": "spice",
            "condiments": "condiment",
            "oils": "oil",
        }
        
        for key, category in category_map.items():
            if key in aisle:
                return category
        
        return "other"
    
    def get_or_create_cuisine(self, session, cuisine_name: str) -> Optional[str]:
        """Get or create Cuisine node."""
        if not cuisine_name:
            return None
        
        cuisine_lower = cuisine_name.lower().strip()
        
        # Check cache
        if cuisine_lower in self.cuisine_cache:
            return self.cuisine_cache[cuisine_lower]
        
        q = """
        MERGE (c:Cuisine {name: $name})
        ON CREATE SET c.created_at = datetime()
        RETURN c.name AS name
        """
        result = session.run(q, name=cuisine_lower).single()
        
        if result:
            self.cuisine_cache[cuisine_lower] = cuisine_lower
            return cuisine_lower
        
        return None
    
    def import_recipe(
        self,
        session,
        recipe_data: Dict,
        detailed_data: Optional[Dict] = None
    ) -> bool:
        """Import a single recipe into Neo4j."""
        try:
            # Generate recipe_id
            spoonacular_id = recipe_data.get("id")
            recipe_id = f"recipe_spoonacular_{spoonacular_id}"
            
            # Check if recipe already exists
            q_check = "MATCH (r:Recipe {recipe_id: $rid}) RETURN r.recipe_id AS id"
            if session.run(q_check, rid=recipe_id).single():
                print(f"  ⏭️  Recipe {recipe_id} already exists, skipping...")
                return False
            
            # Use detailed data if available, otherwise use basic data
            data = detailed_data if detailed_data else recipe_data
            
            # Extract basic info
            title = data.get("title", "")
            summary = data.get("summary", "")
            instructions = data.get("instructions", "")
            image = data.get("image")
            ready_in_minutes = data.get("readyInMinutes", 0)
            servings = data.get("servings", 4)
            
            # Extract cuisines
            cuisines = data.get("cuisines", [])
            if not cuisines:
                cuisines = data.get("cuisine", [])
            if isinstance(cuisines, str):
                cuisines = [cuisines]
            
            # Extract diets
            diets = data.get("diets", [])
            dish_types = data.get("dishTypes", [])
            
            # Extract nutrition
            nutrition = data.get("nutrition", {})
            nutrition_data = {}
            if nutrition:
                nutrients = nutrition.get("nutrients", [])
                for nut in nutrients:
                    name = nut.get("name", "").lower().replace(" ", "_").replace("-", "_")
                    amount = nut.get("amount", 0)
                    nutrition_data[f"nutrition_{name}"] = amount
                
                # Common nutrition fields
                nutrition_data["nutrition_calories"] = next(
                    (n.get("amount", 0) for n in nutrients if n.get("name") == "Calories"),
                    0
                )
                nutrition_data["nutrition_protein"] = next(
                    (n.get("amount", 0) for n in nutrients if n.get("name") == "Protein"),
                    0
                )
                nutrition_data["nutrition_carbs"] = next(
                    (n.get("amount", 0) for n in nutrients if n.get("name") == "Carbohydrates"),
                    0
                )
                nutrition_data["nutrition_fat"] = next(
                    (n.get("amount", 0) for n in nutrients if n.get("name") == "Fat"),
                    0
                )
            
            # Build CREATE query with dynamic nutrition properties
            q_recipe = """
            CREATE (r:Recipe {
                recipe_id: $recipe_id,
                title: $title,
                description: $summary,
                instructions: $instructions,
                image_urls: $image_urls,
                cook_time_min: $cook_time_min,
                total_time_min: $cook_time_min,
                servings: $servings,
                cuisine: $cuisines,
                tags: $tags,
                dish_types: $dish_types,
                diets: $diets,
                spoonacular_id: $spoonacular_id,
                source: 'spoonacular',
                created_at: datetime(),
                updated_at: datetime()
            })
            """
            
            # Add nutrition properties dynamically
            if nutrition_data:
                set_clauses = [f"r.{key} = ${key}" for key in nutrition_data.keys()]
                q_recipe += "\nSET " + ", ".join(set_clauses)
            
            q_recipe += "\nRETURN r.recipe_id AS recipe_id"
            
            params = {
                "recipe_id": recipe_id,
                "title": title,
                "summary": summary or "",
                "instructions": instructions or "",
                "image_urls": [image] if image else [],
                "cook_time_min": ready_in_minutes,
                "servings": servings,
                "cuisines": [c.lower() for c in cuisines] if cuisines else [],
                "tags": dish_types or [],
                "dish_types": dish_types or [],
                "diets": diets or [],
                "spoonacular_id": spoonacular_id,
                **nutrition_data
            }
            
            result = session.run(q_recipe, **params).single()
            
            if not result:
                return False
            
            # Create Cuisine relationships
            for cuisine_name in cuisines:
                cuisine_id = self.get_or_create_cuisine(session, cuisine_name)
                if cuisine_id:
                    q_cuisine = """
                    MATCH (r:Recipe {recipe_id: $rid})
                    MATCH (c:Cuisine {name: $cuisine})
                    MERGE (r)-[:OF_CUISINE]->(c)
                    """
                    session.run(q_cuisine, rid=recipe_id, cuisine=cuisine_id)
            
            # Create Ingredient relationships
            extended_ingredients = data.get("extendedIngredients", [])
            if not extended_ingredients:
                extended_ingredients = recipe_data.get("missedIngredients", []) + \
                                      recipe_data.get("usedIngredients", [])
            
            ingredient_count = 0
            for ing_data in extended_ingredients:
                ingredient_id = self.get_or_create_ingredient(session, ing_data)
                
                if ingredient_id:
                    # Extract quantity and unit
                    amount = ing_data.get("amount", 0)
                    unit = ing_data.get("unit", "")
                    original = ing_data.get("original", "")
                    
                    q_ing = """
                    MATCH (r:Recipe {recipe_id: $rid})
                    MATCH (i:Ingredient {ingredient_id: $ing_id})
                    MERGE (r)-[rel:HAS_INGREDIENT]->(i)
                    SET rel.qty = $qty,
                        rel.unit = $unit,
                        rel.original = $original
                    """
                    session.run(
                        q_ing,
                        rid=recipe_id,
                        ing_id=ingredient_id,
                        qty=amount,
                        unit=unit,
                        original=original
                    )
                    ingredient_count += 1
            
            print(f"  ✅ Imported recipe: {title} ({ingredient_count} ingredients)")
            return True
            
        except Exception as e:
            print(f"  ❌ Error importing recipe: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    async def import_recipes(
        self,
        query: Optional[str] = None,
        cuisine: Optional[str] = None,
        diet: Optional[str] = None,
        intolerances: Optional[List[str]] = None,
        max_ready_time: Optional[int] = None,
        number: int = 10,
        include_nutrition: bool = True
    ):
        """Import multiple recipes from Spoonacular."""
        print(f"\n🚀 Starting import from Spoonacular...")
        print(f"   Query: {query or 'N/A'}")
        print(f"   Cuisine: {cuisine or 'N/A'}")
        print(f"   Number: {number}\n")
        
        imported_count = 0
        skipped_count = 0
        
        with self.driver.session(database=NEO4J_DB) as session:
            # Fetch recipes
            recipes = await self.fetch_recipes(
                query=query,
                cuisine=cuisine,
                diet=diet,
                intolerances=intolerances,
                max_ready_time=max_ready_time,
                number=number
            )
            
            print(f"📥 Fetched {len(recipes)} recipes from Spoonacular\n")
            
            # Import each recipe
            for idx, recipe in enumerate(recipes, 1):
                print(f"[{idx}/{len(recipes)}] Processing: {recipe.get('title', 'Unknown')}")
                
                # Fetch detailed data if needed
                detailed_data = None
                if include_nutrition:
                    recipe_id = recipe.get("id")
                    detailed_data = await self.fetch_recipe_details(recipe_id)
                    # Add small delay to respect rate limits
                    await asyncio.sleep(0.2)
                
                # Import recipe
                success = self.import_recipe(session, recipe, detailed_data)
                
                if success:
                    imported_count += 1
                else:
                    skipped_count += 1
        
        print(f"\n✅ Import completed!")
        print(f"   Imported: {imported_count}")
        print(f"   Skipped: {skipped_count}")
        print(f"   Total: {len(recipes)}")


async def main():
    parser = argparse.ArgumentParser(description="Import recipes from Spoonacular to Neo4j")
    parser.add_argument("--query", type=str, help="Search query")
    parser.add_argument("--cuisine", type=str, help="Cuisine filter (e.g., italian, asian)")
    parser.add_argument("--diet", type=str, help="Diet filter (e.g., vegetarian, vegan)")
    parser.add_argument("--intolerances", type=str, help="Comma-separated intolerances")
    parser.add_argument("--max-ready-time", type=int, help="Maximum ready time in minutes")
    parser.add_argument("--number", type=int, default=10, help="Number of recipes to import")
    parser.add_argument("--include-nutrition", action="store_true", help="Include nutrition data")
    
    args = parser.parse_args()
    
    intolerances_list = None
    if args.intolerances:
        intolerances_list = [i.strip() for i in args.intolerances.split(",")]
    
    importer = SpoonacularImporter()
    
    try:
        await importer.import_recipes(
            query=args.query,
            cuisine=args.cuisine,
            diet=args.diet,
            intolerances=intolerances_list,
            max_ready_time=args.max_ready_time,
            number=args.number,
            include_nutrition=args.include_nutrition
        )
    finally:
        importer.close()


if __name__ == "__main__":
    asyncio.run(main())

