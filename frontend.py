import tkinter

import numpy as np
import tkinter as tk
from tkinter import filedialog as fd
from tkinter.messagebox import showwarning
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import common_use_modules as utils
from datetime import datetime

from kalman_filter import EzKalmanFilter, KalmanFilter


def draw_map(gps_route, kalman_route, physics_route):
    if gps_route is not None:
        min_lat, max_lat, min_lon, max_lon = projection_size(gps_route)
    elif kalman_route is not None:
        min_lat, max_lat, min_lon, max_lon = projection_size(kalman_route)
    elif physics_route is not None:
        min_lat, max_lat, min_lon, max_lon = projection_size(physics_route)
    else:
        raise RuntimeError  # I don't know what went wrong but something went horribly wrong.

    map = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat,
                  llcrnrlon=min_lon, urcrnrlon=max_lon, resolution='h')

    # draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='coral', lake_color='aqua')

    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary(fill_color='aqua')

    # draw lat/lon grid lines every 30 degrees.
    map.drawmeridians(np.arange(0, 360, 30))
    map.drawparallels(np.arange(-90, 90, 30))

    if gps_route is not None:
        plot_route(gps_route, 'r', map)

    if kalman_route is not None:
        plot_route(kalman_route, 'g', map)

    if physics_route is not None:
        plot_route(physics_route, 'y', map)

    plt.title('Kalman Filter')
    plt.show()


def plot_route(route, color, map):
    x = [row[0] for row in route]
    y = [row[1] for row in route]
    map.plot(x, y, linewidth=1.5, color=color)
    map.scatter(x, y, marker='o', color=color, s=6)


def projection_size(route) -> tuple[float, float, float, float]:
    margin = 0.4

    if len(route) == 1:
        return route[0][1] - margin,\
                route[0][1] + margin, \
                route[0][0] - margin, \
                route[0][0] + margin

    min_lat = min([x[1] for x in route])
    max_lat = max([x[1] for x in route])
    min_lon = min([x[0] for x in route])
    max_lon = max([x[0] for x in route])

    delta = max(max_lat - min_lat, max_lon - min_lon)

    delta_lat = delta * margin
    delta_lon = delta * margin

    min_lat -= delta_lat
    max_lat += delta_lat
    min_lon -= delta_lon
    max_lon += delta_lon

    min_lat = utils.clamp(min_lat, -90, 90)
    max_lat = utils.clamp(max_lat, -90, 90)

    return min_lat, max_lat, min_lon, max_lon


# Callback for tkinter button press
def on_click():
    if not draw_measured.get() and not draw_kalman.get() and not draw_physical.get():
        showwarning(title="Warning", message="Select at least one option!")
        return

    filetypes = (
        ('GPS files', '*.gps'),
        ('All files', '*.*')
    )

    filename = fd.askopenfilename(
        title='Open GPS data',
        initialdir='.',
        filetypes=filetypes)

    data = utils.read_gps(filename)

    gps_route, kalman_route, physics_route = None, None, None
    if draw_measured.get():
        gps_route = get_gps_route(data)

    if draw_kalman.get():
        kalman_route = get_kalman_route(data)

    if draw_physical.get():
        physics_route = get_physic_route(data)

    draw_map(gps_route, kalman_route, physics_route)


# Draws route based on received GPS position
def get_gps_route(data):
    return [[float(x[0]), float(x[1])] for x in data]


# Draws route based on Kalman's filter predictions
def get_kalman_route(data):
    position = data[0][0:2]
    sogs = [x[2] for x in data]
    cogs = [x[3] for x in data]

    route = [position]
    start_lin = utils.to_plane_pos(data[0][0:2])

    kf = KalmanFilter(start_lin, utils.get_velocity_vec(utils.knots_to_mps(data[0][2]), data[0][3]), float(observation_noise.get()), float(prediction_noise.get()))

    for i in range(1, len(data)):
        state, noise = kf.predict(60, utils.get_velocity_vec(utils.knots_to_mps(sogs[i]), cogs[i]))
        print(state)
        plane_gps_pos = utils.to_plane_pos(data[i][0:2])
        route.append(utils.to_geo_pos(np.array([state[0], state[2], plane_gps_pos[2]])))
        lin_pos = utils.to_plane_pos(data[i][0:2])
        print(data[i][0:2])
        print(lin_pos)
        kf.update(lin_pos[0:2], 60)

    return route


# Draws route based on initial position and SOG+COG afterward.
def get_physic_route(data):
    position = data[0][0:2]
    sogs = [x[2] for x in data]
    cogs = [x[3] for x in data]

    # assume dt is 60 seconds...
    dt = 60

    route = [position]

    prev_position = position
    # prev_velocity = utils.get_velocity_vec(utils.knots_to_mps(sogs[0]), cogs[0])

    for i in range(1, len(data)):
        # velocity = utils.get_velocity_vec(utils.knots_to_mps(sogs[i]), cogs[i] + i * 10)

        position = utils.predict_physics_pos(prev_position, utils.knots_to_mps(sogs[i]), cogs[i], dt)

        # print(prev_position)
        # acceleration = [(velocity[0] - prev_velocity[0]) / dt,
        #                 (velocity[1] - prev_velocity[1]) / dt]
        # position = prev_position + [velocity[0] * dt, velocity[1] * dt]
        # position += [acceleration[0] * dt * dt, acceleration[1] * dt * dt]

        prev_position = position
        # prev_velocity = velocity

        route.append(position)
        print(position, utils.knots_to_mps(sogs[i]), cogs[i])

    return route


if __name__ == '__main__':
    root = tk.Tk(screenName="kalman")
    title = tk.Label(root, text="Kalman's Filter for Ships:")
    title.pack()

    draw_measured = tk.BooleanVar()
    draw_kalman = tk.BooleanVar()
    draw_physical = tk.BooleanVar()
    prediction_noise = tk.StringVar()
    observation_noise = tk.StringVar()

    prediction_noise.set(0.1)
    observation_noise.set(3.0)

    ck1 = tk.Checkbutton(root, text='Draw Measured', variable=draw_measured, onvalue=True, offvalue=False)
    ck1.pack()

    ck2 = tk.Checkbutton(root, text='Draw Kalman Prediction', variable=draw_kalman, onvalue=True, offvalue=False)
    ck2.pack()

    ck3 = tk.Checkbutton(root, text='Draw Physics-Based', variable=draw_physical, onvalue=True, offvalue=False)
    ck3.pack()

    l1 = tk.Label(root, text="Prediciton noise")
    noise_spin1 = tk.Spinbox(root, from_=0.0, to=10.0, increment=0.1, format="%.1f", textvariable=prediction_noise)
    l2 = tk.Label(root, text="Observation noise")
    noise_spin2 = tk.Spinbox(root, from_=0.0, to=50.0, increment=0.1, format="%.1f", textvariable=observation_noise)
    l1.pack()
    noise_spin1.pack()
    l2.pack()
    noise_spin2.pack()
    button = tk.Button(text="Load data and draw map", command=on_click)
    button.pack()

    now = datetime.now()
    # print(now)

    root.mainloop()
