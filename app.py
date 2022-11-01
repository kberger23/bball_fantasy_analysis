import streamlit as st
from bball_fantasy_analysis import FantasyNBAAnalyser

st.title("Weekly overview")

league = FantasyNBAAnalyser()

def color_survived(val):
    color = 'green' if val <= 4 else 'red'
    return f'background-color: {color}'

week = 3
st.write(f"## Current standing Week {week}")
st.dataframe(data=league.get_league_ranking().style.applymap(color_survived, subset=['Rank']))
