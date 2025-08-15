

class VertexContainer:
    def __init__(self, static_vertices, dynamic_vertices=None):
        # Store the static vertices (immutable part)
        self._static_vertices = static_vertices

        # Initialize the dynamic vertices (mutable part)
        if dynamic_vertices is None:
            self._dynamic_vertices = []
        else:
            self._dynamic_vertices = dynamic_vertices

    def add_vertex(self, vertex):
        """Add a new vertex to the dynamic list."""
        self._dynamic_vertices.append(vertex)
        return len(self._static_vertices) + len(self._dynamic_vertices) - 1
    
    def get_vertex(self, index):
        if index < len(self._static_vertices):
            return self._static_vertices[index]
        else:
            return self._dynamic_vertices[index - len(self._static_vertices)]

    def __getitem__(self, index):
        """Access elements as if the two lists are one."""
        if index < len(self._static_vertices):
            return self._static_vertices[index]
        else:
            return self._dynamic_vertices[index - len(self._static_vertices)]

    def __len__(self):
        """Get the total length of the combined lists."""
        return len(self._static_vertices) + len(self._dynamic_vertices)

    def __iter__(self):
        """Allow iteration over both lists as one."""
        return iter(self._static_vertices + self._dynamic_vertices)
    
    def get_static_vertices(self):
        return self._static_vertices
    
    def get_dynamic_vertices(self):
        return self._dynamic_vertices

    def lerp_verts(self, index0, index1, t):
        vert0 = self.get_vertex(index0)
        vert1 = self.get_vertex(index1)
        return [(1-t)*vert0[i] + t*vert1[i] for i in range(4)]

    def add_lerp_vert3(self, index0, index1, t):
        vert0 = self.get_vertex(index0)
        vert1 = self.get_vertex(index1)
        return self.add_vertex( [(1-t)*vert0[i] + t*vert1[i] for i in range(3)] )

    def add_centroid3(self, idx0, idx1, idx2):
        v0 = self.get_vertex(idx0)
        v1 = self.get_vertex(idx1)
        v2 = self.get_vertex(idx2)
        return self.add_vertex( [ (v0[i] + v1[i] + v2[i]) / 3 for i in range(3) ] )
        


def vertex_vertex_distance(p0,p1):
    return ((p0[0] - p1[0])**2 + (p0[1] - p1[1])**2 + (p0[2] - p1[2])**2)**0.5

def lerp_verts(vert0, vert1, t):
    return [(1-t)*vert0[i] + t*vert1[i] for i in range(4)]

def lerp_verts3(vert0, vert1, t):
    return [(1-t)*vert0[i] + t*vert1[i] for i in range(3)]

def get_t( f0, f1, cpVal ):
    return 0.5 if f0 == f1 else (cpVal - f0) / (f1 - f0)

