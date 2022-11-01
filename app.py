import streamlit as st
from bball_fantasy_analysis import FantasyNBAAnalyser

st.title("Weekly overview")

league = FantasyNBAAnalyser()

def color_survived(val):
    color = '#5eae76' if val <= 4 else '#de796e'
    return f'background-color: {color}'

week = 3
st.write(f"## Standings week {league.current_week}/{league.end_week}")
df = league.get_league_ranking()[['Rank', 'Team', 'W', 'L', 'Ratio', 'Points +', 'Points -']].style.hide_index().applymap(color_survived, subset=['Rank'])
st.write(df.to_html(), unsafe_allow_html=True)

#st.dataframe(data=league.get_league_ranking()[['Rank', 'Team', 'W', 'L', 'Ratio', 'Points', 'Points for', 'Points against']].style.applymap(color_survived, subset=['Rank']))
