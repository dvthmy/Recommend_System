import json, os, base64
from datetime import datetime
from dateutil import parser as date_parser
from fastapi import APIRouter, HTTPException, UploadFile, File
from ..models.user_models import UserProfile, UserProfileUpdate, AllergyUpdateRequest, CuisinePreferenceRequest, CuisinePreferencesUpdate, DietRequest, DietsUpdate
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
           u.avatar_url AS avatar_url,
           u.dietary_plan AS dietary_plan,
           u.auto_dietary_plan AS auto_dietary_plan,
           u.bmi AS bmi,
           u.weight_kg AS weight_kg,
           u.height_cm AS height_cm,
           u.activity_level AS activity_level,
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
            restore_params = {
                "user_id": profile.get("user_id"),
                "max_cook_time": profile.get("max_cook_time"),
                "completed_onboarding": profile.get("completed_onboarding", False),
                "created_at": profile.get("created_at"),
                "updated_at": profile.get("updated_at")
            }
            
            # Add optional fields if they exist
            restore_fields = ["user_id", "max_cook_time", "completed_onboarding", "created_at", "updated_at"]
            if profile.get("username"):
                restore_fields.append("username")
                restore_params["username"] = profile.get("username")
            if profile.get("name"):
                restore_fields.append("name")
                restore_params["name"] = profile.get("name")
            if profile.get("age"):
                restore_fields.append("age")
                restore_params["age"] = profile.get("age")
            if profile.get("age_group"):
                restore_fields.append("age_group")
                restore_params["age_group"] = profile.get("age_group")
            if profile.get("gender"):
                restore_fields.append("gender")
                restore_params["gender"] = profile.get("gender")
            if profile.get("avatar_url"):
                restore_fields.append("avatar_url")
                restore_params["avatar_url"] = profile.get("avatar_url")
            
            fields_str = ", ".join([f"{field}:${field}" for field in restore_fields])
            s.run(f"""
                CREATE (u:User {{{fields_str}}})
            """, **restore_params)

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

            # 5️⃣ Restore FOLLOWS_DIET
            for diet_name in relations.get("FOLLOWS_DIET", []):
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (d:Diet {name:$diet_name})
                    MERGE (u)-[:FOLLOWS_DIET]->(d)
                """, uid=user_id, diet_name=diet_name)

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

    # Get fields that were explicitly set in the request (including None values)
    update_dict = update.dict(exclude_unset=True)

    if "username" in update_dict:
        fields.append("u.username = $username")
        params["username"] = update.username
    
    if "name" in update_dict:
        fields.append("u.name = $name")
        params["name"] = update.name
    
    if "age" in update_dict:
        fields.append("u.age = $age")
        params["age"] = update.age
        # Auto-calculate age_group when age is updated
        if update.age is not None:
            age_group = calculate_age_group(update.age)
            fields.append("u.age_group = $age_group")
            params["age_group"] = age_group
    
    if "gender" in update_dict:
        fields.append("u.gender = $gender")
        params["gender"] = update.gender

    if "max_cook_time" in update_dict:
        fields.append("u.max_cook_time = $max_cook_time")
        params["max_cook_time"] = update.max_cook_time
    
    if "meal_preferences" in update_dict:
        fields.append("u.meal_preferences = $meal_preferences")
        params["meal_preferences"] = update.meal_preferences
    
    if "completed_onboarding" in update_dict:
        fields.append("u.completed_onboarding = $completed_onboarding")
        params["completed_onboarding"] = update.completed_onboarding
    
    if "avatar_url" in update_dict:
        fields.append("u.avatar_url = $avatar_url")
        params["avatar_url"] = update.avatar_url
    
    # Dietary plan fields - handle explicit None values
    if "dietary_plan" in update_dict:
        fields.append("u.dietary_plan = $dietary_plan")
        params["dietary_plan"] = update.dietary_plan
    
    if "auto_dietary_plan" in update_dict:
        fields.append("u.auto_dietary_plan = $auto_dietary_plan")
        params["auto_dietary_plan"] = update.auto_dietary_plan
    
    if "weight_kg" in update_dict:
        fields.append("u.weight_kg = $weight_kg")
        params["weight_kg"] = update.weight_kg
    
    if "height_cm" in update_dict:
        fields.append("u.height_cm = $height_cm")
        params["height_cm"] = update.height_cm
        # Auto-calculate BMI if both weight and height are provided
        if update.weight_kg is not None:
            height_m = update.height_cm / 100.0
            calculated_bmi = update.weight_kg / (height_m ** 2)
            fields.append("u.bmi = $bmi")
            params["bmi"] = calculated_bmi
    
    if "activity_level" in update_dict:
        fields.append("u.activity_level = $activity_level")
        params["activity_level"] = update.activity_level
    
    # Check if we need to calculate BMI from existing height when only weight is updated
    if "weight_kg" in update_dict and "height_cm" not in update_dict and update.weight_kg is not None:
        # Will calculate BMI in the query using existing height_cm
        pass

    # Always update updated_at, even if no other fields are being updated
    if not fields:
        # If no fields to update, just update the timestamp
        set_clause = "u.updated_at = $updated_at"
    else:
        set_clause = ", ".join(fields + ["u.updated_at = $updated_at"])
    
    # Calculate BMI if weight_kg is updated but height_cm is not (use existing height)
    if "weight_kg" in update_dict and "height_cm" not in update_dict and update.weight_kg is not None:
        with get_session() as s_check:
            height_check = s_check.run("""
                MATCH (u:User {user_id: $user_id})
                RETURN u.height_cm AS height_cm
            """, user_id=user_id).single()
            if height_check and height_check.get("height_cm"):
                height_cm = height_check.get("height_cm")
                height_m = height_cm / 100.0
                calculated_bmi = update.weight_kg / (height_m ** 2)
                # Only add BMI if not already in fields
                if "u.bmi = $bmi" not in fields:
                    fields.append("u.bmi = $bmi")
                    params["bmi"] = calculated_bmi
                # Rebuild set_clause
                set_clause = ", ".join(fields + ["u.updated_at = $updated_at"])
    
    q = f"""
    MATCH (u:User {{user_id:$user_id}})
    SET {set_clause}
    RETURN u.user_id AS user_id, u.username AS username, u.name AS name, u.age AS age,
           u.age_group AS age_group, u.gender AS gender, u.max_cook_time AS max_cook_time,
           coalesce(u.meal_preferences, []) AS meal_preferences,
           u.completed_onboarding AS completed_onboarding,
           u.avatar_url AS avatar_url,
           u.dietary_plan AS dietary_plan,
           u.auto_dietary_plan AS auto_dietary_plan,
           u.bmi AS bmi,
           u.weight_kg AS weight_kg,
           u.height_cm AS height_cm,
           u.activity_level AS activity_level,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, **params).single()
        if not rec:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")
        
        # Update BELONGS_TO relationship if gender OR age_group is available
        # Use 'unknown' as placeholder for missing values
        # Delete old BELONGS_TO first, then create new one
        user_info = s.run("""
            MATCH (u:User {user_id: $user_id})
            RETURN u.gender AS gender, u.age_group AS age_group
        """, user_id=user_id).single()
        
        if user_info and (user_info.get("gender") or user_info.get("age_group")):
            gender_value = user_info.get("gender") if user_info.get("gender") else 'unknown'
            age_group_value = user_info.get("age_group") if user_info.get("age_group") else 'unknown'
            # Delete old BELONGS_TO relationships first
            s.run("""
                MATCH (u:User {user_id: $user_id})-[r:BELONGS_TO]->(g:Group)
                DELETE r
            """, user_id=user_id)
            # Create new BELONGS_TO relationship
            s.run("""
                MATCH (u:User {user_id: $user_id})
                MERGE (g:Group {gender: $gender, age_group: $age_group})
                MERGE (u)-[:BELONGS_TO]->(g)
            """, user_id=user_id, gender=gender_value, age_group=age_group_value)

        # 🧠 Backup user info
        data = read_backup()
        profile = dict(rec)

        # collect current relationships
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r) IN ['FAVORS_CUISINE', 'FOLLOWS_DIET'] THEN x.name
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
            "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "HAS_DIETARY_RESTRICTION": []}
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
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
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
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
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
            rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
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
    MATCH (u:User {user_id:$uid})-[:FAVORS_CUISINE]->(c:Cuisine)
    RETURN collect({
        cuisine_name: c.name
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
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add cuisine relationship
        s.run("""
            MATCH (u:User {user_id:$uid})
            MERGE (c:Cuisine {name:$cname})
            MERGE (u)-[:FAVORS_CUISINE]->(c)
        """, uid=user_id, cname=cuisine_name)
        
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
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
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
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Added favorite cuisine: {cuisine_name}", "user_id": user_id}


@router.put("/{user_id}/cuisine-preferences")
async def update_cuisine_preferences(user_id: str, request: CuisinePreferencesUpdate):
    """
    Batch update cuisine preferences (for onboarding or profile edit).
    
    - Removes ALL existing FAVORS_CUISINE relationships
    - Creates new ones based on the cuisines list
    - If cuisines list is empty (No Preferences), only removes old ones
    
    Args:
        user_id: User ID
        request: CuisinePreferencesUpdate with cuisines list
    
    Returns:
        Success message with count of cuisines updated
    """
    cuisines = request.cuisines
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Step 1: Remove all existing FAVORS_CUISINE relationships
        s.run("""
            MATCH (u:User {user_id:$uid})-[r:FAVORS_CUISINE]->(:Cuisine)
            DELETE r
        """, uid=user_id)
        
        # Step 2: Create new relationships (if cuisines list is not empty)
        created_count = 0
        if cuisines:
            for cuisine_name in cuisines:
                # Skip empty strings
                if not cuisine_name or not cuisine_name.strip():
                    continue
                    
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (c:Cuisine {name:$cname})
                    MERGE (u)-[r:FAVORS_CUISINE]->(c)
                    SET r.updated_at = datetime()
                """, uid=user_id, cname=cuisine_name.strip())
                created_count += 1
        
        # Step 3: Update backup
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
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
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
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        if created_count == 0:
            return {
                "message": "Removed all cuisine preferences (No Preferences selected)",
                "user_id": user_id,
                "cuisines_count": 0
            }
        else:
            return {
                "message": f"Updated cuisine preferences: {created_count} cuisines",
                "user_id": user_id,
                "cuisines": cuisines,
                "cuisines_count": created_count
            }


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
            rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
            for row in result:
                if row["rel_type"] in rels and row["target"]:
                    rels[row["rel_type"]].append(row["target"])
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Removed favorite cuisine: {cuisine_name}", "user_id": user_id}


# ======================
# 🖼️ Avatar Upload
# ======================
# ======================
# 🥗 Diet Types
# ======================
@router.get("/{user_id}/diets")
async def get_user_diets(user_id: str):
    """Get user's diet types (e.g., vegetarian, vegan, gluten-free, halal, etc.)"""
    q = """
    MATCH (u:User {user_id:$uid})-[:FOLLOWS_DIET]->(d:Diet)
    RETURN collect({
        diet_name: d.name,
        description: d.description
    }) AS diets
    """
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        rec = s.run(q, uid=user_id).single()
        diets_list = rec["diets"] or []
        return {
            "user_id": user_id, 
            "diets": diets_list,
            "total": len(diets_list)
        }


@router.post("/{user_id}/diets")
async def add_user_diet(user_id: str, request: DietRequest):
    """Add a diet type for a user"""
    diet_name = request.diet_name
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Add diet relationship
        s.run("""
            MATCH (u:User {user_id:$uid})
            MERGE (d:Diet {name:$dname})
            MERGE (u)-[:FOLLOWS_DIET]->(d)
        """, uid=user_id, dname=diet_name)
        
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
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
                }
        
        # Update relations in backup
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r) IN ['FAVORS_CUISINE', 'FOLLOWS_DIET'] THEN x.name
               END AS target
        """
        result = s.run(rel_query, uid=user_id)
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Added diet: {diet_name}", "user_id": user_id}


@router.put("/{user_id}/diets")
async def update_diets(user_id: str, request: DietsUpdate):
    """
    Batch update diets (for onboarding or profile edit).
    
    - Removes ALL existing FOLLOWS_DIET relationships
    - Creates new ones based on the diets list
    - If diets list is empty (No Diet Restrictions), only removes old ones
    
    Args:
        user_id: User ID
        request: DietsUpdate with diets list
    
    Returns:
        Success message with count of diets updated
    """
    diets = request.diets
    
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Step 1: Remove all existing FOLLOWS_DIET relationships
        s.run("""
            MATCH (u:User {user_id:$uid})-[r:FOLLOWS_DIET]->(:Diet)
            DELETE r
        """, uid=user_id)
        
        # Step 2: Create new relationships (if diets list is not empty)
        created_count = 0
        if diets:
            for diet_name in diets:
                # Skip empty strings
                if not diet_name or not diet_name.strip():
                    continue
                    
                s.run("""
                    MATCH (u:User {user_id:$uid})
                    MERGE (d:Diet {name:$dname})
                    MERGE (u)-[r:FOLLOWS_DIET]->(d)
                    SET r.updated_at = datetime()
                """, uid=user_id, dname=diet_name.strip())
                created_count += 1
        
        # Step 3: Update backup
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
                    "relations": {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
                }
        
        # Update relations in backup
        rel_query = """
        MATCH (u:User {user_id:$uid})-[r]->(x)
        RETURN type(r) AS rel_type, 
               CASE 
                 WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                 WHEN type(r) IN ['FAVORS_CUISINE', 'FOLLOWS_DIET'] THEN x.name
               END AS target
        """
        result = s.run(rel_query, uid=user_id)
        rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
        for row in result:
            if row["rel_type"] in rels and row["target"]:
                rels[row["rel_type"]].append(row["target"])
        
        if user_id in data:
            data[user_id]["relations"] = rels
            write_backup(data)
        
        if created_count == 0:
            return {
                "message": "Removed all diets (No Diet Restrictions selected)",
                "user_id": user_id,
                "diets_count": 0
            }
        else:
            return {
                "message": f"Updated diets: {created_count} diets",
                "user_id": user_id,
                "diets": diets,
                "diets_count": created_count
            }


@router.delete("/{user_id}/diets/{diet_name}")
async def remove_user_diet(user_id: str, diet_name: str):
    """Remove a diet type for a user"""
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Remove diet relationship
        s.run("""
            MATCH (u:User {user_id:$uid})-[r:FOLLOWS_DIET]->(d:Diet {name:$dname})
            DELETE r
        """, uid=user_id, dname=diet_name)
        
        # Update backup
        data = read_backup()
        if user_id in data:
            rel_query = """
            MATCH (u:User {user_id:$uid})-[r]->(x)
            RETURN type(r) AS rel_type, 
                   CASE 
                     WHEN type(r) IN ['ALLERGIC_TO','DISLIKES'] THEN x.ingredient_id
                     WHEN type(r) IN ['FAVORS_CUISINE', 'HAS_DIETARY_RESTRICTION'] THEN x.name
                   END AS target
            """
            result = s.run(rel_query, uid=user_id)
            rels = {"ALLERGIC_TO": [], "DISLIKES": [], "FAVORS_CUISINE": [], "FOLLOWS_DIET": []}
            for row in result:
                if row["rel_type"] in rels and row["target"]:
                    rels[row["rel_type"]].append(row["target"])
            data[user_id]["relations"] = rels
            write_backup(data)
        
        return {"message": f"Removed diet: {diet_name}", "user_id": user_id}


# ======================
# 🖼️ Avatar Upload
# ======================
@router.post("/{user_id}/avatar")
async def upload_avatar(user_id: str, file: UploadFile = File(...)):
    """Upload user avatar image - converts to base64 data URL"""
    # Validate file type
    if not file.content_type or not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    # Read file content
    file_content = await file.read()
    
    # Convert to base64 data URL
    base64_content = base64.b64encode(file_content).decode('utf-8')
    data_url = f"data:{file.content_type};base64,{base64_content}"
    
    # Update user profile with avatar_url
    with get_session() as s:
        # Check if user exists
        user_check = s.run("MATCH (u:User {user_id:$uid}) RETURN u", uid=user_id).single()
        if not user_check:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Update avatar_url
        now = datetime.now().isoformat()
        s.run("""
            MATCH (u:User {user_id:$user_id})
            SET u.avatar_url = $avatar_url, u.updated_at = $updated_at
        """, user_id=user_id, avatar_url=data_url, updated_at=now)
        
        # Update backup
        data = read_backup()
        if user_id in data:
            data[user_id]["profile"]["avatar_url"] = data_url
            data[user_id]["profile"]["updated_at"] = now
            write_backup(data)
    
    return {"message": "Avatar uploaded successfully", "user_id": user_id, "avatar_url": data_url}

