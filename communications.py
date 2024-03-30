import socket
import json
from typing import *

def recvlen(sock:socket.socket,n:int):
    data = b""
    while len(data)<n:
        bytesrecieved = sock.recv(n-len(data))
        if not bytesrecieved:
            return False
        data += bytesrecieved
    return data

def msghead(message,header = b"HEAD"):
    return header + len(message).to_bytes(10,"big") + message

class Client:
    client_socket:socket.socket = None
    server_address:str = None
    server_port:int = None
    connection_attempts:int = None
    client_mainloops:Dict[int,None] = {}
    mainloop_running:bool = False

    def __init__(self,ip:str = None,port:int = None,connection_attempts:int = None):
        if ip and port and connection_attempts:
            self.server_address = ip
            self.server_port = int(port)
            self.connection_attempts = int(connection_attempts)
        else:
            config_file = open(__file__[:-len(__file__.split("/")[-1])]+"config/communications.json")
            config = json.load(config_file)
            config_file.close()
            self.server_address = config["server_address"]
            self.server_port = config["server_port"]
            self.connection_attempts = config["connection_attempts"]
    
    def create_client(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        for i in range(self.connection_attempts):
            try:
                self.client_socket.connect((self.server_address,self.server_port))
                break
            except OSError as e:
                print(f"Error encountered. Trying again.\n{str(e)}")
        
    def begin_client_mainloop(self) -> None:
        try:
            self.mainloop_running = True
            while self.mainloop_running:
                for i in self.client_mainloops:
                    self.client_mainloops[i](self.client_socket,self)
        except:
            self.mainloop_running = False
            print("Exiting mainloop...")
    def stop_client_mainloop(self) -> None:
        self.mainloop_running = False

    def add_client_mainloop(self,func) -> int:
        id = len(self.client_mainloops)
        self.client_mainloops[id] = func
        return id
    
    def remove_client_mainloop(self,id) -> bool:
        try:
            del self.client_mainloops[id]
            return True
        except:
            return False

    def handshake(self) -> bool:
        handshake = self.client_socket.recv(4)
        if not handshake or handshake != b"HNDS":
            print("No handshake recieved" if not handshake else f"Invalid handshake:\n{handshake}")
            return False
        self.client_socket.sendall(b"HSAC")
        return True

    def __del__(self) -> None:
        self.destroy()
    
    def destroy(self) -> None:
        self.client_socket.close()