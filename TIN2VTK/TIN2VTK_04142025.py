import numpy as np
import pyvista as pv
import time
import os

# Input and output paths

# Read the VTU file
input_off = input("Please input the absolute path to the tetrahedral mesh:")

tin_directory = os.path.dirname(input_off)

tin_basename = os.path.basename(input_off) # input_vertices_2.off
print("tin_basename: ", tin_basename)

tin_filename = os.path.splitext(tin_basename)[0] # input_vertices_2
print("tin_filename: ", tin_filename)

tin_extension = os.path.splitext(tin_basename)[1] # .off
print("tin_extension: ", tin_extension)

# write the vertices and tetrahedra to a ts file
t0 = time.time()

date = time.strftime("%m,%d,%Y")
date_name = date.split(',')[0] + date.split(',')[1] + date.split(',')[2]

output_vtk = tin_directory + '/' + tin_filename + '_' + date_name + '.vtk'

# Read the OFF file
with open(input_off, 'r') as f:
    lines = [line.strip() for line in f if line.strip() and not line.startswith('#')]

# Check format
if lines[0] != "OFF":
    raise ValueError("Invalid OFF file: missing 'OFF' header.")

# Get counts
num_verts, num_faces, _ = map(int, lines[1].split())

# Parse vertices
vertex_lines = lines[2 : 2 + num_verts]
face_lines = lines[2 + num_verts : 2 + num_verts + num_faces]

points = []
scalars = []
for line in vertex_lines:
    x, y, s = map(float, line.strip().split())
    points.append([x, y, 0.0])  # z = 0 for 2D
    scalars.append(s)

points = np.array(points)
scalars = np.array(scalars)

# Parse triangular faces
faces = []
for line in face_lines:
    tokens = list(map(int, line.strip().split()))
    assert tokens[0] == 3, "Only triangle meshes are supported."
    faces.append([3] + tokens[1:])  # PyVista expects face size prefix

faces_flat = np.array(faces).flatten()

# Create mesh and add scalar field
mesh = pv.PolyData(points, faces_flat)
mesh.point_data["Elevation"] = scalars

# Save the result
mesh.save(output_vtk)
print(f"✅ Successfully converted: {input_off} → {output_vtk}")

t1 = time.time()
print("Total time cost:", t1 - t0)