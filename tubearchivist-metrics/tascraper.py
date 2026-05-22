import json
from time import sleep

import requests
from environment import AppConfig

"""
This is a simple wrapper for the TA API. It is used to get the count of
videos, channels, and playlists in the TA database. It is also used to get
the count of videos, channels, and playlists that have been scraped by the
TA scraper. The TA scraper is a separate process that runs in the
background and scrapes data from YouTube. The TA API is a RESTful API that
allows you to access the data in the TA database. The TA API requires an
API key for authentication. You can get an API key from TA's Application
Settings.

# url = "/api/video/<video-id>/"
# headers = {"Authorization": "Token xxxxxxxxxx"}
# response = requests.get(url, headers=headers)
"""


class APIWrapper:

    def handle_err(self, error):
        # None of the below is used. TODO.
        print("Connection Error: " + str(error))
        print("There was a problem connecting to the TA API")
        print(
            "Please see the above error. This may be because TA is still "
            "starting up or a misconfiguration."
        )
        print("Sleeping for 60 seconds...")
        sleep(60)

    def get_count(self, index_name, keyvalue):

        config = AppConfig().config
        ta_key = config["ta_key"]
        ta_url = config["ta_url"]

        headers = {"Authorization": "Token " + ta_key}

        response = 0

        try:
            # print(ta_url + index_name)
            # print(keyvalue)
            # print("-----------------------------------------------")

            getjson = requests.get(
                ta_url + index_name, headers=headers, timeout=30
            )

            jsonreturn = json.loads(getjson.content)

            response = jsonreturn[keyvalue]
            if response is None:
                response = 0

        except Exception:
            """
            This has turned into a general catch-all for any errors that occur
            when trying to get data from the TA API due to bad error
            management. This could be a connection error, a timeout error, a
            JSON decoding error, or any other error that occurs when trying to
            get data from the TA API. This is not ideal, but it is better than
            crashing the entire scraper. The error is logged to the console,
            and the function returns 0. The scraper will then continue to run
            and try to get data from the TA API again on the next iteration of
            the loop.
            """
            print("No values from " + ta_url + index_name + keyvalue)

        return response
