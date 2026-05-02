from fastapi import FastAPI
from .routers import review, health

app = FastAPI()


app.include_router(review.router)
app.include_router(health.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}