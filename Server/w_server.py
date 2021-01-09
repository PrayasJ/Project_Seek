import asyncio
import json
import logging
import websockets
import csv
import random, string

global avb
global all_user
global parties
all_user = dict() #users online
parties = dict() #parties available
nr = 10 #no of participants in one room
avb = 0 #no of rooms
available_room = "room_"+str(avb)+".txt"

async def create(ws):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    parties[code] = {"participants":1,"p1": ws, "pid1": pid}

async def join(ws):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    temp = parties[code]["participants"] + 1
    parties[code]["participants"] = temp
    parties[code]["p"+str(temp)] = ws
    parties[code]["pid"+str(temp)] = pid
    for i in range(temp-1):
        parties[code]["p"+str(i+1)].send(pid)
        ws.send(parties[code]["pid"+str(i+1)])

async def register(ws):
    global available_room
    data = json.loads(message.decode('UTF-8'))
    f = open(available_room, "r+")
    line = f.readlines()
    f.close()
    if data["party"] == "0":
        if len(line) < nr:
            f = open(available_room, "a+")
            f.write(data["pID"]+",0,0,\n")
            f.close()
            message = data["pID"]
            users = []
            if len(line) > 0:
                for l in line:
                    l = l.split(',')
                    users.append(l[0])
                    await ws.send(l[0])
                await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        if len(line) >= nr:
            avb = avb+1
            available_room = "room_"+str(avb)+".txt"
            f = open(available_room, "a+")
            f.write(data["pID"]+",0,0,\n")
            f.close()
    if data["party"] != "0":
        code = data["code"]
        p = parties[code]["participants"]
        if len(line) < nr - p:
            for i in range(p):
                f = open(available_room, "r+")
                line = f.readlines()
                f.close()
                f = open(available_room, "a+")
                f.write(parties["pid"+str(i+1)]+",0,0,\n")
                f.close()
                message = parties["pid"+str(i+1)]
                users = []
                if len(line) > 0:
                    for l in line:
                        l = l.split(',')
                        users.append(l[0])
                        await ws.send(l[0])
                    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        if len(line) >= nr-p:
            avb = avb+1
            available_room = "room_"+str(avb)+".txt"
            for i in range(p):
                f = open(available_room, "r+")
                line = f.readlines()
                f.close()
                f = open(available_room, "a+")
                f.write(parties["pid"+str(i+1)]+",0,0,\n")
                f.close()
                if len(line) > 0:
                    for l in line:
                        l = l.split(',')
                        users.append(l[0])
                        await ws.send(l[0])
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
    await websocket.send(pID)
    #all_user[data[pID]]= {"ws":websocket,"x":"0","y":"0"}    
    try:
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "play":
                await register(websocket)
            if data["action"] == "create":
                await create(websocket)
            if data["action"] == "move":
                await move_state(data)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)

start_server = websockets.serve(counter, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()