# Recommendation & Compatibility Scoring Engine

## Roommate Compatibility Score (0 - 100%)

The Roommate Compatibility algorithm computes normalized distances across 5 key dimensions:

1. **Budget Overlap Weight (30%)**:
   Calculates ratio of budget intersection range over budget union.
2. **Cleanliness Delta (25%)**:
   Scale 1 to 5. `Score = 1 - (|Level_A - Level_B| / 4)`.
3. **Sleep Schedule Alignment (20%)**:
   Exact match = 1.0, Flexible = 0.8, Opposite (Early Bird vs Night Owl) = 0.3.
4. **Pet & Smoke Policy (15%)**:
   Strict binary match / tolerance compliance.
5. **Location Preference Match (10%)**:
   Trigram distance or direct city string equality.

```
Total Compatibility Score = (0.30 * BudgetScore) + (0.25 * CleanlinessScore) 
                          + (0.20 * ScheduleScore) + (0.15 * PolicyScore) 
                          + (0.10 * LocationScore)
```

## Listing Recommendation Feed
- **Collaborative Filtering**: Users who viewed listing X also saved listing Y.
- **Content-Based Filtering**: Recommends listings matching amenity profiles and price points of previously saved listings.
