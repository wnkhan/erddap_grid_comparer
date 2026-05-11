from typing import Self
import matplotlib.pyplot as plt
from matplotlib.axes import Axes
from matplotlib.figure import Figure
import cartopy.crs as ccrs
import cartopy.feature as cfeature

import pandas as pd

class PlotBuilder:
    def __init__(
            self, 
            source_df: pd.DataFrame,
            from_vehicle=False,
            lon_pad=3,
            lat_pad=3,
            fig_size=(10,8),
            track_col_names: list = ('precise_lon','precise_lat')
    ):
        self.source_df = source_df
        self.from_vehicle = from_vehicle
        self.lon_pad=lon_pad
        self.lat_pad=lat_pad
        self.fig_size=fig_size
        self.track_col_names = track_col_names 
        self.fig = None
        self.ax = None
        self.track = None

    def configure_axes(self) -> Self:

        self.fig = plt.figure(figsize=self.fig_size)
        self.ax = plt.axes(projection=ccrs.PlateCarree())

        lat_col = next(column for column in self.track_col_names if 'lat' in column.lower())
        lon_col = next(column for column in self.track_col_names if 'lon' in column.lower())

        self.track = self.source_df[[lon_col, lat_col]].dropna()

        for col in self.track.columns:
            self.track[col] = self.track[col].astype(float)

        self.ax.set_extent([ # type: ignore
            self.track[lon_col].min() - self.lon_pad,
            self.track[lon_col].max() + self.lon_pad,
            self.track[lat_col].min() - self.lat_pad,
            self.track[lat_col].max() + self.lat_pad,
        ], crs=ccrs.PlateCarree())

        return self

    def add_layers(self) -> Self:
        
        self.ax.add_feature(cfeature.LAND, facecolor="0.9") # type: ignore
        self.ax.add_feature(cfeature.OCEAN, facecolor="lightblue") # type: ignore
        self.ax.coastlines(resolution="10m") # type: ignore
        self.ax.add_feature(cfeature.BORDERS, linestyle=":") # type: ignore
        gridlines = self.ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5) # type: ignore
        gridlines.top_labels = False
        gridlines.right_labels = False

        return self

    def add_track(self, track_title: str) -> Self:
        lat_col = next(column for column in self.track_col_names if 'lat' in column.lower())
        lon_col = next(column for column in self.track_col_names if 'lon' in column.lower())

        if(self.from_vehicle):
            self.ax.plot(self.track[lon_col], self.track[lat_col], color="tab:red", linewidth=2, transform=ccrs.PlateCarree())
            self.ax.scatter(self.track[lon_col].iloc[0], self.track[lat_col].iloc[0], color="green", s=60, label="Start", transform=ccrs.PlateCarree())
            self.ax.scatter(self.track[lon_col].iloc[-1], self.track[lat_col].iloc[-1], color="black", s=60, label="End", transform=ccrs.PlateCarree())
        else:
            self.ax.scatter(self.track[lon_col], self.track[lat_col], color="tab:red", linewidth=2, transform=ccrs.PlateCarree())

        self.ax.set_title(track_title)
        self.ax.legend()

        return self

    def build(self) -> tuple[Figure, Axes]:
        return self.fig, self.ax, self.track
