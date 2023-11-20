import os
from typing import Tuple
import numpy as np


from marinetrafficapi import MarineTrafficApi
import asyncio
import websockets
import json
from datetime import datetime, timezone

import frontend
from kalman_filter import KalmanFilter
import common_use_modules as cum

APIKEY = os.environ['AISAPIKEY']


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

                frontend.gps_route.append([ais_message['Longitude'], ais_message['Latitude']])


test_coords = [[0.0, 0.0], [12.0, -10.0], [15.0, -9.0], [25.0, -8.0], [30.0, -7.0]]


def _process(_delta):
    F = np.array([[1, 0, _delta],  # lat
                  [0, 1, _delta],  # lon
                  [0, 0, 1,]])  # sog

    H = np.array([[1, 0, 0],  # lat
                  [0, 1, 0],  # lon
                  [0, 0, 1]])  # speed

    B = np.zeros((3, 1))

    Q = np.eye(3)
    R = np.eye(3)

    # x = np.array([[initial_latitude],
    #               [initial_longitude],
    #               [initial_sog]])
    #
    # # stachu to jebnie
    # kf = KalmanFilter(state_transition=F, observation=H, control_input=B, process_noise=Q,
    #                   observation_noise=R, state=x)
    # predicted_state = kf.predict(np.zeros((1, 1)))
    #
    # measured_values = np.array([[measured_latitude],
    #                             [measured_longitude],
    #                             [measured_sog]])
    # kf.update(mean=measured_values)


def main():
    asyncio.run(asyncio.run(connect_ais_stream()))


if __name__ == '__main__':
    main()
