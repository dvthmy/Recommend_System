# Food Recommendation API

FastAPI server for the food recommendation service.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements_api.txt
   ```

2. **Set environment variables (optional):**
   ```bash
   export NEO4J_URI="bolt://localhost:7687"
   export NEO4J_USER="neo4j"
   export NEO4J_PASSWORD="Admin123!"
   export NEO4J_DATABASE="food"
   ```

3. **Run the server:**
   ```bash
   # Using batch file (Windows)
   ./run_api.bat
   
   # Or directly
   python api.py
   ```

## API Endpoints

### Health Check
- **GET** `/health` - Check service health and Neo4j connection

### Recommendations
- **POST** `/recommend` - Get recommendations with JSON body
- **GET** `/recommend` - Get recommendations with query parameters

### Data
- **GET** `/ingredients` - List available ingredients
- **GET** `/cuisines` - List available cuisines

### User Profile Management
- **GET** `/users/{user_id}/profile` - Get user profile information
- **PUT** `/users/{user_id}/profile` - Update user profile information

### User Allergies Management
- **GET** `/users/{user_id}/allergies` - Get user's allergies
- **POST** `/users/{user_id}/allergies` - Add allergies for user
- **DELETE** `/users/{user_id}/allergies` - Remove allergies for user

### User Dislikes Management
- **GET** `/users/{user_id}/dislikes` - Get user's dislikes
- **POST** `/users/{user_id}/dislikes` - Add dislikes for user
- **DELETE** `/users/{user_id}/dislikes` - Remove dislikes for user

### User Cuisine Preferences
- **GET** `/users/{user_id}/favorite-cuisines` - Get user's favorite cuisines
- **POST** `/users/{user_id}/favorite-cuisines` - Add favorite cuisine for user
- **DELETE** `/users/{user_id}/favorite-cuisines/{cuisine_name}` - Remove favorite cuisine for user

### Recipe Management
- **GET** `/recipes/{recipe_id}` - Get detailed recipe information
- **GET** `/recipes/search` - Search recipes with various filters
- **GET** `/recipes/by-cuisine/{cuisine}` - Get recipes by cuisine

### Ingredient Management
- **GET** `/ingredients/{ingredient_id}` - Get detailed ingredient information
- **GET** `/ingredients/search` - Search ingredients with various filters
- **GET** `/ingredients/by-category/{category}` - Get ingredients by category
- **GET** `/ingredients/{ingredient_id}/synonyms` - Get ingredient synonyms

### User Interaction Management
- **POST** `/users/{user_id}/interactions` - Record user interactions with recipes
- **GET** `/users/{user_id}/interactions` - Get user's interaction history
- **GET** `/users/{user_id}/interactions/stats` - Get user's interaction statistics
- **POST** `/users/{user_id}/recompute-profile` - Recompute user profile and update vector

## Example Usage

### POST Request
```bash
curl -X POST "http://localhost:8001/recommend" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u_1",
    "ingredient_ids": ["ing_onion", "ing_tomato"],
    "max_cook_time": 45,
    "limit": 10
  }'
```

### GET Request
```bash
curl "http://localhost:8001/recommend?user_id=u_1&ingredient_ids=ing_onion,ing_tomato&max_cook_time=45&limit=10"
```

### Response Format
```json
{
  "results": [
    {
      "recipe_id": "recipe_123",
      "title": "Pho Bo",
      "cuisine": "Vietnamese",
      "cook_time_min": 120,
      "score": 0.85,
      "scores": {
        "s_ing": 0.9,
        "s_text": 0.8,
        "s_pop": 0.7,
        "s_cf": 0.6
      }
    }
  ],
  "total": 1,
  "request_params": {...}
}
```

## User Profile API Examples

### Get User Profile
```bash
curl "http://localhost:8001/users/u_1/profile"
```

### Update User Profile
```bash
curl -X PUT "http://localhost:8001/users/u_1/profile" \
  -H "Content-Type: application/json" \
  -d '{
    "locale": "vi-VN",
    "skill_level": "intermediate",
    "max_cook_time": 60,
    "dietary_preferences": ["vegetarian", "gluten-free"]
  }'
```

### Manage User Allergies
```bash
# Get allergies
curl "http://localhost:8001/users/u_1/allergies"

# Add allergies
curl -X POST "http://localhost:8001/users/u_1/allergies" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_ids": ["ing_onion", "ing_tomato"]
  }'

# Remove allergies
curl -X DELETE "http://localhost:8001/users/u_1/allergies" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_ids": ["ing_onion"]
  }'
```

### Manage User Dislikes
```bash
# Get dislikes
curl "http://localhost:8001/users/u_1/dislikes"

# Add dislikes
curl -X POST "http://localhost:8001/users/u_1/dislikes" \
  -H "Content-Type: application/json" \
  -d '{
    "ingredient_ids": ["ing_garlic"],
    "reasons": {
      "ing_garlic": "Too strong taste"
    }
  }'
```

### Manage Favorite Cuisines
```bash
# Get favorite cuisines
curl "http://localhost:8001/users/u_1/favorite-cuisines"

# Add favorite cuisine
curl -X POST "http://localhost:8001/users/u_1/favorite-cuisines" \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_name": "Vietnamese",
    "preference_level": 5
  }'

# Remove favorite cuisine
curl -X DELETE "http://localhost:8001/users/u_1/favorite-cuisines/Vietnamese"
```

## Recipe API Examples

### Get Recipe Detail
```bash
curl "http://localhost:8001/recipes/rec_1"
```

### Search Recipes
```bash
# Basic search
curl "http://localhost:8001/recipes/search?limit=5"

# Search by query
curl "http://localhost:8001/recipes/search?query=breakfast&limit=3"

# Search by cuisine
curl "http://localhost:8001/recipes/search?cuisine=all&limit=3"

# Search by cooking time
curl "http://localhost:8001/recipes/search?max_cook_time=30&limit=3"

# Search by ingredients
curl "http://localhost:8001/recipes/search?ingredients=ing_onion,ing_tomato&limit=3"

# Complex search with multiple filters
curl "http://localhost:8001/recipes/search?query=chicken&max_cook_time=60&limit=2"
```

### Get Recipes by Cuisine
```bash
# Get recipes by cuisine
curl "http://localhost:8001/recipes/by-cuisine/all?limit=5"

# With pagination
curl "http://localhost:8001/recipes/by-cuisine/all?limit=3&offset=0"
```

## Ingredient API Examples

### Get Ingredient Detail
```bash
curl "http://localhost:8001/ingredients/ing_onion"
```

### Search Ingredients
```bash
# Basic search
curl "http://localhost:8001/ingredients/search?limit=5"

# Search by query
curl "http://localhost:8001/ingredients/search?query=onion&limit=3"

# Search by category
curl "http://localhost:8001/ingredients/search?category=vegetable&limit=3"

# Search by allergen status
curl "http://localhost:8001/ingredients/search?allergen=true&limit=3"

# Complex search with multiple filters
curl "http://localhost:8001/ingredients/search?query=tomato&category=vegetable&allergen=false&limit=2"
```

### Get Ingredients by Category
```bash
# Get ingredients by category
curl "http://localhost:8001/ingredients/by-category/vegetable?limit=5"

# With pagination
curl "http://localhost:8001/ingredients/by-category/fruit?limit=3&offset=0"
```

### Get Ingredient Synonyms
```bash
# Get synonyms for an ingredient
curl "http://localhost:8001/ingredients/ing_onion/synonyms"
```

## User Interaction API Examples

### Record User Interactions
```bash
# Record a view interaction
curl -X POST "http://localhost:8001/users/u_1/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "rec_1",
    "event_type": "view",
    "rating": 4,
    "notes": "Looks delicious!"
  }'

# Record a cook interaction
curl -X POST "http://localhost:8001/users/u_1/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "rec_1",
    "event_type": "cook",
    "rating": 5,
    "duration_minutes": 45,
    "success": true,
    "notes": "Turned out great!"
  }'

# Record a like interaction
curl -X POST "http://localhost:8001/users/u_1/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "rec_2",
    "event_type": "like",
    "rating": 4
  }'

# Record a save interaction
curl -X POST "http://localhost:8001/users/u_1/interactions" \
  -H "Content-Type: application/json" \
  -d '{
    "recipe_id": "rec_3",
    "event_type": "save",
    "notes": "Want to try this later"
  }'
```

### Get User Interactions
```bash
# Get all interactions
curl "http://localhost:8001/users/u_1/interactions?limit=10"

# Get interactions by event type
curl "http://localhost:8001/users/u_1/interactions?event_type=cook&limit=5"

# With pagination
curl "http://localhost:8001/users/u_1/interactions?limit=5&offset=10"
```

### Get Interaction Statistics
```bash
# Get user interaction stats
curl "http://localhost:8001/users/u_1/interactions/stats"
```

### Recompute User Profile
```bash
# Recompute user profile
curl -X POST "http://localhost:8001/users/u_1/recompute-profile" \
  -H "Content-Type: application/json" \
  -d '{
    "force_recompute": true,
    "interaction_types": ["cook", "like", "save"]
  }'
```

## Integration with Frontend

The API runs on port 8001 and can be called from the frontend:

```javascript
// Example frontend call
const response = await fetch('http://localhost:8001/recommend', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({
    user_id: 'u_1',
    ingredient_ids: ['ing_onion', 'ing_tomato'],
    max_cook_time: 45,
    limit: 10
  })
});

const recommendations = await response.json();
```

## API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8001/docs
- **ReDoc**: http://localhost:8001/redoc

## Request Parameters

### RecommendationRequest
- `user_id` (optional): User ID for personalization
- `ingredient_ids` (optional): List of ingredient IDs to search for
- `max_cook_time` (optional): Maximum cooking time in minutes
- `limit` (default: 10): Number of recommendations to return

### UserProfileUpdate
- `locale` (optional): User's locale (e.g., "vi-VN", "en-US")
- `skill_level` (optional): Cooking skill level ("beginner", "intermediate", "advanced")
- `max_cook_time` (optional): Maximum cooking time in minutes (1-480)
- `dietary_preferences` (optional): List of dietary preferences (e.g., ["vegetarian", "gluten-free"])

### AllergyUpdateRequest
- `ingredient_ids` (required): List of ingredient IDs to add/remove as allergies

### DislikeUpdateRequest
- `ingredient_ids` (required): List of ingredient IDs to add/remove as dislikes
- `reasons` (optional): Dictionary mapping ingredient_id to reason for dislike

### CuisinePreferenceRequest
- `cuisine_name` (required): Name of the cuisine
- `preference_level` (optional): Preference level from 1-5 (default: 1)

### Backend Default Parameters (Set automatically)
- `w_ing`: 1.0 (Weight for ingredient overlap score)
- `w_text`: 1.0 (Weight for text similarity score)
- `w_pop`: 1.0 (Weight for popularity score)
- `w_cf`: 1.0 (Weight for collaborative filtering score)
- `norm`: "rank" (Normalization method)
- `pop_half_life`: 60.0 (Popularity half-life in days)
- `diversify`: false (No diversification)
- `mmr_lambda`: 0.7 (MMR lambda parameter)

These parameters match the command line format:
```bash
--w-ing 1.0 --w-text 1.0 --w-pop 1.0 --w-cf 1.0 --norm rank --pop-half-life 60
```

## Troubleshooting

1. **Neo4j Connection Error**: Make sure Neo4j is running and accessible
2. **Database Not Found**: Ensure the database exists and is properly seeded
3. **Import Errors**: Check that all required data has been imported
4. **Port Already in Use**: Change the port in `api.py` if 8001 is occupied
