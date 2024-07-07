from message import P2aMessage, P2bMessage, PreemptedMessage, DecisionMessage
from process import Process
from tcp_connection import TCPConnection


class Commander(Process):
    def __init__(self, env, id, leader, acceptors, replicas, ballot_number, slot_number, command, address, port):
        Process.__init__(self, env, id)
        self.leader = leader
        self.acceptors = acceptors
        self.replicas = replicas
        self.ballot_number = ballot_number
        self.slot_number = slot_number
        self.command = command
        self.address = address
        self.port = port
        self.env.addProc(self, address, port)
        self.tcp_conn = TCPConnection(address, port)

    def body(self):
        waitfor = set()
        for a in self.acceptors:
            self.sendMessage(a, P2aMessage(self.id, self.ballot_number, self.slot_number, self.command))
            waitfor.add(a)

        while True:
            msg = self.tcp_conn.receive()
            if isinstance(msg, P2bMessage):
                if self.ballot_number == msg.ballot_number and msg.src in waitfor:
                    waitfor.remove(msg.src)
                    if len(waitfor) < float(len(self.acceptors)) / 2:
                        for r in self.replicas:
                            self.sendMessage(r, DecisionMessage(self.id, self.slot_number, self.command))
                        return
                else:
                    self.sendMessage(self.leader, PreemptedMessage(self.id, msg.ballot_number))
                    return
