import sys
import os
# from reader import Reader
from scipy.spatial import Delaunay 
import numpy as np

def generate_TIN(pts_file,tin_output_folder):
    '''
    Generate TIN from input point file.
    Return
    tin_file: name of TIN .off file
    points1: updated 2D points (x,y). each pair of (x,y) is unique
    zs1: updated z values of points, in the same order of points1
    tris: triangles of TIN. each triangle is saved as [vid1, vid2, vid3]. vid is point index based on points1
    '''
    points = np.empty(shape=[0, 2])
    zs=list()
    
    # count the lines of the whole txt file
    lines_num = 0
    for lines_num,line in enumerate(open(pts_file,'rU').readlines()):
        lines_num += 1
    
    with open(pts_file) as infile:
        # lines_num= infile.readline().strip()
        # lines_num=int(lines_num)
        for l in range(lines_num):
            line = (infile.readline()).split()
            v1 = float(line[0])
            v2 = float(line[1])
            existed_p = False
            for p in points:
                if p[0]==v1 and p[1]==v2:
                    existed_p = True
                    break
            if existed_p == False:
                points = np.append(points, [[v1,v2]], axis=0)
                zs.append(float(line[2]))
    
    triangles = Delaunay(points) 
    
     
    used_pts = set()
    for tri in triangles.simplices:
        used_pts.add(tri[0])
        used_pts.add(tri[1])
        used_pts.add(tri[2])
    old2new = dict()
    new2old = list()
    zs1 = list()
    points1= np.empty(shape=[0, 2])
    for pid in used_pts:
        points1 = np.append(points1,[[points[pid][0], points[pid][1]]],axis=0)
        old2new[pid] = len(points1)-1
        new2old.append(pid)
        zs1.append(zs[pid])
        
    tris = np.empty(shape=[0, 3])
    for tri in triangles.simplices:
        v1 = tri[0]
        v2 = tri[1]
        v3 = tri[2]
        nv1 = old2new[v1]
        nv2 = old2new[v2]
        nv3 = old2new[v3]
        tris = np.append(tris,[[nv1, nv2, nv3]],axis=0)
   
   # output TIN file, the finename is the same as input file but with different suffix
   # tin_output_folder is the folder path of generated tin file
    tin_file = tin_output_folder + '/' + os.path.basename(pts_file).split('.')[0]  + '.off'
    # tin_file = "pts-dt.off" 
    with open(tin_file,'w') as ofs:
        ofs.write("OFF\n")
        ofs.write("{} {} 0\n".format(len(points1), len(tris)))
        for pid in range(len(points1)):
            ofs.write("{} {} {}\n".format(points[pid][0], points[pid][1],zs1[pid]))
        for tri in tris:
            ofs.write("3 {} {} {}\n".format(int(tri[0]), int(tri[1]), int(tri[2])))
    
    return tin_file

if __name__ == '__main__':
    print("This is used for triangulating a point cloud file in the xyz or txt format to a TIN in off format.")
    # sys.argv[1] should be the point cloud file name
    # # sys.argv[2] should be the output tin directory folder
    tin = generate_TIN(sys.argv[1], sys.argv[2])
    print("The triangulation is done!")