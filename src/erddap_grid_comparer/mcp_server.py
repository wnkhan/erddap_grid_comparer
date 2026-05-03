from typing import Any

from fastmcp import FastMCP

from erddap_grid_comparer.erddap_wrapper import ErddapIngestor 
from erddap_grid_comparer.glider_data_handler import get_glider_datasets, get_glider_dataset_institutions

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
    return get_glider_datasets().to_dict(orient='records')

@mcp.tool
def get_glider_data_institutions() -> set[str]:
    """List institutions associated with available glider datasets.

    Use this tool when a user asks which organizations, institutions, or data
    providers are represented in the glider dataset catalog.
    """
    return get_glider_dataset_institutions()


def main():
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp/"
    )

if __name__ == "__main__":
    main()
