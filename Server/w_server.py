import asyncio
import json
import logging
import websockets
import csv
import random, string

global all_user
global parties
global rooms
all_user = dict() #users online
parties = dict() #parties available
nr = 10 #no of participants in one room
avb = 0 #no of rooms
rooms = dict()
rooms[avb] = {"participants": 0}
available_room = "room_"+str(avb)+".txt"

async def create(ws, message):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    parties[code] = {"participants":1,"p1": ws, "pid1": pid}

async def join(ws, message):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    if code not in parties:
        data = {"action": "join_error"}
        data = json.dumps(data)
        ws.send(data)
    temp = parties[code]["participants"] + 1
    parties[code]["participants"] = temp
    parties[code]["p"+str(temp)] = ws
    parties[code]["pid"+str(temp)] = pid
    for i in range(temp-1):
        data = {"action": "joined_party", "joined_party": pid}
        data = json.dumps(data)
        parties[code]["p"+str(i+1)].send(data)
        data = {"action": "joined_party", "joined_party": parties[code]["pid"+str(i+1)]}
        data = json.dumps(data)
        ws.send(data)

async def register(ws, message):
    global avb
    global available_room
    data = json.loads(message.decode('UTF-8'))
    if data["party"] == "0":
        if rooms[avb]["participants"] < nr:
            rooms[avb][data["pID"]] = {"ws": ws, "x": data["x"], "y": data["y"], "rot": data["rot"]}
            rooms[avb]["participants"] = rooms[avb]["participants"] + 1
            message = {"action": "joined_room", "joined_room": data["pID"]}
            message = json.dumps(message)
            users = []
            if rooms[avb]["participants"] > 1:
                for key in rooms[avb].keys():
                    if key != "participants":
                        users.append(key)
                        data = {"action": "in_room", "in_room": key}
                        data = json.dumps(data)
                        await ws.send(data)
                await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        if rooms[avb]["participants"] >= nr:
            avb = avb+1
            rooms[avb][data["pID"]] = {"ws": ws, "x": data["x"], "y": data["y"], "rot": data["rot"]}
            rooms[avb]["participants"] = 1
    if data["party"] != "0":
        code = data["code"]
        p = parties[code]["participants"]
        if rooms[avb]["participants"] < nr - p:
            for i in range(p):
                rooms[avb][data["pID"]] = {"ws": ws, "x": data["x"], "y": data["y"], "rot": data["rot"]}
                rooms[avb]["participants"] = rooms[avb]["participants"] + 1
                message = {"action": "joined_room", "joined_room": data["pID"]}
                message = json.dumps(message)
                users = []
                if rooms[avb]["participants"] > 1:
                    for key in rooms[avb].keys():
                        if key != "participants" and key != rooms[avb][data["pID"]]:
                            users.append(key)
                            data = {"action": "in_room", "in_room": key}
                            data = json.dumps(data)
                            await ws.send(data)
                    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        if rooms[avb]["participants"] >= nr-p:
            avb = avb+1
            for i in range(p):
                rooms[avb][data["pID"]] = {"ws": ws, "x": data["x"], "y": data["y"], "rot": data["rot"]}
                rooms[avb]["participants"] = rooms[avb]["participants"] + 1
                message = {"action": "joined_room", "joined_room": data["pID"]}
                message = json.dumps(message)
                if rooms[avb]["participants"] > 0:
                    for key in rooms[avb].keys():
                        if key != "participants" and key != rooms[avb][data["pID"]]:
                            users.append(key)
                            data = {"action": "in_room", "in_room": key}
                            data = json.dumps(data)
                            await ws.send(data)
                    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])

async def move_state(data):
    id = data['pID']
    data = json.dumps(data)
    if len(all_user) > 1:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([all_user[user]['ws'].send(data) for user in all_user if user != id])

async def unregister(websocket):
    [all_user.remove(user) for user in all_user if user[1] == websocket]

async def counter(websocket, path):
    pID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    all_user[pID]= {"ws":websocket,"x":"0","y":"0"}
    data = {"action": "sent_pID", "pID": pID}
    data = json.dumps(data)
    await websocket.send(data)
    #all_user[data[pID]]= {"ws":websocket,"x":"0","y":"0"}    
    try:
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "play":
                await register(websocket, message)
            if data["action"] == "create":
                await create(websocket, message)
            if data["action"] == "move":
                await move_state(data)
            if data["action"] == "join":
                await create(websocket, message)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)

start_server = websockets.serve(counter, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()