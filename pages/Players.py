import streamlit as st
import altair as alt
from enum import Enum
from src import agstyler
from src.agstyler import PRECISION_ONE
from load_data import load_bootStrap
from load_data import build_players
from load_data import load_event_live
from load_data import load_fixtures
from load_data import BASE_URL


class Color(Enum):
    RED_LIGHT = "#fcccbb"
    RED_DARK = "#8b0000"
    YELLOW_LIGHT = "#fff0ce"
    YELLOW_DARK = "#ffcc00"
    GREEN_LIGHT = "#abf7b1"
    GREEN_DARK = "#008631"


st.set_page_config(page_title="Players", layout="wide")

st.title('Fantasy Football Python Stuff')

# base url for all FPL API endpoints

bootStrap = load_bootStrap(BASE_URL)
events = load_event_live(BASE_URL, 8)
fixtures = load_fixtures(BASE_URL)

players = build_players(bootStrap)

df = events.merge(fixtures, left_on='fixtureId', right_on='id')

df = df.merge(players, left_on='id_x', right_on='player_id')
# =============================================================================
# st.write(list(df.columns))
# st.write(df.head())
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

if "slider_range" not in st.session_state:
    st.session_state["slider_range"] = (min, max)


player_cost_range = st.sidebar.slider(
    'Player Cost',
    min, max,  step=(0.1), format="%f", key="slider_range")


team_name = players['team_name'].drop_duplicates()
team_choice = st.sidebar.selectbox('Team', team_name, index=None,
                                   placeholder="Select Team...",)

player_select = st.sidebar.selectbox(
    "Search for Player",
    players['web_name'].tolist(),
    index=None,
    placeholder="Enter player name"
)

if player_select:
    display = players.loc[players['web_name'].str.contains(player_select)]

else:
    if player_types == 'ALL':
        if team_choice:
            display = players.loc[(players['team_name'] == team_choice) & (
                player_cost_range[0] <= players['now_cost']) & (players['now_cost'] <= player_cost_range[1])]

        else:
            st.write(player_cost_range)
            display = players.loc[(
                player_cost_range[0] <= players['now_cost']) & (players['now_cost'] <= player_cost_range[1])]
    else:
        st.write(player_types)
        if team_choice:
            display = players.loc[(players['team_name'] == team_choice)
                                  & (players['singular_name_short'] == player_types) & (
                                      player_cost_range[0] <= players['now_cost']) & (players['now_cost'] <= player_cost_range[1])]
        else:
            display = players.loc[(
                players['singular_name_short'] == player_types) & (
                    player_cost_range[0] <= players['now_cost']) & (players['now_cost'] <= player_cost_range[1])]


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

# =============================================================================
# outliers = df[['web_name', 'singular_name_short',
#                'goals_scored', 'assists', 'expected_goal_involvements']]
#
# test = outliers.groupby(['web_name', 'singular_name_short']).sum()
# test['xGI Differential'] = test['goals_scored'] + \
#     test['assists'] - test['expected_goal_involvements']
#
# test = test.sort_values(
#     by=['singular_name_short', 'xGI Differential'])
#
# st.dataframe(test)
# =============================================================================

selected_row = grid["selected_rows"]
if selected_row:
    title = selected_row[0]['first_name'] + \
        ' ' + selected_row[0]['second_name']
    st.title(title)
    st.header(selected_row[0]['team_name'])

    photo = selected_row[0]['photo'].split(".")

    photoUrl = 'https://resources.premierleague.com/premierleague/photos/players/110x140/p' + \
        photo[0] + '.png'

# =============================================================================
#     "https://resources.premierleague.com/premierleague/photos/players/110x140/p${this.code}.png"
#
# =============================================================================
    st.image(photoUrl)

    player = df.loc[df['player_id'] == selected_row[0]['player_id']]
    player.sort_values(by=['event'], ascending=False, inplace=True)

    st.write(player.head())

    chart = alt.Chart(player).mark_point().encode(
        x='event', y='expected_goal_involvements')

    st.altair_chart(chart, use_container_width=True)

    player.loc['total'] = player.sum()

    player.loc[player.index[-1], ['event', 'fixtureId', 'now_cost']] = ''

    custom_css = {
        ".ag-header-cell-label": {"justify-content": "center"},
        ".ag-header-group-cell-label": {"justify-content": "center"}
    }

    player_formatter = {
        'event': ('GW', {'headerTooltip': 'Game Week', 'width': 60}),
        'fixtureId': ('FX', {'headerTooltip': 'Fixture ID', 'width': 60}),
        'now_cost': ('£', {'headerTooltip': 'Cost', 'width': 60}),
        'total_points_x': ('Pts', {'headerTooltip': 'Points', 'width': 60}),
        'starts': ('ST', {'width': 60}),
        'minutes_x': ('MP', {'width': 60}),
        'goals_scored': ('GS', {'width': 60}),
        'assists': ('A', {'width': 60}),
        'expected_goals': ('xG', {'width': 60}),
        'expected_assists': ('xA', {**PRECISION_ONE, 'width': 60}),
        'expected_goal_involvements': ('xGI', {'width': 60}),
        'expected_goals_conceded': ('xGC', {'width': 60}),
        'clean_sheets': ('CS', {'width': 60}),
        'goals_conceded': ('GC', {'width': 60}),
        'own_goals': ('OG', {'width': 60}),
        'penalties_saved': ('PS', {'width': 60}),
        'penalties_missed': ('PM', {'width': 60}),
        'yellow_cards': ('YC', {'width': 60}),
        'red_cards': ('RC', {'width': 60}),
        'saves': ('S', {'width': 60}),
        'bonus': ('B', {'width': 60}),
        'bps': ('BPS', {'width': 60}),

    }

    player_grid = agstyler.draw_grid(
        player,
        formatter=player_formatter,
    )
