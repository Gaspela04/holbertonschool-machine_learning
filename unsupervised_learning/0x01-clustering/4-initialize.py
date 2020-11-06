#!/usr/bin/env python3
"""
Initialize GMM
"""


import numpy as np
kmeans = __import__('1-kmeans').kmeans


def initialize(X, k):
    """
    X is a numpy.ndarray of shape (n, d) containing the data set
    k is a positive integer containing the number of clusters
    You are not allowed to use any loops
    Returns: pi, m, S, or None, None, None on failure
    pi is a numpy.ndarray of shape (k,) containing the priors for each cluster,
    initialized evenly
    m is a numpy.ndarray of shape (k, d) containing the centroid means for
    each cluster, initialized with K-means
    S is a numpy.ndarray of shape (k, d, d) containing the covariance matrices
    for each cluster, initialized as identity matrices
    You should use kmeans = __import__('1-kmeans').kmeans
    """
    if type(k) is not int or k < 1 or type(X) is not np.ndarray or X.ndim != 2:
        return None, None, None

    pi = np.full((k,), 1 / k)
    m = kmeans(X, k)[0]
    S = np.full((k, X.shape[1], X.shape[1]), np.identity(X.shape[1]))
    return pi, m, S
