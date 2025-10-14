# Triangulate big point cloud data in gsapp13 cluster

## 1. navigate to the path
```
/gpfs/data1/cgis1gp/yuehui/codes/cgal_alpha_shape_04042024/cgal_alpha_shape
```


## 2. load basic packages or softwares
```
module load boost/1.84.0
module load qt/5.8.0
module load cgal/4.9
module load cmake/3.10.2
```

If the above did not work, try the following:
```
module load boost/1.59.0
module load qt/5.8.0
module load cgal/4.9
module load cmake/3.10.2
```

## 3. run Delaunay triangulation
```
./cgal_as_lite /gpfs/data1/cgis1gp/yuehui/data/ALS_L1B_20190410/ALS_L1B_20190410T164528_165720_coor_4decimal_downsample.txt 100000
```

this command refers to "./cgal_as_lite /path/to/point_cloud_xyz_file alpha_value"

## Note: the gsapp13 cluster is able to triangulate big point cloud datasets with more than 2 billion points
