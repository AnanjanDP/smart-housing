import os
import threading
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_fastapi_instrumentator import Instrumentator

from app.api.routes import router as search_router
from app.api.ws_chat import ws_router
from app.services.index_manager import get_index_manager


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Build or load the vector index in the background so the service starts accepting requests
    # (and answers /health) immediately; /ready reports when the index is usable.
    manager = get_index_manager()
    threading.Thread(target=manager.start, name="index-warmup", daemon=True).start()
    yield
    manager.stop()


app = FastAPI(
    title="StayMatch Search & Chat Microservice",
    version="1.0.0",
    lifespan=lifespan,
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
    search_router,
    prefix="/api/v1/search",
    tags=["search"]
)

app.include_router(
    ws_router,
    prefix="/api/v1/search",
    tags=["chat_ws"]
)

@app.get("/health")
def health():
    return {"status": "healthy", "service": "search-service"}


@app.get("/ready")
def ready():
    manager = get_index_manager()
    if not manager.ready:
        return JSONResponse(status_code=503, content={"status": "warming_up", "service": "search-service"})
    stats = manager.stats()
    return {
        "status": "ready",
        "service": "search-service",
        "listings": stats["listings"],
        "index_version": stats["version"],
    }


# Prometheus metrics
Instrumentator().instrument(app).expose(app)
