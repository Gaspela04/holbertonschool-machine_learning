#!/usr/bin/env python3
"""
Class Neuron that defines a single neuron performing binary
classification
"""


import numpy as np
""" Single neuron performing binary classification """


class Neuron:
    """Neuron performing binary classification"""

    def __init__(self, nx):
        """
        nx: number of input features
        _W: The weights vector for the neuron. Upon instantiation,
        it should be initialized using a random normal distribution.
        _b: The bias for the neuron. Upon instantiation,
        it should be initialized to 0.
        _A: The activated output of the neuron (prediction).
        Upon instantiation, it should be initialized to 0.
        """
        if type(nx) is not int:
            raise TypeError("nx must be an integer")
        if nx < 1:
            raise ValueError("nx must be a positive integer")

        # Private instance attributes
        self.__W = np.ndarray((1, nx))
        self.__W[0] = np.random.normal(size=nx)
        self.__b = 0
        self.__A = 0

    # getter function
    @property
    def W(self):
        """Return weights vector for the neuron """
        return self.__W

    @property
    def b(self):
        """Return bias for the neuron """
        return self.__b

    @property
    def A(self):
        """Return activated output of the neuron """
        return self.__A