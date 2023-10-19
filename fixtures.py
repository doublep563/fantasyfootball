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


def get_first_event(df):
    df = df.loc[df['event'] > 0]

    min_event = df['event'].unique().min()
    return min_event


def sort_teams(df):
    # =============================================================================
    #     Sort teams by sum descending sum of difficulty.
    #     This list determines sort order in FDR chart
    # =============================================================================
    df2 = df.groupby(['name'])['difficulty'].agg(['sum', 'count'])

    # =============================================================================
    # If there are less than 6 fixtures, add 5(highest difficulty) to the sum
    #
    # =============================================================================
    df2['sum'] = np.where(df2['count'] < 6, (df2['sum'] + 5), df2['sum'])

    # =============================================================================
    # TODO: Where there are more than 6 fixtures
    #
    # =============================================================================

    df_sorted = df2.sort_values(by='sum')

    return df_sorted.index.values.tolist()


render_image = JsCode("""
   const element = document.createElement('span');
   const imageElement = document.createElement('img');

   imageElement.src = params.value

  element.appendChild(imageElement);
  element.appendChild(document.createTextNode(params.value));
  return element;
    """)

st.set_page_config(layout="wide")

bootStrap = load_bootStrap(BASE_URL)
teams = pd.json_normalize(bootStrap['teams'])
teams['logo'] = teams.apply(add_team_logo, axis=1)

fixtures = load_fixtures(BASE_URL)

futureFixtures = load_future_fixtures()

fixtures['difficulty'] = 0
fixtures['event'] = fixtures['event'].fillna(0)
fixtures = fixtures.astype({"event": int})
fixtures = fixtures[fixtures['finished'] == False]

dicList = fixtures.to_dict(orient='records')

i = 1
home = []
away = []

while i <= 20:
    for x in dicList:
        if x['team_h'] == i:
            home.append(x)
    for y in dicList:
        if y['team_a'] == i:
            away.append(y)
    i = i + 1


df_home = pd.DataFrame(home)
df_home['team'] = df_home['team_h']
df_home['opposition'] = df_home['team_a']
df_home['difficulty'] = df_home['team_h_difficulty']
df_home['name'] = df_home['team'].map(
    teams.set_index('id')['name'].to_dict())

df_away = pd.DataFrame(away)
df_away['team'] = df_away['team_a']
df_away['opposition'] = df_away['team_h']
df_away['difficulty'] = df_away['team_a_difficulty']
df_away['name'] = df_away.team.map(
    teams.set_index('id')['name'].to_dict())

df = pd.concat([df_away, df_home])

df['opponent'] = df.opposition.map(
    teams.set_index('id')['short_name'].to_dict())

df['location'] = np.where(df['team'] == df['team_h'], 'H', 'A')

df['opponent_location'] = df['opponent'] + ' (' + df['location'] + ')'

min_event = get_first_event(df)

st.write(min((min_event + 6), 38))

radio_list = [*range(min_event, min((min_event + 6), 38), 1)]

event = st.sidebar.radio(
    "Select starting Game Week",
    radio_list,
    horizontal=True
)

df = df.loc[(df['event'] >= event)
            & (df['event'] < (event + 6))]

sort_order = sort_teams(df)

domain = [1, 2, 3, 4, 5]
range_ = ['#375523', '#01FC7A', '#E7E7E7', '#FF1715', '#80072D']


chart = (
    alt.Chart(df, title="Fixture Difficulty Rating", height=1000, width=900)
    .mark_rect(cornerRadius=5)
    .encode(
        x=alt.X("event",
                type="nominal",
                title="Game Week",
                axis=alt.Axis(labelAngle=0, orient="top",
                              titleFontSize=20, labelFontSize=14, labelFontWeight="bold"),
                ),
        y=alt.Y("name",
                title="Team",
                sort=sort_order,
                axis=alt.Axis(titleFontSize=20, labelFontSize=14,
                              labelFontWeight="bold")
                ),

        color=alt.Color("difficulty",
                        type="nominal",
                        title="",
                        scale=alt.Scale(domain=domain, range=range_)),

    )
).properties(height=alt.Step(30))


text = chart.mark_text().encode(

    detail='difficulty:N',
    text=alt.Text('opponent_location:N'),
    color=alt.condition(1 > alt.expr.datum['difficulty'] > 3,
                        alt.value('white'),
                        alt.value('black'))
)

# =============================================================================
# output = chart + text
# # =============================================================================
output = alt.layer(chart, text).configure_view(stroke='transparent').configure_scale(
    bandPaddingInner=.05,
).configure_title(fontSize=30, anchor='middle')


st.altair_chart(output)
