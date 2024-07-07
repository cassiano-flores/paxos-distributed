import os, signal, sys, time
from acceptor import Acceptor
from leader import Leader
from message import RequestMessage
from replica import Replica
from utils import *

NACCEPTORS = 3
NREPLICAS = 2
NLEADERS = 2
NREQUESTS = 10
NCONFIGS = 2


class Env:
    def __init__(self):
        self.procs = {}

    def sendMessage(self, dst, msg):
        if dst in self.procs:
            self.procs[dst].deliver(msg)

    def addProc(self, proc):
        self.procs[proc.id] = proc
        proc.start()

    def removeProc(self, pid):
        del self.procs[pid]

    def run(self):
        initialconfig = Config([], [], [])
        c = 0

        for i in range(NREPLICAS):
            pid = "replica %d" % i
            Replica(self, pid, initialconfig)
            initialconfig.replicas.append(pid)
        for i in range(NACCEPTORS):
            pid = "acceptor %d.%d" % (c, i)
            Acceptor(self, pid)
            initialconfig.acceptors.append(pid)
        for i in range(NLEADERS):
            pid = "leader %d.%d" % (c, i)
            Leader(self, pid, initialconfig)
            initialconfig.leaders.append(pid)

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
            choice = input("Choose an option: ")
            if choice == 1:
                account = input("Enter account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "deposit %s %s" % (str(account), str(amount)))
            elif choice == 2:
                account = input("Enter account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "withdraw %s %s" % (str(account), str(amount)))
            elif choice == 3:
                from_account = input("Enter from account: ")
                to_account = input("Enter to account: ")
                amount = input("Enter amount: ")
                cmd = Command(client, req_id, "transfer %s %s %s" % (str(from_account), str(to_account), str(amount)))
            elif choice == 4:
                account = input("Enter account: ")
                cmd = Command(client, req_id, "balance %s" % str(account))
            else:
                print("Invalid choice")
                continue

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
