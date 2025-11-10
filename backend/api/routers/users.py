import json, os
from datetime import datetime
from fastapi import APIRouter, HTTPException
from ..models.user_models import UserProfile, UserProfileUpdate
from ..db import get_session

router = APIRouter(prefix="/users", tags=["Users"])

BACKUP_PATH = "backend/data/users/user_backup.json"

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

# ---------- Core routes ----------
@router.get("/{user_id}/profile", response_model=UserProfile)
async def get_user_profile(user_id: str):
    """Get user profile — auto-restore if lost"""
    q = """
    MATCH (u:User {user_id:$user_id})
    RETURN u.user_id AS user_id, u.locale AS locale, u.skill_level AS skill_level,
           u.max_cook_time AS max_cook_time, u.dietary_preferences AS dietary_preferences,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, user_id=user_id).single()
        if rec:
            return dict(rec)

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
                    locale:$locale,
                    skill_level:$skill_level,
                    max_cook_time:$max_cook_time,
                    dietary_preferences:$dietary_preferences,
                    created_at:$created_at,
                    updated_at:$updated_at
                })
            """, **profile)

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
            "locale": "vi-VN",
            "skill_level": "beginner",
            "max_cook_time": 60,
            "dietary_preferences": [],
            "created_at": now,
            "updated_at": now
        }
        s.run("""
            CREATE (u:User {
                user_id:$user_id, locale:$locale, skill_level:$skill_level,
                max_cook_time:$max_cook_time, dietary_preferences:$dietary_preferences,
                created_at:$created_at, updated_at:$updated_at
            })
        """, **default_user)
        return default_user


@router.put("/{user_id}/profile", response_model=UserProfile)
async def update_user_profile(user_id: str, update: UserProfileUpdate):
    """Update user profile + save backup"""
    now = datetime.now()
    fields, params = [], {"user_id": user_id, "updated_at": now}

    if update.locale is not None:
        fields.append("u.locale = $locale")
        params["locale"] = update.locale
    if update.skill_level is not None:
        fields.append("u.skill_level = $skill_level")
        params["skill_level"] = update.skill_level
    if update.max_cook_time is not None:
        fields.append("u.max_cook_time = $max_cook_time")
        params["max_cook_time"] = update.max_cook_time
    if update.dietary_preferences is not None:
        fields.append("u.dietary_preferences = $dp")
        params["dp"] = update.dietary_preferences

    set_clause = ", ".join(fields + ["u.updated_at = $updated_at"])
    q = f"""
    MATCH (u:User {{user_id:$user_id}})
    SET {set_clause}
    RETURN u.user_id AS user_id, u.locale AS locale, u.skill_level AS skill_level,
           u.max_cook_time AS max_cook_time, u.dietary_preferences AS dietary_preferences,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, **params).single()
        if not rec:
            raise HTTPException(status_code=404, detail=f"User {user_id} not found")

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
        locale:$loc,
        skill_level:$lvl,
        max_cook_time:$max_time,
        dietary_preferences:$dp,
        created_at:$now,
        updated_at:$now
    })
    RETURN u.user_id AS user_id, u.locale AS locale, u.skill_level AS skill_level,
           u.max_cook_time AS max_cook_time, u.dietary_preferences AS dietary_preferences,
           u.created_at AS created_at, u.updated_at AS updated_at
    """
    with get_session() as s:
        rec = s.run(q, uid=uid, loc="vi-VN", lvl="beginner", max_time=60, dp=[], now=now).single()

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
    RETURN collect({ingredient_id: i.ingredient_id, name: i.name}) AS allergic_ingredients
    """
    with get_session() as s:
        rec = s.run(q, uid=user_id).single()
        if not rec:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user_id, "allergic_ingredients": rec["allergic_ingredients"] or []}


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
    RETURN collect({cuisine_name: c.name}) AS favorite_cuisines
    """
    with get_session() as s:
        rec = s.run(q, uid=user_id).single()
        if not rec:
            raise HTTPException(status_code=404, detail="User not found")
        return {"user_id": user_id, "favorite_cuisines": rec["favorite_cuisines"] or []}

