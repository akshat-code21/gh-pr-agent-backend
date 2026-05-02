from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class Review(BaseModel):
    url:str

@router.post("/review",tags=["review"])
async def review_pr(review:Review):
    # trigger langgraph agent
    return