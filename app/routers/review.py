from fastapi import APIRouter, Depends
from pydantic import BaseModel

from app.agent.graph import run_agent
from app.services.github import GithubService
from ..dependencies import get_github_token
import asyncio

router = APIRouter()


class Review(BaseModel):
    url: str


@router.post("/review", tags=["review"])
async def review_pr(review: Review, github_token: str = Depends(get_github_token)):
    result = await asyncio.to_thread(run_agent, review.url, github_token)
    review_body = result.get("review")
    if not review_body:
        return {"error": "failed to generate review"}
    github_client = GithubService(github_token)
    comment = github_client.comment_on_pr(review.url, review_body)
    return {
        "commentUrl": comment.html_url,
        "review": review_body,
    }
