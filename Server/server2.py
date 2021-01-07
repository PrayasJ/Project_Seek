import asyncio
import json
import logging
import websockets
import random, string

logging.basicConfig()

STATE = {"value": 0}

USERS = dict()


def move_event():
    return json.dumps({"type": "state", **STATE})

def users_event(ID):
    return json.dumps({"action": "new_user", "ID": ID,"x":USERS[ID]['x'],"y":USERS[ID]['y']})

def users_event_end(ID):
    return json.dumps({"action": "del_user", "ID": ID})

def reg_ID(ID):
    return json.dumps({"action":"join", "ID":ID,"x":USERS[ID]['x'],"y":USERS[ID]['y']})

async def move_state(data):
    id = data['pID']
    data = json.dumps(data)
    if len(USERS) > 1:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([USERS[user]['ws'].send(data) for user in USERS if user != id])


async def notify_users(id, ws):
    if len(USERS) > 1:  # asyncio.wait doesn't accept an empty list
        message = users_event(id)
        await asyncio.wait([USERS[user]['ws'].send(message) for user in USERS if user != id])
        await asyncio.wait([ws.send(users_event(user)) for user in USERS if user != id])

async def notify_users_end(id):
    if len(USERS) > 1:  # asyncio.wait doesn't accept an empty list
        message = users_event_end(id)
        await asyncio.wait([USERS[user]['ws'].send(message) for user in USERS if user != id])

async def register(websocket):
    playerId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    USERS[playerId]= {"ws":websocket,"x":random.randint(-50,50),"y":random.randint(-50,50)}
    await websocket.send(reg_ID(playerId))
    await notify_users(playerId, websocket)


async def unregister(websocket):
    [USERS.remove(user) for user in USERS if user[1] == websocket]
    await notify_users_end([i for i, val in USERS.items() if val['ws'] == websocket][0])


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "move":
                await move_state(data)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)
      

start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()