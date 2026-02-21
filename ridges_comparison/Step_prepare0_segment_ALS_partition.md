## Step 1: Create a grid with four parts

1. Tool: Create Grid
2. Set the extent by "Calculate from Layer", which is the point cloud to be cropped
3. Set width and height
   + width: xmax - xmin, e.g., if we want to have four columns, set Horizontal spacing = Width / 4
   + height: ymax - ymin, similar to the set of width
4. Set horizontal and vertical overlay as 0
5. The generated grid will have a column "id" specifying each part

## Step 2: Add an ID field to the point cloud 

1. Tool: Join Attributes By Location
2. Join features in: the point cloud layer
3. Geometric predicate: intersect
4. By comparing to: the created grid in Step 1
5. Fields to add (IMPORTANT): Select ONLY the grid ID field of the created grid
6. Join type: Take attributes of the first matching feature only (one-to-one)

## Step 3: Split Vector Layer

1. Tool: Split Vector Layer
2. input layer: the joined point cloud layer
3. field: grid ID
4. Advanced Parameters --> output file type: csv
5. Output directory: set a path to store the four parts

## Step 4: Export each part to a csv file

1. Right-click the split layer
2. Export -> Save Feature as CSV
3. In "Select fields to export and their export options": uncheck the "id" column
