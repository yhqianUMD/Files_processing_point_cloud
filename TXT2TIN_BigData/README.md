# Triangulation for big data
Triangulation for point cloud with big size involves CGAL. The input file should be in xyz or txt format.

Steps to complie the CGAL tool:
1. load the following modules in the cluster
   - module load boost/1.59.0
   - module load qt/5.8.0
   - module load cgal/4.9
   - module load cmake/3.10.2
   - module load gcc/8.3.1
2. go to the sources direcory, cmake CMakeLists.txt
3. make
4. triangulation: ./dtri ana.xyz
