#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 15 13:58:02 2023

@author: ubuntu
"""
import pandas as pd
import requests

import apicall as api
from settings import FPL_ID, BASE_URL


def load_bootstrap():
    response = api.load('bootstrap-static', 'bootstrap.json')

    events = pd.json_normalize(response['events'])
    game_settings = pd.json_normalize(response['game_settings'])
    phases = pd.json_normalize(response['phases'])
    teams = pd.json_normalize(response['teams'])
    total_players = response['total_players']
    elements = pd.json_normalize(response['elements'])
    element_stats = pd.json_normalize(response['element_stats'])
    element_types = pd.json_normalize(response['element_types'])

    return events, game_settings, phases, teams, total_players, elements, element_stats, element_types


def load_entry():
    response = api.load("entry/" + str(FPL_ID), 'entry.json')
    entry = pd.json_normalize(response, max_level=0)
    entry = entry.drop(columns="leagues")

    classic = pd.json_normalize(response['leagues']['classic'])
    h2h = pd.json_normalize(response['leagues']['h2h'])
    cup = pd.json_normalize(response['leagues']['cup'])
    cup_matches = pd.json_normalize(response['leagues']['cup_matches'])
    return response, entry, classic, h2h, cup, cup_matches


def load_league_standings(league_id):
    url = "leagues-classic/" + str(league_id) + "/standings"
    return api.load(url, "league_" + str(league_id) + ".json")


def load_picks(entry, event):
    url = "entry/" + str(entry) + "/event/" + str(event) + "/picks/"
    return api.load(url, str(entry) + "-" + str(event) + ".json")


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
    response = api.load('fixtures', 'fixtures.json')
    fixtures = pd.json_normalize(response, max_level=0)
    # stats not decoded. Useless as is.
    stats = fixtures['stats']

    fixtures = fixtures.drop(columns='stats')
    return fixtures, stats


def load_future_fixtures():
    fixtures = requests.get(BASE_URL + 'fixtures/?future=1').json()

    return pd.DataFrame(fixtures)


def build_players(elements, teams, element_types):
    # join players to teams
    df = pd.merge(
        left=elements,
        right=teams,
        left_on='team',
        right_on='id'
    )

    # join player positions
    df = df.merge(
        element_types,
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
