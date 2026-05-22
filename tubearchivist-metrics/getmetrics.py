from tascraper import APIWrapper


class GetMetrics:
    _wrapper = None

    @staticmethod
    def get_wrapper():
        """Get or create the APIWrapper instance"""
        if GetMetrics._wrapper is None:
            GetMetrics._wrapper = APIWrapper()
        return GetMetrics._wrapper

    @staticmethod
    def health_check():
        """Check if TubeArchivist API is healthy"""
        wrapper = GetMetrics.get_wrapper()
        return wrapper.health_check()

    @staticmethod
    def count(index_name, keyvalue=None):
        """
        Get count of documents from API
        or full response if keyvalue is None
        """
        wrapper = GetMetrics.get_wrapper()
        return wrapper.get_count(index_name, keyvalue)

    @staticmethod
    def get_list(index_name):
        """Get list response from API (for endpoints that return arrays)"""
        wrapper = GetMetrics.get_wrapper()
        return wrapper.get_list(index_name)
