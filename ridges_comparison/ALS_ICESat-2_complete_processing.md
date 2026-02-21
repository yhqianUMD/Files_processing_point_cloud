## Step 0. Project and subtract the mean sea surface for ALS point clouds.
  + Python code: Step0_Read_ALS_txt_from_Kyle_12162025.py
  + input: raw point cloud in txt
  + output: preprocessed point cloud in xyz
  + Subsequent process: use the gsapp13 cluster to triangulate the point cloud; use Morse-Spark to extract ice ridges and post-process the results.

## Step 1. Compute the drift velocity
  + Python code: Step1_sift_corrected.ipynb
  + inputs: two DEMs of ALS segments
  + outputs: dx and dy distance
  + notes:
     * We can compute the vx and vy by considering the timing of the two segments.
     * Once we have vx and vy, we can use drift_correct_ALS_point_clouds_02092026.ipynb to drift correct one of the ALS segments to validate if vx and vy are correct.

## Step 2. Drift correct the ICESat-2
  + Python code: Step2_Read_ICESat-2_projection_drift_correct.py
  + inputs: raw ICESat-2 profile photons without re-projection but with elevation correction (DTU21).
  + outputs: A csv or txt file represented the projected, elevation-corrected (DTU21), and drift-corrected ICESat-2 profile.
  + Notes:
    * Python code to drift correct ALS segments: Step2_Read_ALS_txt_from_Kyle_projection_subtraction_mean_sea_drift_correction_02092026.py
    * inputs: the raw ALS point cloud without projection and sea surface level correction (DTU21).
    * outputs: a drift corrected ALS point cloud in xyz format.

## Step3. Interpolate the elevation values of the ALS segment along the ICESat-2 profile
  + Code: the terrain_trees library for interpolation.
  + inputs: TIN, kv, ele_rela_to_sea_surface, ICESat-2 profile with only x and y.


## Step4. Plot the corrected ALS and ICESat-2 profile
  + Python code: Step3_plot_profile_ICESat-2_ALS_peaks.ipynb
  + inputs: the ALS interpolation (txt file) along the ICESat-2 profile, the ICESat-2 csv file
  + outputs: plots of the two datasets.
