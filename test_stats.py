from bball_fantasy_analysis.nba_stats.stats import NBAstats


stats = NBAstats()

#stats.get_matchups_for_day("2022-11-04")
print(stats.team("ATL").get_number_of_games(from_date="2022-11-01", to_date="2022-11-04"))

#print(stats.team("ATL").get_past_games().to_string())