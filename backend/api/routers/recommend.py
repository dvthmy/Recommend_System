from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Optional, List
from ..services.recommender import recommend as rec_impl


router = APIRouter(prefix="/recommend", tags=["Recommend"])


class RecommendRequest(BaseModel):
    user_id: Optional[str] = None
    ingredient_ids: Optional[List[str]] = None
    max_cook_time: Optional[int] = None
    limit: int = 10


@router.post("/", summary="Get recipe recommendations")
async def post_recommend(req: RecommendRequest):
    try:
        results = rec_impl(req.user_id, req.ingredient_ids, req.limit, req.max_cook_time)
        return {"results": results, "total": len(results)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/", summary="GET variant for quick testing")
async def get_recommend(
    user_id: Optional[str] = Query(None),
    ingredient_ids: Optional[str] = Query(None, description="Comma-separated"),
    max_cook_time: Optional[int] = Query(None),
    limit: int = Query(10, ge=1, le=100),
):
    ing_list = [x.strip() for x in ingredient_ids.split(",")] if ingredient_ids else None
    results = rec_impl(user_id, ing_list, limit, max_cook_time)
    return {"results": results, "total": len(results)}