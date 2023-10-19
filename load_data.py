#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 13:58:02 2023

@author: ubuntu
"""
import streamlit as st
import requests
import pandas as pd


BASE_URL = 'https://fantasy.premierleague.com/api/'


@st.cache_data
def load_bootStrap(base_url):
    data_load_state = st.text('Loading bootstrap data...')

    bootStrap = requests.get(base_url + 'bootstrap-static').json()

    data_load_state.text('Loading bootstrap data...done!')

    return bootStrap


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

    df = pd.DataFrame(allStats)

    df['expected_goals'] = pd.to_numeric(df['expected_goals'])
    df['expected_assists'] = pd.to_numeric(df['expected_assists'])
    df['expected_goal_involvements'] = pd.to_numeric(
        df['expected_goal_involvements'])
    df['expected_goals_conceded'] = pd.to_numeric(
        df['expected_goals_conceded'])

    return df


@st.cache_data
def load_fixtures(BASE_URL):
    fixtures = requests.get(BASE_URL + 'fixtures').json()

    df = pd.DataFrame(fixtures)
# =============================================================================
#     df = df.drop(columns=['stats'])
#
# =============================================================================
    return df


def load_future_fixtures():
    fixtures = requests.get(BASE_URL + 'fixtures/?future=1').json()

    return pd.DataFrame(fixtures)


def build_players(bootStrap):
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
