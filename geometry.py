#!/usr/bin/python3

import numpy as np


def get_shape(shape=""):
    if shape == "rectangle":
        nodes   = [[0,0], [0,1], [2,1], [2,0]]
        edge_types = [ "m",  "m",  "d",  "m"]
    elif shape == "angled":
        nodes   = [[1,0], [0,1], [1,2], [3,2], [3,0]]
        edge_types = [ "m",  "m",  "m", "d",  "m"]
    elif shape == "semicircle":
        nodes = [[-np.sin(np.pi * x), np.cos(np.pi * x)] for x in np.linspace(0,1,20)]
        edge_types = ["m" for x in nodes]
        edge_types[-1] = "d"
        edge_types.append("m")
    elif shape == "triangle1":
        nodes = [[1,0], [0,1], [1,2]]
        edge_types = ["m", "m", "d"]
    elif shape == "triangle2":
        nodes = [[1,0], [0,1], [1,2]]
        edge_types = ["m", "m", "d"]
    else:
        print("Shape", shape, "is not defined! Exiting Thread...")
        exit()

    return nodes, edge_types
