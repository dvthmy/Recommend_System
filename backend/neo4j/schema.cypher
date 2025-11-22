// Neo4j schema for Food Recommendation System
// Run with: :source backend/neo4j/schema.cypher (from Neo4j Browser) or via neo4j-admin cypher-shell

//========================
// Constraints (IDs)
//========================
CREATE CONSTRAINT recipe_id_unique IF NOT EXISTS
FOR (r:Recipe)
REQUIRE r.recipe_id IS UNIQUE;

CREATE CONSTRAINT ingredient_id_unique IF NOT EXISTS
FOR (i:Ingredient)
REQUIRE i.ingredient_id IS UNIQUE;

CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User)
REQUIRE u.user_id IS UNIQUE;

// Optional helper labels
CREATE CONSTRAINT tag_name_unique IF NOT EXISTS
FOR (t:Tag)
REQUIRE t.name IS UNIQUE;

CREATE CONSTRAINT cuisine_name_unique IF NOT EXISTS
FOR (c:Cuisine)
REQUIRE c.name IS UNIQUE;

//========================
// Indexes for lookup / filtering
//========================
CREATE INDEX recipe_title_index IF NOT EXISTS FOR (r:Recipe) ON (r.title);
CREATE INDEX recipe_cooktime_index IF NOT EXISTS FOR (r:Recipe) ON (r.cook_time_min);
CREATE INDEX recipe_created_index IF NOT EXISTS FOR (r:Recipe) ON (r.created_at);
CREATE INDEX recipe_updated_index IF NOT EXISTS FOR (r:Recipe) ON (r.updated_at);
CREATE INDEX recipe_rating_index IF NOT EXISTS FOR (r:Recipe) ON (r.rating_value);
CREATE INDEX recipe_cuisine_index IF NOT EXISTS FOR (r:Recipe) ON (r.cuisine);

CREATE INDEX ingredient_canonical_index IF NOT EXISTS FOR (i:Ingredient) ON (i.canonical_name);
CREATE INDEX ingredient_category_index IF NOT EXISTS FOR (i:Ingredient) ON (i.category);

// User profile quick filters
CREATE INDEX user_skill_index IF NOT EXISTS FOR (u:User) ON (u.skill_level);
CREATE INDEX user_locale_index IF NOT EXISTS FOR (u:User) ON (u.locale);

//========================
// Full-text indexes (search by text)
//========================
CREATE FULLTEXT INDEX recipe_text_fts IF NOT EXISTS
FOR (r:Recipe)
ON EACH [r.title, r.instructions, r.tags];

CREATE FULLTEXT INDEX ingredient_name_fts IF NOT EXISTS
FOR (i:Ingredient)
ON EACH [i.canonical_name, i.alt_names];
// Note: synonyms_normalized removed - using alt_names and variations instead

//========================
// Suggested property structures
//========================
// :Recipe {
//   recipe_id: string,
//   title: string,
//   ingredient_names: list<string>,
//   instructions: string,
//   tags: list<string>,
//   cook_time_min: integer,
//   servings: integer,
//   created_at: datetime,
//   updated_at: datetime,
//   cuisine: string,
//   rating_value: float,
//   rating_count: integer,
//   image_urls: list<string>,
//   popularity: {views: integer, saves: integer, cooks: integer, likes: integer},
//   allergens: list<string>, // ingredient_id list (denormalized convenience)
//   nutrition_per_serving: map,
//   cost_estimate: float,
//   equipment_needed: list<string>,
//   video_url: string,
//   alternative_ingredients: list<string>,
//   // vectors as lists (store externally for ANN if using GDS or vector index)
//   tfidf_vector: list<float>,
//   embedding_vector: list<float>,
//   ingredient_vector: list<float>
// }

// :Ingredient {
//   ingredient_id: string,
//   canonical_name: string,
//   base: string,                    // Base ingredient name (e.g., "powder", "juice")
//   category: string,                // Category (e.g., "seasoning", "beverage", "meat", "vegetable")
//   alt_names: list<string>,         // Alternative names/variations
//   variations: string               // JSON string of variations map (from canonical_ingredients_migrated.json)
//                                    // Optional additional properties (may be added later):
//   // global_freq: integer,
//   // allergen_flag: boolean,
//   // conversions: map, // unit->grams
//   // synonyms_normalized: list<string>,
//   // seasonality: list<string>,
//   // perishability: string,
//   // nutrition_per_100g: map,
//   // image_url: string,
//   // common_substitutions: list<string>
// }

// :User {
//   user_id: string,
//   username: string,               // Login username (for authentication)
//   name: string,                   // Display name (optional)
//   password_hash: string,          // Hashed password
//   age: integer,
//   gender: string,
//   meal_preferences: list<string>,
//   allergies: list<string>, // ingredient_ids (denormalized)
//   disliked_ingredients: list<string>, // ingredient_ids (denormalized)
//   explicit_preferences: { fav_cuisines: list<string>, fav_tags: list<string>, disliked_cuisines: list<string> },
//   skill_level: string,
//   max_cook_time: integer,
//   time_constraints: { max_cook_time: integer },
//   user_tfidf_vector: list<float>,
//   user_embedding: list<float>,
//   household_size: integer,
//   health_goals: list<string>,
//   preferred_units: string,
//   locale: string,
//   created_at: datetime,
//   updated_at: datetime
// }

//========================
// Relationships
//========================
// (r:Recipe)-[:HAS_INGREDIENT {qty: float, unit: string, optional: boolean, prep: string}]->(i:Ingredient)
// (r:Recipe)-[:TAGGED_AS]->(t:Tag)
// (r:Recipe)-[:OF_CUISINE]->(c:Cuisine)
// (u:User)-[:HAS_IN_PANTRY {qty: float, unit: string, last_updated: datetime}]->(i:Ingredient)
// (u:User)-[:DISLIKES]->(i:Ingredient)
// (u:User)-[:ALLERGIC_TO]->(i:Ingredient)
// (u:User)-[:FAVORS_CUISINE]->(c:Cuisine)
// (u:User)-[:FAVORS_TAG]->(t:Tag)
// (u:User)-[:INTERACTED_WITH {event_type: string, timestamp: datetime, rating: float}]->(r:Recipe)

//========================
// Example creation templates
//========================
// Ingredient node (matching canonical_ingredients_migrated.json format)
// MERGE (i:Ingredient {ingredient_id: $ingredient_id})
// SET i.canonical_name = $canonical_name,
//     i.base = $base,
//     i.category = $category,
//     i.alt_names = $alt_names,
//     i.variations = $variations  // JSON string of variations map
// 
// Example from canonical_ingredients_migrated.json:
// {
//   "ingredient_id": "ing_onion",
//   "canonical_name": "onion",
//   "base": "onion",
//   "category": "vegetable",
//   "alt_names": ["yellow onion", "white onion"],
//   "variations": {}
// }

// Recipe node and link to cuisine and tags
// MERGE (r:Recipe {recipe_id: $recipe_id})
// SET r += $recipe_props
// WITH r
// UNWIND $tags AS tagName
//   MERGE (t:Tag {name: tagName})
//   MERGE (r)-[:TAGGED_AS]->(t)
// WITH r
// MERGE (c:Cuisine {name: $cuisine})
// MERGE (r)-[:OF_CUISINE]->(c);

// Recipe -> Ingredient edges
// UNWIND $ingredients AS ing
// MATCH (i:Ingredient {ingredient_id: ing.ingredient_id})
// MERGE (r)-[rel:HAS_INGREDIENT]->(i)
// SET rel.qty = ing.qty,
//     rel.unit = ing.unit,
//     rel.optional = coalesce(ing.optional_flag,false),
//     rel.prep = ing.prep;

// User node and pantry
// MERGE (u:User {user_id: $user_id})
// SET u += $user_props;
// UNWIND $pantry AS p
// MATCH (i:Ingredient {ingredient_id: p.ingredient_id})
// MERGE (u)-[hp:HAS_IN_PANTRY]->(i)
// SET hp.qty = p.qty,
//     hp.unit = p.unit,
//     hp.last_updated = p.last_updated;

//========================
// Notes on Vector Similarity
//========================
// Neo4j 5.x supports vector indexes; alternatively use GDS for ANN over embeddings.
// Store vectors on nodes and build GDS graphs for KNN when needed.


