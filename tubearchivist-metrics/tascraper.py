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

    @staticmethod
    def _make_request(url, headers, timeout=30):
        """Make a GET request to the TA API."""
        try:
            response = requests.get(url, headers=headers, timeout=timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Request error from {url}: {e}")
            try:
                print(f"Response body: {response.text}")
            except (AttributeError, NameError) as debug_error:
                print(f"Could not retrieve response body: {debug_error}")
            return None
        except ValueError as e:
            print(f"Error parsing JSON from {url}: {e}")
            return None

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

    def get_count(self, index_name, keyvalue=None):

        config = AppConfig().config
        ta_key = config["ta_key"]
        ta_url = config["ta_url"]

        headers = {
            "Authorization": "Token " + ta_key,
            "Accept": "application/json",
        }

        full_url = ta_url + index_name
        print(f"Full URL: {full_url}")
        if keyvalue:
            print(f"Key to extract: {keyvalue}")

        jsonreturn = self._make_request(full_url, headers)

        if keyvalue is None:
            # Return full response for nested object handling
            return jsonreturn

        response = 0
        if jsonreturn is not None:
            try:
                response = jsonreturn[keyvalue]
                if response is None:
                    response = 0
            except KeyError as e:
                print(
                    f"Key '{keyvalue}' not found in response from {full_url}: {e}"
                )

        return response

    def get_list(self, index_name):
        """Get list response from API (for endpoints that return arrays)"""

        config = AppConfig().config
        ta_key = config["ta_key"]
        ta_url = config["ta_url"]

        headers = {
            "Authorization": "Token " + ta_key,
            "Accept": "application/json",
        }

        full_url = ta_url + index_name
        print(f"Full URL: {full_url}")

        response = self._make_request(full_url, headers)

        if response is None:
            return []

        # If it's a list, return it; otherwise return empty list
        if isinstance(response, list):
            return response

        print(f"Expected list from {full_url} but got: {type(response)}")
        return []
