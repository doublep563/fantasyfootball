import json
from enum import Enum

import pandas as pd
import streamlit as st
from st_keyup import st_keyup

from src import agstyler
from src.agstyler import PRECISION_ONE


class Color(Enum):
    RED_LIGHT = "#fcccbb"
    RED_DARK = "#8b0000"
    YELLOW_LIGHT = "#fff0ce"
    YELLOW_DARK = "#ffcc00"
    GREEN_LIGHT = "#abf7b1"
    GREEN_DARK = "#008631"
    WHITE = "#ffffff"
    BLACK = "#000000"


DOWNLOADS_DIRECTORY = "/home/ubuntu/streamlit/fantasyfootball/downloads/"

st.set_page_config(page_title="Price Changes", layout="wide")

with open(DOWNLOADS_DIRECTORY + 'price-changes.json') as outfile:
    response = json.load(outfile)

df = pd.DataFrame(response['aaData'])
df = df.rename(
    columns={1: "name", 2: "team", 3: "position", 4: "status", 5: "%Owned", 6: "Price", 8: "Changes", 9: "Unlocks",
             10: "Delta", 11: "Target"})
df = df.drop(columns=[0, 7, 12, 13, 14, 15, 16])
df["%Owned"] = pd.to_numeric(df["%Owned"])
df["Price"] = pd.to_numeric(df["Price"])
df["Changes"] = pd.to_numeric(df["Changes"])
df["Delta"] = pd.to_numeric(df["Delta"])
df["Target"] = pd.to_numeric(df["Target"])

display = None

with st.sidebar:
    query = st_keyup("Select Players", placeholder="Enter name", key="0")


# Notice that value updates after every key press
st.write(query)

player_positions = df['position'].unique().tolist()

player_positions.insert(0, "All")

player_types = st.sidebar.radio(
    "Select Position",
    player_positions,
    index=0,
    horizontal=True)

players = df['name'].sort_values().tolist()

query1 = st.sidebar.text_input("Player Name")

if query:
    print(query)
    display = df.loc[df['name'].str.contains(query, case=False)]

else:
    if player_types:
        print(player_types)
        if player_types == "All":
            display = df
        else:
            display = df.loc[df['position'] == player_types]
    else:
        display = df

price_change_formatter = {
    'name': ('Name', {'headerTooltip': 'Name', 'width': 120}),
    'team': ('Team', {'headerTooltip': 'Team', 'width': 120}),
    'position': ('Position', {'headerTooltip': 'Player Position', 'width': 100}),
    'status': ('Status', {'headerTooltip': 'Player Status', 'width': 110}),
    '%Owned': ('%Owned', {**PRECISION_ONE, 'headerTooltip': '%Owned', 'width': 120}),
    'Price': ('Price', {**PRECISION_ONE, 'headerTooltip': 'Price', 'width': 120}),
    'Changes': ('Changes', {'headerTooltip': 'Changes', 'width': 120}),
    'Delta': ('Delta', {'headerTooltip': 'Delta', 'width': 120}),
    'Target': ('Target', {**PRECISION_ONE, 'headerTooltip': 'Target', 'sort': 'desc', 'width': 100}),

}

go = {
    'rowClassRules':
        {
            'rising': 'data.Target >= 90 && data.Target <= 100',
            'rise': 'data.Target >= 100 ',
            'drop': 'data.Target <= -100',
            'dropping': 'data.Target >= -100 && data.Target <= -90',
        }

}
css = {
    '.rise':
        {'background-color': f'{Color.GREEN_DARK.value} !important', 'color': f'{Color.WHITE.value}'},
    '.rising':
        {'background-color': f'{Color.GREEN_LIGHT.value} !important'},
    '.drop':
        {'background-color': f'{Color.RED_DARK.value} !important', 'color': f'{Color.WHITE.value}'},
    '.dropping':
        {'background-color': f'{Color.RED_LIGHT.value} !important'},
    "#gridToolBar": {
        "padding-bottom": "0px !important"}
}
price_change_gird = agstyler.draw_grid(
    display,
    formatter=price_change_formatter,
    grid_options=go,
    css=css,
    fit_columns=True
)
