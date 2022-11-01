import os.path
from pathlib import Path
import json

import pandas as pd
import numpy as np

from typing import Callable, Dict, Union, Type, List

import requests
import time

from yfpy import Data
from yfpy.query import YahooFantasySportsQuery, YahooFantasyObject
from yfpy import models

from .team import Team

import logging
logging.getLogger("yfpy.query").setLevel(level=logging.DEBUG)
logging.getLogger("yfpy.data").setLevel(level=logging.DEBUG)

class Query:

    def __init__(self, game_code, league_id, game_id, save_data=True, force_update=False):
        self.auth_dir = Path(__file__).parent

        # set target directory for data output
        self.data_dir = Path(__file__).parent / "output"

        # create YFPY Data instance for saving/loading data
        self.data = Data(self.data_dir, save_data=save_data)

        self.force_update = force_update

        self.game_code = game_code
        self.league_id = league_id
        self.game_id = game_id


        self.query = YahooFantasySportsQuery(
            self.auth_dir,
            self.league_id,
            game_id=self.game_id,
            game_code=self.game_code,
            offline=False,
            all_output_as_json_str=False,
            consumer_key=self.app_consumer_key,
            consumer_secret=self.app_consumer_secret,
            browser_callback=True
        )

    @property
    def app_auth_file(self):
        with open("private.json", "r") as f:
            return json.load(f)

    @property
    def app_consumer_key(self):
        return self.app_auth_file["consumer_key"]

    @property
    def app_consumer_secret(self):
        return self.app_auth_file["consumer_secret"]

    def retrieve(self, query: Callable, params: Union[Dict[str, str], None] = None, data_type_class: Type[YahooFantasyObject]=None):

        file_path = f"{self.league_id}-{self.game_id}-{self.game_code}-{query.__name__}"
        if params is not None:
            for key, arg in params.items():
                file_path += f"-{key}-{arg}"

        if (self.data.data_dir/f"{file_path}.json").is_file() and not self.force_update:
            self.data.dev_offline = True
            self.data.save_data = False
        else:
            self.data.dev_offline = False
            self.data.save_data = True

        try:
            return self.data.retrieve(file_path, query, params=params, data_type_class=data_type_class)
        except requests.exceptions.HTTPError as e:
            print(f"{e}\n\twaiting 60s")
            time.sleep(120)
            return self.data.retrieve(file_path, query, params=params, data_type_class=data_type_class)


class FantasyNBAAnalyser:

    SEASON = 2023
    GAME_CODE = "nba"
    GAME_ID = 410 # 418
    GAME_KEY = "410" # "418"
    LEAGUE_ID = "170305" #"55686"

    LEAGUE_PLAYER_LIMIT = 101

    def __init__(self):

        #Instantiate query object automatically saving files
        self._query = Query(game_code=self.GAME_CODE, league_id=self.LEAGUE_ID, game_id=self.GAME_ID)

        self._teams = None

    @property
    def app_auth_file(self):
        with open("private.json", "r") as f:
            return json.load(f)

    @property
    def app_consumer_key(self):
        return self.app_auth_file["consumer_key"]

    @property
    def app_consumer_secret(self):
        return self.app_auth_file["consumer_secret"]

    @property
    def teams(self):

        if self._teams is None or True:
            self._teams = []
            teams = self._query.retrieve(self._query.query.get_league_teams)
            for team in teams:
                t = team["team"]
                self._teams.append(Team(self._query, t.name.decode("utf-8"), t.team_id))
        return self._teams

    def get_team_by_name(self, name):
        for team in self.teams:
            if name == team.name:
                return team
        raise KeyError(f"No team found with name {name}")

    def get_league_ranking(self):

        standing = self._query.retrieve(self._query.query.get_league_standings, data_type_class=models.Standings)

        data = []
        for team in standing.teams:
            t = team["team"]
            team_instance = self.get_team_by_name(t.name.decode("utf-8"))
            data.append([t.team_standings.playoff_seed, team_instance.name, t.team_standings.outcome_totals.wins, t.team_standings.outcome_totals.losses, t.team_standings.outcome_totals.percentage, t.team_standings.points_for, np.std(team_instance.get_weekly_points(from_week=self.start_week, to_week=self.current_week)), t.team_standings.points_against, t.team_standings.rank <= 4])

        return pd.DataFrame(data, columns=['Rank', 'Team', 'W', 'L', 'Ratio', 'Points +', 'Standard dev', 'Points -', 'PlayOffs']).sort_values(by=['Rank'], ascending=True)

    @property
    def current_week(self):
        return self._query.retrieve(self._query.query.get_league_metadata, data_type_class=models.League).current_week

    @property
    def start_week(self):
        return self._query.retrieve(self._query.query.get_league_metadata, data_type_class=models.League).start_week

    @property
    def end_week(self):
        return self._query.retrieve(self._query.query.get_league_metadata, data_type_class=models.League).end_week