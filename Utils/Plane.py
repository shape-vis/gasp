import numpy as np
import shapely

from shapely.geometry import Point, Polygon, LinearRing
from sklearn.decomposition import PCA


class Plane:
    def __init__(self, _basis_points):
        # Store the static vertices (immutable part)
        # Step 1: Use PCA to find the plane and the 2D basis within it
        pca = PCA(n_components=3)
        pca.fit(_basis_points)

        # The principal components (eigenvectors) form an orthogonal basis for the best-fit plane
        # print("PCA components", pca.components_)
        self.mean = pca.mean_

        # Step 2: Define the projection matrix using these basis vectors
        projection_matrix12 = np.vstack([pca.components_[0], pca.components_[1]]).T
        projection_matrix13 = np.vstack([pca.components_[0], pca.components_[2]]).T

        centered_points_3d = np.array(_basis_points) - self.mean

        contour2d12 = centered_points_3d @ projection_matrix12
        contour2d13 = centered_points_3d @ projection_matrix13

        poly12 = Polygon(contour2d12)
        poly13 = Polygon(contour2d13)

        if poly12.area > poly13.area:
            self.basis_vec1 = pca.components_[0]
            self.basis_vec2 = pca.components_[1]
            self.projection_matrix = projection_matrix12
            self.poly = poly12
            self.line = LinearRing(contour2d12)

            self.x_range = ( min(c2d[0] for c2d in contour2d12), max(c2d[0] for c2d in contour2d12) )
            self.y_range = ( min(c2d[1] for c2d in contour2d12), max(c2d[1] for c2d in contour2d12) )
        else:
            self.basis_vec1 = pca.components_[0]
            self.basis_vec2 = pca.components_[2]
            self.projection_matrix = projection_matrix13
            self.poly = poly13
            self.line = LinearRing(contour2d13)

            self.x_range = ( min(c2d[0] for c2d in contour2d13), max(c2d[0] for c2d in contour2d13) )
            self.y_range = ( min(c2d[1] for c2d in contour2d13), max(c2d[1] for c2d in contour2d13) )


    def project_points(self, _points_3d):
        centered_points_3d = np.array(_points_3d) - self.mean
        return centered_points_3d @ self.projection_matrix


    def unproject_point(self, p2d):

        # Plane origin and basis vectors from the previous PCA projection
        plane_origin = self.mean  # Origin of the plane in 3D (center of basis points)
        basis_vec1 = self.basis_vec1  # First basis vector in 3D
        basis_vec2 = self.basis_vec2  # Second basis vector in 3D

        # Step 1: Scale the basis vectors by the 2D coordinates
        return plane_origin + p2d[0] * basis_vec1 + p2d[1] * basis_vec2

    def get_polygon(self):
        return self.poly

    def get_line(self):
        return self.line

    def get_range(self):
        return ( self.x_range, self.y_range )
    
    

# # # Example usage:
# basis_points = [
#     [1, 2, 3],
#     [4, 5, 6],
#     [7, 8, 9],
#     [2, 5, 8],
#     [3, 6, 1]
# ]

# plane = Plane(basis_points)

# points_2d = plane.project_points(basis_points)

# with open('plane.obj', 'w') as f:
#     f.write("# Vertices\n")
#     for point in basis_points:
#         f.write(f"v {point[0]} {point[1]} {point[2]}\n")

#     for point_2d in points_2d:
#         p3d = plane.unproject_point(point_2d)
#         # f.write(f"v {point[0]} {point[1]} 0\n")
#         f.write(f"v {p3d[0]} {p3d[1]} {p3d[2]}\n")

#     for i in range(len(basis_points)):
#         f.write(f"l {i+1} {i+1+len(basis_points)}\n")
#         for j in range(i,len(basis_points)):
#             f.write(f"l {i+1+len(basis_points)} {j+1+len(basis_points)}\n")

