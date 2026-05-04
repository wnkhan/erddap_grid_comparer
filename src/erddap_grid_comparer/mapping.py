import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def make_map_axes(source_df, lon_pad=0.2, lat_pad=0.2, figsize=(10, 8)):

    lon_col = next(column for column in source_df.columns if column.lower().startswith("precise_lon"))
    lat_col = next(column for column in source_df.columns if column.lower().startswith("precise_lat"))

    track = source_df[[lon_col, lat_col]].dropna()

    for col in track.columns:
        track[col] = track[col].astype(float)

    fig = plt.figure(figsize=figsize)
    ax= plt.axes(projection=ccrs.PlateCarree())
    ax.set_extent([ # type: ignore
        track[lon_col].min() - lon_pad,
        track[lon_col].max() + lon_pad,
        track[lat_col].min() - lat_pad,
        track[lat_col].max() + lat_pad,
    ], crs=ccrs.PlateCarree())

    ax.add_feature(cfeature.LAND, facecolor="0.9") # type: ignore
    ax.add_feature(cfeature.OCEAN, facecolor="lightblue") # type: ignore
    ax.coastlines(resolution="10m") # type: ignore
    ax.add_feature(cfeature.BORDERS, linestyle=":") # type: ignore
    gridlines = ax.gridlines(draw_labels=True, linestyle="--", alpha=0.5) # type: ignore
    gridlines.top_labels = False
    gridlines.right_labels = False

    return fig, ax, track