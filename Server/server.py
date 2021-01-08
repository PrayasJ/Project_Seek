import socket
from _thread import *
import sys

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server = 'localhost'
port = 4201

server_ip = socket.gethostbyname(server)

try:
    s.bind((server, port))

except socket.error as e:
    print(str(e))

s.listen(2)  #Kitne user aane chahie yha?
print("Waiting for a connection")
id_no = 0
currentId = str(id_no)
pos = ["0:50,50", "1:100,100"]
def threaded_client(conn):
    global currentId, pos, id_no
    conn.send(str.encode(currentId))
    id_no = id_no + 1
    currentId = str(id_no)
    reply = ''
    while True:
        try:
            data = conn.recv(2048)
            reply = data.decode('utf-8')
            if not data:
                conn.send(str.encode("Goodbye"))
                break
            else:
                print("Recieved: " + reply)
                arr = reply.split(":")
                id = int(arr[0])
                pos[id] = reply

                if id == 0: nid = 1
                if id == 1: nid = 0

                reply = pos[nid][:]
                print("Sending: " + reply)

            conn.sendall(str.encode(reply))
        except:
            break

    print("Connection Closed")
    conn.close()

while True:
    conn, addr = s.accept()
    print("Connected to: ", addr)
    conn.send(str.encode("Hello"))
    start_new_thread(threaded_client, (conn,))