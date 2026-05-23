"""
Functionality for setting up the environment for the metrics package.
Reads in environment variables for the application to use.
"""

import os


class AppConfig:
    def __init__(self) -> None:
        self.config = self.get_config()

    @staticmethod
    def get_config():
        """
        Reads in environment variables for the application to use.
        """

        ta_key = os.environ.get("TA_KEY")
        ta_url = os.environ.get("TA_URL")
        listen_port = os.environ.get("LISTEN_PORT", "9934")
        poll_interval = os.environ.get("POLL_INTERVAL", "120")

        # Validate required configuration
        if not ta_url:
            raise ValueError("TA_URL environment variable is required")
        if not ta_key:
            raise ValueError("TA_KEY environment variable is required")

        application = {
            "ta_key": ta_key,
            "ta_url": ta_url,
            "listen_port": listen_port,
            "poll_interval": poll_interval,
        }

        return application
