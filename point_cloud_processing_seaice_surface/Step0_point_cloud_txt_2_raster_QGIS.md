# The following are the main steps to rasterize raw point cloud data in a txt file to a raster grid.

## Step 1. Load the txt file in QGIS

+ Go to Layer > Add Layer > Add Delimited Text Layer.
+ File Name: Select your .txt file.
+ File Format: Custom delimiters > Check the boxes for both Tab and Space.
+ Record and Fields Options: Uncheck "First record has field names".
+ Geometry Definition:
  * X field: Select field_1 (your Easting/Longitude equivalent).
  * Y field: Select field_2 (your Northing/Latitude equivalent).
  * Z field: Select field_3 (your Elevation values).
+ Geometry CRS (Crucial Step): EPSG:3413 (WGS 84 / NSIDC Sea Ice Polar Stereographic North).

## Step 2. Generate the Raster

+ Open the Processing Toolbox (the gear icon) and search for TIN Interpolation.
+ Vector Layer: Select your loaded .txt layer.
+ Interpolation Attribute: Select your elevation (Z) column.
+ Click the [+] button: This adds the layer to the calculation list.
+ Extent (The Area to Cover):
  * Click the "..." button on the far right of the Extent box.
  * Select Calculate from Layer.
  * Choose your point cloud layer (ALS_L1B...).

## Step 3. Output Raster Size (The Resolution)
This is where you define the scale. Since your project is in EPSG:3413 (which uses meters), the numbers you type here represent meters.
+ For the 5m raster:
  * Set Pixel size X to 5.
  * Set Pixel size Y to 5.
+ Interpolated (Saving the File)
  * Click the "..." button next to the Interpolated box.
  * Select Save to File....
  * Give it a name like SeaIce_5m.tif and ensure the format is .tif (GeoTIFF).
