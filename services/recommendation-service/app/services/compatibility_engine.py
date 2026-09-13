from app.models.roommate_matcher import RoommateMatcherModel

class CompatibilityEngineService:
    def __init__(self):
        self.model = RoommateMatcherModel()

    def evaluate_pair(self, request_data):
        score = self.model.compute_compatibility(request_data)
        summary = "Excellent Match!" if score >= 80 else "Good Match" if score >= 60 else "Moderate Fit"
        return score, summary
