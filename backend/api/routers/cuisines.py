from fastapi import APIRouter, HTTPException
from ..db import get_session

router = APIRouter(prefix="/cuisines", tags=["Cuisines"])


@router.get("/")
async def list_cuisines():
    """
    Get all unique cuisines from recipes in the database.
    Returns a list of cuisine names.
    """
    try:
        q = """
        MATCH (r:Recipe)
        WHERE r.cuisine IS NOT NULL
        UNWIND r.cuisine AS cuisine_name
        WITH DISTINCT cuisine_name
        WHERE cuisine_name IS NOT NULL AND cuisine_name <> ''
        RETURN cuisine_name
        ORDER BY cuisine_name
        """
        with get_session() as s:
            results = s.run(q)
            cuisines = [row["cuisine_name"] for row in results if row.get("cuisine_name")]
            return {"cuisines": cuisines}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch cuisines: {str(e)}")

