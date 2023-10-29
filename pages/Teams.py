import altair as alt
import streamlit as st

from load.load_data import load_bootstrap, build_players
from load.load_data import load_event_live
from load.load_data import load_fixtures


def build_teams_chart(df):
    domain = [1, 2, 3, 4, 5]
    range_ = ['#375523', '#01FC7A', '#E7E7E7', '#FF1715', '#80072D']

    chart = (
        alt.Chart(df, title="Teams Expected Goals",
                  height=1000, width=900)
        .mark_rect(cornerRadius=5)
        .encode(
            x=alt.X("event",
                    type="nominal",
                    title="Game Week",
                    axis=alt.Axis(labelAngle=0, orient="top",
                                  titleFontSize=20, labelFontSize=14, labelFontWeight="bold"),
                    ),
            y=alt.Y("Team",
                    title="Team",
                    axis=alt.Axis(titleFontSize=20, labelFontSize=14,
                                  labelFontWeight="bold")
                    ),

            color=alt.Color("expected_goals",
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

    return output


st.set_page_config(page_title="Teams", layout="wide")

events, game_settings, phases, teams, total_players, elements, element_stats, element_types = load_bootstrap()

fixtures, stats = load_fixtures()

events_live = load_event_live(9)
players = build_players(elements, teams, element_types)

display = None
df = events_live.merge(fixtures, left_on='fixtureId', right_on='id')

df = df.merge(players, left_on='id_x', right_on='player_id')

df = df.groupby(['plural_name_short', 'Team', 'event'])[
    ["expected_goals", "goals_scored", "expected_assists", "assists", "goals_conceded",
     "expected_goals_conceded"]].sum().reset_index()

player_types = st.sidebar.radio(
    "Select Position",
    ["ALL", "GKP", "DEF", "MID", "FWD"],
    index=0,
    horizontal=False)

if player_types:
    if player_types == "ALL":
        display = df
    else:
        display = df.loc[(df['plural_name_short'] == player_types)]

col1, col2 = st.columns(2)
with col1:
    st.altair_chart(alt.Chart(display, title="Expected Goals").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(expected_goals)', title='Expected Goals'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))

with col2:
    st.altair_chart(alt.Chart(display, title="Expected Assists").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(expected_assists)', title='Expected Assists'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))

col3, col4 = st.columns(2)

with col3:
    st.altair_chart(alt.Chart(display, title="Goals Scored").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(goals_scored)', title='Goals Scored'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))

with col4:
    st.altair_chart(alt.Chart(display, title="Assists").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(assists)', title='Assists'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))

col5, col6 = st.columns(2)

with col5:
    st.altair_chart(alt.Chart(display, title="Goals Conceded").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(goals_conceded)', title='Goals Conceded'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))

with col6:
    st.altair_chart(alt.Chart(display, title="Expected Goals Conceded").mark_bar().encode(
        x='Team:O',
        y=alt.Y('sum(expected_goals_conceded)', title='Expected Goals Conceded'),
        color=alt.Color("plural_name_short",
                        type="nominal",
                        title="Position",
                        ),
    ))
