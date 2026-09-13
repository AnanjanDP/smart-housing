from pydantic import BaseModel

class RoommateCompatibilityRequest(BaseModel):
    user_id_a: str
    user_id_b: str
    budget_a: float
    budget_b: float
    cleanliness_a: int
    cleanliness_b: int
    schedule_a: str
    schedule_b: str

class RoommateCompatibilityResponse(BaseModel):
    compatibility_score: float
    summary: str
