import numpy as np
import itertools


def rigidity(A):
    assert A.shape[0] == A.shape[1]
    num_points = A.shape[0]
    A = np.logical_or(A, A.T)
    pnt = np.random.rand(num_points, 3)
    edges = list(itertools.combinations((range(num_points)), 2))

    n = num_points
    m = len(edges)
    d = 3

    R = np.zeros(shape=(m, d * n))
    for ii, (u, v) in enumerate(edges):
        if A[u][v]:
            R[ii, u * 3:u * 3 + 3] = pnt[u, :] - pnt[v, :]
            R[ii, v * 3:v * 3 + 3] = pnt[v, :] - pnt[u, :]

    return R
