from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.v1 import api_v1_router
from app.db.init_db import init_db

logger.add("app.log", rotation="10 MB")

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5174",
        "http://localhost:5175",
        "http://127.0.0.1:5175",
    ],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

init_db()


app.include_router(api_v1_router)


@app.get("/")
async def read_root() -> dict:
    return {"Hello": "World"}


@app.get("/health")
async def health_check() -> dict:
    """Health check endpoint for Docker healthcheck"""
    return {"status": "healthy"}
