from tascraper import APIWrapper


class GetMetrics:
    @staticmethod
    def count(index_name, keyvalue=None):
        """Get count of documents from API or full response if keyvalue is None"""
        result = APIWrapper().get_count(index_name, keyvalue)
        return result

    @staticmethod
    def get_list(index_name):
        """Get list response from API (for endpoints that return arrays)"""
        result = APIWrapper().get_list(index_name)
        return result
