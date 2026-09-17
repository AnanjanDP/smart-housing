from fastapi import APIRouter
from app.schemas.search import SearchQueryRequest, SearchResponse
from app.repositories.listing_repository import ListingRepository
from app.services.hybrid_search import HybridSearchEngine

router = APIRouter()
repo = ListingRepository()

@router.post("/query", response_model=SearchResponse)
def search_listings(payload: SearchQueryRequest):
    listings = repo.fetch_all_active_listings()
    
    # Filter by city or price if provided
    if payload.city:
        listings = [l for l in listings if payload.city.lower() in l['city'].lower()]
    if payload.min_price:
        listings = [l for l in listings if l['price'] >= payload.min_price]
    if payload.max_price:
        listings = [l for l in listings if l['price'] <= payload.max_price]

    results = HybridSearchEngine.hybrid_search(payload.query, listings)
    
    return SearchResponse(
        total=len(results),
        mode="hybrid_rrf",
        results=results[:payload.limit]
    )

@router.get("/health")
def router_health():
    return {"status": "healthy", "service": "search-service"}

