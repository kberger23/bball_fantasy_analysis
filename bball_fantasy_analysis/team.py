import numpy as np
from functools import lru_cache

class Team:

    def __init__(self, query, name, id):

        self._query = query

        self.name = name
        self.id = id

    @lru_cache(maxsize=128)
    def get_weekly_points(self, from_week=1, to_week=23):
        points = []
        for i in range(from_week, to_week+1):
            query = self._query.retrieve(self._query.query.get_team_stats_by_week, {"team_id": self.id, "chosen_week": i})
            points.append(query["team_points"].total)

        return np.array(points)
