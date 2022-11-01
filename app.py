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

week = 3
st.write(f"## Standings week {league.current_week}/{league.end_week}")
df = league.get_league_ranking()[['Rank', 'Team', 'W', 'L', 'Ratio', 'Points +', 'Standard dev', 'Points -']].style.hide_index().applymap(color_survived, subset=['Rank']).format(formatter={'Ratio': "{:.2f}", 'Points +': "{:.0f}", 'Standard dev': "{:.0f}", 'Points -': "{:.0f}"})

st.write(df.to_html(), unsafe_allow_html=True)

print(f"Done application in {(datetime.now() - start).total_seconds()}s")
