import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router as recommendation_router

app = FastAPI(
    title="StayMatch Recommendation Microservice",
    version="1.0.0"
)

raw_origins = os.getenv("CORS_ALLOWED_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:8000,http://localhost:5173")
allowed_origins = [o.strip() for o in raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if "*" not in allowed_origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(
    recommendation_router,
    prefix="/api/v1/recommendations",
    tags=["recommendations"]
)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "recommendation-service"}


# Prometheus metrics
Instrumentator().instrument(app).expose(app)