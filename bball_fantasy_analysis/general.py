from pathlib import Path
import json

import pandas as pd

from yfpy import Data
from yfpy.query import YahooFantasySportsQuery


class FantasyNBAAnalyser:
    SEASON = 2023
    GAME_CODE = "nba"
    GAME_ID = 418
    GAME_KEY = "418"
    LEAGUE_ID = "55686"

    LEAGUE_PLAYER_LIMIT = 101

    def __init__(self):

        self.auth_dir = Path(__file__).parent

        # set target directory for data output
        self.data_dir = Path(__file__).parent / "output"

        # create YFPY Data instance for saving/loading data
        self.data = Data(self.data_dir)

        self._query = None

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
    def query(self):

        if self._query is None:
            self._query = YahooFantasySportsQuery(
                self.auth_dir,
                self.LEAGUE_ID,
                game_id=self.GAME_ID,
                game_code=self.GAME_CODE,
                offline=False,
                all_output_as_json_str=False,
                consumer_key=self.app_consumer_key,
                consumer_secret=self.app_consumer_secret,
                browser_callback=True
            )

        return self._query

    def get_league_ranking(self):

        standing = self.query.get_league_standings()

        name, points = [], []
        data = []
        for team in standing.teams:
            t = team["team"]

            data.append([t.team_standings.rank, t.name.decode("utf-8"), t.team_standings.outcome_totals.wins, t.team_standings.outcome_totals.losses, t.team_standings.outcome_totals.percentage, t.team_points.total, t.team_standings.points_for, t.team_standings.points_against, t.team_standings.rank <= 4])
        return pd.DataFrame(data, columns=['Rank', 'Team', 'W', 'L', 'Ratio', 'Points', 'Points for', 'Points against', 'PlayOffs'])
