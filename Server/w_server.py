import asyncio
from asyncio.windows_events import NULL
import json
import logging
import websockets
import csv
import random, string
import time
import http.server
import socketserver, threading
import firebase_admin
from firebase_admin import credentials, firestore

cred = credentials.Certificate("projectseek-firebase.json")
firebase_admin.initialize_app(cred)
firestore_db = firestore.client()
"""

WILL DELETE THIS LATER AFTER USE, JUST LIKE I SHOULD HAVE BEEN.

firestore_db.collection(u'users').document('uid1').set({'name': 'User1', 'Level': '0'})
firestore_db.collection(u'users').document('uid2').set({'name': 'User2', 'Level': '3'})
for snapshot in list(firestore_db.collection('users').stream()):
    print(snapshot.to_dict())
print(firestore_db.collection('users').document('uid3').get().to_dict())
firestore_db.collection('users').document('uid1').delete()
print(list(firestore_db.collection('users').where('u').stream()))
firestore_db.collection('users').document('uid1').update({'Level':1})
"""
global all_user
global parties
global rooms

threads = []
all_user = dict() #users online
parties = dict() #parties available
nr = 6 #no of participants in one room
avb = 0 #no of rooms
rooms = dict()
rooms[avb] = {"participants": 0}
available_room = "room_"+str(avb)+".txt"

async def create(ws, message):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    parties[code] = {"participants":1,"p1": ws, "pID1": pid}
    data = {"action": "created_party"}
    data = json.dumps(data)
    await ws.send(data)

async def join(ws, message):
    data = json.loads(message.decode('UTF-8'))
    code = data["code"]
    pid = data["pID"]
    if code not in parties:
        data = {"action": "join_error"}
        data = json.dumps(data)
        await ws.send(data)
    temp = parties[code]["participants"] + 1
    parties[code]["participants"] = temp
    parties[code]["p"+str(temp)] = ws
    parties[code]["pID"+str(temp)] = pid
    for i in range(temp-1):
        data = {"action": "joined_party", "joined_party": pid}
        data = json.dumps(data)
        await parties[code]["p"+str(i+1)].send(data)
        data = {"action": "joined_party", "joined_party": parties[code]["pID"+str(i+1)]}
        data = json.dumps(data)
        await ws.send(data)

async def look_callback():
    ppl = ["0_1", "0_2", "0_3", "0_4", "1_1", "1_2"]
    data = {"action": "ids"}
    users = []
    time.sleep(6)
    if len(rooms[avb]) == nr + 1:
        for i, key in enumerate(rooms[avb].keys()):
            if key != "participants":
                users.append(key)
                r = random.randint(0, len(ppl) - 1)
                data[key] = ppl[r]
                ppl.pop(r)
    else:
        for i in range(nr - len(rooms[avb]) + 1):
            r = random.randint(0, len(ppl) - 1)
            data["bot_"+str(i)] = ppl[r]
            ppl.pop(r)
        for i, key in enumerate(rooms[avb].keys()):
            if key != "participants":
                users.append(key)
                r = random.randint(0, len(ppl) - 1)
                print(data,key,ppl,r)
                data[key] = ppl[r]
                ppl.pop(r)
            else: rooms[avb][key] = nr
    message = json.dumps(data)
    print(users)
    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])

def look():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(look_callback())
    loop.close()

async def register(ws, message):
    global avb
    global available_room
    data = json.loads(message.decode('UTF-8'))
    if data["party"] == "0":
        if rooms[avb]["participants"] == 0:
            t = threading.Thread(target=look)
            threads.append(t)
            t.start()
            print('A')
        if rooms[avb]["participants"] < nr:
            pID = data["pID"]
            rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0","health":"100"}
            rooms[avb]["participants"] = rooms[avb]["participants"] + 1
            cong = {"action": "entered_room"}
            cong = json.dumps(cong)
            await ws.send(cong)
            message = {"action": "joined_room", "joined_room": pID}
            message = json.dumps(message)
            users = []
            print('N')
            if rooms[avb]["participants"] > 1:
                for key in rooms[avb].keys():
                    if key != "participants" and key != pID:
                        users.append(key)
                        data = {"action": "in_room", "in_room": key}
                        data = json.dumps(data)
                        await ws.send(data)
                await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        else:
            avb = avb+1
            t = threading.Thread(target=look)
            threads.append(t)
            t.start()
            pID = data["pID"]
            rooms[avb] = dict()
            print('S')
            rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0","health":"100"}
            rooms[avb]["participants"] = 1
            print(rooms)
            cong = {"action": "entered_room"}
            cong = json.dumps(cong)
            await ws.send(cong)
    else:
        code = data["code"]
        p = parties[code]["participants"]
        if rooms[avb]["participants"] <= nr - p:
            print('H')
            for i in range(p):
                pID = parties[code]["pID"+str(i+1)]
                ws = parties[code]["p"+str(i+1)]
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0","health":"100"}
                rooms[avb]["participants"] = rooms[avb]["participants"] + 1
                cong = {"action": "entered_room"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID}
                print(message)
                message = json.dumps(message)
                users = []
                if rooms[avb]["participants"] > 1:
                    for key in rooms[avb].keys():
                        if key != "participants" and key != pID:
                            users.append(key)
                            data = {"action": "in_room", "in_room": key}
                            data = json.dumps(data)
                            await ws.send(data)
                    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])
        else:
            avb = avb+1
            t = threading.Thread(target=look)
            threads.append(t)
            t.start()
            rooms[avb] = dict()
            print('UJJAWAL')
            rooms[avb]['participants'] = 0 
            for i in range(p):
                pID = parties[code]["pID"+str(i+1)]
                ws = parties[code]["p"+str(i+1)]
                rooms[avb][pID] = {"ws": ws, "x": "0", "y": "0", "rot": "0","health":"100"}
                rooms[avb]["participants"] = rooms[avb]["participants"] + 1
                cong = {"action": "entered_room"}
                cong = json.dumps(cong)
                await ws.send(cong)
                message = {"action": "joined_room", "joined_room": pID}
                message = json.dumps(message)
                if rooms[avb]["participants"] > 0:
                    for key in rooms[avb].keys():
                        if key != "participants" and key != pID:
                            users.append(key)
                            data = {"action": "in_room", "in_room": key}
                            data = json.dumps(data)
                            await ws.send(data)
                    await asyncio.wait([all_user[user]['ws'].send(message) for user in all_user if user in users])

async def move_state(data):
    pid = data['pID']
    data = json.dumps(data)
    tr = None
    for room in rooms:
        if pid in rooms[room]:
            tr = room
    if len(all_user) > 1:  # asyncio.wait doesn't accept an empty list
        await asyncio.wait([all_user[user]['ws'].send(data) for user in rooms[tr] if user != 'participants'])

async def bullet(data):
    user = data['pID']
    hit = data['hit']
    tr = None
    data = json.dumps(data)
    for room in rooms:
        if hit in rooms[room]:
            tr = room
    data = {'action':'killed','by':user}
    data = json.dumps(data)
    await all_user[hit]['ws'].send(data)
    del rooms[tr][hit]
    #rooms[tr]['participants'] -= 1
    if len(rooms[tr])>1:
        data = {"action": "user_died", "pid": hit}
        data = json.dumps(data)
        await asyncio.wait([all_user[u]['ws'].send(data) for u in rooms[tr] if u != 'participants'])

async def knife(data):
    user = data['pID']
    hit = data['hit']
    tr = None
    data = json.dumps(data)
    for room in rooms:
        if hit in rooms[room]:
            tr = room
    data = {'action':'killed','by':user}
    data = json.dumps(data)
    await all_user[hit]['ws'].send(data)
    del rooms[tr][hit]
    #rooms[tr]['participants'] -= 1
    if len(rooms[tr])>1:
        data = {"action": "user_died", "pid": hit}
        data = json.dumps(data)
        await asyncio.wait([all_user[u]['ws'].send(data) for u in rooms[tr] if u != 'participants'])


async def unregister(websocket):
    u,tr = None, None
    for user in all_user:
        if all_user[user]['ws'] == websocket:
            u = user
            break
    for r in rooms:
        if u in rooms[r]:
            tr = r
            break
    if tr != None:
        del rooms[tr][u]
        #rooms[tr]['participants'] -= 1
        if len(rooms[tr])>1:
            data = {"action": "afk", "pid": u}
            data = json.dumps(data)
            await asyncio.wait([all_user[user]['ws'].send(data) for user in rooms[tr] if user != 'participants'])
    del all_user[u]

async def login_verify(data, ws):
    db = firestore_db.collection('users')
    matched_user = db.where('username','==',data['username'])
    matched_id = list(matched_user.where('password','==',data['password']).stream())
    data = {"action": "login", "state": 'found' if len(matched_id)==1 else 'failed'}
    data = json.dumps(data)
    await ws.send(data)

async def counter(websocket, path):
    pID = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    all_user[pID]= {"ws":websocket,"x":"0","y":"0","health":"100"}
    data = {"action": "sent_pID", "pID": pID}
    data = json.dumps(data)
    await websocket.send(data)
    #all_user[data[pID]]= {"ws":websocket,"x":"0","y":"0"}    
    try:
        async for message in websocket:
            data = json.loads(message.decode('UTF-8'))
            if data["action"] == "play":
                print(data)
                await register(websocket, message)
            elif data["action"] == "create":
                await create(websocket, message)
            elif data["action"] == "move":
                await move_state(data)
            elif data["action"] == "join":
                await join(websocket, message)
            elif data["action"] == "bullet":
                await bullet(data)
            elif data["action"] == "knife":
                await knife(data)
            elif data["action"] == 'login':
                await login_verify(data, websocket)
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)

class routing(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/authentication':
            self.path = 'auth.html'
        return http.server.SimpleHTTPRequestHandler.do_GET(self)
    def do_POST(self):
        if 'sign-in-' in self.path:
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            user = firestore_db.collection('users').document(data['uid']).get().to_dict()
            if user == None:
                firestore_db.collection('users').document(data['uid']).set({'username':'unset'})
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps(user).encode(encoding='utf_8'))

        elif self.path == '/new-user':
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            firestore_db.collection('users').document(data['uid_reg']).set({'username':data['user'],'password':data['pass']})
            self.send_response(200)
            self.end_headers()
        
        elif self.path == "/check-available-username":
            self.data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(self.data_string)
            data = list(firestore_db.collection('users').where('username','==',data['username']).stream())
            self.send_response(200)
            self.end_headers()
            self.wfile.write(json.dumps({'avail':('True' if len(data) != 0 else 'False')}).encode(encoding='utf_8'))
        return

handler_object = routing
auth_serv = socketserver.TCPServer(("", 9898), handler_object)

def routes_thread():
    auth_serv.serve_forever()
    asyncio.get_event_loop().run_until_complete(auth_serv)
    second_loop = asyncio.new_event_loop()
    execute_polling_coroutines_forever(second_loop)
    return

threading.Thread(target=routes_thread).start()

game_serv = websockets.serve(counter, "localhost", 6789)
asyncio.get_event_loop().run_until_complete(game_serv)
asyncio.get_event_loop().run_forever()
