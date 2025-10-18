#!/usr/bin/env python3
"""
Example usage of the Food Recommendation API
"""

import requests
import json

def example_api_calls():
    base_url = "http://localhost:8001"
    
    print("🍽️ Food Recommendation API Examples")
    print("=" * 50)
    
    # Example 1: Basic recommendation with ingredients
    print("\n1. Basic recommendation with ingredients:")
    payload = {
        "ingredient_ids": ["ing_onion", "ing_tomato"],
        "limit": 5
    }
    
    try:
        response = requests.post(f"{base_url}/recommend", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['results'])} recommendations")
            for i, recipe in enumerate(data['results'][:3], 1):
                print(f"   {i}. {recipe['title']} ({recipe['cuisine']}) - Score: {recipe['score']:.3f}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Example 2: Recommendation with user and cooking time
    print("\n2. Recommendation with user ID and cooking time:")
    payload = {
        "user_id": "u_1",
        "ingredient_ids": ["ing_onion", "ing_tomato", "ing_garlic"],
        "max_cook_time": 45,
        "limit": 3
    }
    
    try:
        response = requests.post(f"{base_url}/recommend", json=payload)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['results'])} recommendations for user u_1")
            for i, recipe in enumerate(data['results'], 1):
                print(f"   {i}. {recipe['title']} - {recipe['cook_time_min']} min - Score: {recipe['score']:.3f}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Example 3: GET request (equivalent to command line)
    print("\n3. GET request (command line equivalent):")
    params = {
        "user_id": "u_1",
        "ingredient_ids": "ing_onion,ing_tomato",
        "max_cook_time": 45,
        "limit": 5
    }
    
    try:
        response = requests.get(f"{base_url}/recommend", params=params)
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Found {len(data['results'])} recommendations (GET method)")
            print(f"   📝 Request params used: {data['request_params']}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Example 4: Get available ingredients
    print("\n4. Available ingredients:")
    try:
        response = requests.get(f"{base_url}/ingredients")
        if response.status_code == 200:
            data = response.json()
            ingredients = data.get('ingredients', [])
            print(f"   ✅ Found {len(ingredients)} ingredients")
            print(f"   📝 Sample ingredients: {[ing['name'] for ing in ingredients[:5]]}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")
    
    # Example 5: Get available cuisines
    print("\n5. Available cuisines:")
    try:
        response = requests.get(f"{base_url}/cuisines")
        if response.status_code == 200:
            data = response.json()
            cuisines = data.get('cuisines', [])
            print(f"   ✅ Found {len(cuisines)} cuisines")
            print(f"   📝 Sample cuisines: {cuisines[:5]}")
        else:
            print(f"   ❌ Error: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"   ❌ Connection error: {e}")

if __name__ == "__main__":
    example_api_calls()






