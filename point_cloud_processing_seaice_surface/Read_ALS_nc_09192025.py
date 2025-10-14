#!/usr/bin/env python3
"""
Process ALS netCDF file and compute elevation statistics above mean sea surface.

Usage:
    python process_als.py /path/to/ALS_file1.nc
"""

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
    """Interpolate MSS values for large arrays in chunks."""
    out = np.empty(lon_arr.size, dtype=np.float64)
    for i in range(0, lon_arr.size, block):
        j = min(i + block, lon_arr.size)
        out[i:j] = mss_da.interp(
            {lon_name: xr.DataArray(lon_arr[i:j], dims="p"),
             lat_name: xr.DataArray(lat_arr[i:j], dims="p")},
            method=method
        ).values
    return out


def main(ALS_file1, bool_save = False):
    # Path to DTU21 MSS file (edit if needed)
    DTU = r"C:\Users\yhqian\AppData\Local\GeographicLib\DTU21MSS_1min_WGS84.nc"

    # Open ALS file
    ds_als = xr.open_dataset(ALS_file1, engine='netcdf4')
    print("Header information:", ds_als)

    # Extract arrays
    lon = np.asarray(ds_als["longitude"].values, dtype=np.float64)
    lat = np.asarray(ds_als["latitude"].values,  dtype=np.float64)
    z_ellip = np.asarray(ds_als["elevation"].values, dtype=np.float64)

    # Load DTU21 MSS
    ds_mss = xr.open_dataset(DTU)
    lon_name = [k for k in ds_mss.coords if k.lower().startswith("lon")][0]
    lat_name = [k for k in ds_mss.coords if k.lower().startswith("lat")][0]
    var_name = [k for k in ds_mss.data_vars if ("mss" in k.lower() or "mean_sea" in k.lower())][0]
    mss_da   = ds_mss[var_name]
    units    = str(mss_da.attrs.get("units", "")).lower()

    # Adjust longitude convention
    ds_lons = ds_mss[lon_name].values
    dataset_is_0360 = (np.nanmin(ds_lons) >= 0.0) and (np.nanmax(ds_lons) <= 360.0)
    lon_q = (lon + 360.0) % 360.0 if dataset_is_0360 else ((lon + 180.0) % 360.0) - 180.0
    lat_q = np.clip(lat, -90.0, 90.0)

    # Interpolate MSS at ALS points
    mss = interp_mss_chunked(mss_da, lon_name, lat_name, lon_q, lat_q,
                             block=2_000_000, method="linear")

    # Fallback for seam/NaN
    if np.isnan(mss).any():
        mss_nn = interp_mss_chunked(mss_da, lon_name, lat_name, lon_q, lat_q,
                                    block=2_000_000, method="nearest")
        mss = np.where(np.isnan(mss), mss_nn, mss)

    # Convert units if needed
    if units in ("cm", "centimeter", "centimeters", "centimetres"):
        mss = mss / 100.0

    # Subtract MSS
    z_mss = z_ellip - mss

    # Project lon/lat to EPSG:3413
    to_3413 = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(3413), always_xy=True)
    x_3413, y_3413 = to_3413.transform(lon, lat)

    # Build (N,3) array
    mask = np.isfinite(x_3413) & np.isfinite(y_3413) & np.isfinite(z_mss) & (z_mss >= -5) & (z_mss <= 10)
    pts = np.column_stack((x_3413[mask], y_3413[mask], z_mss[mask]))

    # Print ranges
    print("Longitude range:", np.nanmin(lon), "to", np.nanmax(lon))
    print("Latitude range: ", np.nanmin(lat), "to", np.nanmax(lat))
    print("X_3413 range:   ", np.nanmin(x_3413), "to", np.nanmax(x_3413))
    print("Y_3413 range:   ", np.nanmin(y_3413), "to", np.nanmax(y_3413))
    print("Elevation range:", np.nanmin(z_mss), "to", np.nanmax(z_mss))

    lon_min, lon_max = np.nanmin(lon), np.nanmax(lon)
    lat_min, lat_max = np.nanmin(lat), np.nanmax(lat)
    x_min,   x_max   = np.nanmin(x_3413), np.nanmax(x_3413)
    y_min,   y_max   = np.nanmin(y_3413), np.nanmax(y_3413)
    z_min,   z_max   = np.nanmin(z_mss),  np.nanmax(z_mss)

    # Basic statistics
    z = z_mss
    mean_val   = np.mean(z)
    median_val = np.median(z)
    std_val    = np.std(z, ddof=1)
    min_val    = np.min(z)
    max_val    = np.max(z)
    rng_val    = max_val - min_val

    mode_res   = stats.mode(z, keepdims=True)
    mode_val   = mode_res.mode[0]
    mode_count = mode_res.count[0]

    p25, p75 = np.percentile(z, [25, 75])
    iqr_val  = p75 - p25

    # Print stats
    print(f"Count:       {z.size:,}")
    print(f"Mean:        {mean_val:.4f} m")
    print(f"Median:      {median_val:.4f} m")
    print(f"Mode:        {mode_val:.4f} m (count={mode_count})")
    print(f"Std dev:     {std_val:.4f} m")
    print(f"Range:       {rng_val:.4f} m")
    print(f"Min, Max:    {min_val:.4f}, {max_val:.4f} m")
    print(f"25th, 75th:  {p25:.4f}, {p75:.4f} m")
    print(f"IQR:         {iqr_val:.4f} m")

    stats_dict = {
        "ALS_file": Path(ALS_file1).name,
        "LonMin": f"{lon_min:.6f}",
        "LonMax": f"{lon_max:.6f}",
        "LatMin": f"{lat_min:.6f}",
        "LatMax": f"{lat_max:.6f}",
        "Xmin_3413": f"{x_min:.4f}",
        "Xmax_3413": f"{x_max:.4f}",
        "Ymin_3413": f"{y_min:.4f}",
        "Ymax_3413": f"{y_max:.4f}",
        "Zmin_MSS": f"{z_min:.4f}",
        "Zmax_MSS": f"{z_max:.4f}",
        "Num_points": z.size,
        "Mean_z": f"{mean_val:.4f}",
        "Median_z": f"{median_val:.4f}",
        "Mode_z": f"{mode_val:.4f}",
        "ModeCount_z": int(mode_count),
        "StdDev_z": f"{std_val:.4f}",
        "Range_z": f"{rng_val:.4f}",
        "Min_z": f"{min_val:.4f}",
        "Max_z": f"{max_val:.4f}",
        "P25_z": f"{p25:.4f}",
        "P75_z": f"{p75:.4f}",
        "IQR_z": f"{iqr_val:.4f}",
    }

    if str(bool_save).strip().lower() in {"y", "yes", "true", "1"}:
        inpath = Path(ALS_file1)
        out_xyz = inpath.with_suffix(".xyz")  # same folder, replace .nc with .xyz

        # Save as XYZ (space-separated, no header – CloudCompare-friendly)
        np.savetxt(out_xyz, pts, fmt="%.4f %.4f %.4f")
        print(f"Wrote XYZ to: {out_xyz}")
    
    # csv_file = Path("C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/ALS_stats.csv")
    # write_header = not csv_file.exists()

    # with open(csv_file, "a", newline="") as f:
    #     writer = csv.DictWriter(f, fieldnames=stats_dict.keys())
    #     if write_header:
    #         writer.writeheader()
    #     writer.writerow(stats_dict)

    # print(f"Appended stats to {csv_file}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print('Usage: python Read_ALS_nc_09192025.py "C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/ALS_L1B_20190410T181210_183728.nc" 1')
        sys.exit(1)

    ALS_file1 = sys.argv[1]
    bool_save = sys.argv[2] if len(sys.argv) > 2 else False
    print("ALS_file1:", ALS_file1)
    t0 = time.time()
    main(ALS_file1, bool_save)
    t1 = time.time()
    print("Time cost of whole process:", t1 - t0)