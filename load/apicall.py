import requests
import os
import json
import time
BASE_URL = 'https://fantasy.premierleague.com/api/'
DOWNLOADS_DIRECTORY = "/home/ubuntu/streamlit/fantasyfootball/downloads/"
FOUR_HOURS = 60 * 60 * 4


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
