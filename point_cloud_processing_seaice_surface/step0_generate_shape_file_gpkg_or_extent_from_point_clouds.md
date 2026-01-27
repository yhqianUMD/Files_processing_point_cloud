# The following are the steps to generate an accurate shape file or gpkg file from a point cloud stored in txt or xyz format.

## Step 1: Load the txt file via "Add Layer" -> "Vector Layer"

## Step 2: Generate a concave hull
+ search "concave" and go to "concave hull (by layer)"
+ uncheck the box "Allow holes"
+ set the threshold as "0.001" or "0.01"
+ directly click "Run"

## Step 3: Export the concave hull to a gpkg file
+ right click the concave hull
+ save the selected features as gpkg


# The following are the steps to generate a rectangle shape file or extent from a point cloud stored in txt or xyz format.

+ Step 1: Load the txt file "Add Layer" -> "Vector Layer"

+ Step 2: Search for the tool "Extract layer extent".

+ Step 3: Input layer -> Select your point cloud txt file.

+ Step 4: clip Run.
