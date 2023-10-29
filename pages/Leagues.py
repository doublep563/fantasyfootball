import pandas as pd
import streamlit as st

from load.load_data import load_entry, load_league_standings, load_picks

response, entry, classic, h2h, cup, cup_matches = load_entry()

st.dataframe(entry)
st.dataframe(classic)
st.dataframe(h2h)
st.dataframe(cup)
st.dataframe(cup_matches)
# classics = pd.json_normalize(response['leagues']['classic'])
# h2h = pd.json_normalize(response['leagues']['h2h'])
# cup = pd.json_normalize(response['leagues']['cup'])
# cup_matches = pd.json_normalize(response['leagues']['cup_matches'])
# leagues = pd.json_normalize(response['leagues'])
# st.dataframe(classics)
#
# league = load_league_standings(517549)
#
# league_df = pd.json_normalize(league['standings']['results'])
# st.dataframe(league_df)
#
# entry_picks = load_picks(3847231, 10)
#
# st.json(entry_picks)
