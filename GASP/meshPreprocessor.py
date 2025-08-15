import Utils.MeshContainer as MC
import Utils.VertexContainer as VC
import Utils.Debugger as Debugger

from Utils.EdgeMap import EdgeMap
from Utils.FilterTriangleContainer import FilterTriangleContainer


def splitMultipleCriticalPointTriangles(mesh: MC, CP, mesh_slices=20):

    edgemap = EdgeMap()
    split_mesh = MC.MeshContainer(static_vertices=mesh.get_static_vertices())

    def splitEdge( v1, v2 ):
        if not edgemap.exists(v1, v2):
            edgemap.add_edge(v1, v2, split_mesh.add_vertex( VC.lerp_verts(mesh.get_vertex(v1), mesh.get_vertex(v2), 0.5) ))
        return edgemap.get_edge(v1, v2)

    def splitTriangle4way( v1, v2, v3 ):
        v12 = splitEdge(v1, v2)
        v13 = splitEdge(v1, v3)
        v23 = splitEdge(v2, v3)
        split_mesh.add_triangle([v1, v12, v13])
        split_mesh.add_triangle([v12, v2, v23])
        split_mesh.add_triangle([v13, v23, v3])
        split_mesh.add_triangle([v12, v23, v13])

    def splitTriangle2way( v1, v2, v3 ):
        v12 = splitEdge(v1, v2)
        split_mesh.add_triangle([v1, v12, v3])
        split_mesh.add_triangle([v12, v2, v3])

    flag = 0

    for face in mesh.get_triangle_iterator():
        if face[0] in CP and face[1] in CP and face[2] in CP:
            flag = 1
            break
            splitTriangle4way( face[0], face[1], face[2] )
        elif face[0] in CP and face[1] in CP:
            flag = 1
            break
            splitTriangle2way( face[0], face[1], face[2] )
        elif face[1] in CP and face[2] in CP:
            flag = 1
            break
            splitTriangle2way( face[1], face[2], face[0] )
        elif face[2] in CP and face[0] in CP:
            flag = 1
            break
            splitTriangle2way( face[2], face[0], face[1] )
        else:
            continue
            split_mesh.add_triangle(face)


    if flag:
        for face in mesh.get_triangle_iterator():
            splitTriangle4way (face[0], face[1], face[2] )
    else:
        for face in mesh.get_triangle_iterator():
            split_mesh.add_triangle(face)


    Debugger.writeMesh('mesh_preprocessed.obj', split_mesh)

    # create function-based triangle filter
    output_mesh = FilterTriangleContainer(split_mesh, mesh_slices)

    for i,tris in enumerate(output_mesh.get_levels()):
        Debugger.writeObj(f'mesh_slice_{i}.obj', output_mesh.get_vertices(), tris, [])

    return output_mesh

   