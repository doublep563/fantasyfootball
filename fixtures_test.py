#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 19 12:38:58 2023

@author: ubuntu
"""
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 14:09:05 2023

@author: ubuntu
"""




import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
from load_data import load_bootStrap
from load_data import load_fixtures
from load_data import load_future_fixtures
from load_data import BASE_URL
from st_aggrid.shared import JsCode
def add_team_logo(row):
    return 'https://resources.premierleague.com/premierleague/badges/50/t' + \
        str(row['code']) + '.png'


render_image = JsCode("""
   const element = document.createElement('span');
   const imageElement = document.createElement('img');

   imageElement.src = params.value

  element.appendChild(imageElement);
  element.appendChild(document.createTextNode(params.value));
  return element;
    """)


def add_dummy_fixtures(fixtures, dummyFixtures):
    print("Calling add_dummy_fixtures")
    """
        Each dummy fixture has home and away team.
    """

    home_team = dummyFixtures['team_h'].tolist()
    print(home_team)
    home_fixtures = fixtures[(fixtures['team_h'] == 13)
                             | (fixtures['team_a'] == 13)]

    home_events = home_fixtures['event'].unique()

    events = fixtures['event'].unique()
    print(home_events)
    print(events)

    difference = list(set(events) - set(home_events))

    print("Missing fixtures for event " + str(difference))


st.set_page_config(layout="wide")

bootStrap = load_bootStrap(BASE_URL)
teams = pd.json_normalize(bootStrap['teams'])
teams['logo'] = teams.apply(add_team_logo, axis=1)

fixtures = load_fixtures(BASE_URL)

fixtures['difficulty'] = 0
fixtures['event'] = fixtures['event'].fillna(0)
fixtures = fixtures.astype({"event": int})

fixtures = fixtures[fixtures['finished'] == False]

df_no_fixtures = fixtures[fixtures['event'] == 0]

if len(df_no_fixtures.index) > 0:
    print("We need dummy fixtures")
    add_dummy_fixtures(fixtures, df_no_fixtures)

# =============================================================================
# dicList = fixtures.to_dict(orient='records')
#
# i = 1
# home = []
# away = []
#
# while i <= 20:
#     for x in dicList:
#         if x['team_h'] == i:
#             home.append(x)
#     for y in dicList:
#         if y['team_a'] == i:
#             away.append(y)
#     i = i + 1
#
#
# df_home = pd.DataFrame(home)
# df_home['team'] = df_home['team_h']
# df_home['opposition'] = df_home['team_a']
# df_home['difficulty'] = df_home['team_h_difficulty']
# df_home['name'] = df_home['team'].map(
#     teams.set_index('id')['name'].to_dict())
#
# df_away = pd.DataFrame(away)
# df_away['team'] = df_away['team_a']
# df_away['opposition'] = df_away['team_h']
# df_away['difficulty'] = df_away['team_a_difficulty']
# df_away['name'] = df_away.team.map(
#     teams.set_index('id')['name'].to_dict())
#
# df = pd.concat([df_away, df_home])
#
# df['opponent'] = df.opposition.map(
#     teams.set_index('id')['short_name'].to_dict())
#
# df['location'] = np.where(df['team'] == df['team_h'], 'H', 'A')
#
# df['opponent_location'] = df['opponent'] + ' (' + df['location'] + ')'
#
# =============================================================================
