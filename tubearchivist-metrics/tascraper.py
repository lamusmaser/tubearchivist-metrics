# import json
from time import sleep

import requests
from environment import AppConfig

"""
This is a simple wrapper for the TA API. It is used to get stats from
TubeArchivist with efficient single-request-per-endpoint pattern.

Request structure:
1. Build request with URL, headers, and timeout
2. Execute request and check HTTP response status
3. Parse JSON response
4. Extract metrics from response

Error handling (in reverse order of processing):
- Response layer: HTTP status codes
- Parsing layer: JSON decode errors
- Application layer: Missing keys in response
"""


class APIWrapper:

    @staticmethod
    def _make_request(url, headers, timeout=30):
        """
        Make a GET request to the TA API.
        Returns: response dict/list or None on error
        """
        try:
            response = requests.get(url, headers=headers, timeout=timeout)

            # Response layer: Check HTTP status
            if response.status_code < 200 or response.status_code >= 300:
                print(
                    f"Response error from {url}: "
                    f"HTTP {response.status_code}"
                )
                try:
                    print(f"Response body: {response.text}")
                except Exception as e:
                    print(f"Could not retrieve response body: {e}")
                return None

            # Parsing layer: Decode JSON
            try:
                json_response = response.json()
                return json_response
            except ValueError as e:
                print(f"JSON parse error from {url}: {e}")
                print(
                    f"Response received from {url}: {type(response.text).__name__}"  # noqa: E501
                )
                print(f"Response text: {response.text}")
                return None

        except requests.exceptions.RequestException as e:
            # Request layer: Connection, timeout, etc.
            print(f"Request error from {url}: {e}")
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

    def _get_headers(self):
        """Build standard API request headers"""
        config = AppConfig().config
        ta_key = config["ta_key"]

        return {
            "Authorization": "Token " + ta_key,
            "Accept": "application/json",
        }

    def health_check(self):
        """
        Check if TubeArchivist API is healthy.

        Returns:
            True if health check passes, False otherwise
        """
        config = AppConfig().config
        ta_url = config["ta_url"]

        health_url = ta_url + "/api/health/"
        headers = {"Accept": "application/json"}

        print(f"Health check: {health_url}")

        try:
            response = requests.get(health_url, headers=headers, timeout=10)

            if response.status_code < 200 or response.status_code >= 300:
                print(f"Health check failed: HTTP {response.status_code}")
                return False

            # Check response text for "OK" (handles both "OK" and plain OK)
            response_text = response.text.strip()
            if response_text == "OK" or response_text == '"OK"':
                print("Health check passed")
                return True
            else:
                print(f"Health check unexpected response: {response.text}")
                return False

        except requests.exceptions.RequestException as e:
            print(f"Health check request error: {e}")
            return False

    def ping(self):
        """
        Test API ping endpoint and extract TubeArchivist version.

        Returns:
            List of version numbers [major, minor, patch] or None on error
        """
        config = AppConfig().config
        ta_url = config["ta_url"]

        ping_url = ta_url + "/api/ping/"
        headers = self._get_headers()

        print(f"Ping: {ping_url}")

        try:
            response = self._make_request(ping_url, headers)

            if response is None:
                print("Ping request returned no response")
                return None

            # Check for pong response
            if response.get("response") != "pong":
                print(f"Ping response unexpected: {response}")
                return None

            # Extract and parse version
            if "version" not in response:
                print("Ping response missing version field")
                return None

            version_string = response["version"]

            # Parse version string (e.g., "v0.5.3" or "0.5.3")
            try:
                # Strip 'v' prefix if present
                if isinstance(
                    version_string, str
                ) and version_string.startswith("v"):
                    version_string = version_string[1:]

                # Remove unstable suffix if present
                if isinstance(version_string, str):
                    version_string = version_string.rstrip("-unstable")

                # Parse into list of integers
                version_list = [int(x) for x in version_string.split(".")]
                version_display = ".".join(str(x) for x in version_list)
                print(f"TubeArchivist version: {version_display}")
                return version_list
            except (AttributeError, TypeError, ValueError) as e:
                print(
                    f"Could not parse version string '{version_string}': {e}"
                )
                return None

        except Exception as e:
            print(f"Ping request error: {e}")
            return None

    def get_stats_for_endpoint(self, endpoint):
        """
        Make a single request to an endpoint and return the full response.

        Args:
            endpoint: API endpoint path (e.g., "/api/stats/download/")

        Returns:
            dict or list: Full response from API, None on error
        """
        config = AppConfig().config
        ta_url = config["ta_url"]

        full_url = ta_url + endpoint
        headers = self._get_headers()

        print(f"Requesting: {full_url}")

        response = self._make_request(full_url, headers)

        return response

    def extract_metric(self, response, key_path):
        """
        Extract a metric from response using dot-notation key path.

        Args:
            response: Response dict from API
            key_path: Key or dot-notation path
                (e.g., "pending" or "type_videos.doc_count")

        Returns:
            Value or 0 if key not found
        """
        if response is None:
            return 0

        try:
            keys = key_path.split(".")
            value = response

            for key in keys:
                if isinstance(value, dict):
                    # Check if key exists before accessing
                    if key not in value:
                        print(
                            f"Key '{key}' not found in path '{key_path}'. "
                            f"Available keys: {list(value.keys())}"
                        )
                        return 0
                    value = value[key]
                    # Handle None values mid-traversal
                    if value is None:
                        print(
                            f"Key '{key}' in path '{key_path}' has None value."
                            f" Available keys: {list(response.keys())}"
                        )
                        return 0
                else:
                    print(
                        f"Cannot traverse key '{key}' in non-dict value. "
                        f"Current value type: {type(value).__name__}, "
                        f"value: {value}"
                    )
                    return 0

            # Handle final None value
            if value is None:
                return 0

            return value

        except (KeyError, TypeError) as e:
            print(f"Key path '{key_path}' not found in response: {e}")
            return 0

    def is_metric_missing(self, response, key_path):
        """
        Check if a metric is missing or None in the response.

        Args:
            response: Response dict from API
            key_path: Key or dot-notation path

        Returns:
            True if metric is missing or None, False otherwise
        """
        if response is None or not isinstance(response, dict):
            return True

        keys = key_path.split(".")
        current = response

        for key in keys:
            if isinstance(current, dict):
                if key not in current:
                    return True
                current = current.get(key)
            else:
                return True

        return current is None

    def get_count(self, index_name, keyvalue=None):
        """
        Legacy method for backwards compatibility.

        Args:
            index_name: API endpoint
            keyvalue: Key to extract from response

        Returns:
            Extracted value or 0
        """
        response = self.get_stats_for_endpoint(index_name)

        if keyvalue is None:
            return response

        return self.extract_metric(response, keyvalue)

    def get_list(self, index_name):
        """
        Get list response from API (for endpoints that return arrays).

        Args:
            index_name: API endpoint

        Returns:
            List from response or empty list on error
        """
        response = self.get_stats_for_endpoint(index_name)

        if response is None:
            return []

        if isinstance(response, list):
            return response

        print(
            f"Expected list from {index_name} "
            f"but got: {type(response).__name__}"
        )
        return []
