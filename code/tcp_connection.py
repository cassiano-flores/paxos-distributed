import socket
import threading
import time
import json


class TCPConnection:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = None
        self.lock = threading.Lock()
        self.connected = False

    def connect(self):
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.address, self.port))
                self.connected = True
                print("Connected to %s:%s" % (str(self.address), str(self.port)))
            except Exception as e:
                print("\nConnection failed to %s:%s, retrying..." % (str(self.address), str(self.port)))
                time.sleep(5)

    def send(self, message):
        with self.lock:
            if not self.connected:
                self.connect()
            try:
                self.sock.sendall(json.dumps(message).encode())
            except Exception as e:
                print("Failed to send message to %s:%s, retrying..." % (str(self.address), str(self.port)))
                self.connected = False
                self.connect()

    def receive(self):
        with self.lock:
            if not self.connected:
                self.connect()
            try:
                data = self.sock.recv(4096)
                if data:
                    return json.loads(data.decode())
            except Exception as e:
                print("Failed to receive message from %s:%s, retrying..." % (str(self.address), str(self.port)))
                self.connected = False
                self.connect()
        return None
