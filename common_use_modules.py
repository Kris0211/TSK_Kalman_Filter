import numpy as np


def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x


def knots_to_mps(knots) -> float:
    return knots * 0.5144


def read_gps(filename) -> np.array:
    file = open(filename)
    n = 4
    l = np.fromfile(file, sep='\n')
    a = [l[i:i+n] for i in range(0, len(l), n)]
    file.close()
    return np.asarray(a)


def append_gps(filename, arr):
    file = open(filename, "ab")
    np.savetxt(file, arr, delimiter=",")
    file.close()
