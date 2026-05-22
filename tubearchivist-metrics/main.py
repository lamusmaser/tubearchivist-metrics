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
    def __init__(self, poll_interval=None):
        if poll_interval is None:
            poll_interval = int(config["poll_interval"])

        self.poll_interval = poll_interval

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

    def run_metrics_loop(self):
        """
        Runs a loop that will update the metrics every poll_interval.
        """
        while True:
            self.retrieve_metrics()
            time.sleep(self.poll_interval)

    def retrieve_metrics(self):
        """
        Retrieves the metrics from the database and updates the metrics.
        Makes one request per endpoint and extracts all associated metrics.
        """

        print("Obtaining Metrics from API")

        # Check API health first
        if not GetMetrics.health_check():
            print("API health check failed, skipping metrics collection")
            return

        # Define metrics grouped by endpoint to minimize requests
        endpoints_map = {
            "/api/stats/download/": {
                "pending": self.pending_downloads,
                "ignore": self.ignore_downloads,
                "pending_videos": self.pending_videos,
                "pending_shorts": self.pending_shorts,
                "pending_streams": self.pending_streams,
            },
            "/api/stats/video/": {
                "doc_count": self.videos_total,
                "media_size": self.videos_media_size,
                "duration": self.videos_duration,
                "type_videos.doc_count": self.videos_type_videos_count,
                "type_videos.media_size": self.videos_type_videos_media_size,
                "type_videos.duration": self.videos_type_videos_duration,
                "type_shorts.doc_count": self.videos_type_shorts_count,
                "type_shorts.media_size": self.videos_type_shorts_media_size,
                "type_shorts.duration": self.videos_type_shorts_duration,
                "type_streams.doc_count": self.videos_type_streams_count,
                "type_streams.media_size": self.videos_type_streams_media_size,
                "type_streams.duration": self.videos_type_streams_duration,
                "active_true.doc_count": self.videos_active_true_count,
                "active_true.media_size": self.videos_active_true_media_size,
                "active_true.duration": self.videos_active_true_duration,
                "active_false.doc_count": self.videos_active_false_count,
                "active_false.media_size": self.videos_active_false_media_size,
                "active_false.duration": self.videos_active_false_duration,
            },
            "/api/stats/channel/": {
                "doc_count": self.channel_total,
                "active_true": self.channel_active,
                "active_false": self.channel_inactive,
                "subscribed_true": self.channel_subscribed,
                "subscribed_false": self.channel_unsubscribed,
            },
            "/api/stats/playlist/": {
                "doc_count": self.playlists_total,
                "active_true": self.playlists_active,
                "active_false": self.playlists_inactive,
                "subscribed_true": self.playlists_subscribed,
                "subscribed_false": self.playlists_unsubscribed,
            },
        }

        api_wrapper = GetMetrics.get_wrapper()

        # Process each endpoint with a single request
        for endpoint, metrics_dict in endpoints_map.items():
            response = api_wrapper.get_stats_for_endpoint(endpoint)

            # Extract each metric from the response
            for key_path, gauge in metrics_dict.items():
                value = api_wrapper.extract_metric(response, key_path)
                gauge.set(value)

        # Handle array-based endpoints (biggestchannels, downloadhist)
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

        downloadhist = api_wrapper.get_list(
            index_name="/api/stats/downloadhist/"
        )
        if downloadhist and len(downloadhist) > 0:
            latest = downloadhist[0]
            self.downloadhist_latest_count.set(latest.get("count", 0))
            self.downloadhist_latest_media_size.set(
                latest.get("media_size", 0)
            )


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
