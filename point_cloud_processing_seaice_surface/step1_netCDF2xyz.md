# Converting a NetCDF file to an OFF file

## 1. the file 'Read_ALS_nc_09192025.py' is used to convert a netCDF file to a xyz file

this file includes two main steps:

### 1) subtract the elevation values by the mean sea ice surface DTU21MSS_1min_WGS84.nc

```
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

# Interpolate MSS at ALS points
mss = interp_mss_chunked(mss_da, lon_name, lat_name, lon_q, lat_q,
                          block=2_000_000, method="linear")

# Subtract MSS
z_mss = z_ellip - mss
```


## 2) project the longitude and latitude to x and y coordinates

```
# Extract arrays
lon = np.asarray(ds_als["longitude"].values, dtype=np.float64)
lat = np.asarray(ds_als["latitude"].values,  dtype=np.float64)
z_ellip = np.asarray(ds_als["elevation"].values, dtype=np.float64)
    
# Project lon/lat to EPSG:3413
to_3413 = Transformer.from_crs(CRS.from_epsg(4326), CRS.from_epsg(3413), always_xy=True)
x_3413, y_3413 = to_3413.transform(lon, lat)
```

## command to run this file in python
```
conda activate seaice_env
```

```
python Read_ALS_nc_09192025.py "C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/ALS_L1B_20190410T181210_183728.nc" 1
```
the command refers to "python /path/to/python/script /path/to/nc_file write_output2xyz_or_not"

## 2. the file 'Read_downsample_ALS_xyz_09222025.py' is used to download the point clouds in xyz format to 0.0001 of its size

## command to run this file in python
```
python Read_downsample_ALS_xyz_09222025.py "C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/ALS_L1B_20190410T164528_165720.xyz"
```
