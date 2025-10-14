import trimesh
import geopandas as gpd
from shapely.geometry import Polygon
import time
import sys
import os

def convert_off_to_gpkg(off_file_path, target_crs):
    """
    Converts a 3D mesh in an OFF file to a 2D GeoPackage of polygons.

    Args:
        off_file_path (str): The path to the input .off mesh file.
        gpkg_file_path (str): The path for the output .gpkg file.
        target_crs (str): The EPSG code for the coordinate reference system (e.g., 'EPSG:3413').
    """
    try:
        # 1. Load the mesh file using trimesh
        print(f"Loading mesh from {off_file_path}...")
        mesh = trimesh.load_mesh(off_file_path)
        print("Mesh loaded successfully.")

        # 2. Extract vertices and faces
        # We only need the X and Y coordinates for a 2D footprint
        vertices_2d = mesh.vertices[:, :2]

        # 3. Create a list of Shapely Polygons from the mesh faces
        print("Creating polygons from mesh faces...")
        polygons = [Polygon(vertices_2d[face]) for face in mesh.faces]
        print(f"{len(polygons)} polygons created.")

        # 4. Create a GeoDataFrame
        gdf = gpd.GeoDataFrame(geometry=polygons, crs=target_crs)
        print(f"GeoDataFrame created with CRS {target_crs}.")

        # Build new filename by reusing the old one
        base, _ = os.path.splitext(off_file_path)   # split into (path+name, extension)
        gpkg_file_path = base + ".gpkg"

        # 5. Save the GeoDataFrame to a GeoPackage file
        gdf.to_file(gpkg_file_path, driver='GPKG')
        print(f"Successfully saved GeoPackage to {gpkg_file_path}")

    except Exception as e:
        print(f"An error occurred: {e}")
        print("Please ensure the input file exists and is a valid OFF file.")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print('Usage: python convert_off2gpkg.py "C:/Users/yhqian/Downloads/PointClouds/ALS_L1B_20190410T181210_183728_coor_4decimal_downsample_as_100000.off"')
        sys.exit(1)

    ALS_off_file1 = sys.argv[1]
    print("ALS_off_file1:", ALS_off_file1)

    crs_code = 'EPSG:3413'

    t0 = time.time()
    convert_off_to_gpkg(ALS_off_file1, crs_code)
    t1 = time.time()
    print("Time cost of whole process:", t1 - t0)