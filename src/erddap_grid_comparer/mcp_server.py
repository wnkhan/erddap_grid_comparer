from typing import Any

from fastmcp import FastMCP

from erddap_grid_comparer import get_erddap_data_servers as list_erddap_data_servers

mcp = FastMCP("erddap-grid-comparer")


@mcp.tool
def get_erddap_data_servers() -> list[dict[str, Any]]:
    """List known ERDDAP data servers available for ocean, glider, gridded, and environmental databases.
    Use this tool when a users asks which ERDDAP servers, data portals, data sources,
    endpoints or providers are available before searching for datasets or retrieving
    oceanographic data.
    """
    return list_erddap_data_servers()

def main():
    mcp.run(
        transport="http",
        host="0.0.0.0",
        port=8000,
        path="/mcp/"
    )

if __name__ == "__main__":
    main()