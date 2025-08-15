import shapely
import math

import networkx as nx

import Utils.VertexContainer as VC

from shapely.geometry import Point, Polygon, LinearRing
from Utils.Plane import Plane
from Utils.QuadraticSurface import QuadraticSurface


class Contour:
    def __init__(self, vertexContainer, cutTriangles, iso_value):
    
        def interpolatePoint(f0, f1, iso_value, p, q, vertexContainer, temp_array):
            t = VC.get_t( f0, f1, iso_value )
            if f0 != f1 and 0 < t < 1:
                temp_array.append({'edge': (p, q) if p < q else (q, p), 'point': vertexContainer.lerp_verts( p, q, t )}) 
                return True
            return False
            
        def sortsPoints(contour):

            def prepVertex(isoVert):
                return ( isoVert['point'][0], isoVert['point'][1], isoVert['point'][2] )
            
            G = nx.Graph()
            pointMap = {}
            for edge in contour:
                p0 = edge[0]['edge']
                p1 = edge[1]['edge']
                pointMap[p0] = edge[0]
                pointMap[p1] = edge[1]
                G.add_edge(p0, p1)

            orderedNodes = list(nx.dfs_preorder_nodes(G, source = contour[0][0]['edge']))
            # closedLoop = G.has_edge(orderedNodes[-1], contour[0][0]['edge'] )
            return [ prepVertex(pointMap[p]) for p in orderedNodes ]    

        self.contour = None
        self.plane = None

        singleContour = []

        for triangle in cutTriangles:
            
            temp_array = []
            
            v0, v1, v2 = triangle[0], triangle[1], triangle[2]
            f0, f1, f2 = vertexContainer[v0][3], vertexContainer[v1][3], vertexContainer[v2][3]

            bag = []
            if math.isclose(f0 , iso_value): bag.append(v0)
            if math.isclose(f1 , iso_value): bag.append(v1)
            if math.isclose(f2 , iso_value): bag.append(v2)

            if len(bag) == 2:
                temp_array.append({'edge': (bag[0],bag[0]), 'point':vertexContainer[bag[0]]}) 
                temp_array.append({'edge': (bag[1],bag[1]), 'point':vertexContainer[bag[1]]}) 
                
            elif len(bag) == 1:
                pointAdded = False
                if v0 in bag:   pointAdded = interpolatePoint(f1, f2, iso_value, v1, v2, vertexContainer, temp_array)
                elif v1 in bag: pointAdded = interpolatePoint(f0, f2, iso_value, v0, v2, vertexContainer, temp_array)
                elif v2 in bag: pointAdded = interpolatePoint(f0, f1, iso_value, v0, v1, vertexContainer, temp_array)

                if pointAdded: temp_array.append({'edge': (bag[0],bag[0]), 'point':vertexContainer[bag[0]]}) 

            elif len(bag) == 0:
                interpolatePoint(f0, f1, iso_value, v0, v1, vertexContainer, temp_array)
                interpolatePoint(f0, f2, iso_value, v0, v2, vertexContainer, temp_array)
                interpolatePoint(f1, f2, iso_value, v1, v2, vertexContainer, temp_array)

            if len(temp_array) == 2:
                singleContour.append(temp_array)

        # modified_contour, isLoop = organizeContourPoints(singleContour)
        self.contour = sortsPoints(singleContour)

    def get_contour(self):
        return self.contour

    def boundaryPoints(self, minoffset, maxoffset, step=1):
        points = []
        index = []
        for i in range(minoffset,maxoffset,step):
            _i = i % len(self.contour)
            points.append( self.contour[_i] )
            index.append(_i)
        return points, index

    def boundaryPointsInterpolated(self, start, offset, steps):
        points = [ self.contour[start] ]
        index = [ start ]
        for i in range(1,steps+1):
            vp = start + i*offset
            vm = start - i*offset
            _vp0 = int(vp) % len(self.contour)
            _vp1 = int(vp+1) % len(self.contour)
            _vm0 = int(vm) % len(self.contour)
            _vm1 = int(vm+1) % len(self.contour)
            tp = vp-math.floor(vp)
            tm = 1-tp

            points.append( VC.lerp_verts3(self.contour[_vp0], self.contour[_vp1], tp ) )
            index.append(vp)

            points.append( VC.lerp_verts3(self.contour[_vm0], self.contour[_vm1], tm ) )
            index.append(vm)

        return points, index
        
    
    def __len__(self):
        """Get the total length of the combined lists."""
        return len(self.contour)


    def _calculateInterior(self):
        if self.plane is None:
            self.plane = Plane(self.contour)
            self.poly = self.plane.get_polygon()
            self.line = self.plane.get_line()
            x_range, y_range = self.plane.get_range()
            self.x_min, self.x_max = x_range
            self.y_min, self.y_max = y_range


    def _test_interior_points(self, start, offset, steps, buffer):
        largestDistance = -1
        farthestPoint = None
        newPoints = []

        for i in range (1, steps[0]):
            x_val = start[0] + offset[0] * i
            for j in range (1, steps[1]):
                y_val = start[1] + offset[1] * j
                
                p = Point(x_val,y_val)

                if ( p.within(self.poly)):
                    pointDistance = shapely.distance( p, self.line )

                    if pointDistance > buffer:
                        newPoints.append( self.plane.unproject_point( (p.x,p.y) ) )
                    elif pointDistance > largestDistance:
                        largestDistance = pointDistance
                        farthestPoint = p

        if len(newPoints) == 0 and farthestPoint is not None:
            newPoints.append( self.plane.unproject_point( (farthestPoint.x, farthestPoint.y) ) )

        return newPoints



    def _get_count_and_offset(self, num_point_range):

        x_spacing = (self.x_max-self.x_min)/num_point_range[1]
        y_spacing = (self.y_max-self.y_min)/num_point_range[1]
        point_spacing = max(x_spacing, y_spacing)

        self.interior_num_points = ( max(num_point_range[0], int( (self.x_max-self.x_min)/point_spacing ) + 1), 
                                     max(num_point_range[0], int( (self.y_max-self.y_min)/point_spacing ) + 1) )

        self.interior_offset = ( (self.x_max - self.x_min) / (self.interior_num_points[0]), 
                                 (self.y_max - self.y_min) / (self.interior_num_points[1]) )

        # return (x_num_points, y_num_points), (x_offset, y_offset)

    def interiorPoints(self, num_point_range, buffer):

        self._calculateInterior()
        self._get_count_and_offset(num_point_range)

        return self._test_interior_points( (self.x_min,self.y_min), self.interior_offset, self.interior_num_points, buffer)
    

    def interiorPointsByLocation( self, start_loc_3d, range_percent, num_point_range, buffer ):

        self._calculateInterior()

        start_loc = self.plane.project_points(start_loc_3d)
        self._get_count_and_offset(num_point_range)

        # num_points, offset = self._get_count_and_offset(range_percent, num_point_range)
        offset = (self.interior_offset[0] * range_percent, self.interior_offset[1] * range_percent)

        x_min = start_loc[0] - offset[0] * self.interior_num_points[0]
        y_min = start_loc[1] - offset[1] * self.interior_num_points[1]

        return self._test_interior_points( (x_min,y_min), offset, (2*self.interior_num_points[0], 2*self.interior_num_points[1]), buffer)




#######################################################################################################

def createFixedContours(vertexContainer, cutTriangles, contour_space, _lowest, _highest ):

    lowest = min(_lowest, _highest)
    highest = max(_lowest, _highest)

    total_diff = highest - lowest

    numberOfContours = max(1, int (total_diff / contour_space))

    diff = total_diff / (numberOfContours + 1)
    iso_array = [ lowest + (i + 1) * diff for i in range (numberOfContours) ]

    return iso_array, [ Contour(vertexContainer, cutTriangles, iso_value) for iso_value in iso_array ]


def createAdaptiveContours(vertexContainer, cutTriangles, old_iso_array, _lowest, _highest, len_array, max_length ):

    lowest = min(_lowest, _highest)
    highest = max(_lowest, _highest)

    total_diff = highest - lowest

    # numberOfContours = max(1, int (total_diff / contour_space))
    numberOfContours = len(old_iso_array)

    # diff = total_diff / (numberOfContours + 1)
    # old_iso_array = [ lowest + (i + 1) * diff for i in range (numberOfContours) ]

    ia = [ lowest, *old_iso_array, highest ]

    iso_array = []
    for i in range(numberOfContours+1):
        if i != 0: iso_array.append(ia[i])
        # print( " > ", len_array[i], ia[i], ia[i+1] )
        if len_array[i] > max_length:
            sub = int(len_array[i]/max_length)
            for j in range(sub):
                t = (j+1)/(sub+1)
                # print("    > ", ia[i]*(1-t)+ia[i+1]*t )
                iso_array.append(ia[i]*(1-t)+ia[i+1]*t)

    # print(old_iso_array)
    # print(iso_array)
    # print()


    return iso_array, [ Contour(vertexContainer, cutTriangles, iso_value) for iso_value in iso_array ]
