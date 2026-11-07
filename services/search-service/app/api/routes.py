import hmac

from fastapi import APIRouter, Depends, Header, HTTPException

from app.core.config import settings
from app.repositories.listing_repository import ListingRepositoryError
from app.schemas.search import SearchQueryRequest, SearchResponse
from app.services.index_manager import get_index_manager
from app.services.search_orchestrator import run_search

router = APIRouter()


def require_admin(x_admin_token: str = Header(default="")):
    expected = settings.SEARCH_ADMIN_TOKEN
    if not expected or not hmac.compare_digest(x_admin_token.encode(), expected.encode()):
        raise HTTPException(status_code=403, detail="Forbidden")


@router.post("/query", response_model=SearchResponse)
def search_listings(payload: SearchQueryRequest):
    mode, results, index_version = run_search(get_index_manager(), payload)
    return SearchResponse(
        total=len(results),
        mode=mode,
        index_version=index_version,
        results=results,
    )


@router.get("/index/stats")
def index_stats():
    return get_index_manager().stats()


@router.post("/index/refresh", dependencies=[Depends(require_admin)])
def refresh_index(force: bool = False):
    try:
        result = get_index_manager().refresh(force=force)
    except ListingRepositoryError as exc:
        raise HTTPException(status_code=503, detail=f"Listings unavailable: {exc}")
    return result.as_dict()


@router.get("/health")
def router_health():
    return {"status": "healthy", "service": "search-service"}
