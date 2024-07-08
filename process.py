import multiprocessing
from threading import Thread
from tcp_connection import TCPConnection


class Process(Thread):
    def __init__(self, env, id):
        super(Process, self).__init__()
        self.inbox = multiprocessing.Manager().Queue()
        self.env = env
        self.id = id
        self.tcp_conn = None

    def run(self):
        try:
            self.body()
            self.env.removeProc(self.id)
        except EOFError:
            print("Exiting..")

    def getNextMessage(self):
        if self.tcp_conn:
            return self.tcp_conn.receive()
        else:
            return self.inbox.get()

    def sendMessage(self, dst, msg):
        if self.tcp_conn:
            self.tcp_conn.send(dst, msg)
        else:
            self.env.sendMessage(dst, msg)

    def deliver(self, msg):
        if self.tcp_conn:
            self.tcp_conn.send(msg)
        else:
            self.inbox.put(msg)
