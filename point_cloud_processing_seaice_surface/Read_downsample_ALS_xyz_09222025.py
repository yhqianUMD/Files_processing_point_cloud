import sys
import numpy as np
import os
import time

def main(filename):
    # Load x, y, z into a NumPy array
    points = np.loadtxt(filename)

    print("Loaded", points.shape[0], "points")
    # downsample the points

    # Suppose points is your (67548680, 3) array
    n_points = points.shape[0]

    # Take 0.1% of them
    sample_size = int(n_points * 0.0001)

    # Randomly choose indices without replacement
    idx = np.random.choice(n_points, size=sample_size, replace=False)

    # Subsample the array
    points_sampled = points[idx]

    print(points_sampled.shape)

    t0 = time.time()

    # Build new filename by reusing the old one
    base, _ = os.path.splitext(filename)   # split into (path+name, extension)
    file_name_txt = base + "_coor_4decimal_downsample.txt"

    # Save points to txt
    np.savetxt(file_name_txt, points_sampled, fmt="%.4f")

    t1 = time.time()
    print("Saved to:", file_name_txt)
    print("Time cost:", t1 - t0)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python Read_downsample_ALS_xyz_09222025.py "C:/Users/yhqian/OneDrive - University of Maryland/Programming/data/seaice_yh/ALS_from_St/AWI_ALS_files_from_Kyle/ALS_L1B_20190410T181210_183728.xyz"')
        sys.exit(1)

    ALS_xyz_file1 = sys.argv[1]
    print("ALS_xyz_file1:", ALS_xyz_file1)
    t0 = time.time()
    main(ALS_xyz_file1)
    t1 = time.time()
    print("Time cost of whole process:", t1 - t0)