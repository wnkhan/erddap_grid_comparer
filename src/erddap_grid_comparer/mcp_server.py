from typing import Any
import json

from fastmcp import FastMCP
from fastmcp.utilities.types import Image

from erddap_grid_comparer.erddap_wrapper import ErddapIngestor
from erddap_grid_comparer.glider_data_handler import (
    get_glider_dataset_institutions,
    get_glider_datasets,
    get_grid_labels,
    build_grid_plot,
    get_grid_summary_data
)

mcp = FastMCP("erddap-grid-comparer")


@mcp.tool
def get_erddap_data_servers() -> list[dict[str, Any]]:
    """List known ERDDAP data servers available for ocean, glider, gridded, and environmental databases.
    Use this tool when a users asks which ERDDAP servers, data portals, data sources,
    endpoints or providers are available before searching for datasets or retrieving
    oceanographic data.
    """
    return ErddapIngestor.get_servers()


@mcp.tool
def get_glider_data() -> list[dict[Any, Any]]:
    """List available glider datasets from the configured ERDDAP glider data source.

    Use this tool when a user asks to search, browse, or inspect known glider
    datasets and their associated metadata.
    """
    return get_glider_datasets().to_dict(orient="records")


@mcp.tool
def get_glider_data_institutions() -> set[str]:
    """List institutions associated with available glider datasets.

    Use this tool when a user asks which organizations, institutions, or data
    providers are represented in the glider dataset catalog.
    """
    return get_glider_dataset_institutions()


@mcp.tool
def search_glider_grid_labels(
    lat_min: str | int | float,
    lat_max: str | int | float,
    lon_min: str | int | float,
    lon_max: str | int | float,
) -> list[str]:
    """Search cached glider grid labels that overlap a latitude/longitude bounding box.

    Use this tool when a user asks which cached glider grid cells are available
    for a region, bounding box, latitude range, longitude range, or map extent.
    The latitude and longitude arguments may be strings or numbers and are
    interpreted as decimal degrees.
    """
    return get_grid_labels(lat_min, lat_max, lon_min, lon_max)


@mcp.tool
def plot_glider_grid_paths(grid_labels: list[str]):
    """Plot glider paths given a grid label

    Use this tool after getting the grid labels that correspond to the glider paths within a
    grid label to display the glider tracks within that grid. The inputs to this tool are the grid_labels
    extracted by the search_glider_grid_labels tool. This tool will retrun the grid_label along with the associated
    plot.
    """
    return [
        Image(data=build_grid_plot(grid_labels), format="png"),
        json.dumps(get_grid_summary_data(grid_labels), indent=2)
    ]


def main():
    mcp.run(transport="http", host="0.0.0.0", port=8000, path="/mcp/")


if __name__ == "__main__":
    main()
