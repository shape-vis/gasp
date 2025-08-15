import networkx as nx

import Utils.Debugger as Debugger

from Utils.MeshContainer import MeshContainer


def cutConnectedComponents( cutMesh : MeshContainer, fileNumber ):

    # create a graph with edges as the edges of the triangles and extract connected components
    Gr = nx.Graph()

    for triangle in cutMesh.get_triangle_iterator():
        Gr.add_edge(triangle[0], triangle[1])
        Gr.add_edge(triangle[0], triangle[2])
        Gr.add_edge(triangle[1], triangle[2])
        
    cc = list(nx.connected_components(Gr))

    # add triangles to their connected component and update flags
    cc_tri = [ [] for _ in range(len(cc)) ]
    cc_flag = [ 0 for _ in range(len(cc)) ]
    for triangle in cutMesh.get_triangle_iterator():
        for idx in range(len(cc)):
            if triangle[0] in cc[idx]:
                cc_tri[idx].append(triangle)
                cc_flag[idx] = cc_flag[idx] | triangle[3]
                break
    
    # add connected components to valid or not based on flags
    validCCTriangles = []
    invalidCCTriangles = []
    for i in range(len(cc_tri)):
        if cc_flag[i] == 3:
            validCCTriangles.append(cc_tri[i])
        else:
            invalidCCTriangles.append(cc_tri[i])
    
    if len(validCCTriangles) == 0:
        print(f'  WARNING: No connected components found in cut {fileNumber}')
        print(f'           Number of triangles in cut: {cutMesh.get_triangle_length()}')
        print(f'           Flag: {cc_flag}')

    for i in range(0, len(validCCTriangles)):
        Debugger.writeObj( f'cut_cc/cut_cc_{fileNumber}_{i}.obj', cutMesh.get_vertex_iterator(), validCCTriangles[i], [] )

    for i in range(0, len(invalidCCTriangles)):
        Debugger.writeObj( f'cut_cc/cut_cc_{fileNumber}_invalid_{i}.obj', cutMesh.get_vertex_iterator(), invalidCCTriangles[i], [] )

    return validCCTriangles

