import os
from typing import Tuple

import numpy as np
import tkinter as tk
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
from marinetrafficapi import MarineTrafficApi
import asyncio
import websockets
import json
from datetime import datetime, timezone
from kalman_filter import KalmanFilter
import common_use_modules as cum

APIKEY = os.environ['AISAPIKEY']

gps_route = []
kalman_route = []
physics_route = []


async def connect_ais_stream():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": APIKEY,  # Required !
                             "BoundingBoxes": [[[-90, -180], [90, 180]]],  # Required!
                             "FiltersShipMMSI": ["368207620", "367719770", "211476060"],  # Optional!
                             "FilterMessageTypes": ["PositionReport"]}  # Optional!

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)


        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                # the message parameter contains a key of the message type which contains the message itself
                ais_message = message['Message']['PositionReport']
                print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} "
                      f"Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']} "
                      f"SOG: {ais_message['Sog']} COG: {ais_message['Cog']}")

                gps_route.append([ais_message['Longitude'], ais_message['Latitude']])
                draw_map(gps_route, kalman_route, physics_route)


test_coords = [[0.0, 0.0], [12.0, -10.0], [15.0, -9.0], [25.0, -8.0], [30.0, -7.0]]


def knots_to_mps(knots) -> float:
    return knots * 0.5144


def projection_size(route) -> tuple[float, float, float, float]:

    margin = 0.2

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

    min_lat = cum.clamp(min_lat, -90, 90)
    max_lat = cum.clamp(max_lat, -90, 90)

    return min_lat, max_lat, min_lon, max_lon


def draw_map(gps_route, kalman_route, physics_route):
    # set up orthographic map projection with
    # perspective of satellite looking down at 50N, 100W.
    # use low resolution coastlines.
    min_lat, max_lat, min_lon, max_lon = projection_size(gps_route)
    map = Basemap(projection='cyl', llcrnrlat=min_lat, urcrnrlat=max_lat,
                  llcrnrlon=min_lon,urcrnrlon=max_lon, resolution='l')
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
    for i in range(0, len(gps_route) - 1):
        map.drawgreatcircle(gps_route[i][0], gps_route[i][1], gps_route[i+1][0],
                            gps_route[i+1][1], linewidth=1.5, color='r')
    map.scatter([p[0] for p in gps_route], [p[1] for p in gps_route], marker='o', color='r')
    plt.title('Kalman Filter')
    plt.show()


def _process(_delta):
    F = np.array([[1, 0, _delta],  # lat
                  [0, 1, _delta],  # lon
                  [0, 0, 1,]])  # sog

    H = np.array([[1, 0, 0],  # lat
                  [0, 1, 0],  # lon
                  [0, 0, 1]])  # speed

    B = np.zeros((4, 1))

    Q = np.eye(4)
    R = np.eye(3)

    x = np.array([[initial_latitude],
                  [initial_longitude],
                  [initial_sog]])

    # stachu to jebnie
    kf = KalmanFilter(state_transition=F, observation=H, control_input=B, process_noise=Q, observation_noise=R, state=x)
    predicted_state = kf.predict(np.zeros((1, 1)))

    measured_values = np.array([[measured_latitude],
                                [measured_longitude],
                                [measured_sog]])
    kf.update(mean=measured_values)


def main():
    asyncio.run(asyncio.run(connect_ais_stream()))
    # draw_map(test_coords, None, None)


if __name__ == '__main__':
    main()
