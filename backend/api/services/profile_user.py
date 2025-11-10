from typing import Optional
from ..db import get_session




def get_user_profile(user_id: str) -> Optional[dict]:
    q = """
    MATCH (u:User {user_id: $uid})
    RETURN u AS user
    """
    with get_session() as s:
        rec = s.run(q, uid=user_id).single()
        return rec["user"] if rec else None