# #!/usr/bin/env python3
# """
# 🍳 Food Recommendation System Demo - Compatible with your 'food' Neo4j DB

# ✅ Fully aligned with your current schema:
#    - Uses `popularity_score`, `rating_avg`, `dietary_preferences`, `name`
#    - Handles `cuisine` arrays via toString()
#    - Works with HAS_INGREDIENT & INTERACTED_WITH relationships
# """

# from neo4j import GraphDatabase
# import json


# class FoodRecommendationDemo:
#     def __init__(self, uri=None, username=None, password=None):
#         import os
#         uri = uri or os.getenv('NEO4J_URI', 'bolt://localhost:7687')
#         username = username or os.getenv('NEO4J_USERNAME', 'neo4j')
#         password = password or os.getenv('NEO4J_PASSWORD', "Admin123!")
#         self.driver = GraphDatabase.driver(uri, auth=(username, password))

#     def close(self):
#         self.driver.close()

#     # -----------------------------------------------------------------
#     # 🔹 Top Popular Recipes
#     # -----------------------------------------------------------------
#     def get_popular_recipes(self, limit=10):
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (r:Recipe)
#                 WHERE r.popularity_score > 0
#                 RETURN r.title, r.popularity_score, r.cuisine, r.cook_time_min
#                 ORDER BY r.popularity_score DESC
#                 LIMIT $limit
#             """, limit=limit)

#             print("🍽️  TOP POPULAR RECIPES")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['r.popularity_score']} - {record['r.title']}")
#                 print(f"   Cuisine: {record['r.cuisine']} | Time: {record['r.cook_time_min']} min")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Recipes by Ingredient
#     # -----------------------------------------------------------------
#     def get_recipes_by_ingredient(self, ingredient_name, limit=5):
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
#                 WHERE toLower(i.name) = toLower($ingredient)
#                 RETURN r.title, r.popularity_score, r.cuisine
#                 ORDER BY r.popularity_score DESC
#                 LIMIT $limit
#             """, ingredient=ingredient_name, limit=limit)

#             print(f"🥘 RECIPES WITH {ingredient_name.upper()}")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['r.popularity_score']} - {record['r.title']}")
#                 print(f"   Cuisine: {record['r.cuisine']}")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Collaborative Filtering
#     # -----------------------------------------------------------------
#     def collaborative_filtering(self, user_id, limit=5):
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (u1:User {user_id: $user_id})-[:INTERACTED_WITH]->(r1:Recipe)<-[:INTERACTED_WITH]-(u2:User)
#                 WHERE u1 <> u2
#                 WITH u1, u2, COUNT(r1) AS common_recipes
#                 ORDER BY common_recipes DESC
#                 LIMIT 3
#                 MATCH (u2)-[:INTERACTED_WITH]->(r2:Recipe)
#                 WHERE NOT EXISTS { (u1)-[:INTERACTED_WITH]->(r2) }
#                 RETURN DISTINCT r2.title AS title,
#                                 r2.cuisine AS cuisine,
#                                 r2.popularity_score AS popularity
#                 ORDER BY popularity DESC
#                 LIMIT $limit
#             """, user_id=user_id, limit=limit)

#             print(f"👥 COLLABORATIVE FILTERING FOR USER {user_id}")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['popularity']} - {record['title']}")
#                 print(f"   Cuisine: {record['cuisine']}")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Ingredient-based Recommendations
#     # -----------------------------------------------------------------
#     def ingredient_based_recommendations(self, recipe_id, limit=5):
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (r1:Recipe {recipe_id: $recipe_id})-[:HAS_INGREDIENT]->(i:Ingredient)<-[:HAS_INGREDIENT]-(r2:Recipe)
#                 WHERE r1 <> r2
#                 WITH r2, COUNT(i) AS common_ingredients
#                 ORDER BY common_ingredients DESC, r2.popularity_score DESC
#                 RETURN r2.title AS title,
#                        r2.cuisine AS cuisine,
#                        r2.popularity_score AS popularity,
#                        common_ingredients
#                 LIMIT $limit
#             """, recipe_id=recipe_id, limit=limit)

#             print(f"🔗 SIMILAR RECIPES TO {recipe_id}")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['popularity']} - {record['title']}")
#                 print(f"   Common ingredients: {record['common_ingredients']} | Cuisine: {record['cuisine']}")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Cuisine-based Recommendations
#     # -----------------------------------------------------------------
#     def cuisine_recommendations(self, cuisine, limit=5):
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (r:Recipe)
#                 WHERE toLower(toString(head(r.cuisine))) CONTAINS toLower($cuisine)
#                 RETURN r.title, r.popularity_score, r.cook_time_min
#                 ORDER BY r.popularity_score DESC
#                 LIMIT $limit
#             """, cuisine=cuisine, limit=limit)

#             print(f"🌍 TOP {cuisine.upper()} RECIPES")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['r.popularity_score']} - {record['r.title']}")
#                 print(f"   Time: {record['r.cook_time_min']} min")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Unified Recommendations (Combined)
#     # -----------------------------------------------------------------
#     def combined_recommendations(self, user_id, limit=10):
#         """Unified recommendations combining ingredient, cuisine, CF, and popular."""
#         with self.driver.session(database="food") as session:
#             result = session.run("""
#                 MATCH (u:User {user_id: $user_id})
#                 OPTIONAL MATCH (u)-[:INTERACTED_WITH]->(r1:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
#                 WITH u,
#                     COLLECT(DISTINCT i.name) AS used_ingredients,
#                     coalesce(u.dietary_preferences, []) AS diet_prefs,
#                     coalesce(u.skill_level, 'unknown') AS skill,
#                     coalesce(u.max_cook_time, 120) AS max_time

#                 // --- Recipes with overlapping ingredients ---
#                 CALL {
#                     WITH used_ingredients
#                     MATCH (r:Recipe)-[:HAS_INGREDIENT]->(i:Ingredient)
#                     WHERE size(used_ingredients) > 0 AND i.name IN used_ingredients
#                     RETURN DISTINCT r AS rec1
#                     LIMIT 20
#                 }

#                 // --- Recipes matching user’s favorite cuisines ---
#                 CALL {
#                     WITH u
#                     MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
#                     MATCH (r:Recipe)
#                     WHERE toLower(toString(head(r.cuisine))) CONTAINS toLower(c.name)
#                     RETURN DISTINCT r AS rec2
#                     LIMIT 20
#                 }

#                 // --- Collaborative Filtering (similar users) ---
#                 CALL {
#                     WITH u
#                     MATCH (u)-[:INTERACTED_WITH]->(r3:Recipe)<-[:INTERACTED_WITH]-(other:User)-[:INTERACTED_WITH]->(r4:Recipe)
#                     WHERE u <> other AND NOT EXISTS { (u)-[:INTERACTED_WITH]->(r4) }
#                     RETURN DISTINCT r4 AS rec3
#                     LIMIT 20
#                 }

#                 // --- Recipes aligned with dietary preferences ---
#                 CALL {
#                     WITH diet_prefs
#                     MATCH (r:Recipe)
#                     WHERE size(diet_prefs) > 0 AND ANY(d IN diet_prefs WHERE toLower(toString(head(r.cuisine))) CONTAINS toLower(d))
#                     RETURN DISTINCT r AS rec4
#                     LIMIT 20
#                 }

#                 // --- Popular fallback (for all users) ---
#                 CALL {
#                     MATCH (r5:Recipe)
#                     WHERE r5.popularity_score > 0
#                     RETURN DISTINCT r5 AS rec5
#                     ORDER BY r5.popularity_score DESC
#                     LIMIT 10
#                 }

#                 WITH COALESCE(COLLECT(DISTINCT rec1), []) +
#                     COALESCE(COLLECT(DISTINCT rec2), []) +
#                     COALESCE(COLLECT(DISTINCT rec3), []) +
#                     COALESCE(COLLECT(DISTINCT rec4), []) +
#                     COALESCE(COLLECT(DISTINCT rec5), []) AS allRecs

#                 UNWIND allRecs AS rec
#                 RETURN DISTINCT rec.title AS title,
#                                 rec.cuisine AS cuisine,
#                                 rec.cook_time_min AS cook_time,
#                                 rec.popularity_score AS popularity
#                 LIMIT $limit
#             """, user_id=user_id, limit=limit)

#             print(f"🍱 UNIFIED RECOMMENDATIONS FOR {user_id}")
#             print("=" * 60)
#             found = False
#             for record in result:
#                 found = True
#                 print(f"⭐ {record['popularity']} - {record['title']}")
#                 print(f"   Cuisine: {record['cuisine']} | Time: {record['cook_time']} min")
#                 print()
#             if not found:
#                 print("⚠️ No personalized matches found — showing global popular recipes instead.")

#     # -----------------------------------------------------------------
#     # 🔹 User Preferences
#     # -----------------------------------------------------------------
#     def get_user_preferences(self, user_id, limit =5):
#         with self.driver.session(database="food") as session:
#             user_info = session.run("""
#                 MATCH (u:User {user_id: $user_id})
#                 RETURN u.name AS name,
#                        u.skill_level AS skill_level,
#                        u.max_cook_time AS max_cook_time,
#                        u.dietary_preferences AS dietary_preferences
#                 LIMIT $limit
#             """, user_id=user_id, limit=limit).single()

#             if user_info:
#                 print(f"👤 USER PROFILE: {user_info['name']}")
#                 print("=" * 60)
#                 print(f"Skill level: {user_info['skill_level']}")
#                 print(f"Max cook time: {user_info['max_cook_time']}")
#                 print(f"Dietary preferences: {user_info['dietary_preferences']}")
#                 print()

#             result = session.run("""
#                 MATCH (u:User {user_id: $user_id})-[:INTERACTED_WITH]->(r:Recipe)
#                 RETURN r.title AS title,
#                        r.popularity_score AS popularity,
#                        r.cuisine AS cuisine
#                 ORDER BY popularity DESC
#                 LIMIT $limit
#             """, user_id=user_id, limit=limit)

#             print("❤️  INTERACTED RECIPES")
#             print("=" * 60)
#             for record in result:
#                 print(f"⭐ {record['popularity']} - {record['title']}")
#                 print(f"   Cuisine: {record['cuisine']}")
#                 print()

#     # -----------------------------------------------------------------
#     # 🔹 Run Full Demo
#     # -----------------------------------------------------------------
#     def run_demo(self):
#         print("🍳 FOOD RECOMMENDATION SYSTEM DEMO (HAS_INGREDIENT & INTERACTED_WITH)")
#         print("=" * 80)
#         print()

#         self.get_user_preferences("survey_1")
#         self.combined_recommendations("user_1", 10)
#         self.collaborative_filtering("survey_25", 5)
#         self.ingredient_based_recommendations("rec_100", 5)
#         self.get_recipes_by_ingredient("ing_garlic", 3)
#         self.cuisine_recommendations("Vietnamese", 3)
#         self.get_popular_recipes(5)

#         print("🎉 Demo completed! Explore Neo4j Browser at http://localhost:7474")


# # ---------------------------------------------------------------------
# # Entry Point
# # ---------------------------------------------------------------------
# def main():
#     demo = FoodRecommendationDemo()
#     try:
#         demo.run_demo()
#     finally:
#         demo.close()


# if __name__ == "__main__":
#     main()


#!/usr/bin/env python3
"""
🍲 RecipeRec-inspired Graph Neural Network for Neo4j
----------------------------------------------------
Fully fixed version:
 - Handles missing Ingredient nodes
 - Builds consistent edge shapes
 - Safe HGTConv call (only valid edge types)
 - Uploads recipe embeddings back to Neo4j

Author: Jovana Golubovic
"""

#!/usr/bin/env python3
"""
🍳 RecipeRec-inspired Graph Neural Network for Neo4j
----------------------------------------------------
✅ Handles empty Ingredient nodes
✅ Adds reverse edges (for bidirectional message passing)
✅ Fixes KeyError 'User'
✅ Uploads embeddings safely to Neo4j

Author: Jovana Golubovic
"""

import json
import torch
import torch.nn as nn
import torch.nn.functional as F
from tqdm import tqdm
from neo4j import GraphDatabase
from torch_geometric.data import HeteroData
from torch_geometric.nn import HGTConv
from sklearn.preprocessing import LabelEncoder


# ============================================================
# STEP 1: CONNECT TO NEO4J AND EXPORT GRAPH
# ============================================================
class Neo4jGraphExporter:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="Admin123!", db="food"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        self.db = db

    def export(self, output="graph_data.json"):
        query = """
        MATCH (r:Recipe)
        OPTIONAL MATCH (u:User)-[:INTERACTED_WITH]->(r)
        OPTIONAL MATCH (r)-[:HAS_INGREDIENT]->(i:Ingredient)
        WITH coalesce(u.user_id, "anonymous") AS user, r, collect(DISTINCT i.canonical_name) AS all_ingredients
        RETURN user AS user,
            r.recipe_id AS recipe,
            [x IN all_ingredients WHERE x IS NOT NULL] AS ingredients


        """
        with self.driver.session(database=self.db) as session:
            data = [dict(record) for record in session.run(query)]

        with open(output, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

        print(f"✅ Exported {len(data)} user–recipe–ingredient records to {output}")
        return data

    def close(self):
        self.driver.close()


# ============================================================
# STEP 2: BUILD HETEROGENEOUS GRAPH
# ============================================================
def build_hetero_graph(data):
    users, recipes, ingredients = [], [], []
    for d in data:
        if not d.get("user") or not d.get("recipe"):
            continue
        users.append(d["user"])
        recipes.append(d["recipe"])
        for ing in d.get("ingredients", []):
            if ing and ing.strip():
                ingredients.append(ing)

    user_enc = LabelEncoder().fit(users)
    recipe_enc = LabelEncoder().fit(recipes)
    ing_enc = LabelEncoder().fit(ingredients) if len(ingredients) > 0 else None

    data_obj = HeteroData()
    data_obj["User"].num_nodes = len(user_enc.classes_)
    data_obj["Recipe"].num_nodes = len(recipe_enc.classes_)
    data_obj["Ingredient"].num_nodes = len(ing_enc.classes_) if ing_enc else 0

    user_idx = {u: user_enc.transform([u])[0] for u in users}
    recipe_idx = {r: recipe_enc.transform([r])[0] for r in recipes}
    ing_idx = {i: ing_enc.transform([i])[0] for i in ing_enc.classes_} if ing_enc else {}

    # --- User → Recipe edges ---
    user_recipe_edges = []
    for d in data:
        u = user_idx.get(d["user"])
        r = recipe_idx.get(d["recipe"])
        if u is not None and r is not None:
            user_recipe_edges.append([u, r])

    ur_edge = torch.tensor(user_recipe_edges, dtype=torch.long).t().contiguous()
    data_obj["User", "INTERACTED_WITH", "Recipe"].edge_index = ur_edge

    # --- Reverse edges: Recipe → User ---
    if ur_edge.numel() > 0:
        rev_ur = ur_edge.flip(0)
        data_obj["Recipe", "INTERACTED_BY", "User"].edge_index = rev_ur

    # --- Recipe → Ingredient edges ---
    if ing_enc and len(ing_idx) > 0:
        recipe_ing_edges = []
        for d in data:
            r = recipe_idx.get(d["recipe"])
            for ing in d.get("ingredients", []):
                if ing in ing_idx:
                    recipe_ing_edges.append([r, ing_idx[ing]])
        if len(recipe_ing_edges) > 0:
            ri_edge = torch.tensor(recipe_ing_edges, dtype=torch.long).t().contiguous()
            data_obj["Recipe", "HAS_INGREDIENT", "Ingredient"].edge_index = ri_edge
            # Reverse: Ingredient → Recipe
            data_obj["Ingredient", "IN_INGREDIENT_OF", "Recipe"].edge_index = ri_edge.flip(0)
        else:
            data_obj["Recipe", "HAS_INGREDIENT", "Ingredient"].edge_index = torch.empty((2, 0), dtype=torch.long)
    else:
        data_obj["Recipe", "HAS_INGREDIENT", "Ingredient"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # --- Recipe → Recipe self-loop (keeps it stable) ---
    rr_edge = torch.arange(data_obj["Recipe"].num_nodes, dtype=torch.long).unsqueeze(0).repeat(2, 1)
    data_obj["Recipe", "SIMILAR_TO", "Recipe"].edge_index = rr_edge

    # --- Random features ---
    for ntype in data_obj.node_types:
        n = data_obj[ntype].num_nodes
        data_obj[ntype].x = torch.randn(n, 64)

    print("✅ HeteroData built successfully:")
    print(data_obj)
    return data_obj, user_enc, recipe_enc


# ============================================================
# STEP 3: MODEL — Mini RecipeRec
# ============================================================
class MiniRecipeRec(nn.Module):
    def __init__(self, metadata, hidden_dim=64, heads=4):
        super().__init__()
        self.conv = HGTConv(hidden_dim, hidden_dim, metadata, heads=heads)
        self.lin = nn.Linear(hidden_dim, hidden_dim)

    def forward(self, x_dict, edge_index_dict):
        h = self.conv(x_dict, edge_index_dict)
        out = {k: F.relu(self.lin(v)) for k, v in h.items()}
        return out


# ============================================================
# STEP 4: TRAINING
# ============================================================
def train_model(model, data, epochs=10, lr=0.001):
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    u_r_edges = data["User", "INTERACTED_WITH", "Recipe"].edge_index
    print(f"Training on {u_r_edges.shape[1]} user–recipe interactions...")

    for epoch in range(epochs):
        model.train()
        optimizer.zero_grad()

        # filter valid relations
        valid_edges = {k: v for k, v in data.edge_index_dict.items() if v.size(1) > 0}
        h = model(data.x_dict, valid_edges)

        # ensure both exist
        if "User" not in h or "Recipe" not in h:
            print("⚠️ Skipping epoch: missing User or Recipe embeddings")
            continue

        user_emb = h["User"]
        recipe_emb = h["Recipe"]

        pos_u = u_r_edges[0]
        pos_r = u_r_edges[1]
        neg_r = torch.randint(0, recipe_emb.size(0), pos_r.size(), dtype=torch.long)

        pos_scores = (user_emb[pos_u] * recipe_emb[pos_r]).sum(dim=1)
        neg_scores = (user_emb[pos_u] * recipe_emb[neg_r]).sum(dim=1)
        loss = torch.mean(F.relu(1.0 - pos_scores + neg_scores))

        loss.backward()
        optimizer.step()
        print(f"Epoch {epoch+1}/{epochs} | Loss: {loss.item():.4f}")

    return model, h.get("Recipe", torch.zeros(1, 64)).detach()


# ============================================================
# STEP 5: UPLOAD EMBEDDINGS
# ============================================================
def upload_embeddings(recipe_enc, embeddings, uri="bolt://localhost:7687",
                      user="neo4j", password="Admin123!", db="food"):
    driver = GraphDatabase.driver(uri, auth=(user, password))
    with driver.session(database=db) as session:
        print("📤 Uploading embeddings to Neo4j...")
        for recipe, idx in zip(recipe_enc.classes_, range(len(recipe_enc.classes_))):
            emb = embeddings[idx].tolist()
            session.run("""
                MATCH (r:Recipe {recipe_id: $rid})
                SET r.embedding = $emb
            """, rid=recipe, emb=emb)
    driver.close()
    print(f"✅ Uploaded {len(recipe_enc.classes_)} recipe embeddings!")


# ============================================================
# STEP 6: MAIN
# ============================================================
def main():
    exporter = Neo4jGraphExporter()
    graph_data = exporter.export()
    exporter.close()

    hetero_graph, user_enc, recipe_enc = build_hetero_graph(graph_data)
    model = MiniRecipeRec(hetero_graph.metadata(), hidden_dim=64, heads=4)
    trained_model, recipe_embeddings = train_model(model, hetero_graph, epochs=10)
    upload_embeddings(recipe_enc, recipe_embeddings)

    print("\n🎉 Training complete! Try this query in Neo4j Browser:")
    print("""
    MATCH (r1:Recipe {recipe_id:'rec_100'}), (r2:Recipe)
    WHERE r1 <> r2
    WITH r2, gds.similarity.cosine(r1.embedding, r2.embedding) AS score
    RETURN r2.title, score
    ORDER BY score DESC LIMIT 10;
    """)


if __name__ == "__main__":
    main()
