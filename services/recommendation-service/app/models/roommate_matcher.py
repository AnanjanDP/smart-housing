class RoommateMatcherModel:
    def compute_compatibility(self, req) -> float:
        budget_diff = abs(req.budget_a - req.budget_b)
        budget_score = max(0.0, 100.0 - (budget_diff / 50.0))
        clean_score = 100.0 - (abs(req.cleanliness_a - req.cleanliness_b) * 20.0)
        schedule_score = 100.0 if req.schedule_a == req.schedule_b else 70.0
        
        final_score = (0.4 * budget_score) + (0.35 * clean_score) + (0.25 * schedule_score)
        return round(final_score, 1)
