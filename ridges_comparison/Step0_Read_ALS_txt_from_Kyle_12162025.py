#!/usr/bin/env python3
import sys
import numpy as np
import xarray as xr
from pyproj import CRS, Transformer
from scipy import stats
import csv
from pathlib import Path
import time

def interp_mss_chunked(mss_da, lon_name, lat_name, lon_arr, lat_arr,
                       block=2_000_000, method="linear"):
    """Interpolate MSS values for large arrays in chunks (from your prior code)."""
    out = np.empty(lon_arr.size, dtype=np.float64)
    for i in range(0, lon_arr.size, block):
        j = min(i + block, lon_arr.size)
        out[i:j] = mss_da.interp(
            {lon_name: xr.DataArray(lon_arr[i:j], dims="p"),
             lat_name: xr.DataArray(lat_arr[i:j], dims="p")},
            method=method
        ).values
    return out

def load_dtu21_mss(dtu_nc_path):
    ds_mss = xr.open_dataset(dtu_nc_path)

    lon_name = [k for k in ds_mss.coords if k.lower().startswith("lon")][0]
    lat_name = [k for k in ds_mss.coords if k.lower().startswith("lat")][0]
    var_name = [k for k in ds_mss.data_vars
                if ("mss" in k.lower() or "mean_sea" in k.lower())][0]

    mss_da = ds_mss[var_name]
    units = str(mss_da.attrs.get("units", "")).lower()

    ds_lons = ds_mss[lon_name].values
    dataset_is_0360 = (np.nanmin(ds_lons) >= 0.0) and (np.nanmax(ds_lons) <= 360.0)

    return mss_da, lon_name, lat_name, units, dataset_is_0360

def correct_txt_with_dtu21mss(
    input_txt,
    output_xyz,
    dtu_nc_path=r"C:\Users\yhqian\AppData\Local\GeographicLib\DTU21MSS_1min_WGS84.nc",
    block=2_000_000
):
    # Load DTU21MSS grid once
    mss_da, lon_name, lat_name, units, dataset_is_0360 = load_dtu21_mss(dtu_nc_path)

    # --- Pass 1: read lon/lat/z_raw into arrays (fast, simple) ---
    lon_list, lat_list, zraw_list = [], [], []
    with open(input_txt, "r") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            parts = line.split(",")
            if len(parts) < 4:
                continue  # or raise an error if you prefer strict parsing

            lon = float(parts[0])
            lat = float(parts[1])
            z_raw = float(parts[3])  # 4th column in your TXT

            lon_list.append(lon)
            lat_list.append(lat)
            zraw_list.append(z_raw)

    lon = np.asarray(lon_list, dtype=np.float64)
    lat = np.asarray(lat_list, dtype=np.float64)
    z_raw = np.asarray(zraw_list, dtype=np.float64)

    # Match the MSS longitude convention (same logic as your .nc script)
    lon_q = (lon + 360.0) % 360.0 if dataset_is_0360 else ((lon + 180.0) % 360.0) - 180.0
    lat_q = np.clip(lat, -90.0, 90.0)

    # Interpolate MSS at points
    mss = interp_mss_chunked(mss_da, lon_name, lat_name, lon_q, lat_q,
                             block=block, method="linear")

    # Fallback for NaNs (e.g., seam)
    if np.isnan(mss).any():
        mss_nn = interp_mss_chunked(mss_da, lon_name, lat_name, lon_q, lat_q,
                                    block=block, method="nearest")
        mss = np.where(np.isnan(mss), mss_nn, mss)

    # Convert MSS units if needed
    if units in ("cm", "centimeter", "centimeters", "centimetres"):
        mss = mss / 100.0

    # Correct elevation
    z_mss = z_raw - mss

    # Project lon/lat to EPSG:3413
    to_3413 = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(3413), always_xy=True)
    x_3413, y_3413 = to_3413.transform(lon, lat)

    # Build (N,3) array
    mask = np.isfinite(x_3413) & np.isfinite(y_3413) & np.isfinite(z_mss) & (z_mss >= -5) & (z_mss <= 10)
    pts = np.column_stack((x_3413[mask], y_3413[mask], z_mss[mask]))

    # Write XYZ: lon lat z_corrected
    np.savetxt(output_xyz, pts, fmt="%.4f %.4f %.4f")
    print(f"Wrote corrected XYZ to: {output_xyz}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print('Usage: python Read_ALS_txt_from_Kyle_12162025.py input.txt output.xyz')
        sys.exit(1)

    correct_txt_with_dtu21mss(sys.argv[1], sys.argv[2])
