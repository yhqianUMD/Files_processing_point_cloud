import sys
import os
import numpy as np
import time

def Convert_tri2vtk(tin_file,tin_output_folder):
    '''
    Convert a TIN file in the format of tri to VTK
    Return
    tin_file: name of TIN .off file
    points1: updated 2D points (x,y). each pair of (x,y) is unique
    zs1: updated z values of points, in the same order of points1
    tris: triangles of TIN. each triangle is saved as [vid1, vid2, vid3]. vid is point index based on points1
    '''
    tin_basename = os.path.basename(tin_file)
    VTK_file = tin_output_folder + '/' + os.path.splitext(tin_basename)[0]  + '_test.VTK'
    
    if os.path.splitext(tin_basename)[1] == '.tri':
        with open(tin_file) as infile:
            line = (infile.readline()).split()
            vertices_num=int(line[0])
            print("vnum: {}".format(vertices_num))
            with open(VTK_file, 'w', newline='') as writer:
                # writer = csv.writer(ofs_pts)
                writer.write('# vtk DataFile Version 2.0\n')
                writer.write('\n')
                writer.write('ASCII\n')
                writer.write('\n')
                writer.write('DATASET UNSTRUCTURED_GRID\n')
                writer.write('\n')
                writer.write(f'POINTS {vertices_num} float\n')
                
                for l in range(vertices_num):
                    line = infile.readline().split()
                    v = [float(line[0]),float(line[1]),float(line[2])] # x,y,ele,self_index, ele_order
                    writer.write(f"{v[0]} {v[1]} {v[2]}\n")
                
                line = (infile.readline()).split()
                triangles_num = int(line[0])
                print("tnum: {}".format(triangles_num))
                
                writer.write('\n')
                writer.write(f'CELLS {triangles_num} {triangles_num * 4}\n')
                for l in range(triangles_num):
                    line = infile.readline().split()
                    t = [3, int(line[0]),int(line[1]),int(line[2])] # x,y,ele,self_index, ele_order
                    writer.write(f"{t[0]} {t[1]} {t[2]} {t[3]}\n")
                    
                writer.write('\n')
                writer.write(f"CELL_TYPES {triangles_num}\n")
                for l in range(triangles_num):
                    writer.write("7 ")
                writer.write('\n')
                writer.close()
                
        print("Conversion complete.")
    
    if os.path.splitext(tin_basename)[1] == '.off':
        with open(tin_file) as infile:
            trash = infile.readline()
            line = (infile.readline()).split()
            vertices_num=int(line[0])
            triangles_num = int(line[1])
            print("vnum: {}".format(vertices_num))
            print("tnum: {}".format(triangles_num))
            
            with open(VTK_file, 'w', newline='') as writer:
                # writer = csv.writer(ofs_pts)
                writer.write('# vtk DataFile Version 2.0\n')
                writer.write('\n')
                writer.write('ASCII\n')
                writer.write('\n')
                writer.write('DATASET UNSTRUCTURED_GRID\n')
                writer.write('\n')
                writer.write(f'POINTS {vertices_num} float\n')
                
                for l in range(vertices_num):
                    line = infile.readline().split()
                    v = [float(line[0]),float(line[1]),float(line[2])] # x,y,ele,self_index, ele_order
                    writer.write(f"{v[0]} {v[1]} {v[2]}\n")
                
                writer.write('\n')
                writer.write(f'CELLS {triangles_num} {triangles_num * 4}\n')
                for l in range(triangles_num):
                    line = infile.readline().split()
                    t = [3, int(line[0]),int(line[1]),int(line[2])] # x,y,ele,self_index, ele_order
                    writer.write(f"{t[0]} {t[1]} {t[2]} {t[3]}\n")
                    
                writer.write('\n')
                writer.write(f"CELL_TYPES {triangles_num}\n")
                for l in range(triangles_num):
                    writer.write("7 ")
                writer.write('\n')
                writer.close()
                
        print("Conversion complete.")
            
    return VTK_file

if __name__ == '__main__':
    print("This is used for converting a TIN file from off/tri to a vtk file.")
    # sys.argv[1] should be the TIN file name
    # # sys.argv[2] should be the output tin directory folder
    vtk = Convert_tri2vtk(sys.argv[1], sys.argv[2])
    print("The convertion from a TIN to a vtk file is done!")