import asyncio
import json
import logging
import websockets
import random, string

logging.basicConfig()

STATE = {"value": 0}

USERS = set()


def state_event():
    return json.dumps({"type": "state", **STATE})


def users_event(id):
    return json.dumps({"type": "new_user", "id": id,"x":len(USERS)*5})

def reg_ID(ID):
    return json.dumps({"type":"join", "ID":ID})

async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def notify_users(id):
    if len(USERS) > 1:  # asyncio.wait doesn't accept an empty list
        message = users_event(id)
        await asyncio.wait([user[1].send(message) for user in USERS if user[0] != id])


async def register(websocket):
    playerId = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    USERS.add((playerId, websocket))
    await websocket.send(reg_ID(playerId))
    await notify_users(playerId)


async def unregister(websocket):
    [USERS.remove(user) for user in USERS if user[1] == websocket]
    await notify_users()


async def counter(websocket, path):
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "move":
                print(data["key"],data["pID"])
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)
      

start_server = websockets.serve(counter, "localhost", 6789)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()