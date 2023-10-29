#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Oct 26 13:04:54 2023

@author: ubuntu
"""

import os

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = 'https://fantasy.premierleague.com/api/'
DOWNLOADS_DIRECTORY = "/home/ubuntu/streamlit/fantasyfootball/downloads/"
FOUR_HOURS = 60 * 60 * 4
FPL_ID = 26431

print(ROOT_DIR)
