// Simplified seed script for users (force 200 users)
:param numUsers => 200;

// Get ingredient IDs
MATCH (i:Ingredient)
WITH collect(i.ingredient_id) AS allIngredientIds

// Create users
UNWIND range(1, $numUsers) AS idx
WITH idx, allIngredientIds,
     rand() AS r1, rand() AS r2, rand() AS r3

// Create user with basic properties
MERGE (u:User {user_id: 'u_' + toString(idx)})
SET u.dietary_preferences = CASE WHEN r1 < 0.10 THEN ['vegetarian'] WHEN r1 < 0.15 THEN ['vegan'] ELSE [] END,
    u.allergies = [],
    u.disliked_ingredients = [],
    u.skill_level = CASE WHEN r2 < 0.50 THEN 'beginner' WHEN r2 < 0.85 THEN 'intermediate' ELSE 'advanced' END,
    u.max_cook_time = CASE WHEN r3 < 0.25 THEN 20 WHEN r3 < 0.55 THEN 30 WHEN r3 < 0.80 THEN 45 ELSE 60 END,
    u.user_tfidf_vector = null,
    u.user_embedding = null,
    u.household_size = toInteger(1 + floor(rand()*4)),
    u.health_goals = [],
    u.preferred_units = 'metric',
    u.locale = 'vi-VN'

// Add some pantry items (simplified)
WITH u, allIngredientIds, toInteger(5 + floor(rand() * 10)) AS pantrySize
WITH u, [i IN range(0, size(allIngredientIds)-1) | allIngredientIds[i]][..pantrySize] AS pantryIds
FOREACH (ingId IN pantryIds |
  MERGE (i:Ingredient {ingredient_id: ingId})
  MERGE (u)-[hp:HAS_IN_PANTRY]->(i)
  SET hp.qty = toFloat(1 + floor(rand()*10)),
      hp.unit = 'pcs',
      hp.last_updated = datetime()
)

RETURN count(u) as users_created;


