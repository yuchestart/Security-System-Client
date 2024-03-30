from communications import Client, recvlen, msghead
from typing import *
import cv2
import numpy as np
import atexit
import socket
import os
import sys

customconnectionparams: Dict[str,Any] = {
    "ip":None,
    "port":None,
    "connection_attempts":None
}

for argument in sys.argv:
    arg = argument.split("=")
    if arg[0] in customconnectionparams:
        customconnectionparams[arg[0]] = arg[1]

client: Client = None
cap: cv2.VideoCapture = None
shutdown: bool = False
@atexit.register
def cleanup():
    global cap,client,shutdown
    cap.release()
    client.destroy()
    cv2.destroyAllWindows()
    print("Program Terminated")
    if shutdown:
        print("Shutting down system...")
        os.system("sudo shutdown -h now")


def client_mainloop(sock: socket.socket, client: Client):
    global cap,shutdown
    cancontinue = recvlen(sock,4)
    if cancontinue != b"CTLS":
        if cancontinue == b"STDN":
            print("Shutting down client...")
            client.stop_client_mainloop()
            cleanup()
            shutdown = True
            return
        else:
            print("Server didn't send header." if not cancontinue else f"Server sent invalid header:\n{str(cancontinue)}")
        client.stop_client_mainloop()
    ret,frame = cap.read()
    if ret:
        frame_scaled = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        ret,buf = cv2.imencode('.png',frame_scaled)
        if not ret:
            print("Failure to encode.")
            client.stop_client_mainloop()
        buf = buf.tobytes()
        sock.sendall(msghead(buf,b"LVST"))
    else:
        print("Camera had failed.")
        client.stop_client_mainloop()

cap = cv2.VideoCapture(0)
ret,frame = cap.read()
if not ret:
    print("Failure to initialize camera.")
    quit()

print("Camera created.")

client = Client(**customconnectionparams)
client.create_client()

print("Client created")

handshake = client.handshake()
if not handshake:
    print("Handshake failed!")
    quit()

print("Handshake accepeted; Beginning mainloop")

client.add_client_mainloop(client_mainloop)

client.begin_client_mainloop()