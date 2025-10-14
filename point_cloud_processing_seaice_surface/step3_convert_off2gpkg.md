# Converting an OFF file to a gpkg file so that we can display it in QGIS

## 1. the file 'convert_off2gpkg.py' is used to convert an OFF file to a gpkg file

Since the input mesh is a 2.5D triangle mesh, the main steps include extracting the x and y coordinates of vertices, storing triangles as polygons, and setting the coordinate reference system.

## command to run this file in python

```
python convert_off2gpkg.py "C:/Users/yhqian/Downloads/PointClouds/ALS_L1B_20190410T181210_183728_coor_4decimal_downsample_as_100000.off"
```
