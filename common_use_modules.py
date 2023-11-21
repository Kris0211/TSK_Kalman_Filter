from math import cos, sin

import numpy as np


def clamp(x, min, max):
    if x < min:
        return min
    elif x > max:
        return max
    else:
        return x


def get_velocity_vec(sog: float, cog: float):
    return [sog * cos(cog), sog * sin(cog)]


def knots_to_mps(knots: float) -> float:
    return knots * 0.5144


def read_gps(filename) -> np.array:
    file = open(filename)
    n = 7
    l = np.fromfile(file, sep='\n')
    a = [l[i:i+n] for i in range(0, len(l), n)]
    file.close()
    return a


def append_gps(filename, arr,):
    file = open(filename, "ab")
    np.savetxt(file, arr, delimiter=",")
    file.close()
