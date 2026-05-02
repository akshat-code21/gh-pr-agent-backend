from fastapi import Header, HTTPException


async def get_github_token(x_github_token: str = Header(...)):
    if not x_github_token:
        raise HTTPException(status_code=401, detail="X-GitHub-Token header is required")
    return x_github_token