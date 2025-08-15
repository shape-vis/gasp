import itertools
import Utils.FileIO


class MeshContainer:
    def __init__(self, static_triangles=None, dynamic_triangles=None, static_edges=None, dynamic_edges=None, static_vertices=None, dynamic_vertices=None):
        # Store the static triangles (immutable part)
        if static_triangles is None:
            self._static_triangles = []
        else:
            self._static_triangles = static_triangles

        # Initialize the dynamic triangles (mutable part)
        if dynamic_triangles is None:
            self._dynamic_triangles = []
        else:
            self._dynamic_triangles = dynamic_triangles

        # Store the static edges (immutable part)
        if static_edges is None:
            self._static_edges = []
        else:
            self._static_edges = static_edges
        
        # Initialize the dynamic edges (mutable part)
        if dynamic_edges is None:
            self._dynamic_edges = []
        else:
            self._dynamic_edges = dynamic_edges

        # Store the static vertices (immutable part)
        if static_vertices is None:
            self._static_vertices = []
        else:
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
    
    def add_edge(self, edge):
        """Add a new edge to the dynamic list."""
        self._dynamic_edges.append(edge)
        return len(self._static_edges) + len(self._dynamic_edges) - 1
    
    def add_triangle(self, triangle):
        """Add a new triangle to the dynamic list."""
        self._dynamic_triangles.append(triangle)
        return len(self._static_triangles) + len(self._dynamic_triangles) - 1
    
    def get_vertex(self, index):
        """Access elements as if the two lists are one."""
        if index < len(self._static_vertices):
            return self._static_vertices[index]
        else:
            return self._dynamic_vertices[index - len(self._static_vertices)]
        
    def get_edge(self, index):
        """Access elements as if the two lists are one."""
        if index < len(self._static_edges):
            return self._static_edges[index]
        else:
            return self._dynamic_edges[index - len(self._static_edges)]
        
    def get_triangle(self, index):
        """Access elements as if the two lists are one."""
        if index < len(self._static_triangles):
            return self._static_triangles[index]
        else:
            return self._dynamic_triangles[index - len(self._static_triangles)]

    def get_vertex_length(self):
        """Get the total length of the combined lists."""
        return len(self._static_vertices) + len(self._dynamic_vertices)
    
    def get_edge_length(self):
        """Get the total length of the combined lists."""
        return len(self._static_edges) + len(self._dynamic_edges)
    
    def get_triangle_length(self):
        """Get the total length of the combined lists."""
        return len(self._static_triangles) + len(self._dynamic_triangles)

    def get_vertex_iterator(self):
        """Allow iteration over both lists as one."""
        return itertools.chain(self._static_vertices, self._dynamic_vertices)
        # return iter(self._static_vertices + self._dynamic_vertices)
    
    def get_edge_iterator(self):
        """Allow iteration over both lists as one."""
        return itertools.chain(self._static_edges, self._dynamic_edges)
        # return iter(self._static_edges + self._dynamic_edges)
    
    def get_triangle_iterator(self):
        """Allow iteration over both lists as one."""
        return itertools.chain(self._static_triangles, self._dynamic_triangles)
        # return iter(self._static_triangles + self._dynamic_triangles)
    
    def get_static_vertices(self):
        return self._static_vertices
    
    def get_dynamic_vertices(self):
        return self._dynamic_vertices
    
    def get_static_edges(self):
        return self._static_edges
    
    def get_dynamic_edges(self):
        return self._dynamic_edges
    
    def get_static_triangles(self):
        return self._static_triangles
    
    def get_dynamic_triangles(self):
        return self._dynamic_triangles
    
    def writeObj(self, filename):
        Utils.FileIO.writeObj(filename, self.get_vertex_iterator(), self.get_triangle_iterator(), self.get_edge_iterator())
        
