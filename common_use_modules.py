import math
from math import cos, sin, radians, pi

import numpy as np

earth_radius = 6378137


def clamp(x, _min, _max):
    if x < _min:
        return _min
    elif x > _max:
        return _max
    return x


def get_velocity_vec(sog: float, cog: float) -> [float, float]:
    return [sog * sin(cog), sog * cos(cog)]


def knots_to_mps(knots: float) -> float:
    return knots * 0.5144


def read_gps(filename) -> np.array:
    file = open(filename)
    n = 4
    l = np.fromfile(file, sep='\n')
    a = [l[i:i+n] for i in range(0, len(l), n)]
    file.close()
    return a


def append_gps(filename, arr,):
    file = open(filename, "ab")
    np.savetxt(file, arr, delimiter=",")
    file.close()


def predict_physics_pos(start_pos, sog, cog, dt):
    delta_x = sog * sin(radians(cog)) * dt
    delta_y = sog * cos(radians(cog)) * dt

    lat = start_pos[1] + 180 / pi * delta_y / earth_radius
    lon = start_pos[0] + 180 / pi / sin(radians(start_pos[1])) * delta_x / earth_radius

    return np.array([lon, lat])


def to_lin_pos(geo_pos):
    x1 = earth_radius * math.radians(geo_pos[0])
    y1 = earth_radius * math.radians(math.tan(math.pi / 4 + math.radians(geo_pos[1]) / 2))
    return np.array([x1, y1])


def to_plane_pos(point: np.ndarray):
    point_radians = point * pi / 180
    x = earth_radius * cos(point_radians[1]) * cos(point_radians[0])
    y = earth_radius * cos(point_radians[1]) * sin(point_radians[0])
    z = earth_radius * sin(point_radians[1])

    return np.array([x, y, z])


def to_geo_pos(point: np.ndarray):
    r = np.sqrt(np.sum(np.power(point, 2)))
    lon = math.degrees(np.arctan(point[1] / point[0]))
    lat = math.degrees(np.arcsin(point[2] / r))

    return np.array([lon, lat])
