#!/usr/bin/python3

import pickle

from tkinter import filedialog
from tkinter import *

import numpy as np

import matplotlib.pyplot as plt

from shapely.geometry import Point, LineString
from shapely.geometry.polygon import Polygon


def load_data(fname):
    with open(fname, "rb") as f:
        datadict = pickle.load(f)
    return datadict


def present_data(data):
    try:
        endpoints = data["ends"]
        plt.figure()
        ends = [e[1] for e in endpoints]

        num_bins = 1000
        # the histogram of the data
        n, bins, patches = plt.hist(ends, num_bins, density=1, facecolor='blue', alpha=0.5)
        plt.xlabel("Position")
        plt.ylabel("Freq.")
        plt.title("Detector POSITION histogram")
        plt.grid()
    except Exception as e:
        print(e)

    try:
        opls = data["opls"]
        plt.figure()

        num_bins = 1000
        # the histogram of the data
        n, bins, patches = plt.hist(opls, num_bins, density=1, facecolor='blue', alpha=0.5)
        plt.xlabel("OPL")
        plt.ylabel("Freq.")
        plt.title("Detector OPTICAL PATH LENGTH histogram")
        plt.grid()
    except Exception as e:
        print(e)

    try:
        print("MEAN OPL:", np.mean(opls))
        print("MAX/MIN OPL:", max(opls), min(opls))
    except Exception as e:
        print(e)

    try:
        enddirs = data["dir"]
        plt.figure()

        num_bins = 300
        # the histogram of the data
        angles = []
        wall_normal = [-1,0,0]
        for d in enddirs:
            angle = np.arcsin(np.dot(d,wall_normal))/ (np.linalg.norm(d) * np.linalg.norm(wall_normal))
            angle = 180 * angle/np.pi
            angles.append(angle)
            angles.append(-angle)

        n, bins, patches = plt.hist(angles, num_bins, density=1, facecolor='blue', alpha=0.5)
        plt.xlabel("Angle of exit (yz plane) (Radians)")
        plt.ylabel("Freq.")
        plt.title("Detector EXIT ANGLE histogram")
        plt.grid()
    except Exception as e:
        print(e)

    try:
        print("MEAN OPL:", np.mean(opls))
        print("MAX/MIN OPL:", max(opls), min(opls))
    except Exception as e:
        print(e)

    try:
        plt.figure()
        stage = data["stage"]
        tiles = stage["raypoints"]
        plt.scatter([t[0] for t in tiles], [t[1] for t in tiles])
        plt.plot(*stage["polygon"].exterior.xy, color="green", linewidth=2);
        for e in stage["edges"]:
            edge = stage["edges"][e]
            if edge["type"] == "detector":
                plt.plot([edge["from"][0], edge["to"][0]], [edge["from"][1], edge["to"][1]], color="red", linewidth = 3)
        plt.title("Geometry of " + stage["name"] + " concentrator\n zwalls=" + str(stage["zwalls"]) + ", " + str(stage["numradials"]) + " rays per point")
        plt.show()
        exit()

    except Exception as e:
        print(str(e))

    plt.show()



def main():
    root = Tk()
    root.withdraw()
    fname = filedialog.askopenfilename(initialdir = "./data/",title = "Select file",filetypes = (("pickle files","*.pickle"),("all files","*.*")))
    root.destroy()

    data = load_data(fname)
    print(data.keys())
    present_data(data)

main()
