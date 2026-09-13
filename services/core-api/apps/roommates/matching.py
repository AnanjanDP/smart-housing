class RoommateMatcher:
    @staticmethod
    def calculate_compatibility(profile_a, profile_b) -> float:
        """
        Calculates a compatibility score between 0.0 and 100.0 based on 5 weighted metrics:
        1. Budget Overlap (30%)
        2. Cleanliness Alignment (25%)
        3. Sleep Schedule Match (20%)
        4. Pets & Smoking Tolerance (15%)
        5. Preferred Location (10%)
        """
        # 1. Budget Overlap
        max_min = max(float(profile_a.budget_min), float(profile_b.budget_min))
        min_max = min(float(profile_a.budget_max), float(profile_b.budget_max))
        budget_score = 1.0 if min_max >= max_min else 0.0

        # 2. Cleanliness Delta (Scale 1-5)
        clean_delta = abs(profile_a.cleanliness_level - profile_b.cleanliness_level)
        clean_score = 1.0 - (clean_delta / 4.0)

        # 3. Sleep Schedule
        if profile_a.sleep_schedule == profile_b.sleep_schedule:
            schedule_score = 1.0
        elif 'FLEXIBLE' in (profile_a.sleep_schedule, profile_b.sleep_schedule):
            schedule_score = 0.8
        else:
            schedule_score = 0.4

        # 4. Policy (Smoking & Pets)
        policy_score = 1.0 if (profile_a.smoking_allowed == profile_b.smoking_allowed and 
                              profile_a.pets_allowed == profile_b.pets_allowed) else 0.5

        # 5. Location Match
        loc_score = 1.0 if (profile_a.preferred_location and profile_b.preferred_location and 
                            profile_a.preferred_location.lower() in profile_b.preferred_location.lower()) else 0.5

        total_score = (
            (0.30 * budget_score) +
            (0.25 * clean_score) +
            (0.20 * schedule_score) +
            (0.15 * policy_score) +
            (0.10 * loc_score)
        ) * 100.0

        return round(total_score, 1)
