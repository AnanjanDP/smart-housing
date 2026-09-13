from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router as search_router

app = FastAPI(
    title="StayMatch Search Microservice",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    search_router,
    prefix="/api/v1/search",
    tags=["search"]
)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "search-service"}


# Prometheus metrics
Instrumentator().instrument(app).expose(app)