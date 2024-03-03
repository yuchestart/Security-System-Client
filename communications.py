import socket
import json
from typing import *
class Client:
    client_socket:socket.socket = None
    server_address:str = None
    server_port:int = None
    client_mainloops:Dict[int,None] = {}
    mainloop_running:bool = False

    def __init__(self):
        config_file = open("./config/communications.json")
        config = json.load(config_file)
        config_file.close()
        self.server_address = config["server_address"]
        self.server_port = config["server_port"]
    
    def create_client(self) -> None:
        self.client_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        self.client_socket.connect((self.server_address,self.server_port))
    
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

    def __del__(self) -> None:
        self.destroy()
    
    def destroy(self) -> None:
        self.client_socket.close()