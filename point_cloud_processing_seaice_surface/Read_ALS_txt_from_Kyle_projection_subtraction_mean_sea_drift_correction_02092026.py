#!/usr/bin/env python3
import sys
import numpy as np
import xarray as xr
from pyproj import CRS, Transformer
from pathlib import Path

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
    x_velocity=0.0,           # meters / second
    y_velocity=0.0,           # meters / second
    timing_reference=0.0,     # seconds since 2018-01-01 00:00:00
    dtu_nc_path=r"C:\Users\yhqian\AppData\Local\GeographicLib\DTU21MSS_1min_WGS84.nc",
    block=2_000_000
):
    # Load DTU21MSS grid once
    mss_da, lon_name, lat_name, units, dataset_is_0360 = load_dtu21_mss(dtu_nc_path)

    # --- Pass 1: read lon/lat/time/z_raw into arrays ---
    lon_list, lat_list, t_list, zraw_list = [], [], [], []
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
            t   = float(parts[2])   # 3rd column: timing (seconds since 2018-01-01)
            z_raw = float(parts[3]) # 4th column: elevation

            lon_list.append(lon)
            lat_list.append(lat)
            t_list.append(t)
            zraw_list.append(z_raw)

    lon = np.asarray(lon_list, dtype=np.float64)
    lat = np.asarray(lat_list, dtype=np.float64)
    t   = np.asarray(t_list, dtype=np.float64)
    z_raw = np.asarray(zraw_list, dtype=np.float64)

    # Match the MSS longitude convention
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

    # --- Drift correction (velocity * delta_time) ---
    dt = (t - float(timing_reference))  # seconds
    x_corr = x_3413 - dt * float(x_velocity)
    y_corr = y_3413 - dt * float(y_velocity)

    # Build (N,3) array (keep your existing filters)
    mask = (
        np.isfinite(x_corr) & np.isfinite(y_corr) & np.isfinite(z_mss) &
        (z_mss >= -5) & (z_mss <= 10)
    )
    pts = np.column_stack((x_corr[mask], y_corr[mask], z_mss[mask]))

    # Write XYZ: x y z_corrected
    np.savetxt(output_xyz, pts, fmt="%.4f %.4f %.4f")
    print(f"Wrote corrected XYZ to: {output_xyz}")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Project lon/lat to EPSG:3413, subtract DTU21 MSS, and drift-correct x/y using velocities."
    )
    parser.add_argument("input_txt", help="Input TXT with lon,lat,time(sec since 2018-01-01),elev")
    parser.add_argument("output_xyz", help="Output XYZ with x_3413_drift, y_3413_drift, z_mss")
    parser.add_argument("--vx", type=float, default=0.0, help="x velocity in meters/second")
    parser.add_argument("--vy", type=float, default=0.0, help="y velocity in meters/second")
    parser.add_argument("--tref", type=float, default=0.0, help="reference time in seconds since 2018-01-01")
    parser.add_argument("--dtu_nc", type=str, default=r"C:\Users\yhqian\AppData\Local\GeographicLib\DTU21MSS_1min_WGS84.nc",
                        help="Path to DTU21MSS NetCDF")
    parser.add_argument("--block", type=int, default=2_000_000, help="chunk size for MSS interpolation")

    args = parser.parse_args()
    # usage: python Read_ALS_txt_from_Kyle_12162025.py input.txt output.xyz --vx 0.12 --vy -0.08 --tref 392000000

    correct_txt_with_dtu21mss(
        args.input_txt,
        args.output_xyz,
        x_velocity=args.vx,
        y_velocity=args.vy,
        timing_reference=args.tref,
        dtu_nc_path=args.dtu_nc,
        block=args.block
    )
