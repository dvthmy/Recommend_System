import json, os
from datetime import datetime
from dateutil import parser as date_parser
from fastapi import APIRouter, HTTPException
from ..models.user_models import UserProfile, UserProfileUpdate, AllergyUpdateRequest, CuisinePreferenceRequest
from ..db import get_session

router = APIRouter(prefix="/users", tags=["Users"])

BACKUP_PATH = "data/users/user_backup.json"

# ---------- Utility functions ----------
def read_backup():
    if not os.path.exists(BACKUP_PATH):
        return {}
    try:
        with open(BACKUP_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        return {}

def write_backup(data):
    os.makedirs(os.path.dirname(BACKUP_PATH), exist_ok=True)
    with open(BACKUP_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def calculate_age_group(age: int) -> str:
    """Calculate age_group from age number"""
    if age < 18:
        return "<18"
    elif 18 <= age <= 30:
        return "18-30"
    elif 31 <= age <= 34:
        return "30-34"
    elif 35 <= age <= 44:
        return "35-44"
    elif 45 <= age <= 54:
        return "45-54"
    else:  # age >= 55
        return "55+"

# ---------- Core routes ----------
@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile — auto-restore if lost"""
    q = """
    MATCH (u:User {user_id:$user_id})
    RETURN u.user_id AS user_id, u.username AS username, u.name AS name, u.age AS age,
           u.age_group AS age_group, u.gender AS gender, u.max_cook_time AS max_cook_time,
           coalesce(u.meal_preferences, []) AS meal_preferences,
           u.completed_onboarding AS completed_onboarding,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, user_id=user_id).single()
        if rec:
            # Convert to dict and handle None values
            profile = dict(rec)
            # Ensure all fields are present (set None for missing fields)
            profile.setdefault("username", None)
            profile.setdefault("age", None)
            profile.setdefault("age_group", None)
            profile.setdefault("gender", None)
            
            # Convert Neo4j DateTime objects to Python datetime objects
            def convert_datetime(value):
                if value is None:
                    return None
                # Check if it's a Neo4j DateTime object
                if hasattr(value, 'to_native'):
                    # Neo4j DateTime object - convert to Python datetime
                    return value.to_native()
                elif isinstance(value, str):
                    # String - try to parse
                    try:
                        return date_parser.parse(value)
                    except (ValueError, TypeError):
                        return value
                elif isinstance(value, datetime):
                    # Already a Python datetime
                    return value
                return value
            
            profile["created_at"] = convert_datetime(profile.get("created_at"))
            profile["updated_at"] = convert_datetime(profile.get("updated_at"))
            
            return profile

        # ❌ Not found → try to restore
        backup_all = read_backup()
        backup = backup_all.get(user_id)
        if backup:
            profile = backup["profile"]
            relations = backup.get("relations", {})
            print(f"🩹 Restoring user {user_id} with relations from backup...")

            # 1️⃣ Restore User node
            s.run("""
                CREATE (u:User {
                    user_id:$user_id,
                    max_cook_time:$max_cook_time,
                    completed_onboarding:$completed_onboarding,
                    created_at:$created_at,
                    updated_at:$updated_at
                })
            """, 
            user_id=profile.get("user_id"),
            max_cook_time=profile.get("max_cook_time"),
            completed_onboarding=profile.get("completed_onboarding", False),
            created_at=profile.get("created_at"),
            updated_at=profile.get("updated_at"))

            # 2️⃣ Restore ALLERGIC_TO
            for ing_id in relations.get("ALLERGIC_TO", []):
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (i:Ingredient {ingredient_id:$ing_id})
                    MERGE (u)-[:ALLERGIC_TO]->(i)
                """, uid=user_id, ing_id=ing_id)

            # 3️⃣ Restore DISLIKES
            for ing_id in relations.get("DISLIKES", []):
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (i:Ingredient {ingredient_id:$ing_id})
                    MERGE (u)-[:DISLIKES]->(i)
                """, uid=user_id, ing_id=ing_id)

            # 4️⃣ Restore FAVORS_CUISINE
            for cname in relations.get("FAVORS_CUISINE", []):
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (c:Cuisine {name:$cname})
                    MERGE (u)-[:FAVORS_CUISINE]->(c)
                """, uid=user_id, cname=cname)

            return profile

        # ⚙️ No backup at all → create new default user
        now = datetime.now().isoformat()
        default_user = {
            "user_id": user_id,
            "max_cook_time": 60,
            "created_at": now,
            "updated_at": now
        }
        s.run("""
            CREATE (u:User {
                user_id:$user_id,
                max_cook_time:$max_cook_time,
                created_at:$created_at, updated_at:$updated_at
            })
        """, **default_user)
        return default_user


@router.put("/{user_id}/profile", response_model=UserProfile)
async def update_user_profile(user_id: str, update: UserProfileUpdate):
    """Update user profile + save backup"""
    now = datetime.now().isoformat()
    fields, params = [], {"user_id": user_id, "updated_at": now}

    if update.username is not None:
        fields.append("u.username = $username")
        params["username"] = update.username
    
    if update.name is not None:
        fields.append("u.name = $name")
        params["name"] = update.name
    
    if update.age is not None:
        fields.append("u.age = $age")
        params["age"] = update.age
        # Auto-calculate age_group when age is updated
        age_group = calculate_age_group(update.age)
        fields.append("u.age_group = $age_group")
        params["age_group"] = age_group
    
    if update.gender is not None:
        fields.append("u.gender = $gender")
        params["gender"] = update.gender

    if update.max_cook_time is not None:
        fields.append("u.max_cook_time = $max_cook_time")
        params["max_cook_time"] = update.max_cook_time
    
    if update.meal_preferences is not None:
        fields.append("u.meal_preferences = $meal_preferences")
        params["meal_preferences"] = update.meal_preferences
    
    if update.completed_onboarding is not None:
        fields.append("u.completed_onboarding = $completed_onboarding")
        params["completed_onboarding"] = update.completed_onboarding

    # Always update updated_at, even if no other fields are being updated
    if not fields:
        # If no fields to update, just update the timestamp
        set_clause = "u.updated_at = $updated_at"
    else:
        set_clause = ", ".join(fields + ["u.updated_at = $updated_at"])
    
    q = f"""
    MATCH (u:User {{user_id:$user_id}})
    SET {set_clause}
    RETURN u.user_id AS user_id, u.username AS username, u.name AS name, u.age AS age,
           u.age_group AS age_group, u.gender AS gender, u.max_cook_time AS max_cook_time,
           coalesce(u.meal_preferences, []) AS meal_preferences,
           u.completed_onboarding AS completed_onboarding,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, **params).single()
        if not rec:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Update BELONGS_TO relationship if gender or age_group changed
        # Get current gender and age_group from updated user
        user_info = s.run("""
            MATCH (u:User {user_id: $user_id})
            RETURN u.gender AS gender, u.age_group AS age_group
        """, user_id=user_id).single()
        
        if user_info and user_info.get("gender") and user_info.get("age_group"):
            s.run("""
                MATCH (u:User {user_id: $user_id})
                MERGE (g:Group {gender: $gender, age_group: $age_group})
                MERGE (u)-[:BELONGS_TO]->(g)
            """, user_id=user_id, gender=user_info["gender"], age_group=user_info["age_group"])

        # 🧠 Backup user info
        data = read_backup()
        profile = dict(rec)

        # collect current relationships
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r)='FAVORS_CUISINE' THEN x.name
               END AS target
        """
        result = s.run(rel_query, uid=user_id)
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])

        data[user_id] = {"profile": profile, "relations": rels}
        write_backup(data)
        return profile
    
@router.post("/", response_model=UserProfile)
async def create_user():
    import uuid
    now = datetime.now().isoformat()
    uid = f"user_{uuid.uuid4().hex[:8]}"
    q = """
    CREATE (u:User {
        user_id:$uid,
        max_cook_time:$max_time,
        completed_onboarding:$completed_onboarding,
        created_at:$now,
        updated_at:$now
    })
    RETURN u.user_id AS user_id, u.max_cook_time AS max_cook_time,
           u.completed_onboarding AS completed_onboarding,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, uid=uid, max_time=60, completed_onboarding=False, now=now).single()

        # backup immediately
        data = read_backup()
        data[uid] = {
            "profile": dict(rec),
            "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
        }
        write_backup(data)

        return dict(rec)

# ======================
# 🧄 Allergies
# ======================
@router.get("/{user_id}/allergies")
async def get_user_allergies(user_id: str):
    q = """
    MATCH (u:User {user_id:$uid})-[:ALLERGIC_TO]->(i:Ingredient)
    RETURN collect({
        ingredient_id: i.ingredient_id, 
        ingredient_name: COALESCE(i.name, i.canonical_name, i.ingredient_id),
        name: COALESCE(i.name, i.canonical_name, i.ingredient_id)
    }) AS allergies
    """
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        rec = s.run(q, uid=user_id).single()
        allergies_list = rec["allergies"] or []
        return {
            "user_id": user_id, 
            "allergies": allergies_list,
            "total": len(allergies_list)
        }


@router.post("/{user_id}/allergies")
async def add_user_allergies(user_id: str, request: AllergyUpdateRequest):
    """Add allergies for a user"""
    ingredient_ids = request.ingredient_ids
    if not ingredient_ids:
        return {"message": "No ingredient IDs provided", "user_id": user_id}
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add each allergy relationship
        for ing_id in ingredient_ids:
            s.run("""
                MATCH (u:User {user_id:$uid})
                MERGE (i:Ingredient {ingredient_id:$ing_id})
                ON CREATE SET i.name = COALESCE(i.canonical_name, $ing_id)
                MERGE (u)-[r:ALLERGIC_TO]->(i)
            """, uid=user_id, ing_id=ing_id)
        
        # Update backup
        data = read_backup()
        if user_id not in data:
            # Get user profile
            profile_rec = s.run("""
                MATCH (u:User {user_id:$uid})
                RETURN u.user_id AS user_id, u.username AS username, u.age AS age,
                       u.gender AS gender, u.max_cook_time AS max_cook_time,
                       u.created_at AS created_at, u.updated_at AS updated_at
            """, uid=user_id).single()
            if profile_rec:
                data[user_id] = {
                    "profile": dict(profile_rec),
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
                }
        
        # Update relations in backup
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r)='FAVORS_CUISINE' THEN x.name
               END AS target
        """
        result = s.run(rel_query, uid=user_id)
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Added {len(ingredient_ids)} allergies", "user_id": user_id}


@router.delete("/{user_id}/allergies")
async def remove_user_allergies(user_id: str, request: AllergyUpdateRequest):
    """Remove allergies for a user"""
    ingredient_ids = request.ingredient_ids
    if not ingredient_ids:
        return {"message": "No ingredient IDs provided", "user_id": user_id}
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove each allergy relationship
        for ing_id in ingredient_ids:
            s.run("""
                MATCH (u:User {user_id:$uid})-[r:ALLERGIC_TO]->(i:Ingredient {ingredient_id:$ing_id})
                DELETE r
            """, uid=user_id, ing_id=ing_id)
        
        # Update backup
        data = read_backup()
        if user_id in data:
            rel_query = """
            MATCH (u:User {user_id:$uid})-[r]->(x)
            RETURN type(r) AS rel_type, 
                   CASE 
                     WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                     WHEN type(r)='FAVORS_CUISINE' THEN x.name
                   END AS target
            """
            result = s.run(rel_query, uid=user_id)
            rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
            for row in result:
                if row["rel_type"] in rels and row["target"]:
                    rels[row["rel_type"]].append(row["target"])
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Removed {len(ingredient_ids)} allergies", "user_id": user_id}


# ======================
# 😖 Dislikes
# ======================
@router.get("/{user_id}/dislikes")
async def get_user_dislikes(user_id: str):
    q = """
    MATCH (u:User {user_id:$uid})-[:DISLIKES]->(i:Ingredient)
    RETURN collect({ingredient_id: i.ingredient_id, name: i.name}) AS disliked_ingredients
    """
    with get_session() as s:
        rec = s.run(q, uid=user_id).single()
        if not rec:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user_id, "disliked_ingredients": rec["disliked_ingredients"] or []}


# ======================
# 🍣 Favorite cuisines
# ======================
@router.get("/{user_id}/favorite-cuisines")
async def get_user_favorite_cuisines(user_id: str):
    q = """
    MATCH (u:User {user_id:$uid})-[r:FAVORS_CUISINE]->(c:Cuisine)
    RETURN collect({
        cuisine_name: c.name,
        preference_level: COALESCE(r.preference_level, 5)
    }) AS favorite_cuisines
    """
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        rec = s.run(q, uid=user_id).single()
        cuisines_list = rec["favorite_cuisines"] or []
        return {
            "user_id": user_id, 
            "favorite_cuisines": cuisines_list,
            "total": len(cuisines_list)
        }


@router.post("/{user_id}/favorite-cuisines")
async def add_user_favorite_cuisine(user_id: str, request: CuisinePreferenceRequest):
    """Add a favorite cuisine for a user"""
    cuisine_name = request.cuisine_name
    preference_level = request.preference_level
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add cuisine relationship with preference level
        s.run("""
            MATCH (u:User {user_id:$uid})
            MERGE (c:Cuisine {name:$cname})
            MERGE (u)-[r:FAVORS_CUISINE]->(c)
            SET r.preference_level = $level
        """, uid=user_id, cname=cuisine_name, level=preference_level)
        
        # Update backup
        data = read_backup()
        if user_id not in data:
            # Get user profile
            profile_rec = s.run("""
                MATCH (u:User {user_id:$uid})
                RETURN u.user_id AS user_id, u.username AS username, u.age AS age,
                       u.gender AS gender, u.max_cook_time AS max_cook_time,
                       u.created_at AS created_at, u.updated_at AS updated_at
            """, uid=user_id).single()
            if profile_rec:
                data[user_id] = {
                    "profile": dict(profile_rec),
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
                }
        
        # Update relations in backup
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r)='FAVORS_CUISINE' THEN x.name
               END AS target
        """
        result = s.run(rel_query, uid=user_id)
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Added favorite cuisine: {cuisine_name}", "user_id": user_id}


@router.delete("/{user_id}/favorite-cuisines/{cuisine_name}")
async def remove_user_favorite_cuisine(user_id: str, cuisine_name: str):
    """Remove a favorite cuisine for a user"""
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove cuisine relationship
        s.run("""
            MATCH (u:User {user_id:$uid})-[r:FAVORS_CUISINE]->(c:Cuisine {name:$cname})
            DELETE r
        """, uid=user_id, cname=cuisine_name)
        
        # Update backup
        data = read_backup()
        if user_id in data:
            rel_query = """
            MATCH (u:User {user_id:$uid})-[r]->(x)
            RETURN type(r) AS rel_type, 
                   CASE 
                     WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                     WHEN type(r)='FAVORS_CUISINE' THEN x.name
                   END AS target
            """
            result = s.run(rel_query, uid=user_id)
            rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": []}
            for row in result:
                if row["rel_type"] in rels and row["target"]:
                    rels[row["rel_type"]].append(row["target"])
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Removed favorite cuisine: {cuisine_name}", "user_id": user_id}

