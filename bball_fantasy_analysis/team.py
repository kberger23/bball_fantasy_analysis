import numpy as np
from functools import lru_cache

from yfpy import models

class Positions:

    BENCH = "BN"
    INJURED = "IL"
    UTIL = "UTIL"
    CENTER = "C"
    FORWARD = "F"
    POWER_FORWARD = "PF"
    SMALL_FORWARD = "SF"

class Player:

    def __init__(self, query, player: dict):

        self._query = query
        self._player = player["player"]
        print(self._player)

    @property
    def name(self):
        return self._player.name.full

    @property
    def id(self):
        return self._player.player_id

    @property
    def plays(self):
        if self._player.selected_position.position not in [Positions.INJURED, Positions.BENCH]:
            return False
        else:
            return True


class Roster:

    def __init__(self, query, roster, week):

        self._query = query
        self.week = week
        self._roster = roster
        self._players = []

        for player in self._roster.players:
            self._players.append(Player(query, player))

        for player in self._players:
            print(player.plays)


class Team:

    def __init__(self, query, name, id):

        self._query = query

        self.name = name
        self.id = id
        self._rosters = dict()


    @lru_cache(maxsize=128)
    def get_weekly_points(self, from_week=1, to_week=23):
        weeks = range(from_week, to_week+1)
        points = np.zeros_like(weeks)
        for ii, weekCtr in enumerate(weeks):
            query = self._query.retrieve(self._query.query.get_team_stats_by_week, {"team_id": self.id, "chosen_week": weekCtr})
            points[ii](query["team_points"].total)

        return points

    def get_optimal_roster_for_week(self, week):
        if f"{week}" not in list(self._rosters.keys()):

            roster = self._query.retrieve(self._query.query.get_team_roster_by_week, {"team_id": self.id, "chosen_week": week}, data_type_class=models.Roster)
            self._rosters[f"{week}"] = Roster(self._query, roster, week=week)
