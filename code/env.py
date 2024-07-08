import os
import signal
import sys
import time
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from utils import *
from tcp_connection import TCPConnection

NACCEPTORS = 3
NREPLICAS = 2
NLEADERS = 2

# addresses and ports
ADDRESSES = {
    "replica": [("127.0.0.1", 5001), ("127.0.0.1", 5002)],
    "acceptor": [("127.0.0.1", 5003), ("127.0.0.1", 5004), ("127.0.0.1", 5005)],
    "leader": [("127.0.0.1", 5006), ("127.0.0.1", 5007)]
}


class Env:
    def __init__(self):
        self.procs = {}

    def sendMessage(self, dst, msg):
        if dst in self.procs:
            self.procs[dst].deliver(msg)

    def addProc(self, proc, address, port):
        self.procs[proc.id] = proc
        proc.tcp_conn = TCPConnection(address, port)

    def removeProc(self, pid):
        del self.procs[pid]

    def run(self):
        initialconfig = Config([], [], [])
        processes = []

        # Start replicas
        for i, (address, port) in enumerate(ADDRESSES["replica"]):
            pid = "replica %d" % i
            proc = Replica(self, pid, initialconfig, address, port)
            initialconfig.replicas.append(pid)
            self.addProc(proc, address, port)
            processes.append(proc)

        # Start acceptors
        for i, (address, port) in enumerate(ADDRESSES["acceptor"]):
            pid = "acceptor %d" % i
            proc = Acceptor(self, pid, address, port)
            initialconfig.acceptors.append(pid)
            self.addProc(proc, address, port)
            processes.append(proc)

        # Start leaders
        for i, (address, port) in enumerate(ADDRESSES["leader"]):
            pid = "leader %d" % i
            proc = Leader(self, pid, initialconfig, address, port)
            initialconfig.leaders.append(pid)
            self.addProc(proc, address, port)
            processes.append(proc)

        # Start all processes
        for proc in processes:
            proc.start()

        time.sleep(1)
        client = "client"
        req_id = 0

        while True:
            print("\n#------------------------------------------------------#")
            print("1. deposit  (account, amount)")
            print("2. withdraw (account, amount)")
            print("3. transfer (from_account, to_account, amount)")
            print("4. balance  (account)")
            print("#------------------------------------------------------#\n")
            choice = int(input("Choose an option: "))
            if choice == 1:
                account = input("Enter account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "deposit %s %s" % (account, amount))
            elif choice == 2:
                account = input("Enter account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "withdraw %s %s" % (account, amount))
            elif choice == 3:
                from_account = input("Enter from account: ")
                to_account = input("Enter to account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "transfer %s %s %s" % (from_account, to_account, amount))
            elif choice == 4:
                account = input("Enter account: ")
                cmd = Command(client, req_id, "balance %s" % account)
            else:
                print("Invalid choice")
                continue

            print(initialconfig.replicas)
            for r in initialconfig.replicas:
                self.sendMessage(r, RequestMessage(client, cmd))
                time.sleep(1)

            req_id += 1

    def terminate_handler(self, signal, frame):
        self._graceexit()

    def _graceexit(self, exitcode=0):
        sys.stdout.flush()
        sys.stderr.flush()
        os._exit(exitcode)


def main():
    e = Env()
    e.run()
    signal.signal(signal.SIGINT, e.terminate_handler)
    signal.signal(signal.SIGTERM, e.terminate_handler)
    signal.pause()


if __name__ == '__main__':
    main()
