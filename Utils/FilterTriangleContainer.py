import itertools
from Utils.MeshContainer import MeshContainer
import math


class FilterTriangleContainer:
    def __init__(self, mesh : MeshContainer, subd_levels=20):
        
        self.vertices = mesh.get_static_vertices() + mesh.get_dynamic_vertices()

        minVal = float('inf')
        maxVal = float('-inf')

        for v in self.vertices:
            f = v[3]
            minVal = min(minVal, f)
            maxVal = max(maxVal, f)

        minVal = minVal - 0.0001
        maxVal = maxVal + 0.0001
        
        levels = [ [] for i in range(0, subd_levels) ]
        levelMin = [ maxVal for i in range(0, subd_levels) ]
        levelMax = [ minVal for i in range(0, subd_levels) ]
                
        for t in mesh.get_triangle_iterator():
            avgVal = (self.vertices[t[0]][3] + self.vertices[t[1]][3] + self.vertices[t[2]][3]) / 3.0
            curLevel = int( (avgVal - minVal) / (maxVal - minVal) * subd_levels )
            levelMin[curLevel] = min(levelMin[curLevel], self.vertices[t[0]][3], self.vertices[t[1]][3], self.vertices[t[2]][3])
            levelMax[curLevel] = max(levelMax[curLevel], self.vertices[t[0]][3], self.vertices[t[1]][3], self.vertices[t[2]][3])
            levels[curLevel].append(t)

        self.levels = levels
        self.levelMin = levelMin
        self.levelMax = levelMax


    def get_levels(self):
        return self.levels
    
    def get_vertices(self):
        return self.vertices

    def get_vertex(self, idx):
        return self.vertices[idx]
        
    def get_vertex_iterator(self):
        """Allow iteration over both lists as one."""
        return iter(self.vertices)

    def get_iterator(self, minV, maxV):
        if minV > maxV:
            print(f'Error: minV > maxV: {minV} > {maxV}')
        #     minV, maxV = maxV, minV
        idx = filter(lambda x: self.levelMax[x] >= minV and self.levelMin[x] <= maxV, range(len(self.levels)))
        out = list(map( lambda x: self.levels[x], idx))
        
        # print(f'id: {idx}')
        
        return itertools.chain(*out)
    
