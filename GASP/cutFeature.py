import networkx as nx

import Utils.MeshContainer as MC
import Utils.VertexContainer as VC
import Utils.Debugger as Debugger

from Utils.EdgeMap import EdgeMap
from Utils.FilterTriangleContainer import FilterTriangleContainer


def __cutAtIso(edgemap : EdgeMap, vertex_container : VC.VertexContainer, src, dst, oldTriangles, isoContour, isThin, srcOrDst):

    def getCrossingVertex( vIdx0, vIdx1, f0, f1 ):
        if not edgemap.exists(vIdx0, vIdx1):
            edgemap.add_edge( vIdx0, vIdx1, vertex_container.add_vertex( VC.lerp_verts(vertex_container[vIdx0], vertex_container[vIdx1], VC.get_t(f0, f1, isoContour) ) ) )
        return edgemap.get_edge(vIdx0, vIdx1)
        
    cutTriangles = []

    compDir = 1 if srcOrDst == 'src' else -1
    
    for face in oldTriangles:
        
        triV = face[0:3]
        flag = face[3]

        f = [ vertex_container[v][3] for v in triV ]

        bucket = []
        cutTriangle = False

        for i in range(3):
            j = (i + 1) % 3

            # if isThin:
            #     if f[i]*compDir >= (isoContour - 0.0000001)*compDir or triV[i] == src or triV[i] == dst:
            #         bucket.append(triV[i])
            # else:
            #     if f[i]*compDir >= isoContour*compDir: 
            #         bucket.append(triV[i])

            if f[i]*compDir >= isoContour*compDir: 
                    bucket.append(triV[i])
            

            if (f[j] > isoContour and f[i] < isoContour) or (f[i] > isoContour and f[j] < isoContour):
                cutTriangle = True
                bucket.append( getCrossingVertex(triV[i], triV[j], f[i], f[j]) )

        if len(bucket) == 3 and not cutTriangle:
            cutTriangles.append( face )

        if len(bucket) == 3 and cutTriangle:
            cutTriangles.append( [ bucket[0], bucket[1], bucket[2], flag ])

        if len(bucket) == 4:
            cutTriangles.append( [ bucket[0], bucket[1], bucket[2], flag ] )
            cutTriangles.append( [ bucket[0], bucket[2], bucket[3], flag ] )

        if len(bucket) == 5:
            cutTriangles.append( face )

    return cutTriangles



def __roughCutAndCategorize(trisFilter, vertices, src, dst, betweenCPS, srcVal, dstVal, epsilon):

    GSrc = nx.Graph()
    GDst = nx.Graph()

    

    for face in trisFilter.get_iterator(srcVal+epsilon, dstVal-epsilon):
        withinEpsSrc = False
        withinEpsDst = False

       
        for v in face:
            f = vertices[v][3]

        
            if v == src or srcVal <= f <= srcVal+epsilon: 
                withinEpsSrc = True
            if v == dst or dstVal-epsilon <= f <= dstVal:   
                withinEpsDst = True
        
        if withinEpsSrc:
            for i in range(3):
                GSrc.add_edge(face[i], face[(i+1)%3])
               
        if withinEpsDst:
            for i in range(3):
                GDst.add_edge(face[i], face[(i+1)%3])
    

    srcFlags = list(nx.descendants(GSrc,src))
    dstFlags = list(nx.descendants(GDst,dst))

 
    cutTriangles = []
    cutEdges = []

    for face in trisFilter.get_iterator(srcVal+epsilon, dstVal-epsilon):
        below, above, flag = 0, 0, 0
        bucket = []

        src_dst = False
        for v in face:
            if v == src or v == dst:
                src_dst = True

            f = vertices[v][3]
            if f < srcVal:
                below += 1
            if f > dstVal:
                above += 1

            if abs(f-srcVal) <= 0.0 or abs(dstVal-f) <= 0.0:
                bucket.append(v)

            if v in srcFlags:
                flag = flag | 1
            if v in dstFlags:
                flag = flag | 2
            if v in betweenCPS:
                flag = flag | 4

        if not( above == 3 or below == 3 ) or src_dst:
            cutTriangles.append( [ face[0], face[1], face[2], flag ] )

        if len(bucket) == 2:
            cutEdges.append( [ bucket[0], bucket[1], 0 ] )
    

    return cutTriangles, cutEdges



def cutFeature(profiler, input_mesh : FilterTriangleContainer, criticalPoints, cp_pair, epsilon, isThin, fileNumber ):

    src, dst = cp_pair

    # vertices = input_mesh.get_vertices()
    vertex_container = VC.VertexContainer(static_vertices=input_mesh.get_vertices())
    edgemap = EdgeMap()

    srcVal = input_mesh.get_vertex(src)[3]
    dstVal = input_mesh.get_vertex(dst)[3]

    

    
    betweenCPS = list(filter(lambda x:
    round(vertex_container[x][3], 6) > round(srcVal, 6) and
    round(vertex_container[x][3], 6) < round(dstVal, 6),
    criticalPoints.keys()))

    # betweenCPS = list(filter(lambda x: vertex_container[x][3] > srcVal and vertex_container[x][3] < dstVal, criticalPoints.keys()))



    for betweenCP in betweenCPS:

        if srcVal <= vertex_container[betweenCP][3] <= srcVal+epsilon:
            print(f"  WARNING: CP {betweenCP} ({vertex_container[betweenCP][3]}) WITHIN EPSILON OF SOURCE CP {src} ({srcVal})")
        if dstVal-epsilon <= vertex_container[betweenCP][3] <= dstVal:
            print(f"  WARNING: CP {betweenCP} ({vertex_container[betweenCP][3]}) WITHIN EPSILON OF DESTINATION CP {dst} ({dstVal})")
    
    profile_filter = profiler.add_subprofiler('filter')
    cutTriangles, cutEdges = __roughCutAndCategorize(input_mesh, vertex_container, src, dst, betweenCPS, srcVal, dstVal, epsilon)
    profile_filter.stop()

    Debugger.writeObj(f'cut/cut_{fileNumber}_rough.obj', vertex_container, cutTriangles, cutEdges)

    profiler_bot_cut = profiler.add_subprofiler('bottom_cut')
    cutTriangles = __cutAtIso(edgemap, vertex_container, src, dst, cutTriangles, srcVal + epsilon, isThin, 'src')
    profiler_bot_cut.stop()

    Debugger.writeObj(f'cut/cut_{fileNumber}_src.obj', vertex_container, cutTriangles, cutEdges)
    
    profiler_top_cut = profiler.add_subprofiler('top_cut')
    cutTriangles = __cutAtIso(edgemap, vertex_container, src, dst, cutTriangles, dstVal - epsilon, isThin, 'dst')
    profiler_top_cut.stop()

    Debugger.writeObj(f'cut/cut_{fileNumber}_dst.obj', vertex_container, cutTriangles, cutEdges)

    return MC.MeshContainer(static_vertices=vertex_container.get_static_vertices(), dynamic_vertices=vertex_container.get_dynamic_vertices(), dynamic_triangles=cutTriangles, dynamic_edges=cutEdges)


def cutFeature0Persistence(input_mesh : FilterTriangleContainer, cp_pair, epsilon = 0.00001 ):

    cpVal = input_mesh.get_vertex(cp_pair[0])[3]
    out_mesh = MC.MeshContainer( static_vertices=input_mesh.get_vertices() )
    edgemap = EdgeMap()

    def addVertex( v1, v2, t ):
        if not edgemap.exists(v1,v2):
            edgemap.add_edge( v1, v2, out_mesh.add_vertex( VC.lerp_verts(out_mesh.get_vertex(v1), out_mesh.get_vertex(v2), t) ) )
        return edgemap.get_edge(v1, v2)

    for face in input_mesh.get_iterator(cpVal-epsilon, cpVal+epsilon):
        triV = face[0:3]
        bucket = []
        above, below = 0, 0
        f = [ out_mesh.get_vertex(v)[3] for v in triV ]    

        for i in range(3):
            if f[i] < cpVal: below += 1
            if f[i] > cpVal: above += 1
            if abs(f[i]-cpVal) < epsilon:
                bucket.append(triV[i])
            
        if len(bucket) == 3:
            out_mesh.add_triangle( [ bucket[0], bucket[1], bucket[2], 0 ])
            
        elif len(bucket) == 2:
            out_mesh.add_edge( [ bucket[0], bucket[1], 0 ] )
            
        elif above > 0 and below > 0: 
            
            for i in range(3):  
                j = (i + 1) % 3
                if f[i] == f[j] or triV[i] in bucket or triV[j] in bucket:
                    continue

                t = VC.get_t(f[i], f[j], cpVal)
                
                if 0 < t < 1:
                    bucket.append( addVertex(triV[i], triV[j], t) )

                if len(bucket) == 2:
                    out_mesh.add_edge( [ bucket[0], bucket[1], 0 ] )
                    break
    
    return out_mesh

