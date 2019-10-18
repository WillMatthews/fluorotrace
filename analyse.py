#!/usr/bin/python3

import pickle

import numpy as np

import matplotlib.pyplot as plt



def load_data(fname):
    with open(fname, "rb") as f:
        datadict = pickle.load(f)
    return datadict


def present_data(endpoints, opls, enddirs):
    try:
        plt.figure()
        ends = [e[1] for e in endpoints]

        num_bins = 1000
        # the histogram of the data
        n, bins, patches = plt.hist(ends, num_bins, density=1, facecolor='blue', alpha=0.5)
        plt.xlabel("Position")
        plt.ylabel("Freq.")
        plt.title("Detector POSITION histogram")
    except Exception:
        pass

    try:
        plt.figure()

        num_bins = 1000
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

    try:
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
    except Exception:
        pass

    try:
        print("MEAN OPL:", np.mean(opls))
        print("MAX/MIN OPL:", max(opls), min(opls))
    except Exception:
        pass


    plt.show()



def main():

    data = load_data("./data-2019-10-18_14:23:57.pickle")
    print(data.keys())
    present_data(data["ends"], data["opls"], data["dir"])

main()
