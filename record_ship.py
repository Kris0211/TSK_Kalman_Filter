import asyncio
import json
import os
from datetime import datetime, timezone
import common_use_modules as utils

import numpy as np
import websockets

APIKEY = os.environ['AISAPIKEY']


async def connect_ais_stream():
    async with websockets.connect("wss://stream.aisstream.io/v0/stream") as websocket:
        subscribe_message = {"APIKey": APIKEY,  # Required !
                             "BoundingBoxes": [[[-90, -180], [90, 180]]],  # Required!
                             "FiltersShipMMSI": ship_ids,  # Optional!
                             "FilterMessageTypes": ["PositionReport"]}  # Optional!

        subscribe_message_json = json.dumps(subscribe_message)
        await websocket.send(subscribe_message_json)

        print("Connected to API")

        async for message_json in websocket:
            message = json.loads(message_json)
            message_type = message["MessageType"]

            if message_type == "PositionReport":
                # the message parameter contains a key of the message type which contains the message itself
                ais_message = message['Message']['PositionReport']
                print(f"[{datetime.now(timezone.utc)}] ShipId: {ais_message['UserID']} "
                      f"Latitude: {ais_message['Latitude']} Longitude: {ais_message['Longitude']} "
                      f"SOG: {ais_message['Sog']} COG: {ais_message['Cog']}")

                a = np.asarray([ais_message['Longitude'],
                                ais_message['Latitude'],
                                ais_message['Sog'],
                                ais_message['Cog']])
                filename = "recordings/" + str(ais_message['UserID']) + ".gps"
                utils.append_gps(filename, a)
                # print(cum.read_gps(filename))

if __name__ == "__main__":
    ship_ids = ["230625000", "246891000", "219027776", "636019921", "636021605", "626317000"]
    asyncio.run(connect_ais_stream())
