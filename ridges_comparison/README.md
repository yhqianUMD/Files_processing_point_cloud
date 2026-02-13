## 1. Quantitatively evaluate ridges between distributed and non-distributed results
  + python file: comparison_spatial_idx_01282026.py
  + command: python comparison_spatial_idx_01282026.py
  + inputs: 1) reference ridges, 2) extracted distributed ridges, 3) distance buffer (e.g. 1.0 m).

## 2. Quantitatively evaluate distributed ridges and ridge peaks
  + python file: comparison_ridge_peaks_02032026.py
  + command: python comparison_ridge_peaks_02032026.py
  + inputs: 1) reference ridge peaks, 2) extracted distributed ridges, 3) distance buffer (e.g. 5.0 m).

## 3. Get drift correction velocity or distance
  + python file: sift_corrected.ipynb under /Seaice_ALS_Summer2025/drift_correction
  + inputs: two DEMs built from point cloud segments
  + Notes: The velocity is obtained by dividing the dx and dy with the time differences between the middle time of the two DEMs (or ALS segments).

## 4. Drift correct ICESat-2 ridge peaks
  + python file: Read_ICESat-2_projection_drift_correct.ipynb under /Seaice_ALS_Summer2025/drift_correction
  + inputs: velocity along dx and dy, as well as the reference time (delta_time)
  + Notes: The reference time is usually the middle time of the period of an ALS point cloud segment.
