import streamlit as st
import pandas as pd
import requests
from enum import Enum
from src import agstyler
from src.agstyler import PRECISION_ONE


class Color(Enum):
    RED_LIGHT = "#fcccbb"
    RED_DARK = "#8b0000"
    YELLOW_LIGHT = "#fff0ce"
    YELLOW_DARK = "#ffcc00"
    GREEN_LIGHT = "#abf7b1"
    GREEN_DARK = "#008631"


@st.cache_data
def load_bootStrap(base_url):
    data_load_state = st.text('Loading bootstrap data...')

    bootStrap = requests.get(base_url + 'bootstrap-static').json()

    data_load_state.text('Loading bootstrap data...done!')

    return bootStrap


def build_players(bootstrap):
    # create players dataframe
    players = pd.json_normalize(bootStrap['elements'])

    # create teams dataframe
    teams = pd.json_normalize(bootStrap['teams'])

    positions = pd.json_normalize(bootStrap['element_types'])

    # join players to teams
    df = pd.merge(
        left=players,
        right=teams,
        left_on='team',
        right_on='id'
    )

    # join player positions
    df = df.merge(
        positions,
        left_on='element_type',
        right_on='id'
    )

    # rename columns
    df = df.rename(
        columns={'name': 'team_name', 'singular_name': 'position_name', 'minutes_x': 'minutes',
                 'short_name': 'Team', 'id': 'element_type',
                 'id_x': 'player_id'}
    )

    df = df.drop(columns=['minutes', 'goals_scored', 'assists', 'clean_sheets',
                          'goals_conceded', 'own_goals', 'penalties_saved', 'penalties_missed',
                          'yellow_cards', 'red_cards', 'saves', 'bonus', 'bps', 'influence', 'creativity',
                          'threat', 'ict_index', 'expected_goals', 'expected_assists', 'expected_goal_involvements',
                          'expected_goals_conceded', 'starts', 'in_dreamteam', 'pulse_id'
                          ])
    # Maybe trouble. Why are there duplicates???
    df = df.loc[:, ~df.columns.duplicated()].copy()
    df['now_cost'] = df['now_cost'] / 10

    # Drop players who are not available
    df = df[~df['status'].isin(['u'])]

    return df


@st.cache_data
def load_event_live(base_url, currentEvent):

    data_load_state = st.text('Loading event live data...')

    i = 1
    allStats = []

    while i <= currentEvent:
        print(i)
        event = requests.get(base_url + 'event/' + str(i) + '/live/').json()
        for element in event['elements']:
            fixtureId = 0
            id = element['id']
            if len(element['explain']):
                fixtureId = (element['explain'][0]['fixture'])
            else:
                fixtureId = 999
            stats = element['stats']
            stats['id'] = id
            stats['fixtureId'] = fixtureId
            allStats.append(stats)
        i += 1

    data_load_state.text('Loading event live data...done!')

    return pd.DataFrame(allStats)


@st.cache_data
def load_fixtures(BASE_URL):
    fixtures = requests.get(BASE_URL + 'fixtures').json()

    fixturesDF = pd.DataFrame(fixtures)
    fixturesDF = fixturesDF.drop(columns=['stats'])

    return fixturesDF


def check_status(row):
    highlight = 'background-color: tomato;'
    injured = 'background-color: gold;'
    default = ''

    # must return one string per cell in this row
    if row['status'] in ['s', 'i']:
        return [highlight]*9
    elif row['status'] in ['d']:
        return [injured]*9
    else:
        return [default]*9


st.title('Fantasy Football Python Stuff')

# base url for all FPL API endpoints
BASE_URL = 'https://fantasy.premierleague.com/api/'

bootStrap = load_bootStrap(BASE_URL)
events = load_event_live(BASE_URL, 8)
fixtures = load_fixtures(BASE_URL)

players = build_players(bootStrap)

df = events.merge(fixtures, left_on='fixtureId', right_on='id')

df = df.merge(players, left_on='id_x', right_on='player_id')

# =============================================================================
# st.write(list(df.columns.values))
# st.write(df.head())
#
# st.write(len(events.index))
# st.write(len(fixtures.index))
# st.write(len(df.index))
# =============================================================================

display = None

# =============================================================================
# players = players[['Name', 'Cost',
#                    'Team', 'team_name', 'POS', 'Points', 'status', 'news', 'news_added']]
#
# =============================================================================

player_types = st.sidebar.radio(
    "Position",
    ["ALL", "GKP", "DEF", "MID", "FWD"],
    index=0,
    horizontal=True)

min = (players['now_cost'].min())
max = (players['now_cost'].max())

values = st.sidebar.slider(
    'Player Cost',
    min, max, (min, max), step=(0.1), format="%f")

team_name = players['team_name'].drop_duplicates()
team_choice = st.sidebar.selectbox('Team', team_name, index=None,
                                   placeholder="Select Team...",)

if player_types == 'ALL':
    if team_choice:
        display = players.loc[(players['team_name'] == team_choice) & (
            values[0] <= players['now_cost']) & (players['now_cost'] <= values[1])]

    else:
        st.write(values)
        display = players.loc[(
            values[0] <= players['now_cost']) & (players['now_cost'] <= values[1])]
else:
    st.write(player_types)
    if team_choice:
        display = players.loc[(players['team_name'] == team_choice)
                              & (players['singular_name_short'] == player_types) & (
                                  values[0] <= players['now_cost']) & (players['now_cost'] <= values[1])]
    else:
        display = players.loc[(
            players['singular_name_short'] == player_types) & (
                values[0] <= players['now_cost']) & (players['now_cost'] <= values[1])]


with st.sidebar:

    formatter = {
        'web_name': ('Name', {'width': 110}),
        'team_name': ('Team', {'width': 60}),
        'singular_name_short': ('Pos', {'width': 60}),
        'now_cost': ('Cost', {**PRECISION_ONE, 'width': 60}),
        'total_points': ('Points', {'width': 60}),
    }

    go = {
        'rowClassRules':
            {'injured': 'data.status == "i"',
             'suspended': 'data.status == "s"',
             'doubtful': 'data.status == "d"',
             }

    }
    css = {
        '.injured':
            {'background-color': f'{Color.RED_LIGHT.value} !important'},
        '.suspended':
            {'background-color': f'{Color.RED_LIGHT.value} !important'},
        '.doubtful':
            {'background-color': f'{Color.YELLOW_LIGHT.value} !important'},
            "#gridToolBar": {
                "padding-bottom": "0px !important"}

    }

    grid = agstyler.draw_grid(
        display,
        formatter=formatter,
        grid_options=go,
        css=css,
        use_checkbox=True,
        selection="single",
        fit_columns=True
    )

selected_row = grid["selected_rows"]
if selected_row:
    st.write(selected_row[0]['web_name'])
