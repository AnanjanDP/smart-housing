import unittest
from app.models.roommate_matcher import RoommateMatcherModel

class MockReq:
    budget_a = 1500
    budget_b = 1550
    cleanliness_a = 4
    cleanliness_b = 4
    schedule_a = "EARLY_BIRD"
    schedule_b = "EARLY_BIRD"

class TestRoommateMatching(unittest.TestCase):
    def test_roommate_compatibility(self):
        matcher = RoommateMatcherModel()
        score = matcher.compute_compatibility(MockReq())
        self.assertGreaterEqual(score, 80.0)

if __name__ == '__main__':
    unittest.main()
