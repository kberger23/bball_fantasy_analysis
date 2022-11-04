import datetime

from nba_api.stats.static import teams
from nba_api.stats.endpoints import LeagueGameFinder
from nba_api.stats.endpoints import LeagueSeasonMatchups, CommonTeamYears, ScoreboardV2

import json
from functools import lru_cache
from datetime import date, timedelta, datetime


def print_dict(dict):
    print(json.dumps(dict, sort_keys=True, indent=4))

class Team:

    def __init__(self, team_info, league_info):

        self._team_info = team_info
        self._league_info = league_info

    @property
    def full_name(self):
        return self._team_info["full_name"]

    @property
    def name(self):
        return self._team_info["nickname"]

    @property
    def abbreviation(self):
        return self._team_info["abbreviation"]

    @property
    def id(self):
        return self._team_info["id"]

    def get_past_games(self):
        return LeagueGameFinder(team_id_nullable=self.id).get_data_frames()[0]

    def get_number_of_games(self, from_date, to_date):
        from_date_dt = datetime.strptime(from_date, '%Y-%m-%d').date()
        to_date_dt = datetime.strptime(to_date, '%Y-%m-%d').date()

        games = 0
        for n in range(int((to_date_dt - from_date_dt).days + 1)):
            current_date = from_date_dt + timedelta(n)
            matchups = self._league_info.get_matchups_for_day(current_date)

            print(current_date)
            for matchup in matchups:
                print(matchup["HOME"]["TEAM_ABBREVIATION"], matchup["AWAY"]["TEAM_ABBREVIATION"])
                if self.id in [matchup["HOME"]["TEAM_ID"], matchup["AWAY"]["TEAM_ID"]]:
                    games += 1

        return games


class GeneralInfo:

    def __init__(self):
        pass

    @staticmethod
    def list_to_dict(list, headers):
        return {k : v for k, v in zip(headers, list)}

    @lru_cache(maxsize=1280)
    def get_matchups_for_day(self, date):

        scoreboard = ScoreboardV2(game_date=date).get_dict()
        headers = scoreboard["resultSets"][1]["headers"]
        matchups_list = scoreboard["resultSets"][1]["rowSet"]

        matchups = []
        for i in range(len(matchups_list) // 2):
            matchup = {}
            ii = i * 2
            matchup["HOME"] = self.list_to_dict(matchups_list[ii], headers)
            matchup["AWAY"] = self.list_to_dict(matchups_list[ii + 1], headers)
            matchups.append(matchup)

        return matchups

class NBAstats:

    def __init__(self, season=None):

        self._league_info = GeneralInfo()
        # Instantiate teams
        nba_teams = teams.get_teams()
        self._teams = dict()
        for team in nba_teams:
            self._teams[team['abbreviation']] = Team(team, league_info=self._league_info)

    def team(self, key: str):

        if key in list(self._teams.keys()):
            return self._teams[key]
        else:
            for teamKey, team in self._teams.items():
                if team.name == key or team.full_name == key:
                    return team

        raise KeyError(f"Not found a team with key {key}.")

