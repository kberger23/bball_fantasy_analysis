import streamlit as st
from bball_fantasy_analysis import FantasyNBAAnalyser

from datetime import datetime

st.title("Weekly overview")

start = datetime.now()
print(f"Restart application at {start}")
league = FantasyNBAAnalyser()

def color_survived(val):
    color = '#5eae76' if val <= 4 else '#de796e'
    return f'background-color: {color}'

def color_lucky_weeks(row):
    if row[0] == df["Wins against the mean"].max():
        return [f'background-color: #5eae76']
    elif row[0] == df["Wins against the mean"].min():
        return [f'background-color: #de796e']
    else:
        return [f'background-color: default']

week = 3
st.write(f"## Standings week {league.current_week}/{league.end_week}")
df = league.get_league_ranking()[['Rank', 'Team', 'W', 'L', 'Ratio', 'Points +', 'Standard dev', 'Points -', 'Wins against the mean']]
df_styled = df.style.hide_index().applymap(color_survived, subset=['Rank']).apply(color_lucky_weeks, subset=['Wins against the mean'], axis=1).format(formatter={'Ratio': "{:.2f}", 'Points +': "{:.0f}", 'Standard dev': "{:.0f}", 'Points -': "{:.0f}"})

st.write(df_styled.to_html(), unsafe_allow_html=True)
st.write(f"#### Number points for the average week are {league.mean_points:.02f}")

st.write(f"# Matchup for the current week {league.current_week}")
matchups = league.get_matchup_week(league.current_week)
matchups_styled = matchups.style.hide_index().format(formatter={'Points': "{:.1f}", 'Proj': "{:.1f}"})
st.write(matchups_styled.to_html(), unsafe_allow_html=True)

league.teams[1].get_optimal_roster_for_week(league.current_week)

print(f"Done application in {(datetime.now() - start).total_seconds()}s")
