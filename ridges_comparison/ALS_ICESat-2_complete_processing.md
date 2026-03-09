## Pre-step0.Project from nc file to xyz file and stores the x, y, t, and z columns
  + Python code: PreStep0_Read_ALS_nc_03092026.py
  + input: the nc file and a boolean value "bool_save" to save the file or not
  + output: a xyz file storing x, y, t, z
  + Notes:
    * the t is gps_utc_offset, which is processed via "t_gps_2018 = utc_unix - unix_ref_2018_sec + gps_utc_offset"
    * the points stored in the output file have been projected to ESPG3413, and subtracted the mean sea surface via DTU2021
    * the output is a whole segment, we may need to use the CloudCompare to crop a portition of the points, where the cropped output in CloudCompare stores x, y, z, t
    * if Pre-step0 is conducted, Step 0 is not needed.

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
  + Note: for the input of the ICESat-2 profile with only x and y, we do not need to crop this profile to limit it to the area of TIN, as the terrain tree library will only interpolate the points within TIN.


## Step4. Plot the corrected ALS and ICESat-2 profile
  + Python code: Step3_plot_profile_ICESat-2_ALS_peaks.ipynb
  + inputs: the ALS interpolation (txt file) along the ICESat-2 profile, the ICESat-2 csv file
  + outputs: plots of the two datasets.
