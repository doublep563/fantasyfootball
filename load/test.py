import logging

import requests
import os
import json
import time

BASE_URL = 'https://fantasy.premierleague.com/api/'
DOWNLOADS_DIRECTORY = "/home/ubuntu/streamlit/fantasyfootball/downloads/"
FPL_STATS_URL = "https://www.fplstatistics.co.uk/Home/IndexAndroid2"
FOUR_HOURS = 60 * 60 * 4
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

try:
    import http.client as http_client
except ImportError:
    # Python 2
    import httplib as http_client

# You must initialize logging, otherwise you'll not see debug output.
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True


def load(url, file):
    if os.path.exists(DOWNLOADS_DIRECTORY + file):
        print("File Found in downloads")
        file_modified_time = os.path.getmtime(DOWNLOADS_DIRECTORY + file)
        if (time.time() - file_modified_time) > FOUR_HOURS:
            print("Aged file - Download")
            response = requests.get(BASE_URL + url).json()

            with open(DOWNLOADS_DIRECTORY + file, "w") as outfile:
                json.dump(response, outfile)
            return response
        else:
            print("Return local file")
            with open(DOWNLOADS_DIRECTORY + file) as fp:
                response = json.load(fp)

            return response
    else:
        print("File not found")
        response = requests.get(
            BASE_URL + url).json()

        with open(DOWNLOADS_DIRECTORY + file, "w") as outfile:
            json.dump(response, outfile)
        return response


def load_fpl_stats(file):
    if os.path.exists(DOWNLOADS_DIRECTORY + file):
        print("File Found in downloads")
        file_modified_time = os.path.getmtime(DOWNLOADS_DIRECTORY + file)
        if (time.time() - file_modified_time) > FOUR_HOURS:
            print("Aged file - Download")
            response = requests.get(FPL_STATS_URL).json()

            with open(DOWNLOADS_DIRECTORY + file, "w") as outfile:
                json.dump(response, outfile)
            return response
        else:
            print("Return local file")
            with open(DOWNLOADS_DIRECTORY + file) as fp:
                response = json.load(fp)

            return response
    else:
        print("File not found")
        response = requests.get(FPL_STATS_URL,headers=headers).json()

        with open(DOWNLOADS_DIRECTORY + file, "w") as outfile:
            json.dump(response, outfile)
        return response


response = requests.get(FPL_STATS_URL)
print(response)
# load_fpl_stats('price-changes.json')
