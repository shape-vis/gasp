import os
import Utils.FileIO as FileIO
from pathlib import Path

filePath = './'
enabled = False

def set_file_path(path):
    global filePath
    filePath = path
    Path(f'./{filePath}/contour').mkdir(parents=True, exist_ok=True)
    Path(f'./{filePath}/cut').mkdir(parents=True, exist_ok=True)
    Path(f'./{filePath}/cut_cc').mkdir(parents=True, exist_ok=True)

def set_enabled(value):
    global enabled
    enabled = value

def make_file_path(filename):
    global filePath
    return os.path.join(f'./{filePath}/', filename)

def writeMesh(filename, mesh):
    if enabled:
        mesh.writeObj( make_file_path(filename) )

def writeObj(filename, vertices, triangles = [], edges = []):
    if enabled:
        FileIO.writeObj( make_file_path(filename), vertices, triangles, edges )

def writeContours(filename, contours):
    if enabled:
        FileIO.writeContours( filePath + filename, contours )

def writeString(filename, string):
    if enabled:
        with open( make_file_path(filename), 'w') as file:
            file.write(string)

def writeGraphPointsPath( filename, srcVert, dstVert, point, path ):
    if enabled:
        if path is None:
            vert_map = { }
            verts = [ ]
        else:
            vert_map = { path[0]: 0, path[-1]: 1 }
            verts = [ srcVert, dstVert ]

        for i,layer in enumerate(point):
            for j,p in enumerate(layer):
                vert_map[(i,j)] = len(verts)
                verts.append(p)
        
        edges = []
        if path is not None:
            for i in range(len(path)-1):
                edges.append((vert_map[path[i]], vert_map[path[i+1]]))

        FileIO.writeObj( filePath + filename, verts, edges=edges )
        