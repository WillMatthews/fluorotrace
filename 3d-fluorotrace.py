#!/usr/bin/python3

import pickle
import copy
import random
import datetime

import numpy as np

from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon

import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D

import progressbar


def get_stage(shape="rectangle", zwalls=(0,1)):
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
    stage = {"name":shape,
        "polygon":poly,
        "zwalls":zwalls,
        "edges":{},
        "xrange": [min([x[0] for x in nodes]),max([x[0] for x in nodes])],
        "yrange": [min([x[1] for x in nodes]),max([x[1] for x in nodes])],
        "zrange": [zwalls[0], zwalls[1]]
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
        stage["edges"][i] = {"from":edge1, "to":edge2, "dir":np.array([dy, -dx, 0]), "line":LineString([edge1, edge2]), "type":t}

    return stage


def rotation_matrix(axis, theta):
    """
    Return the rotation matrix associated with counterclockwise rotation about
    the given axis (vec) by theta radians.
    """
    axis = np.asarray(axis)
    axis = axis / np.sqrt(np.dot(axis, axis))
    a = np.cos(theta / 2.0)
    b, c, d = -axis * np.sin(theta / 2.0)
    aa, bb, cc, dd = a * a, b * b, c * c, d * d
    bc, ad, ac, ab, bd, cd = b * c, a * d, a * c, a * b, b * d, c * d
    return np.array([[aa + bb - cc - dd, 2 * (bc + ad), 2 * (bd - ac)],
                     [2 * (bc - ad), aa + cc - bb - dd, 2 * (cd + ab)],
                     [2 * (bd + ac), 2 * (cd - ab), aa + dd - bb - cc]])


def random_fibonacci_sphere(samples):
    rnd = random.random()
    rand_rot_mat = rotation_matrix([random.random(), random.random(), random.random()], 2*np.pi*random.random())
    points = []
    offset = 2./samples
    increment = np.pi * (3. - np.sqrt(5.));

    for i in range(samples):
        y = ((i * offset) - 1) + (offset / 2);
        r = np.sqrt(1 - pow(y,2))

        phi = ((i + rnd) % samples) * increment

        x = np.cos(phi) * r
        z = np.sin(phi) * r

        points.append(np.dot(rand_rot_mat, [x,y,z]))

    return points

    # fig = plt.figure()
    # ax = fig.add_subplot(111, projection='3d')
    # xs = random_fibonacci_sphere(100)
    # ax.scatter([x[0] for x in xs], [x[1] for x in xs], [x[2] for x in xs])
    # plt.show()
    # exit()


def normalise(x):
    return x / np.linalg.norm(x)


def reflect(ray, norm):
    raydir = np.array(ray["dir"])
    norm = np.array(norm)
    return normalise((np.dot(raydir,norm)) * -2 * norm + raydir)


def sim_ray(ray, stage, dl=0.1,max_steps=10000):
    path, itercount, detected  = [], 0, False
    minz, maxz = stage["zwalls"]
    while not detected:
        if itercount > max_steps:
            return None, None
        itercount += 1
        oldray = copy.deepcopy(ray)
        path.append(oldray["pos"])
        ray["pos"] += ray["dir"] * dl
        if not stage["polygon"].contains(Point(ray["pos"][0], ray["pos"][1])):
            ## find intersecting line...
            test_line = LineString([(ray["pos"][0], ray["pos"][1]), (oldray["pos"][0], oldray["pos"][1])])
            for e in stage["edges"].keys():
                intersection = (stage["edges"][e]["line"].intersection(test_line))
                if not intersection.is_empty:
                    do_reflect, ref = (True if stage["edges"][e]["type"] == "mirror" else False), e
                    is_dump = (True if stage["edges"][e]["type"] == "dump" else False)
                    break
            else:
                print("NO INTERSECTION ERROR")
                return None, None

            if do_reflect:
                ray["pos"] -= ray["dir"] * dl
                wall = normalise(stage["edges"][ref]["dir"])
                ray["dir"] = reflect(ray, wall)
            else:
                if is_dump:
                    return None, None
                return path, itercount * dl

        if ray["pos"][2] < minz:
            ray["dir"] = reflect(ray,[0,0,1])
        elif ray["pos"][2] > maxz:
            ray["dir"] = reflect(ray,[0,0,-1])


def add_raypoints(stage, spacetup, num_radials):
    (xd, yd, zd) = spacetup
    xs = np.linspace(stage["xrange"][0]+0.1, stage["xrange"][1]-0.1, xd)
    ys = np.linspace(stage["yrange"][0]+0.1, stage["yrange"][1]-0.1, yd)
    zs = np.linspace(stage["zrange"][0]+0.1, stage["zrange"][1]-0.1, zd)

    tiles, cnt = [], 0
    for x in xs:
        for y in ys:
            if stage["polygon"].contains(Point(x, y)):
                ts = [[x,y,z] for z in zs]
                for t in ts:
                        tiles.append(t)
                        cnt += 1

    stage["raypoints"] = tiles
    stage["numradials"] = num_radials
    print(cnt, "RayPoints Added: ", cnt * num_radials, "rays to be traced")



def run_trial(stage, spacetup, num_radials, show_single_trace=False, step_size=0.1, max_steps=10000):

    add_raypoints(stage, spacetup, num_radials)
    tiles = stage["raypoints"]

    endpoints, opls, enddirs = [], [], []
    for j in progressbar.progressbar(range(len(tiles)), redirect_stdout=True):
        tile = tiles[j]
        print("TILE", j+1, "/", len(tiles))
        raydirs = random_fibonacci_sphere(num_radials)
        for i, raydir in enumerate(raydirs):
            raydir_norm = normalise(np.array(raydir))
            rayObj = {"dir": raydir_norm , "pos": np.array(tile)}
            path, opl = sim_ray(rayObj, stage, dl=step_size, max_steps=max_steps)
            if path is not None:
                last_point = path[-1]
                last_point2 = path[-2]
                endpoints.append(last_point)
                end_dir = normalise([ x-y for x,y in zip(last_point,last_point2) ])
                enddirs.append(end_dir)
            if opl is not None:
                opls.append(opl)

            if path is not None and show_single_trace:
                fig = plt.figure()
                ax = fig.add_subplot(111, projection='3d')
                ax.scatter([x[0] for x in path], [x[1] for x in path], [x[2] for x in path])
                break
        if show_single_trace:
            break

    if show_single_trace:
        ax.scatter([t[0] for t in tiles], [t[1] for t in tiles], [t[2] for t in tiles])
        plt.plot(*stage["polygon"].exterior.xy, color="green", linewidth=2);
        for e in stage["edges"]:
            edge = stage["edges"][e]
            if edge["type"] == "detector":
                plt.plot([edge["from"][0], edge["to"][0]], [edge["from"][1], edge["to"][1]], color="red", linewidth = 3)
        plt.title("Geometry")
        plt.show()
        exit()

    return endpoints, opls, enddirs


def save_data(endpoints, opls, enddirs, stage):
    datadict = {"ends":endpoints, "opls":opls, "dir":enddirs, "stage":stage}
    with open("./data/data-" + stage["name"] + "-{date:%Y-%m-%d_%H:%M:%S}.pickle".format( date=datetime.datetime.now()), "wb") as f:
        pickle.dump(datadict, f)


def main():
    stage = get_stage(shape="semicircle",zwalls=(0,0.1))
    num_radials = 3
    endpoints, opls, enddirs = run_trial(stage, (15,15,4), num_radials,show_single_trace=False, step_size = 0.01, max_steps= 10000)
    save_data(endpoints, opls, enddirs, stage)


main()
print("EOF")
