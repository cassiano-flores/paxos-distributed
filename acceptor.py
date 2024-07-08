from utils import PValue
from process import Process
from message import P1aMessage, P1bMessage, P2aMessage, P2bMessage
from tcp_connection import TCPConnection


class Acceptor(Process):
    def __init__(self, env, id, address, port):
        Process.__init__(self, env, id)
        self.ballot_number = None
        self.accepted = set()
        self.address = address
        self.port = port
        self.env.addProc(self, address, port)
        self.tcp_conn = TCPConnection(address, port)

    def body(self):
        print("Here I am: " + self.id)
        while True:
            msg = self.tcp_conn.receive()
            if isinstance(msg, P1aMessage):
                if msg.ballot_number > self.ballot_number:
                    self.ballot_number = msg.ballot_number
                self.sendMessage(msg.src, P1bMessage(self.id, self.ballot_number, self.accepted))
            elif isinstance(msg, P2aMessage):
                if msg.ballot_number == self.ballot_number:
                    self.accepted.add(PValue(msg.ballot_number, msg.slot_number, msg.command))
                self.sendMessage(msg.src, P2bMessage(self.id, self.ballot_number, msg.slot_number))
