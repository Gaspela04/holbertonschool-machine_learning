#!/usr/bin/env python3
matrix = [[1, 3, 9, 4, 5, 8], [2, 4, 7, 3, 4, 0], [0, 3, 4, 6, 1, 5]]
the_middle = []
""" array[2:4] Get middle in six elements, [[9, 4], [7, 3], [4, 6]] """
the_middle = [array[2:4] for array in matrix]
print("The middle columns of the matrix are: {}".format(the_middle))