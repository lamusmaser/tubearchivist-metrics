# import json
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
            print(f"URL: {ta_url + index_name}")
            print(f"Query params: {keyvalue}")

            getjson = requests.get(
                ta_url + index_name,
                headers=headers,
                timeout=30,
            )

            # Check for HTTP errors
            getjson.raise_for_status()

            jsonreturn = getjson.json()

            response = jsonreturn[keyvalue]
            if response is None:
                response = 0

        except requests.exceptions.RequestException as e:
            print(f"Request error from {ta_url}{index_name}: {e}")
        except (KeyError, ValueError) as e:
            print(
                f"Error parsing response from {ta_url}{index_name} "
                f"(key '{keyvalue}'): {e}"
            )
        except Exception as e:
            print(f"Unexpected error from {ta_url}{index_name}: {e}")

        return response
