import socket
import threading
import time
import json
from custom_encoder import CustomEncoder

class TCPConnection:
    def __init__(self, address, port):
        self.address = address
        self.port = port
        self.sock = None
        self.lock = threading.Lock()
        self.connected = False
        self.server_thread = threading.Thread(target=self.run_server)
        self.server_thread.daemon = True
        self.server_thread.start()

    def run_server(self):
        server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_sock.bind((self.address, self.port))
        server_sock.listen(5)
        #print("Server listening on %s:%s" % (self.address, self.port))
        while True:
            client_sock, client_addr = server_sock.accept()
            print("Accepted connection from %s:%s" % (client_addr[0], client_addr[1]))
            client_thread = threading.Thread(target=self.handle_client, args=(client_sock,))
            client_thread.daemon = True
            client_thread.start()

    def handle_client(self, client_sock):
        while True:
            try:
                data = client_sock.recv(4096)
                if data:
                    message = json.loads(data.decode())
                    # Process the received message here
                    print("Received message:", message)
                else:
                    break
            except Exception as e:
                print("Error handling client:", e)
                break
        client_sock.close()

    def connect(self):
        while not self.connected:
            try:
                self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self.sock.connect((self.address, self.port))
                self.connected = True
                print("Connected to %s:%s" % (self.address, self.port))
            except Exception as e:
                print("Connection failed to %s:%s, retrying..." % (self.address, self.port))
                time.sleep(5)

    def send(self, message):
        #with self.lock:
        if not self.connected:
            self.connect()
        try:
            self.sock.sendall(json.dumps(message, cls=CustomEncoder).encode())
            print("Sent!")
        except Exception as e:
            print(e)
            print("Failed to send message to %s:%s, retrying..." % (self.address, self.port))
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
                print("Failed to receive message from %s:%s, retrying..." % (self.address, self.port))
                self.connected = False
                self.connect()
        return None
