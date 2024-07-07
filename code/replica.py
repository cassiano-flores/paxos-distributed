from process import Process
from message import ProposeMessage, DecisionMessage, RequestMessage
from utils import *
from bank import Bank


class Replica(Process):
    def __init__(self, env, id, config):
        Process.__init__(self, env, id)
        self.slot_in = self.slot_out = 1
        self.proposals = {}
        self.decisions = {}
        self.requests = []
        self.config = config
        self.env.addProc(self)
        self.bank = Bank()

    def propose(self):
        while len(self.requests) != 0 and self.slot_in < self.slot_out + WINDOW:
            if self.slot_in > WINDOW and self.slot_in - WINDOW in self.decisions:
                if isinstance(self.decisions[self.slot_in - WINDOW], ReconfigCommand):
                    r, a, l = self.decisions[self.slot_in - WINDOW].config.split(';')
                    self.config = Config(r.split(','), a.split(','), l.split(','))
                    print(self.id, ": new config:", self.config)
            if self.slot_in not in self.decisions:
                cmd = self.requests.pop(0)
                self.proposals[self.slot_in] = cmd
                for ldr in self.config.leaders:
                    self.sendMessage(ldr, ProposeMessage(self.id, self.slot_in, cmd))
            self.slot_in += 1

    def perform(self, cmd):
        for s in range(1, self.slot_out):
            if self.decisions[s] == cmd:
                self.slot_out += 1
                return
        if isinstance(cmd, ReconfigCommand):
            self.slot_out += 1
            return

        # Process bank commands here
        op_parts = cmd.op.split()
        print("\n#------------------------------------------------------#")
        print("            " + str(self.id).upper())
        print("       operation: %s" % str(op_parts[0]))
        print("         account: %s" % str(op_parts[1]))

        if op_parts[0] == "deposit":
            account, amount = op_parts[1], int(op_parts[2])
            self.bank.deposit(account, amount)
            print("          amount: +$%s" % str(op_parts[2]))

        elif op_parts[0] == "withdraw":
            account, amount = op_parts[1], int(op_parts[2])
            success = self.bank.withdraw(account, amount)
            if success:
                print("          amount: -$%s" % str(op_parts[2]))
            else:
                print("     description: withdraw failed! there is not enough balance")

        elif op_parts[0] == "transfer":
            from_account, to_account, amount = op_parts[1], op_parts[2], int(op_parts[3])
            success = self.bank.transfer(from_account, to_account, amount)
            if success:
                print("     description: send $%s to %s successfully!" % (str(amount), str(to_account)))
            else:
                print("     description: transfer failed! there is not enough balance")

        elif op_parts[0] == "balance":
            account = op_parts[1]
            balance = self.bank.get_balance(account)
            print("         balance: $%s" % (str(balance)))

        print("#------------------------------------------------------#")
        self.slot_out += 1

    def body(self):
        print("Here I am: " + self.id)
        while True:
            msg = self.getNextMessage()
            if isinstance(msg, RequestMessage):
                # print("%s received RequestMessage: %s" % (str(self.id), str(msg.command)))
                self.requests.append(msg.command)
            elif isinstance(msg, DecisionMessage):
                # print("%s received DecisionMessage: %s" % (str(self.id), str(msg.command)))
                self.decisions[msg.slot_number] = msg.command
                while self.slot_out in self.decisions:
                    if self.slot_out in self.proposals:
                        if self.proposals[self.slot_out] != self.decisions[self.slot_out]:
                            self.requests.append(self.proposals[self.slot_out])
                        del self.proposals[self.slot_out]
                    self.perform(self.decisions[self.slot_out])
            else:
                print("Replica: unknown msg type")
            self.propose()
