import numpy as np

class QuadraticSurface:
    def __init__(self, points):
        X = points[:, 0]
        Y = points[:, 1]
        Z = points[:, 2]

        # Design matrix
        A = np.column_stack((X**2, Y**2, X*Y, X, Y, np.ones_like(X)))

        # Solve for coefficients using least squares
        self.coeffs, _, _, _ = np.linalg.lstsq(A, Z, rcond=None)


    def project_point(self, point):
        # Projected point retains (x, y) and ignores the original z.
        return point[:2]

    def unproject_point(self, point):
        a, b, c, d, e, f = self.coeffs
        x, y = point[:2]
        z = a * x**2 + b * y**2 + c * x * y + d * x + e * y + f
        return (x, y, z)
