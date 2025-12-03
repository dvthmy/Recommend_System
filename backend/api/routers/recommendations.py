#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Recommendation Sessions API
---------------------------
Handles creation and visualization of recommendation sessions with full graph explanations.
"""

from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from datetime import datetime
import uuid
import sys
import os

# Add scripts directory to path for importing recommender
# __file__ = backend/api/routers/recommendations.py
# Need to go up 3 levels to reach project root, then into scripts
backend_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))  # backend/
scripts_dir = os.path.join(backend_root, 'scripts')
if scripts_dir not in sys.path:
    sys.path.insert(0, scripts_dir)

from ..models.recommendation_models import (
    RecommendationSessionCreate,
    RecommendationSessionResponse,
    SessionGraphResponse
)
from ..db import get_session

router = APIRouter(prefix="/recommendations", tags=["Recommendations"])


@router.post("/sessions", response_model=RecommendationSessionResponse)
async def create_recommendation_session(request: RecommendationSessionCreate):
    """
    Create a new recommendation session with full graph context.
    
    This creates:
    1. RecommendationSession node
    2. Links to User, Group, Cuisines, Ingredients
    3. Gets recommendations from recommend_graph.py
    4. Links recommended recipes to session
    
    Returns session with all context for visualization.
    """
    user_id = request.user_id
    session_id = str(uuid.uuid4())
    
    with get_session() as session:
        # STEP 1: Create RecommendationSession node
        q_create_session = """
        MATCH (u:User {user_id: $uid})
        CREATE (s:RecommendationSession {
            session_id: $sid,
            created_at: datetime(),
            ingredient_ids: $ingredient_ids,
            ingredient_names: $ingredient_names,
            preferred_cuisines: $preferred_cuisines,
            max_cook_time: $max_cook_time
        })
        MERGE (u)-[:HAS_SESSION]->(s)
        RETURN s.session_id as session_id, s.created_at as created_at
        """
        
        result = session.run(
            q_create_session,
            uid=user_id,
            sid=session_id,
            ingredient_ids=request.ingredient_ids or [],
            ingredient_names=request.ingredient_names or [],
            preferred_cuisines=request.preferred_cuisines or [],
            max_cook_time=request.max_cook_time
        ).single()
        
        if not result:
            raise HTTPException(status_code=404, detail="User not found")
        
        # STEP 2: Link session to Group (traits)
        q_link_group = """
        MATCH (u:User {user_id: $uid})-[:HAS_SESSION]->(s:RecommendationSession {session_id: $sid})
        MATCH (u)-[:BELONGS_TO]->(g:Group)
        MERGE (s)-[:WITH_TRAIT]->(g)
        RETURN g.gender as gender, g.age_group as age_group
        """
        
        group_result = session.run(q_link_group, uid=user_id, sid=session_id).single()
        traits = None
        if group_result:
            traits = {
                "gender": group_result.get("gender"),
                "age_group": group_result.get("age_group")
            }
        
        # STEP 3: Link session to Cuisines
        q_link_cuisines = """
        MATCH (u:User {user_id: $uid})-[:HAS_SESSION]->(s:RecommendationSession {session_id: $sid})
        MATCH (u)-[:FAVORS_CUISINE]->(c:Cuisine)
        MERGE (s)-[:WITH_CUISINE]->(c)
        RETURN collect(c.name) as cuisines
        """
        
        cuisine_result = session.run(q_link_cuisines, uid=user_id, sid=session_id).single()
        cuisines = cuisine_result.get("cuisines", []) if cuisine_result else []
        
        # STEP 4: Link session to Ingredients (if provided)
        ingredient_list = []
        if request.ingredient_ids:
            q_link_ingredients = """
            MATCH (s:RecommendationSession {session_id: $sid})
            UNWIND $ingredient_ids as ing_id
            MATCH (i:Ingredient {ingredient_id: ing_id})
            MERGE (s)-[:WITH_INGREDIENT]->(i)
            RETURN collect(i.ingredient_id) as ingredients
            """
            
            ing_result = session.run(
                q_link_ingredients,
                sid=session_id,
                ingredient_ids=request.ingredient_ids
            ).single()
            
            ingredient_list = ing_result.get("ingredients", []) if ing_result else []
        
        # STEP 5: Get recommendations from recommend_graph.py
        try:
            # Import from scripts directory (added to sys.path at top of file)
            from recommend_graph import GraphHybridRecommender
            
            # Get Neo4j connection info from config
            from ..config import settings
            uri = getattr(settings, 'NEO4J_URI', 'bolt://localhost:7687')
            username = getattr(settings, 'NEO4J_USER', 'neo4j')
            password = getattr(settings, 'NEO4J_PASSWORD', 'Admin123!')
            database = getattr(settings, 'NEO4J_DATABASE', 'test')
            
            recommender = GraphHybridRecommender(uri, username, password, database)
            
            recommendations = recommender.recommend(
                user_id=user_id,
                ingredient_ids=request.ingredient_ids,
                ingredient_names=request.ingredient_names,
                limit=30,
                min_match_ratio=0.3,
                max_cook_time=request.max_cook_time,
                preferred_cuisines=request.preferred_cuisines
            )
            
            recommender.close()
            
            # STEP 6: Link recommended recipes to session
            if recommendations:
                recipe_ids = [rec['recipe_id'] for rec in recommendations[:10]]  # Top 10
                
                q_link_recipes = """
                MATCH (s:RecommendationSession {session_id: $sid})
                UNWIND $recipe_ids as rid
                MATCH (r:Recipe {recipe_id: rid})
                MERGE (s)-[:RECOMMENDED]->(r)
                """
                
                session.run(q_link_recipes, sid=session_id, recipe_ids=recipe_ids)
                
                print(f"✅ Created {len(recipe_ids)} RECOMMENDED relationships for session {session_id}", file=sys.stderr)
            
            # Build response
            recommended_recipes = [
                {
                    "recipe_id": rec['recipe_id'],
                    "title": rec['title'],
                    "match_percent": rec['match_percent'],
                    "reasoning": rec['reasoning']
                }
                for rec in recommendations[:10]
            ]
            
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}", file=sys.stderr)
            import traceback
            traceback.print_exc()
            recommended_recipes = []
        
        return RecommendationSessionResponse(
            session_id=session_id,
            user_id=user_id,
            created_at=result.get("created_at"),
            traits=traits,
            cuisines=cuisines,
            ingredients=ingredient_list,
            recommended_recipes=recommended_recipes
        )


@router.get("/sessions/{session_id}/graph", response_model=SessionGraphResponse)
async def get_session_graph(session_id: str):
    """
    Get full graph visualization data for a recommendation session.
    
    Returns all nodes and relationships for Neo4j visualization:
    - User node
    - Session node
    - Group node (traits)
    - Cuisine nodes
    - Ingredient nodes
    - Recipe nodes
    - All connecting relationships
    
    Use this for:
    - Neo4j Browser visualization
    - D3.js graph rendering
    - Explaining recommendations
    """
    
    with get_session() as session:
        # Query to get all nodes and relationships
        q_graph = """
        MATCH (s:RecommendationSession {session_id: $sid})
        MATCH (u:User)-[:HAS_SESSION]->(s)
        
        OPTIONAL MATCH (s)-[:WITH_TRAIT]->(g:Group)
        OPTIONAL MATCH (s)-[:WITH_CUISINE]->(c:Cuisine)
        OPTIONAL MATCH (s)-[:WITH_INGREDIENT]->(i:Ingredient)
        OPTIONAL MATCH (s)-[:RECOMMENDED]->(r:Recipe)
        
        RETURN 
            u, s, g,
            collect(DISTINCT c) as cuisines,
            collect(DISTINCT i) as ingredients,
            collect(DISTINCT r) as recipes
        """
        
        result = session.run(q_graph, sid=session_id).single()
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        # Build nodes list
        nodes = []
        relationships = []
        
        # User node
        user_node = dict(result.get("u"))
        nodes.append({
            "id": user_node.get("user_id"),
            "label": "User",
            "properties": user_node
        })
        
        # Session node
        session_node = dict(result.get("s"))
        nodes.append({
            "id": session_node.get("session_id"),
            "label": "RecommendationSession",
            "properties": session_node
        })
        
        # User -> Session relationship
        relationships.append({
            "from": user_node.get("user_id"),
            "to": session_node.get("session_id"),
            "type": "HAS_SESSION"
        })
        
        # Group node (if exists)
        if result.get("g"):
            group_node = dict(result.get("g"))
            group_id = f"Group_{group_node.get('gender')}_{group_node.get('age_group')}"
            nodes.append({
                "id": group_id,
                "label": "Group",
                "properties": group_node
            })
            
            # Session -> Group relationship
            relationships.append({
                "from": session_node.get("session_id"),
                "to": group_id,
                "type": "WITH_TRAIT"
            })
        
        # Cuisine nodes
        for cuisine in result.get("cuisines", []):
            if cuisine:
                cuisine_dict = dict(cuisine)
                nodes.append({
                    "id": cuisine_dict.get("name"),
                    "label": "Cuisine",
                    "properties": cuisine_dict
                })
                
                # Session -> Cuisine relationship
                relationships.append({
                    "from": session_node.get("session_id"),
                    "to": cuisine_dict.get("name"),
                    "type": "WITH_CUISINE"
                })
        
        # Ingredient nodes
        for ingredient in result.get("ingredients", []):
            if ingredient:
                ing_dict = dict(ingredient)
                nodes.append({
                    "id": ing_dict.get("ingredient_id"),
                    "label": "Ingredient",
                    "properties": ing_dict
                })
                
                # Session -> Ingredient relationship
                relationships.append({
                    "from": session_node.get("session_id"),
                    "to": ing_dict.get("ingredient_id"),
                    "type": "WITH_INGREDIENT"
                })
        
        # Recipe nodes
        for recipe in result.get("recipes", []):
            if recipe:
                recipe_dict = dict(recipe)
                nodes.append({
                    "id": recipe_dict.get("recipe_id"),
                    "label": "Recipe",
                    "properties": recipe_dict
                })
                
                # Session -> Recipe relationship
                relationships.append({
                    "from": session_node.get("session_id"),
                    "to": recipe_dict.get("recipe_id"),
                    "type": "RECOMMENDED"
                })
        
        # Build Cypher query for reference
        cypher_query = f"""
MATCH (u:User)-[:HAS_SESSION]->(s:RecommendationSession {{session_id: '{session_id}'}})
OPTIONAL MATCH (s)-[:WITH_TRAIT]->(g:Group)
OPTIONAL MATCH (s)-[:WITH_CUISINE]->(c:Cuisine)
OPTIONAL MATCH (s)-[:WITH_INGREDIENT]->(i:Ingredient)
OPTIONAL MATCH (s)-[:RECOMMENDED]->(r:Recipe)
RETURN u, s, g, c, i, r
        """
        
        return SessionGraphResponse(
            session_id=session_id,
            nodes=nodes,
            relationships=relationships,
            cypher_query=cypher_query.strip()
        )


@router.get("/sessions/{session_id}")
async def get_session_details(session_id: str):
    """Get basic session details without full graph"""
    
    with get_session() as session:
        q = """
        MATCH (u:User)-[:HAS_SESSION]->(s:RecommendationSession {session_id: $sid})
        OPTIONAL MATCH (s)-[:RECOMMENDED]->(r:Recipe)
        RETURN 
            s.session_id as session_id,
            s.created_at as created_at,
            u.user_id as user_id,
            collect(r.recipe_id) as recipe_ids
        """
        
        result = session.run(q, sid=session_id).single()
        
        if not result:
            raise HTTPException(status_code=404, detail="Session not found")
        
        return {
            "session_id": result.get("session_id"),
            "created_at": result.get("created_at"),
            "user_id": result.get("user_id"),
            "recipe_count": len(result.get("recipe_ids", []))
        }


@router.get("/users/{user_id}/sessions")
async def get_user_sessions(user_id: str, limit: int = 10):
    """Get all recommendation sessions for a user"""
    
    with get_session() as session:
        q = """
        MATCH (u:User {user_id: $uid})-[:HAS_SESSION]->(s:RecommendationSession)
        OPTIONAL MATCH (s)-[:RECOMMENDED]->(r:Recipe)
        WITH s, count(r) as recipe_count
        RETURN 
            s.session_id as session_id,
            s.created_at as created_at,
            recipe_count
        ORDER BY s.created_at DESC
        LIMIT $limit
        """
        
        result = session.run(q, uid=user_id, limit=limit)
        
        sessions = [
            {
                "session_id": row.get("session_id"),
                "created_at": row.get("created_at"),
                "recipe_count": row.get("recipe_count")
            }
            for row in result
        ]
        
        return {
            "user_id": user_id,
            "sessions": sessions,
            "total": len(sessions)
        }

