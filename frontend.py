import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import common_use_modules as utils

#gps_route = []
#kalman_route = []
#physics_route = []

def on_click():
    if draw_measured.get():
        print("owo")
    if draw_kalman.get():
        print("uwu")
    if draw_physical.get():
        print("nya")


def draw():
    print("haha nie.")


def draw_map(gps_route, kalman_route, physics_route):
    # set up orthographic map projection with
    # perspective of satellite looking down at 50N, 100W.
    # use low resolution coastlines.
    min_lat, max_lat, min_lon, max_lon = projection_size(gps_route)
    map = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat,
                  llcrnrlon=min_lon,urcrnrlon=max_lon, resolution='h')
    # draw coastlines, country boundaries, fill continents.
    map.drawcoastlines(linewidth=0.25)
    map.drawcountries(linewidth=0.25)
    map.fillcontinents(color='coral', lake_color='aqua')
    # draw the edge of the map projection region (the projection limb)
    map.drawmapboundary(fill_color='aqua')
    # map.drawgreatcircle(xx, yy,linewidth=1.5,color='r')
    # draw lat/lon grid lines every 30 degrees.
    map.drawmeridians(np.arange(0, 360, 30))
    map.drawparallels(np.arange(-90, 90, 30))
    # make up some data on a regular lat/lon grid.
    # nlats = 73
    # nlons = 145
    # delta = 2. * np.pi / (nlons - 1)
    # lats = (0.5 * np.pi - delta * np.indices((nlats, nlons))[0, :, :])
    # lons = (delta * np.indices((nlats, nlons))[1, :, :])
    # wave = 0.75 * (np.sin(2. * lats) ** 8 * np.cos(4. * lons))
    # mean = 0.5 * np.cos(2. * lats) * ((np.sin(2. * lats)) ** 2 + 2.)
    # compute native map projection coordinates of lat/lon grid.
    # x, y = map(lons * 180. / np.pi, lats * 180. / np.pi)
    # contour data over the map.
    # map.contour(x, y, wave + mean, 15, linewidths=1.5)

    gps_x = [row[0] for row in gps_route]
    gps_y = [row[1] for row in gps_route]
    map.plot(gps_x, gps_y, linewidth=1.5, color='r')
    map.scatter([p[0] for p in gps_route], [p[1] for p in gps_route], marker='o', color='r', s=6)

    # print(gps_route)
    # gps_route = [[4.52, 51.83], [4.52, 51.83]]
    # for i in range(0, len(gps_route) - 1):
    #     print(gps_route[i][0], gps_route[i][1], gps_route[i+1][0], gps_route[i+1][1])
    #     map.drawgreatcircle(gps_route[i][0], gps_route[i][1], gps_route[i+1][0],
    #                         gps_route[i+1][1], linewidth=1.5, color='r')

    plt.title('Kalman Filter')
    plt.show()


def projection_size(route) -> tuple[float, float, float, float]:
    margin = 0.4

    if len(route) == 1:
        return route[0][1] - margin, route[0][1] + margin, route[0][0] - margin, route[0][0] + margin

    min_lat = min([x[1] for x in route])
    max_lat = max([x[1] for x in route])
    min_lon = min([x[0] for x in route])
    max_lon = max([x[0] for x in route])

    # delta_lat = max_lat - min_lat
    # delta_lon = max_lon - min_lat

    delta = max(max_lat - min_lat, max_lon - min_lon)
    # delta = max(delta, 5)

    delta_lat = delta * margin
    delta_lon = delta * margin

    # delta_lat = max(delta_lat, 1)
    # delta_lon = max(delta_lon, 1)

    min_lat -= delta_lat
    max_lat += delta_lat
    min_lon -= delta_lon
    max_lon += delta_lon

    min_lat = utils.clamp(min_lat, -90, 90)
    max_lat = utils.clamp(max_lat, -90, 90)

    return min_lat, max_lat, min_lon, max_lon


if __name__ == '__main__':
    root = tk.Tk(screenName="kalman")
    title = tk.Label(root, text="Kalman's Filter for Ships:")
    title.pack()

    draw_measured = tk.BooleanVar()
    draw_kalman = tk.BooleanVar()
    draw_physical = tk.BooleanVar()

    ck1 = tk.Checkbutton(root, text='Draw Measured', variable=draw_measured, onvalue=True, offvalue=False,
                         command=on_click)
    ck1.pack()

    ck2 = tk.Checkbutton(root, text='Draw Kalman Prediction', variable=draw_kalman, onvalue=True, offvalue=False,
                         command=on_click)
    ck2.pack()

    ck3 = tk.Checkbutton(root, text='Draw Physics-Based', variable=draw_physical, onvalue=True, offvalue=False,
                         command=on_click)
    ck3.pack()

    id_textbox = tk.Text(root, height=1)
    id_textbox.pack()

    button = tk.Button(text="Draw map", command=draw)
    button.pack()

    root.mainloop()
