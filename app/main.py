from fastapi import FastAPI
from .routers import review, health
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

origins = [
    "http://localhost",
    "http://localhost:3000",
    "https://pr-agent.akshat21.me"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(review.router)
app.include_router(health.router)

@app.get("/")
def read_root():
    return {"Hello": "World"}