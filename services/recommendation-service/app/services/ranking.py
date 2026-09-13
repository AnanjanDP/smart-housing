class RankingService:
    @staticmethod
    def rank_items(items, key="recommendation_score"):
        return sorted(items, key=lambda x: x.get(key, 0), reverse=True)
