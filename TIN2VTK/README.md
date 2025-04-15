# Converting a TIN file in OFF format to a VTK file

## 1. The TIN2VTK.py is used to convert a TIN to a VTK file. The following generated datasets are used in single-node TTK

The input parameters expected are:
- tin_file: the TIN file name
- tin_output_folder: the output vtk directory folder

Example:
```
python C:/Users/yhqian/Documents/cos_sum.tri C:/Users/yhqian/Documents
```

## 2. The TIN2VTK_04142025.py is used to convert a TIN to a VTK file. The following generated datasets are used in MPI-supported TTK.

* install and import pyvista packages
  ```
  pip install pyvista
  import pyvista as pv
  ```
* run the Python script. Remember to update the path to the input OFF file
  ```
  python TIN2VTK_04142025.py
  ```
