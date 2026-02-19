#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Converted from Jupyter notebook: Read_ICESat-2_projection_drift_correct.ipynb

This script provides utilities to:
  1) Project ICESat-2 (lon,lat) points to EPSG:3413
  2) Apply drift correction using velocities (vx, vy) and a reference time (delta_time)
  3) Optionally write CSV and GeoPackage outputs
  4) Convert between UTC timestamps and ICESat-2 delta_time (seconds since 2018-01-01 GPS)
"""

from __future__ import annotations

import argparse
from pathlib import Path
import numpy as np
import pandas as pd
from pyproj import CRS, Transformer

# For geometry output
import geopandas as gpd
from shapely.geometry import Point

#!/usr/bin/env python3
"""
Read a comma-separated TXT file with columns:
  lon, lat, time, ele
Project lon/lat (EPSG:4326) to x/y in EPSG:3413,
apply constant drift correction (vx, vy),
and store drift-corrected coordinates as Point geometry.

Usage:
  python project_txt_to_3413_drift.py input.txt --vx 12.3 --vy -45.6
  python project_txt_to_3413_drift.py input.txt --vx 12.3 --vy -45.6 --out_csv out.csv --out_gpkg out.gpkg
"""

def project_txt(
    in_txt: str,
    vx: float = 0.0,
    vy: float = 0.0,
    delta_time: float = 0.0,
    out_csv: str | None = None,
    out_txt: str | None = None,
    out_gpkg: str | None = None,
    save_csv: bool = True,
    save_txt: bool = False,
    save_gpkg: bool = False,
) -> tuple[Path, Path | None]:
    in_path = Path(in_txt)

    # Default output paths
    if out_csv is None:
        out_csv_path = in_path.with_suffix("").with_name(in_path.stem + "_epsg3413_drift_plus_dx_02172026.csv")
    else:
        out_csv_path = Path(out_csv)
    
    if out_txt is None:
        out_txt_path = in_path.with_suffix("").with_name(in_path.stem + "_epsg3413_drift_xy_plus_dx_02172026.txt")
    else:
        out_txt_path = Path(out_txt)

    if out_gpkg is None:
        out_gpkg_path = in_path.with_suffix("").with_name(in_path.stem + "_epsg3413_drift.gpkg")
    else:
        out_gpkg_path = Path(out_gpkg)

    # Read: lon, lat, time, ele (comma-separated, no header)
    df = pd.read_csv(
        in_path,
        header=None,
        names=["lon", "lat", "time", "ele"],
        sep=",",
        engine="c",
        comment="#",
        skip_blank_lines=True,
    )

    # Ensure numeric (robust to stray whitespace)
    for c in ["lon", "lat", "time", "ele"]:
        df[c] = pd.to_numeric(df[c], errors="coerce")

    # Drop rows that can't be projected
    valid = np.isfinite(df["lon"].to_numpy()) & np.isfinite(df["lat"].to_numpy())
    df = df.loc[valid].reset_index(drop=True)

    # Project lon/lat to EPSG:3413
    transformer = Transformer.from_crs(
        CRS.from_epsg(4326),  # WGS84 lon/lat
        CRS.from_epsg(3413),  # NSIDC Sea Ice Polar Stereographic North
        always_xy=True
    )

    lon = df["lon"].to_numpy(dtype=np.float64)
    lat = df["lat"].to_numpy(dtype=np.float64)
    x_3413, y_3413 = transformer.transform(lon, lat)

    df["x_3413"] = x_3413
    df["y_3413"] = y_3413

    # ---- Drift correction (constant offsets, in same units as EPSG:3413, i.e., meters) ----
    t = df["time"].to_numpy(dtype=np.float64)
    dt = t - delta_time  # seconds since reference
    df["x_3413_dc"] = df["x_3413"] - vx * dt
    df["y_3413_dc"] = df["y_3413"] - vy * dt

    # Quick sanity prints
    print(f"Read {len(df):,} valid rows from: {in_path}")
    print(f"Drift velocity: vx={vx} m/s, vy={vy} m/s")
    print(f"X_3413 range:    {np.nanmin(df['x_3413']):.3f} to {np.nanmax(df['x_3413']):.3f}")
    print(f"Y_3413 range:    {np.nanmin(df['y_3413']):.3f} to {np.nanmax(df['y_3413']):.3f}")
    print(f"X_3413_dc range: {np.nanmin(df['x_3413_dc']):.3f} to {np.nanmax(df['x_3413_dc']):.3f}")
    print(f"Y_3413_dc range: {np.nanmin(df['y_3413_dc']):.3f} to {np.nanmax(df['y_3413_dc']):.3f}")

    # Save CSV
    # df.to_csv(out_csv_path, index=False)
    if save_csv:
        cols_out = ["x_3413_dc", "y_3413_dc", "ele"]
        df_out = df[cols_out]

        df_out.to_csv(out_csv_path, index=False)
        print(f"Wrote CSV:  {out_csv_path}")

    # Save txt with only x and y, and the first row specifies the number of points
    if save_txt:
        write_xy_count_txt(out_txt_path, df["x_3413_dc"], df["y_3413_dc"])
        print(f"Wrote XY TXT: {out_txt_path}")

    # ---- Geometry output (Point from drift-corrected coordinates) ----
    # Use GeoPandas + Shapely points; CRS must match the coordinates (EPSG:3413)
    # gdf = gpd.GeoDataFrame(
    #     df,
    #     geometry=gpd.points_from_xy(df["x_3413_dc"], df["y_3413_dc"]),
    #     crs="EPSG:3413"
    # )
    if save_csv and save_gpkg:
        gdf = gpd.GeoDataFrame(
            df_out.copy(),
            geometry=gpd.points_from_xy(df_out["x_3413_dc"], df_out["y_3413_dc"]),
            crs="EPSG:3413"
        )

        # Write to GeoPackage (recommended) - works well in QGIS/ArcGIS
        # Layer name can be customized; default "points"
        gdf.to_file(out_gpkg_path, layer="points", driver="GPKG")
        print(f"Wrote GPKG: {out_gpkg_path}")

    return out_csv_path

def write_xy_count_txt(out_txt: str | Path, x: np.ndarray, y: np.ndarray, fmt: str = "%.6f") -> Path:
    """
    Write a TXT file:
      line 1: number of points (N)
      lines 2..N+1: "x y" per line

    Args:
      out_txt: output path
      x, y: 1D arrays of same length
      fmt: float format for x/y
    """
    out_txt = Path(out_txt)
    x = np.asarray(x).ravel()
    y = np.asarray(y).ravel()
    if x.size != y.size:
        raise ValueError(f"x and y length mismatch: {x.size} vs {y.size}")

    N = x.size
    with out_txt.open("w", newline="\n") as f:
        f.write(f"{N}\n")
        # write one point per line
        for xi, yi in zip(x, y):
            f.write((fmt % xi) + " " + (fmt % yi) + "\n")

    return out_txt

from datetime import datetime, timedelta, timezone

def utc_to_icesat2_epoch(
    utc_time_str: str,
    time_format: str = "%Y%m%dT%H%M%S",
    gps_minus_utc: int = 18
) -> float:
    """
    Convert UTC time string to ICESat-2 delta_time
    (seconds since 2018-01-01 00:00:00 GPS time).

    Parameters
    ----------
    utc_time_str : str
        UTC time string (e.g., "20190410T174554")
    time_format : str
        Format string for datetime.strptime (default: "%Y%m%dT%H%M%S")
    gps_minus_utc : int
        Leap seconds (GPS - UTC). 
        Use 18 for years 2017–present (valid for 2019 data).

    Returns
    -------
    float
        ICESat-2 delta_time in seconds
    """

    # 1) Parse UTC time
    utc_time = datetime.strptime(utc_time_str, time_format).replace(tzinfo=timezone.utc)

    # 2) Convert UTC -> GPS (add leap seconds)
    gps_time = utc_time + timedelta(seconds=gps_minus_utc)

    # 3) ATLAS SDP epoch (GPS time reference)
    atlas_epoch = datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # 4) Compute delta_time
    delta_time = (gps_time - atlas_epoch).total_seconds()

    return delta_time

# als_time_str = "20190410T174554"
# print("ICESat-2 delta_time:", utc_to_icesat2_epoch(als_time_str))

def icesat2_epoch_to_utc(
    delta_time: float,
    gps_minus_utc: int = 18
) -> datetime:
    """
    Convert ICESat-2 delta_time (seconds since 2018-01-01 GPS)
    to UTC datetime.

    Parameters
    ----------
    delta_time : float
        ICESat-2 delta_time (seconds since 2018-01-01 GPS epoch)
    gps_minus_utc : int
        Leap seconds (GPS - UTC). 
        Use 18 for 2018–present.

    Returns
    -------
    datetime
        UTC datetime object
    """

    # 1) ATLAS GPS epoch
    atlas_epoch = datetime(2018, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

    # 2) Convert delta_time -> GPS time
    gps_time = atlas_epoch + timedelta(seconds=delta_time)

    # 3) Convert GPS -> UTC (subtract leap seconds)
    utc_time = gps_time - timedelta(seconds=gps_minus_utc)

    return utc_time
    
# print("UTC time:", icesat2_epoch_to_utc(40153572.0))

def _build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Project lon/lat to EPSG:3413, drift-correct using velocities, and export outputs."
    )
    p.add_argument("in_txt", help="Input TXT/CSV (comma-separated) with columns: lon,lat,time,ele (no header)")

    p.add_argument("--vx", type=float, default=0.0, help="x velocity (m/s)")
    p.add_argument("--vy", type=float, default=0.0, help="y velocity (m/s)")
    p.add_argument(
        "--tref", "--delta_time",
        dest="delta_time",
        type=float,
        default=0.0,
        help="Reference time (seconds since 2018-01-01 00:00:00 GPS) used in dt = time - tref"
    )

    # Output paths
    p.add_argument("--out_csv", default=None, help="Output CSV path (optional)")
    p.add_argument("--out_txt", default=None, help="Output XY TXT path (first line N, then 'x y')")
    p.add_argument("--out_gpkg", default=None, help="Output GeoPackage path (optional)")

    # What to write
    p.add_argument("--no_csv", action="store_true", help="Do not write CSV")
    p.add_argument("--save_txt", action="store_true", help="Write XY TXT")
    p.add_argument("--save_gpkg", action="store_true", help="Write GeoPackage")

    return p

def main() -> int:
    # parser = _build_arg_parser()
    # args = parser.parse_args()
    # project_txt(
    #     in_txt=args.in_txt,
    #     vx=args.vx,
    #     vy=args.vy,
    #     delta_time=args.delta_time,
    #     out_csv=args.out_csv,
    #     out_gpkg=args.out_gpkg,
    # )
    # return 0

    in_txt = 'C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/UMD_elevation_data/strong_beam/UMDRDA_ATL03_20190410152144_01890303_007_01_gt2l_DTU21_Elevation.txt'
    vx = -0.02078199
    vy = 0.0035027
    delta_time = 40151271.76974

    project_txt(
        in_txt,
        vx,
        vy,
        delta_time,
        save_csv=True,
        save_txt=True,
    )

if __name__ == '__main__':
    raise SystemExit(main())
