import typing
import pandas as pd
import threading
from erddapy import ERDDAP, servers

GLIDER_SERVER_NAME = "ngdac"
GLIDER_URL = str(servers[GLIDER_SERVER_NAME].url)

SERVER_DEFAULTS = {
    "protocol": "tabledap",
    "response": "csv"
}


class ErddapIngestor:

    def __init__(self, server_name):
        self._server_name = server_name
        self._local = threading.local()

    @property
    def e(self):
        return self._get_client()

    def _get_client(self):
        client = getattr(self._local, "client", None)
        if client is None:
            client = ERDDAP(self._server_name, **SERVER_DEFAULTS)
            self._local.client = client
        return client

    @classmethod
    def get_servers(cls) -> list[dict[str,str]]:
        return [{label: server.url} for label, server in servers.items()]
        

    def dataset_search(
        self,
        search_for='"sound speed" salinity temp',
        *,
        min_lat=None,
        max_lat=None,
        min_lon=None,
        max_lon=None,
        protocol=None,
        response="csv",
        **search_filters,
    ):
        """Search the glider ERDDAP catalog and return the results as a DataFrame."""
        bounds = {
            "min_lat": min_lat,
            "max_lat": max_lat,
            "min_lon": min_lon,
            "max_lon": max_lon,
        }
        search_params = {
            key: value
            for key, value in bounds.items()
            if value is not None
        }
        search_params.update(search_filters)

        client = self._get_client()
        url = client.get_search_url(
            search_for=search_for,
            response=response,
            protocol=protocol,
            **search_params,
        )
        return pd.read_csv(url).drop_duplicates()

    def get_dataset_metadata(self, dataset_id):
        client = self._get_client()
        target_dataset_id = dataset_id if dataset_id else client.dataset_id
        return pd.read_csv(client.get_info_url(target_dataset_id))


    def get_dataset(self, dataset_id, variables):
        client = self._get_client()
        client.dataset_id = dataset_id
        return pd.read_csv(client.get_download_url(variables=variables))
