#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 13:58:02 2023

@author: ubuntu
"""
import pandas as pd
import requests
import streamlit as st

import apicall as api

BASE_URL = 'https://fantasy.premierleague.com/api/'
DOWNLOADS_DIRECTORY = 'downloads/'
FOUR_HOURS = 60 * 60 * 4


def load_bootstrap():
    return api.load('bootstrap-static', 'bootstrap.json')


def load_event_live(current_event):
    i = 1
    all_stats = []

    while i <= current_event:
        url = "event/" + str(i) + "/live/"
        file = "event-live-" + str(i) + ".json"
        event = api.load(url, file)
        for element in event['elements']:
            element_id = element['id']
            if len(element['explain']):
                fixture_id = (element['explain'][0]['fixture'])
            else:
                fixture_id = 999
            stats = element['stats']
            stats['id'] = element_id
            stats['fixtureId'] = fixture_id
            all_stats.append(stats)
        i += 1

    df = pd.DataFrame(all_stats)

    df['expected_goals'] = pd.to_numeric(df['expected_goals'])
    df['expected_assists'] = pd.to_numeric(df['expected_assists'])
    df['expected_goal_involvements'] = pd.to_numeric(
        df['expected_goal_involvements'])
    df['expected_goals_conceded'] = pd.to_numeric(
        df['expected_goals_conceded'])

    return df


def load_fixtures():
    fixtures = api.load('fixtures', 'fixtures.json')
    # fixtures = requests.get(BASE_URL + 'fixtures').json()

    df = pd.DataFrame(fixtures)
    # =============================================================================
    #     df = df.drop(columns=['stats'])
    #
    # =============================================================================
    return df


def load_future_fixtures():
    fixtures = requests.get(BASE_URL + 'fixtures/?future=1').json()

    return pd.DataFrame(fixtures)


def build_players(bootstrap):
    # create players dataframe
    players = pd.json_normalize(bootstrap['elements'])

    # create teams dataframe
    teams = pd.json_normalize(bootstrap['teams'])

    positions = pd.json_normalize(bootstrap['element_types'])

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
