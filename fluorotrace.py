#!/usr/bin/python3

import numpy as np
import copy
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
from matplotlib import cm
import random

def get_stage(shape="rectangle"):
    print("Building Stage")
    if shape == "rectangle":
        nodes   = [[0,0],[0,1],[2,1],[2,0]]
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


    poly = Polygon([n for n in nodes])
    stage = {"polygon":poly,
        "edges":{},
        "xrange": [min([x[0] for x in nodes]),max([x[0] for x in nodes])],
        "yrange": [min([x[1] for x in nodes]),max([x[1] for x in nodes])]
        }

    for i in range(len(nodes)):
        edge1 = nodes[i]
        if i == len(nodes)-1:
            edge2 = nodes[0]
        else:
            edge2 = nodes[i+1]

        dx, dy = edge2[0]-edge1[0], edge2[1] - edge1[1]
        if edge_types[i] == "m":
            t = "mirror"
        elif edge_types[i] == "dump":
            t = "dump"
        elif edge_types[i] == "d":
            t = "detector"
        else:
            raise Exception
        print(edge1, edge2)
        stage["edges"][i] = {"from":edge1, "to": edge2, "dir":np.array([dy,-dx]) , "line": LineString([edge1, edge2]) ,"type":t}

    return stage



def normalise(x):
    return x / np.linalg.norm(x)


def reflect(ray, norm):
    raydir = ray["dir"]
    return normalise((np.dot(raydir,norm)) * -2 * norm + raydir)


def sim_ray(ray, stage, dx=0.1):
    detected = False
    itercount = 0
    path = []
    while not detected:
        if itercount > 10000:
            return None, None
        itercount += 1
        oldray = copy.deepcopy(ray)
        path.append(oldray["pos"])
        ray["pos"] += ray["dir"] * dx
        if not stage["polygon"].contains(Point(ray["pos"][0], ray["pos"][1])):
            ## find intersecting line...
            test_line = LineString([(ray["pos"][0], ray["pos"][1]), (oldray["pos"][0], oldray["pos"][1])])
            for e in stage["edges"].keys():
                #print("==============")
                #print(test_line)
                #print(stage["edges"][e]["line"])
                intersection = (stage["edges"][e]["line"].intersection(test_line))
                #print(intersection)
                if not intersection.is_empty:
                    do_reflect, ref = (True if stage["edges"][e]["type"] == "mirror" else False), e
                    is_dump = (True if stage["edges"][e]["type"] == "dump" else False)
                    break
            else:
                print("NO INTERSECTION ERROR")
                return None, None

            if do_reflect:
                ray["pos"] -= ray["dir"] * dx
                wall = normalise(stage["edges"][ref]["dir"])
                ray["dir"] = reflect(ray, wall)
                #print("REFLECT!", "iters:",itercount, "ray:", ray)
                #print("\n"*3)
            else:
                if is_dump:
                    return None, None
                #print("Struck detector")
                return path, itercount * dx



stage = get_stage(shape="semicircle")


num_radials = 1000

xs = np.linspace(stage["xrange"][0]+0.1,stage["xrange"][1]-0.1,15)
ys = np.linspace(stage["yrange"][0]+0.1,stage["yrange"][1]-0.1,10)

tiles = []
for x in xs:
    for y in ys:
        if stage["polygon"].contains(Point(x, y)):
            tiles.append([x,y])
            print("Tile Added", (x,y))

# tiles = [[0.5, 0.5]]

endpoints = []
opls = []
plt.figure()
for j, tile in enumerate(tiles):
    phi = random.random()
    print("TILE", j+1, "/", len(tiles))
    for i in range(num_radials):
        rayObj = {"dir": normalise(np.array([np.sin(phi + 2 * np.pi * i/num_radials),np.cos(phi + 2 * np.pi * i/num_radials)])) , "pos": np.array(tile)}
        #print("RAY", i+1, "/", num_radials)
        path, opl = sim_ray(rayObj, stage)
        if path is not None:
            endpoints.append(path[-1])
        if opl is not None:
            opls.append(opl)

        if path is not None:
            pass
            #xs = [p[0] for p in path]
            #ys = [p[1] for p in path]
            #plt.plot(xs,ys)

plt.scatter([t[0] for t in tiles], [t[1] for t in tiles])
plt.plot(*stage["polygon"].exterior.xy, color="green", linewidth=2);
for e in stage["edges"]:
    edge = stage["edges"][e]
    if edge["type"] == "detector":
        plt.plot([edge["from"][0], edge["to"][0]], [edge["from"][1], edge["to"][1]], color="red", linewidth = 3)
plt.title("Geometry")


try:
    plt.figure()
    ends = [e[1] for e in endpoints]

    num_bins = 100
    # the histogram of the data
    n, bins, patches = plt.hist(ends, num_bins, density=1, facecolor='blue', alpha=0.5)
    plt.xlabel("Position")
    plt.ylabel("Freq.")
    plt.title("Detector POSITION histogram")
except Exception:
    pass


try:
    plt.figure()

    num_bins = 100
    # the histogram of the data
    n, bins, patches = plt.hist(opls, num_bins, density=1, facecolor='blue', alpha=0.5)
    plt.xlabel("OPL")
    plt.ylabel("Freq.")
    plt.title("Detector OPTICAL PATH LENGTH histogram")
except Exception:
    pass

try:
    print("MEAN OPL:", np.mean(opls))
    print("MAX/MIN OPL:", max(opls), min(opls))
except Exception:
    pass

plt.show()
