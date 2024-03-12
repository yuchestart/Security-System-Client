#Import modules
from communications import Client
import cv2
import numpy as np
import atexit
import socket

#Declare variables
client: Client = None
cap: cv2.VideoCapture = None

#Cleanup code
@atexit.register
def cleanup():
    global cap,client
    cap.release()
    client.destroy()
    cv2.destroyAllWindows()
    print("Program terminated.")


def recv(sock:socket.socket,n: int):
    data = b""
    while len(data)<n:
        bytesrecieved = sock.recv(n-len(data))
        if not bytesrecieved:
            return False
        data += bytesrecieved
    return data

#Defining Functions
def msg_with_header(message):
    return b"HEAD"+bytes(f"{len(message):<10}","utf-8") + message

def client_mainloop(sock: socket.socket,client: Client):
    global cap
    cancontinue = recv(sock,8)
    if (not cancontinue) or (cancontinue != b"CONTINUE"):
        print("Server didn't accept.")
        print("Reason: " + "Message sent was invalid" if cancontinue != b"CONTINUE" else "Message was never sent.")
        print(cancontinue)
        client.stop_client_mainloop()
    #Wait for approval from server.
    ret,frame = cap.read()
    if ret:
        frame_scaled = cv2.resize(frame,(0,0),fx=0.25,fy=0.25)
        ret,buf = cv2.imencode(".png",frame_scaled)
        if not ret:
            print("It for some reason failed to encode")
            client.stop_client_mainloop()
        buf = buf.tobytes()
        sock.sendall(msg_with_header(buf))
    else:
        print("Camera failed!")
        client.stop_client_mainloop()
    

print("Begin program")

cap = cv2.VideoCapture(0)
ret,frame = cap.read()
if not ret:
    print("Camera has failed to create!")
    quit()

print("Camera created")

client = Client()
client.create_client()

print("Client created")

handshake = client.client_socket.recv(9)
if (not handshake) or (handshake != b"HANDSHAKE"):
    print("Invalid handshake.")
    quit()

client.client_socket.sendall(b"HANDSHAKE_ACCEPTED")

print("Handshake accepted; Beginning mainloop")

client.add_client_mainloop(client_mainloop)

client.begin_client_mainloop()