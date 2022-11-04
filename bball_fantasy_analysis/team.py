import numpy as np
from functools import lru_cache

from yfpy import models
from .nba_stats import stats

class Positions:

    BENCH = "BN"
    INJURED = "IL"
    UTIL = "UTIL"
    CENTER = "C"
    FORWARD = "F"
    POWER_FORWARD = "PF"
    SMALL_FORWARD = "SF"

class WeeklyTeamPlayer:

    def __init__(self, query, nba_stats:stats.Team, player: dict, week):

        self._query = query
        self._nba_stats = nba_stats
        self._player = player["player"]

        self._week = week

    @property
    def name(self):
        return self._player.name.full

    @property
    def id(self):
        return self._player.player_id

    @property
    def key(self):
        return self._player.player_key

    @property
    def plays(self):
        if self._player.selected_position.position not in [Positions.INJURED, Positions.BENCH]:
            return False
        else:
            return True

    @property
    def team(self):
        return self._player.editorial_team_abbr

    @property
    def weekly_stats(self):
        stats = self._query.retrieve(self._query.query.get_player_stats_by_week, {"player_key": self.key, "chosen_week": self._week}, data_type_class=models.Player)
        return stats.player_points.total

    @property
    def games_per_week(self):
        return self._nba_stats.team(self.team).get_number_of_games(from_date="2022-11-01", to_date="2022-11-04")

class WeeklyRoster:

    def __init__(self, query, nba_stats, roster, week):

        self._query = query
        self._nba_stats = nba_stats
        self.week = week
        self._roster = roster
        self.players = []

        for player in self._roster.players:
            self.players.append(WeeklyTeamPlayer(query, self._nba_stats, player, week))

        for player in self.players:
            print(player.name, player.weekly_stats)


class Team:

    def __init__(self, query, nba_stats, name, id):

        self._query = query
        self._nba_stats = nba_stats

        self.name = name
        self.id = id
        self._rosters = dict()


    @lru_cache(maxsize=128)
    def get_weekly_points(self, from_week=1, to_week=23):
        weeks = range(from_week, to_week+1)
        points = np.zeros_like(weeks)
        for ii, weekCtr in enumerate(weeks):
            query = self._query.retrieve(self._query.query.get_team_stats_by_week, {"team_id": self.id, "chosen_week": weekCtr})
            points[ii] = query["team_points"].total

        return points

    def get_roster_for_week(self, week):
        if f"{week}" not in list(self._rosters.keys()):

            roster = self._query.retrieve(self._query.query.get_team_roster_by_week, {"team_id": self.id, "chosen_week": week}, data_type_class=models.Roster)
            self._rosters[f"{week}"] = WeeklyRoster(self._query, self._nba_stats, roster, week=week)

        return self._rosters[f"{week}"]

    def get_optimal_roster_for_week(self, week):

        pass
