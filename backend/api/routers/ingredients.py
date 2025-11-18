from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
from ..db import get_session
import traceback
import logging

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/ingredients", tags=["Ingredients"])

@router.get("/")
async def list_ingredients(limit: int = Query(100, ge=1, le=200)):
    """
    List all ingredients (paginated).
    Returns basic info matching Ingredient schema.
    """
    q = """
    MATCH (i:Ingredient)
    RETURN 
        i.ingredient_id AS ingredient_id,
        i.canonical_name AS canonical_name,
        coalesce(i.canonical_name, i.name) AS name,
        i.base AS base,
        i.category AS category,
        coalesce(i.alt_names, []) AS alt_names,
        i.variations AS variations,
        coalesce(i.allergen_flag, false) AS allergen
    ORDER BY canonical_name
    LIMIT $limit
    """
    with get_session() as s:
        return {"ingredients": [dict(r) for r in s.run(q, limit=limit)]}


@router.get("/search")
async def search_ingredients(
    query: Optional[str] = Query(None, description="Search query (name, alt_names, synonyms)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    allergen: Optional[bool] = Query(None, description="Filter by allergen flag (true = only allergens, false = only non-allergens)"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Search ingredients by name, alternative names, or synonyms.
    Uses improved matching: exact match > starts with > word boundary > contains > fulltext.
    """
    params = {"limit": limit, "offset": offset}
    where = []
    
    if query:
        query_lower = query.lower().strip()
        query_trimmed = query_lower.strip()
        params["q"] = query
        params["q_lower"] = query_lower
        params["q_trimmed"] = query_trimmed
        # For starts-with matching in fulltext
        params["q_starts"] = query_lower + "*"
        # For word boundary matching (space before and after)
        params["q_lower_space"] = " " + query_lower + " "
        
        # Build WHERE clause with multiple matching strategies
        where.append("""
            (
                // Exact match (highest priority)
                i.ingredient_id = $q OR
                toLower(i.canonical_name) = $q_lower OR
                $q IN i.alt_names OR
                // Starts with (high priority)
                toLower(i.canonical_name) STARTS WITH $q_lower OR
                any(alt IN i.alt_names WHERE toLower(alt) STARTS WITH $q_lower) OR
                // Contains match (lower priority)
                toLower(i.canonical_name) CONTAINS $q_lower OR
                any(alt IN i.alt_names WHERE toLower(alt) CONTAINS $q_lower)
            )
        """)
    
    if category:
        where.append("i.category = $category")
        params["category"] = category
    
    if allergen is not None:
        if allergen:
            where.append("coalesce(i.allergen_flag, false) = true")
        else:
            where.append("coalesce(i.allergen_flag, false) = false")
    
    where_clause = " AND ".join(where) if where else "1=1"
    
    try:
        with get_session() as s:
            if query:
                # Count query
                count_q = f"""
                MATCH (i:Ingredient)
                WHERE {where_clause}
                RETURN count(i) AS total
                """
                
                # Improved search query with better scoring - prioritize starts with
                # Simplified: match ingredients first, then calculate scores
                search_q = f"""
                MATCH (i:Ingredient)
                WHERE {where_clause}
                WITH i,
                    // Pre-calculate match types to ensure correct priority
                    CASE WHEN i.ingredient_id = $q THEN 1 ELSE 0 END AS is_exact_id,
                    CASE WHEN toLower(i.canonical_name) = $q_lower THEN 1 ELSE 0 END AS is_exact_name,
                    CASE WHEN $q IN i.alt_names THEN 1 ELSE 0 END AS is_exact_alt,
                    CASE WHEN toLower(i.canonical_name) STARTS WITH $q_lower THEN 1 ELSE 0 END AS starts_with_name,
                    CASE WHEN any(alt IN i.alt_names WHERE toLower(alt) STARTS WITH $q_lower) THEN 1 ELSE 0 END AS starts_with_alt,
                    CASE WHEN toLower(i.canonical_name) CONTAINS $q_lower THEN 1 ELSE 0 END AS contains_name,
                    CASE WHEN any(alt IN i.alt_names WHERE toLower(alt) CONTAINS $q_lower) THEN 1 ELSE 0 END AS contains_alt
                WITH i, is_exact_id, is_exact_name, is_exact_alt, starts_with_name, starts_with_alt,
                     contains_name, contains_alt,
                    // Calculate match score (higher = better match) - check in priority order
                    CASE 
                        // Priority 1: Exact match = highest score (100)
                        WHEN is_exact_id = 1 THEN 100
                        WHEN is_exact_name = 1 THEN 95
                        WHEN is_exact_alt = 1 THEN 90
                        
                        // Priority 2: Starts with (canonical_name) = very high score (85)
                        WHEN starts_with_name = 1 THEN 85
                        
                        // Priority 3: Starts with (alt_names) = high score (82)
                        WHEN starts_with_alt = 1 THEN 82
                        
                        // Priority 4: Contains match (canonical_name) = lower score (50-60)
                        WHEN contains_name = 1 THEN 
                            CASE
                                // Word boundary match (space before and after) - highest contains score
                                WHEN toLower(i.canonical_name) CONTAINS $q_lower_space THEN 60
                                // Ends with query
                                WHEN toLower(i.canonical_name) ENDS WITH $q_lower THEN 55
                                // Just contains (lowest)
                                ELSE 50
                            END
                        
                        // Priority 5: Contains match (alt_names) = lowest score (45)
                        WHEN contains_alt = 1 THEN 45
                        
                        ELSE 0
                    END AS match_score
                WHERE match_score > 0
                RETURN 
                    i.ingredient_id AS ingredient_id,
                    i.canonical_name AS canonical_name,
                    coalesce(i.canonical_name, i.name) AS name,
                    i.base AS base,
                    i.category AS category,
                    coalesce(i.alt_names, []) AS alt_names,
                    i.variations AS variations,
                    coalesce(i.allergen_flag, false) AS allergen,
                    match_score
                ORDER BY match_score DESC, canonical_name ASC
                SKIP $offset LIMIT $limit
                """
                
                total = s.run(count_q, **params).single()["total"]
                items = [dict(r) for r in s.run(search_q, **params)]
            else:
                # Simple list if no query
                list_q = f"""
                MATCH (i:Ingredient)
                WHERE {where_clause}
                RETURN 
                    i.ingredient_id AS ingredient_id,
                    i.canonical_name AS canonical_name,
                    coalesce(i.canonical_name, i.name) AS name,
                    i.base AS base,
                    i.category AS category,
                    coalesce(i.alt_names, []) AS alt_names,
                    i.variations AS variations,
                    coalesce(i.allergen_flag, false) AS allergen
                ORDER BY canonical_name ASC
                SKIP $offset LIMIT $limit
                """
                count_q_simple = f"MATCH (i:Ingredient) WHERE {where_clause} RETURN count(i) AS total"
                total = s.run(count_q_simple, **params).single()["total"]
                items = [dict(r) for r in s.run(list_q, **params)]
            
            return {
                "ingredients": items,
                "total": total,
                "limit": limit,
                "offset": offset,
                "has_more": offset + limit < total
            }
    except Exception as e:
        logger.error(f"Error in search_ingredients: {str(e)}")
        logger.error(traceback.format_exc())
        raise HTTPException(status_code=500, detail=f"Search error: {str(e)}")


@router.get("/{ingredient_id}")
async def get_ingredient(ingredient_id: str):
    """
    Get ingredient detail by ID.
    Returns all properties matching Ingredient schema in Neo4j.
    """
    q = """
    MATCH (i:Ingredient {ingredient_id:$id})
    RETURN 
        i.ingredient_id AS ingredient_id,
        i.canonical_name AS canonical_name,
        coalesce(i.canonical_name, i.name) AS name,
        i.base AS base,
        i.category AS category,
        coalesce(i.alt_names, []) AS alt_names,
        i.variations AS variations,
        coalesce(i.allergen_flag, false) AS allergen
    """
    with get_session() as s:
        rec = s.run(q, id=ingredient_id).single()
        if not rec:
            raise HTTPException(status_code=404, detail="Ingredient not found")
        return dict(rec)