import time

from environment import AppConfig
from getmetrics import GetMetrics
from prometheus_client import Gauge, start_http_server

config = AppConfig().config

# Print configuration on console when starting the application

print("Configuration is currently set to:")
print(f'TA URL: {config["ta_url"]}')
print(f'Listen Port: {config["listen_port"]}')
print(f'Polling interval (seconds): {config["poll_interval"]}')


class AppMetrics:
    # Endpoint configuration mapping endpoint name to path and metrics
    ENDPOINTS_MAP = {
        "download": {
            "path": "/api/stats/download/",
            "metrics": {
                "pending": "pending_downloads",
                "ignore": "ignore_downloads",
                "pending_videos": "pending_videos",
                "pending_shorts": "pending_shorts",
                "pending_streams": "pending_streams",
            },
        },
        "video": {
            "path": "/api/stats/video/",
            "metrics": {
                "doc_count": "videos_total",
                "media_size": "videos_media_size",
                "duration": "videos_duration",
                "type_videos.doc_count": "videos_type_videos_count",
                "type_videos.media_size": "videos_type_videos_media_size",
                "type_videos.duration": "videos_type_videos_duration",
                "type_shorts.doc_count": "videos_type_shorts_count",
                "type_shorts.media_size": "videos_type_shorts_media_size",
                "type_shorts.duration": "videos_type_shorts_duration",
                "type_streams.doc_count": "videos_type_streams_count",
                "type_streams.media_size": "videos_type_streams_media_size",
                "type_streams.duration": "videos_type_streams_duration",
                "active_true.doc_count": "videos_active_true_count",
                "active_true.media_size": "videos_active_true_media_size",
                "active_true.duration": "videos_active_true_duration",
                "active_false.doc_count": "videos_active_false_count",
                "active_false.media_size": "videos_active_false_media_size",
                "active_false.duration": "videos_active_false_duration",
            },
        },
        "channel": {
            "path": "/api/stats/channel/",
            "metrics": {
                "doc_count": "channel_total",
                "active_true": "channel_active",
                "active_false": "channel_inactive",
                "subscribed_true": "channel_subscribed",
                "subscribed_false": "channel_unsubscribed",
            },
        },
        "playlist": {
            "path": "/api/stats/playlist/",
            "metrics": {
                "doc_count": "playlists_total",
                "active_true": "playlists_active",
                "active_false": "playlists_inactive",
                "subscribed_true": "playlists_subscribed",
                "subscribed_false": "playlists_unsubscribed",
            },
        },
    }

    def __init__(self, poll_interval=None):
        if poll_interval is None:
            poll_interval = int(config["poll_interval"])

        self.poll_interval = poll_interval
        self.version = None  # Will be set during health check

        # Metrics to expose

        self.ignore_downloads = Gauge(
            "yta_ignore_downloads", "Total number of ignored videos"
        )
        self.pending_downloads = Gauge(
            "yta_pending_downloads", "Total number of pending downloads"
        )
        self.pending_videos = Gauge(
            "yta_pending_videos", "Total number of pending video downloads"
        )
        self.pending_shorts = Gauge(
            "yta_pending_shorts", "Total number of pending shorts downloads"
        )
        self.pending_streams = Gauge(
            "yta_pending_streams", "Total number of pending stream downloads"
        )
        """
         These 3 are sub, sub bits of the tree.
         I've done all this in a really hacky way
         that only supports a depth of 1,
         ideally needs a full rewrite

         self.watch_total = Gauge("yta_watch_total", "Total number of Videos")
         self.watch_unwatched = Gauge(
         "yta_watch_unwatched", "Total number of unwatched videos"
         )
         self.watch_watched = Gauge(
         "yta_watch_watched", "Total number of watched videos"
         )
        """
        self.videos_total = Gauge("yta_videos_total", "Total number of videos")

        self.channel_total = Gauge(
            "yta_channel_total", "Total number of channels"
        )
        self.channel_active = Gauge(
            "yta_channel_active", "Total number of active channels"
        )
        self.channel_inactive = Gauge(
            "yta_channel_inactive", "Total number of inactive channels"
        )
        self.channel_subscribed = Gauge(
            "yta_channel_subscribed", "Total number of subscribed channels"
        )
        self.channel_unsubscribed = Gauge(
            "yta_channel_unsubscribed", "Total number of unsubscribed channels"
        )

        self.playlists_total = Gauge(
            "yta_playlists_total", "Total number of playlists"
        )
        self.playlists_active = Gauge(
            "yta_playlists_active", "Total number of active playlists"
        )
        self.playlists_inactive = Gauge(
            "yta_playlists_inactive", "Total number of inactive playlists"
        )
        self.playlists_subscribed = Gauge(
            "yta_playlists_subscribed", "Total number of subscribed playlists"
        )
        self.playlists_unsubscribed = Gauge(
            "yta_playlists_unsubscribed",
            "Total number of unsubscribed playlists",
        )

        # Video stats with nested breakdown
        self.videos_media_size = Gauge(
            "yta_videos_media_size", "Total media size of videos"
        )
        self.videos_duration = Gauge(
            "yta_videos_duration", "Total duration of videos"
        )
        self.videos_type_videos_count = Gauge(
            "yta_videos_type_videos_count", "Total video type count"
        )
        self.videos_type_videos_media_size = Gauge(
            "yta_videos_type_videos_media_size", "Total video type media size"
        )
        self.videos_type_videos_duration = Gauge(
            "yta_videos_type_videos_duration", "Total video type duration"
        )
        self.videos_type_shorts_count = Gauge(
            "yta_videos_type_shorts_count", "Total shorts type count"
        )
        self.videos_type_shorts_media_size = Gauge(
            "yta_videos_type_shorts_media_size", "Total shorts type media size"
        )
        self.videos_type_shorts_duration = Gauge(
            "yta_videos_type_shorts_duration", "Total shorts type duration"
        )
        self.videos_type_streams_count = Gauge(
            "yta_videos_type_streams_count", "Total streams type count"
        )
        self.videos_type_streams_media_size = Gauge(
            "yta_videos_type_streams_media_size",
            "Total streams type media size",
        )
        self.videos_type_streams_duration = Gauge(
            "yta_videos_type_streams_duration", "Total streams type duration"
        )
        self.videos_active_true_count = Gauge(
            "yta_videos_active_true_count", "Total active videos count"
        )
        self.videos_active_true_media_size = Gauge(
            "yta_videos_active_true_media_size",
            "Total active videos media size",
        )
        self.videos_active_true_duration = Gauge(
            "yta_videos_active_true_duration", "Total active videos duration"
        )
        self.videos_active_false_count = Gauge(
            "yta_videos_active_false_count", "Total inactive videos count"
        )
        self.videos_active_false_media_size = Gauge(
            "yta_videos_active_false_media_size",
            "Total inactive videos media size",
        )
        self.videos_active_false_duration = Gauge(
            "yta_videos_active_false_duration",
            "Total inactive videos duration",
        )

        # Biggest channels (latest entry)
        self.biggest_channels_latest_count = Gauge(
            "yta_biggest_channels_latest_count",
            "Latest biggest channel doc count",
        )
        self.biggest_channels_latest_duration = Gauge(
            "yta_biggest_channels_latest_duration",
            "Latest biggest channel duration",
        )
        self.biggest_channels_latest_media_size = Gauge(
            "yta_biggest_channels_latest_media_size",
            "Latest biggest channel media size",
        )

        # Download history (latest entry)
        self.downloadhist_latest_count = Gauge(
            "yta_downloadhist_latest_count", "Latest download history count"
        )
        self.downloadhist_latest_media_size = Gauge(
            "yta_downloadhist_latest_media_size",
            "Latest download history media size",
        )

        # Health metrics per endpoint
        self.endpoint_health = {}
        self.endpoint_names = [
            "download",
            "video",
            "channel",
            "playlist",
        ]
        for endpoint_name in self.endpoint_names:
            self.endpoint_health[endpoint_name] = Gauge(
                f"yta_endpoint_{endpoint_name}_unavailable",
                f"Number of unavailable metrics from {endpoint_name} endpoint",
            )

    def _get_gauge(self, gauge_name):
        """Get gauge object by attribute name."""
        return getattr(self, gauge_name)

    def _get_endpoint_metrics(self, endpoint_name):
        """
        Get the actual gauge objects for an endpoint's metrics.

        Args:
            endpoint_name: Name of endpoint (e.g., "video")

        Returns:
            dict: Mapping of key_path to gauge objects
        """
        endpoint_config = self.ENDPOINTS_MAP[endpoint_name]
        metrics_dict = {}

        for key_path, gauge_attr in endpoint_config["metrics"].items():
            metrics_dict[key_path] = self._get_gauge(gauge_attr)

        return metrics_dict

    def _process_array_endpoints(self, api_wrapper):
        """
        Process array-based endpoints (biggestchannels, downloadhist).

        Args:
            api_wrapper: APIWrapper instance
        """
        # Handle biggestchannels
        biggestchannels = api_wrapper.get_list(
            index_name="/api/stats/biggestchannels/"
        )
        if biggestchannels and len(biggestchannels) > 0:
            latest = biggestchannels[0]
            self.biggest_channels_latest_count.set(latest.get("doc_count", 0))
            self.biggest_channels_latest_duration.set(
                latest.get("duration", 0)
            )
            self.biggest_channels_latest_media_size.set(
                latest.get("media_size", 0)
            )

        # Handle downloadhist
        downloadhist = api_wrapper.get_list(
            index_name="/api/stats/downloadhist/"
        )
        if downloadhist and len(downloadhist) > 0:
            latest = downloadhist[0]
            self.downloadhist_latest_count.set(latest.get("count", 0))
            self.downloadhist_latest_media_size.set(
                latest.get("media_size", 0)
            )

    def run_metrics_loop(self):
        """
        Runs a loop that will update the metrics every poll_interval.
        """
        retry_count = 0
        max_retries = 5
        retry_delay = 10  # seconds

        while retry_count < max_retries:
            try:
                # Try to get initial metrics
                if GetMetrics.health_check():
                    # Get version on successful health check
                    self.version = GetMetrics.ping()
                    if self.version:
                        print(f"API version detected: {self.version}")
                    self.retrieve_metrics()
                    print("Initial metrics collection successful")
                    break
                else:
                    raise Exception("Health check failed")
            except Exception as e:
                retry_count += 1
                if retry_count < max_retries:
                    print(
                        f"Metrics collection failed (attempt {retry_count}"
                        f"/{max_retries}), retrying in {retry_delay}s: {e}"
                    )
                    time.sleep(retry_delay)
                    retry_delay = min(
                        retry_delay * 2, 60
                    )  # Exponential backoff, max 60s
                else:
                    print(
                        f"Metrics collection failed after {max_retries} "
                        f"attempts, continuing anyway: {e}"
                    )

        # Main loop
        while True:
            try:
                self.retrieve_metrics()
            except Exception as e:
                print(f"Error in metrics collection loop: {e}")

            time.sleep(self.poll_interval)

    def retrieve_metrics(self):
        """
        Retrieves the metrics from the database and updates the metrics.
        Makes one request per endpoint and extracts all associated metrics.
        """

        print(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')}| Obtaining Metrics from API"
        )

        # Check API health first
        if not GetMetrics.health_check():
            print(
                f"{time.strftime('%Y-%m-%d %H:%M:%S')}| API health check failed, skipping metrics collection"  # noqa: E501
            )
            return

        # Get version if not already set
        if self.version is None:
            self.version = GetMetrics.ping()
            if self.version:
                print(f"API version detected: {self.version}")

        api_wrapper = GetMetrics.get_wrapper()

        # Process each endpoint
        for endpoint_name in self.endpoint_names:
            self._process_endpoint(api_wrapper, endpoint_name)

        # Process array-based endpoints
        self._process_array_endpoints(api_wrapper)

        print(
            f"{time.strftime('%Y-%m-%d %H:%M:%S')}| Metrics collection completed successfully"  # noqa: E501
        )

    def _process_endpoint(self, api_wrapper, endpoint_name):
        """
        Process a single endpoint and update its metrics.

        Args:
            api_wrapper: APIWrapper instance
            endpoint_name: Name of endpoint (e.g., "video")
        """
        endpoint_config = self.ENDPOINTS_MAP[endpoint_name]
        endpoint_path = endpoint_config["path"]
        metrics_dict = self._get_endpoint_metrics(endpoint_name)
        unavailable_count = 0

        response = api_wrapper.get_stats_for_endpoint(endpoint_path)

        # Extract each metric from the response
        for key_path, gauge in metrics_dict.items():
            value, was_missing = api_wrapper.extract_metric(response, key_path)

            # Track metrics that are unavailable
            if was_missing:
                unavailable_count += 1

            gauge.set(value)

        # Update endpoint health metric
        self.endpoint_health[endpoint_name].set(unavailable_count)


def main():
    """Main Entry Point"""
    listen_port = int(config["listen_port"])
    poll_interval = int(config["poll_interval"])

    app_metrics = AppMetrics(
        poll_interval=poll_interval,
    )
    start_http_server(listen_port)
    app_metrics.run_metrics_loop()


if __name__ == "__main__":
    main()
