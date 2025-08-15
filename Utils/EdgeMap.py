

class EdgeMap:
    def __init__(self):
        # Store the static vertices (immutable part)
        self.edge_map = {}

    def exists(self, v1, v2):
        edge = (min(v1, v2), max(v1, v2))
        return edge in self.edge_map
    
    def add_edge(self, v1, v2, vertex_id):
        edge = (min(v1, v2), max(v1, v2))
        self.edge_map[edge] = vertex_id
        return vertex_id
    
    def get_edge(self, v1, v2):
        edge = (min(v1, v2), max(v1, v2))
        return self.edge_map[edge]
    
    