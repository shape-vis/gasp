import os
import json
import csv

from pathlib import Path

import Utils.MeshContainer as MeshContainer


def readObj(filename, func_method='x'):
    faces = []
    vertices = []
    with open(filename) as file:
        for line in file:
            line = line.split()
            if (line[0] == 'f'): faces.append([int(line[1])-1, int(line[2])-1, int(line[3])-1])
            if (line[0] == 'v'): 
                if func_method == 'x':
                    vertices.append([float(line[1]), float(line[2]), float(line[3]), float(line[1])])
                elif func_method == 'y':
                    vertices.append([float(line[1]), float(line[2]), float(line[3]), float(line[2])])
                elif func_method == 'z':
                    vertices.append([float(line[1]), float(line[2]), float(line[3]), float(line[3])])                
                else:
                    # vertices.append([float(line[1]), float(line[2]), float(line[3]), -1])
                    vertices.append([float(line[1]), float(line[2]), float(line[3]), float(line[4])])

    return MeshContainer.MeshContainer(static_vertices=vertices, static_triangles=faces)


def readRGfile(filename):

    criticalPointsPair = set()
    cps = {}

    with open(filename, 'r') as f:
        line = f.readline().split()

        nodes = int(line[0])
        edges = int(line[1])

        for i in range(nodes):
            line = f.readline().split()
            cps[int(line[0])] = [float(line[1]),line[2]]

        for i in range(edges):
            line = f.readline().split()
        
            src = int(line[0])
            dst = int(line[1])

            if cps[dst][0]<cps[src][0]:
                src, dst = dst, src

            criticalPointsPair.add((src, dst))
    

    # TODO: FIX THIS FUNCTION
    # writeCriticalPoints(model, axisDirection, saddle, extremum, cps, vertices, criticalPointFilePath)

    return cps, criticalPointsPair

def writeString(filename, string):
    with open( filename, 'w') as file:
        file.write(string)


def writeJson(filename, object):
    with open( filename, 'w') as file:
        file.write(json.dumps(object, indent=2))


def writeObj(filename, vertices, faces=[], edges=[]):
    with open(filename, 'w') as file:
        for v in vertices:
            file.write(f'v {v[0]} {v[1]} {v[2]}\n')

        for t in faces:
            file.write(f'f {t[0]+1} {t[1]+1} {t[2]+1}\n')
        
        for e in edges:
            file.write(f'l {e[0]+1} {e[1]+1}\n')



def writeContours(contourPath, contours):
    for idx, contour_obj in  enumerate(contours):
        contour = contour_obj.get_contour()
        edges = []
        for i in range(len(contour) - 1):
            edges.append((i, i + 1))
        edges.append((len(contour) - 1, 0 ))
        writeObj(f'{contourPath}_{idx}.obj', contour , [], edges)



# Single ReebGraph write
def writeRG_full( reebGraph, reeb_graph_file ):
    Path(os.path.dirname(reeb_graph_file)).mkdir(parents=True, exist_ok=True)
    with open(reeb_graph_file, 'w') as reeb_graph:
        count = 0
        for d_path in reebGraph:
            count += 1
            for j in range(len(d_path)):
                x, y, z = d_path[j]
                reeb_graph.write(f'v {x:.6f} {y:.6f} {z:.6f}\n')

            for j in range (len(d_path) - 1):
                reeb_graph.write('l ' + str(count) + ' ' + str(count+1) + '\n')
                count += 1



#######################FOR DEBUGGING###############################




def write_to_csv(filename, data_list):
    """
    Writes a list of tuples to a CSV file.
    
    Parameters:
        filename (str): The CSV file name.
        data_list (list of tuples): Each tuple contains (Edge ID, Value 1, Value 2, Value 3, Value 4).
    """
    write_header = False

    # Check if the file exists; if not, set flag to write header
    try:
        with open(filename, 'r') as file:
            pass  # If file exists, do nothing
    except FileNotFoundError:
        write_header = True  # File doesn't exist, we need to write a header

    with open(filename, mode='a', newline='') as file:
        writer = csv.writer(file)
        
        # Write header only if the file is new
        if write_header:
            writer.writerow(["Source", "Destination", "Source Value", "Destination Value", "Cut Triangles"])
        
        # Write all tuples from the list
        writer.writerows(data_list)


