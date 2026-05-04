import os
import re
from pathlib import Path
from io import BytesIO


import cartopy.crs as ccrs

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from erddap_grid_comparer.mapping import make_map_axes

import pandas as pd
from erddap_grid_comparer.erddap_wrapper import ErddapIngestor, GLIDER_URL
from erddap_grid_comparer.glider_cache import (
    list_grid_labels,
    load_grid_data
)


GLIDER_CACHE_DIR = Path(os.getenv("ERDDAP_GLIDER_CACHE_DIR", "data/glider_grid_cache"))
GRID_LABEL_PATTERN = re.compile(
    r"lat_(?P<lat_min>-?\d+(?:\.\d+)?)_(?P<lat_max>-?\d+(?:\.\d+)?)_"
    r"lon_(?P<lon_min>-?\d+(?:\.\d+)?)_(?P<lon_max>-?\d+(?:\.\d+)?)"
)


def get_glider_datasets() -> pd.DataFrame:
    ingestor = ErddapIngestor(GLIDER_URL)
    return ingestor.dataset_search()[["Title", "Summary", "Institution"]]


def get_glider_dataset_institutions() -> set[str]:
    institutions = list(get_glider_datasets()["Institution"].unique())
    institutions = {insta for row in institutions for insta in row.split(",")}
    return institutions


def _ranges_overlap(first_min: float, first_max: float, second_min: float, second_max: float) -> bool:
    return first_min < second_max and second_min < first_max


def _grid_label_overlaps_bounds(
    grid_label: str,
    lat_min: float,
    lat_max: float,
    lon_min: float,
    lon_max: float,
) -> bool:
    for match in GRID_LABEL_PATTERN.finditer(grid_label):
        grid_lat_min = float(match.group("lat_min"))
        grid_lat_max = float(match.group("lat_max"))
        grid_lon_min = float(match.group("lon_min"))
        grid_lon_max = float(match.group("lon_max"))

        if _ranges_overlap(grid_lat_min, grid_lat_max, lat_min, lat_max) and _ranges_overlap(
            grid_lon_min,
            grid_lon_max,
            lon_min,
            lon_max,
        ):
            return True

    return False


def get_grid_labels(
    lat_min: str | int | float,
    lat_max: str | int | float,
    lon_min: str | int | float,
    lon_max: str | int | float,
) -> list[str]:
    grid_labels = list_grid_labels(GLIDER_CACHE_DIR)
    lat_min_float = float(lat_min)
    lat_max_float = float(lat_max)
    lon_min_float = float(lon_min)
    lon_max_float = float(lon_max)

    if lat_min_float > lat_max_float:
        lat_min_float, lat_max_float = lat_max_float, lat_min_float

    if lon_min_float > lon_max_float:
        lon_min_float, lon_max_float = lon_max_float, lon_min_float

    return [
        grid_label
        for grid_label in grid_labels
        if _grid_label_overlaps_bounds(
            grid_label,
            lat_min_float,
            lat_max_float,
            lon_min_float,
            lon_max_float,
        )
    ]

def build_grid_plot(grid_labels: list[str]):
    #Just process first grid label for now
    grid_label = grid_labels[0]
    lon_col = "precise_lon"
    lat_col = "precise_lat"

    glider_data_df = load_grid_data(GLIDER_CACHE_DIR, grid_label)
    fig, ax, track = make_map_axes(
        glider_data_df, 
        lon_pad=7,
        lat_pad=3
    )

    fig, ax, track = make_map_axes(glider_data_df, lon_pad=7, lat_pad=3)

    ax.plot(track[lon_col], track[lat_col], color="tab:red", linewidth=2, transform=ccrs.PlateCarree())
    ax.scatter(track[lon_col].iloc[0], track[lat_col].iloc[0], color="green", s=60, label="Start", transform=ccrs.PlateCarree())
    ax.scatter(track[lon_col].iloc[-1], track[lat_col].iloc[-1], color="black", s=60, label="End", transform=ccrs.PlateCarree())

    ax.set_title(f"Glider Track: {grid_label}")
    ax.legend()

    buffer = BytesIO()
    fig.savefig(buffer, format="png",bbox_inches="tight", dpi=150)
    plt.close(fig)

    return buffer.getvalue()

if __name__ == "__main__":
    image_bytes = build_grid_plot(get_grid_labels(20, 30, -95, -85))
    with open("glider_grid_paths.png","wb") as image_file:
        image_file.write(image_bytes)
    print("Wrote file for grid label")