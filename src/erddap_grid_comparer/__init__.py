"""ERDDAP Grid Comparer package."""

from erddap_grid_comparer.erddap_wrapper import ErddapIngestor, GLIDER_URL
from erddap_grid_comparer.glider_data_handler import get_erddap_data_servers

__all__ = [
    "ErddapIngestor",
    "GLIDER_URL",
    "get_erddap_data_servers"
]
