import math
import networkx as nx
import functools

import Utils.VertexContainer as VC

from Utils import Debugger
from Utils.EdgeMap import EdgeMap

# INTERIOR_METHOD_SPACING = 0.15
INTERIOR_METHOD_NUM_POINTS = [4, 8]

BOUNDARY_METHOD_MAX_POINTS = 40
BOUNDARY_METHOD_SUBDIVISION = 0.25


def getPath(contourPoints, srcVert, dstVert, distFunc):

    def buildGraphEdges_v2(G, srcNodes, srcLayerIdx, dstNodes, dstLayerIdx ):
        for i, sN in enumerate(srcNodes):
            for j, dN in enumerate(dstNodes):
                G.add_edge( (srcLayerIdx,i), (dstLayerIdx,j), weight = distFunc(sN, dN))
        return G
        
    Gr = nx.Graph()
    for i in range (len(contourPoints) - 1):
        Gr = buildGraphEdges_v2(Gr, contourPoints[i], i, contourPoints[i + 1], i+1)

    Gr = buildGraphEdges_v2(Gr, [srcVert], -1,  contourPoints[0], 0 )
    Gr = buildGraphEdges_v2(Gr, [dstVert], -2, contourPoints[-1], len(contourPoints) - 1)

    try:
        return list(nx.dijkstra_path(Gr, (-1,0), (-2,0), weight='weight'))
    except:
        # print('  ERROR: No path found (source:', srcVert, 'destination:', dstVert,')')
        return None
    
    
def pathToPoints(srcVert, dstVert, contourPoints, path):
    pathPoint = [ (srcVert[0], srcVert[1], srcVert[2]) ]
    for p in path[1:-1]:
        pathPoint.append( contourPoints[p[0]][p[1]] )
    pathPoint.append( (dstVert[0], dstVert[1], dstVert[2]) )
    return pathPoint

   
###################################################################################################################


def boundaryMethod(profiler, contourArray, srcVert, dstVert, fileID):

    profiler_pp1 = profiler.add_subprofiler("Point + Path #1", start=True)
    contourPoints =  []
    contourIndex = []
    for layer in range (len(contourArray)):
        stepSize = max(2,int(len(contourArray[layer])/BOUNDARY_METHOD_MAX_POINTS))
        points, index = contourArray[layer].boundaryPoints(0, len(contourArray[layer]), stepSize)
        contourPoints.append(points)
        contourIndex.append(index)
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance )
    profiler_pp1.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_1.obj', srcVert, dstVert, contourPoints, path)

    if path is None:
        print(f"  ERROR: No path found for feature {fileID} (source:{srcVert}, 'destination:{dstVert}).")
        return []

    profiler_pp2 = profiler.add_subprofiler("Point + Path #2", start=True)
    contourPoints =  []
    newContourIndex = []
    for pnt in path[1:-1]:
        stepSize = max(2,int(len(contourArray[pnt[0]])/BOUNDARY_METHOD_MAX_POINTS))
        idx = contourIndex[pnt[0]][pnt[1]]
        points, index = contourArray[pnt[0]].boundaryPoints(idx-stepSize, idx+stepSize+1, 1)
        contourPoints.append(points)
        newContourIndex.append(index)
    contourIndex = newContourIndex
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance )
    profiler_pp2.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_2.obj', srcVert, dstVert, contourPoints, path)



    profiler_pp3 = profiler.add_subprofiler("Point + Path #3", start=True)
    contourPoints =  []
    for pnt in path[1:-1]:
        idx = contourIndex[pnt[0]][pnt[1]]
        points, index = contourArray[pnt[0]].boundaryPointsInterpolated(idx, BOUNDARY_METHOD_SUBDIVISION, int(2/BOUNDARY_METHOD_SUBDIVISION) )
        contourPoints.append(points)
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance )
    profiler_pp3.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_3.obj', srcVert, dstVert, contourPoints, path)

    return pathToPoints(srcVert, dstVert, contourPoints, path)


###################################################################################################################


def interiorMethod(profiler, contours, srcVert, dstVert, buffer, fileID):

    profiler_pp1 = profiler.add_subprofiler("Point + Path #1", start=True)
    contourPoints =  []
    for contour in contours:
        contourPoints.append( contour.interiorPoints(INTERIOR_METHOD_NUM_POINTS, buffer) )
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance)
    profiler_pp1.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_1.obj', srcVert, dstVert, contourPoints, path)

    if path is None:
        print(f"  WARNING: No path found for feature {fileID} (source:{srcVert}, 'destination:{dstVert}). Reverting to boundary approach.")
        return boundaryMethod(profiler, contours, srcVert, dstVert, fileID)

    profiler_pp2 = profiler.add_subprofiler("Point + Path #2", start=True)
    newContourPoints =  []
    for pnt in path[1:-1]:
        newContourPoints.append( contours[pnt[0]].interiorPointsByLocation( contourPoints[pnt[0]][pnt[1]], 0.25, INTERIOR_METHOD_NUM_POINTS, buffer ) )
    contourPoints = newContourPoints
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance)
    profiler_pp2.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_2.obj', srcVert, dstVert, contourPoints, path)

    profiler_pp3 = profiler.add_subprofiler("Point + Path #3", start=True)
    newContourPoints =  []
    for pnt in path[1:-1]:
        newContourPoints.append( contours[pnt[0]].interiorPointsByLocation( contourPoints[pnt[0]][pnt[1]], 0.125, INTERIOR_METHOD_NUM_POINTS, buffer ) )
    contourPoints = newContourPoints
    path = getPath(contourPoints, srcVert, dstVert, VC.vertex_vertex_distance)
    profiler_pp3.stop()

    Debugger.writeGraphPointsPath(f'/contour/contour_{fileID}_path_reg_iter_3.obj', srcVert, dstVert, contourPoints, path)

    return pathToPoints(srcVert, dstVert, contourPoints, path)


###################################################################################################################


def __findPath(srcP, destP, vert_cont, tris, edges):
    
    Gr = nx.Graph()

    for edge in edges:
        Gr.add_edge(edge[0], edge[1], weight = VC.vertex_vertex_distance( vert_cont[edge[0]], vert_cont[edge[1]] ))

    for triangle in tris:
        for i in range(0, 3):
            j = (i + 1) % 3
            Gr.add_edge(triangle[i], triangle[j], weight = VC.vertex_vertex_distance( vert_cont[triangle[i]], vert_cont[triangle[j]] ))

    path_idx = list(nx.dijkstra_path(Gr, srcP, destP, weight = 'weight'))
    length_of_path = nx.path_weight(Gr, path_idx, weight = 'weight')
    path = [ vert_cont[d][:3] for d in path_idx ]

    return path_idx, path, length_of_path


def __extractAndSubdividePathTrianges(vert_cont, triangles, path_idx):

    vertex2Triangle = {}
    newTriangles = []
    edgemap = EdgeMap()
    extTriangles = set()

    for tri in triangles:
        for v in tri[0:3]:
            if v not in vertex2Triangle:
                vertex2Triangle[v] = []
            vertex2Triangle[v].append( (tri[0],tri[1],tri[2]) )

    for p in path_idx:
        if p in vertex2Triangle:
            for tri in vertex2Triangle[p]:
                extTriangles.add(tri)

    for tri in extTriangles:
        centroidIndex = vert_cont.add_centroid3(*tri)

        for i in range(3):
            j = (i + 1) % 3

            if not edgemap.exists(tri[i], tri[j]):
                edgemap.add_edge(tri[i], tri[j], vert_cont.add_lerp_vert3(tri[i], tri[j], 0.5))

            newTriangles.append([tri[i], edgemap.get_edge(tri[i], tri[j]), centroidIndex])
            newTriangles.append([edgemap.get_edge(tri[i], tri[j]), tri[j], centroidIndex])

    return newTriangles


def thinFeatureMethod(cutMesh, cp_pair, fileID, maxSubdivisionIterations=5):

    src, dst = cp_pair

    cutTriangles = cutMesh.get_dynamic_triangles()
    cutEdges = cutMesh.get_dynamic_edges()
    vert_cont = VC.VertexContainer( static_vertices=cutMesh.get_static_vertices(), dynamic_vertices=cutMesh.get_dynamic_vertices())

    path_idx, init_arc_path, prev_path_length = __findPath(src, dst, vert_cont, cutTriangles, cutEdges)
    curr_arc_path = init_arc_path
    
    for iteration in range(maxSubdivisionIterations-1):
        Debugger.writeObj(f'contour/contour_{fileID}_path_thin_iter_{iteration+1}.obj', vert_cont, cutTriangles, curr_arc_path)

        cutTriangles = __extractAndSubdividePathTrianges(vert_cont, cutTriangles, path_idx)
        path_idx, curr_arc_path, curr_path_length = __findPath(src, dst, vert_cont, cutTriangles, cutEdges)

        if abs(curr_path_length - prev_path_length) < 0.00001:
            break
        prev_path_length = curr_path_length

    return curr_arc_path

