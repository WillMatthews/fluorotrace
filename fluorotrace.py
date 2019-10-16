#!/usr/bin/python3

import numpy as np
import copy
from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon
import matplotlib.pyplot as plt
from matplotlib import cm


def get_stage():

    a,b,c,d = (0,0),(0,1),(2,1),(2,0)
    poly = Polygon([a,b,c,d])
    stage = {"polygon":poly,
        "nodes": {
            "A":np.array(a),
            "B":np.array(b),
            "C":np.array(c),
            "D":np.array(d)
        },
        "edges":{
            1:{"dir":np.array([1,0]) , "line": LineString([a,b]) ,"type":"mirror"},
            2:{"dir":np.array([0,-1]) , "line": LineString([b,c]) ,"type":"mirror"},
            3:{"dir":np.array([-1,0]) , "line": LineString([c,d]) ,"type":"detector"},
            4:{"dir":np.array([0,1]) , "line": LineString([d,a]) ,"type":"mirror"}
        }}

    return stage



def normalise(x):
    return x / np.linalg.norm(x)


def reflect(ray, norm):
    raydir = ray["dir"]
    return normalise((np.dot(raydir,norm)) * -2 * norm + raydir)


def sim_ray(ray, stage, dx=0.001):
    detected = False
    itercount = 0
    path = []
    while not detected:
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
                    break
            else:
                print("NO INTERSECTION")
                return

            if do_reflect:
                ray["pos"] -= ray["dir"] * dx
                wall = normalise(stage["edges"][ref]["dir"])
                ray["dir"] = reflect(ray, wall)
                #print("REFLECT!", "iters:",itercount, "ray:", ray)
                #print("\n"*3)
            else:
                print("struck detector")
                return path



stage = get_stage()
rayObj = {"dir": normalise(np.array([-0.2,0.9])) , "pos": np.array([0.5,0.5])}

path = sim_ray(rayObj, stage)

print(path)

xs = [p[0] for p in path]
ys = [p[1] for p in path]
l = np.linspace(0,0.9,len(xs))

plt.scatter(xs,ys,c=cm.hot(l))
plt.plot(*stage["polygon"].exterior.xy);
plt.plot([2,2],[0,1],color="red")
plt.title("Single Ray Trace")
plt.show()
