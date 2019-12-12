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
import geometry
import lux

N1 = 1.492 # acrylic?
N2 = 1.00027 # air at STP
CRIT_ANGLE = np.arcsin(N2/N1)
print("Assuming Critical Angle", "{:0.3f}".format(CRIT_ANGLE * 180/np.pi), "Deg")


def get_stage(shape="rectangle", zwalls=(0,1)):
    print("Building Stage for",shape,"...")
    nodes, edge_types = geometry.get_shape(shape)

    poly = Polygon([n for n in nodes])
    stage = {"name":shape,
        "polygon":poly,
        "zwalls":zwalls,
        "edges":{},
        "xrange": [min([x[0] for x in nodes]), max([x[0] for x in nodes])],
        "yrange": [min([x[1] for x in nodes]), max([x[1] for x in nodes])],
        "zrange": [zwalls[0], zwalls[1]]
        }

    for i in range(len(nodes)):
        edge1 = nodes[i]
        if i == len(nodes)-1:
            edge2 = nodes[0]
        else:
            edge2 = nodes[i+1]

        dx, dy = edge2[0] - edge1[0], edge2[1] - edge1[1]
        if edge_types[i] == "m":
            t = "mirror"
        elif edge_types[i] == "dump":
            t = "dump"
        elif edge_types[i] == "d":
            t = "detector"
        else:
            raise Exception
        #print(edge1, edge2)
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


def normalise(x):
    if np.linalg.norm(x) == 0:
        raise ValueError("Vector presented to normalise() had norm of zero")
    return x / np.linalg.norm(x)


def reflect(ray, norm):
    raydir = normalise(np.array(ray[0]))
    norm = normalise(np.array(norm))
    return normalise((np.dot(raydir,norm)) * -2 * norm + raydir)


def ray_angle(ray, norm):
    raydir = normalise(np.array(ray[0]))
    norm = np.array(norm)
    return np.arccos(np.dot(raydir, norm))


def is_outside_crit_angle(ray, wall, crit_angle=np.pi/2):
    angle = np.abs(ray_angle(ray, wall)) - np.pi/2
    #if angle < crit_angle:
    #    print("TIR-TERMINATED RAY: GOT ANGLE", "{:0.2f}".format(angle), "{:0.2f}".format(crit_angle))
    return True if angle > crit_angle else False


#@profile
def sim_ray(ray, stage, dl=0.1, max_steps=10000):
    path, itercount, detected  = [], 0, False
    minz, maxz = stage["zwalls"]
    while not detected:
        if itercount > max_steps:
            return None, None
        itercount += 1
        oldray = ray
        path.append(oldray[1])
        ray = (ray[0], ray[1] + ray[0] * dl)

        if not stage["polygon"].contains(Point(ray[1][0], ray[1][1])):
            ## find intersecting line...
            test_line = LineString([(ray[1][0], ray[1][1]), (oldray[1][0], oldray[1][1])])
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
                itercount -= 1
                wall = normalise(stage["edges"][ref]["dir"])
                if is_outside_crit_angle(ray, wall, CRIT_ANGLE):
                    ray = (reflect(ray, wall), ray[1] - ray[0] * dl)
                else:
                    return None, None # Ray Exited
            else:
                if is_dump:
                    return None, None # Ray has hit beam dump
                return path, itercount * dl

        if ray[1][2] < minz:
            itercount -= 1
            wall = [0, 0, 1]
            if is_outside_crit_angle(ray, wall, CRIT_ANGLE):
                ray = (reflect(ray, wall), ray[1] - ray[0] * dl)
            else:
                return None, None # Ray Exited
        elif ray[1][2] > maxz:
            itercount -= 1
            wall = [0, 0, -1]
            if is_outside_crit_angle(ray, wall, CRIT_ANGLE):
                ray = (reflect(ray, wall), ray[1] - ray[0] * dl)
            else:
                return None, None # Ray Exited


def add_raypoints(stage, num_raypoints=1000, num_radials=200):
    raypoints, cnt = [], 0
    while len(raypoints) < num_raypoints:
        x = random.random()*(stage["xrange"][1]-stage["xrange"][0])+wstage["xrange"][0]
        y = random.random()*(stage["yrange"][1]-stage["yrange"][0])+stage["yrange"][0]
        z = random.random()*(stage["zrange"][1]-stage["zrange"][0])+stage["zrange"][0]
        if stage["polygon"].contains(Point(x, y)):
            raypoints.append([x, y, z])

    stage["raypoints"] = raypoints
    stage["numradials"] = num_radials
    print(stage["name"] + ":", len(raypoints), "RayPoints Added: ", len(raypoints) * num_radials, "rays to be traced")


def run_trial(stage, show_single_trace=False, step_size=0.1, max_steps=10000,use_progbar=True):

    tiles = stage["raypoints"]

    endpoints, opls, enddirs = [], [], []
    if use_progbar:
        loopiter = progressbar.progressbar(range(len(tiles)), redirect_stdout=False)
    else:
        loopiter = range(len(tiles))
    for j in loopiter:
        tile = tiles[j]
        print(stage["name"] + ": TILE", j+1, "/", len(tiles))
        raydirs = random_fibonacci_sphere(stage["numradials"])
        for i, raydir in enumerate(raydirs):
            raydir_norm = normalise(np.array(raydir))
            rayObj = (raydir_norm, np.array(tile))
            path, opl = sim_ray(rayObj, stage, dl=step_size, max_steps=max_steps)
            if path is not None and len(path) > 3:
                last_point = path[-1]
                last_point2 = path[-3]
                endpoints.append(last_point)
                end_dir = normalise([ x-y for x,y in zip(last_point,last_point2)])
                enddirs.append(end_dir)
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
    with open("./data/data-" + stage["name"] + "-{date:%Y-%m-%d_%H:%M:%S}.pickle".format(date=datetime.datetime.now()), "wb") as f:
        pickle.dump(datadict, f)


def main():
    f = lux.Flag()
    f.busy()
    #shapes = ["rectangle", "semicircle", "triangle1","angled"]
    shapes = ["angled"]
    for shp in shapes:
        stage = get_stage(shape=shp, zwalls=(0, 0.1))
        add_raypoints(stage, num_raypoints=10000, num_radials=1000)

        endpoints, opls, enddirs = run_trial(stage, show_single_trace=True, step_size = 0.01, max_steps=10000)
        save_data(endpoints, opls, enddirs, stage)
    f.ready()


def external_run(shape="", num_raypoints=1000, num_radials=200, max_steps=10000, zwalls=(0,0.1), step_size=0.01):
    if shape != "":
        stage = get_stage(shape=shape,zwalls=zwalls)
        add_raypoints(stage, num_raypoints=num_raypoints, num_radials=num_radials)
        endpoints, opls, enddirs = run_trial(stage, show_single_trace=False, step_size = step_size, max_steps=max_steps,use_progbar=False)
        save_data(endpoints, opls, enddirs, stage)


if __name__ == "__main__":
    main()
    print("EOF")
