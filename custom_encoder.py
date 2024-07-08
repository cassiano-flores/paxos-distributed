import json
from utils import Command, ReconfigCommand, Config, BallotNumber, PValue
from message import Message

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, Message):
            return obj.__dict__
        if isinstance(obj, Command):
            return {"client": obj.client, "req_id": obj.req_id, "op": obj.op}
        if isinstance(obj, ReconfigCommand):
            return {"client": obj.client, "req_id": obj.req_id, "config": obj.config}
        if isinstance(obj, Config):
            return {"replicas": obj.replicas, "acceptors": obj.acceptors, "leaders": obj.leaders}
        if isinstance(obj, BallotNumber):
            return {"round": obj.round, "leader_id": obj.leader_id}
        if isinstance(obj, PValue):
            return {"ballot_number": obj.ballot_number, "slot_number": obj.slot_number, "command": obj.command}
        return json.JSONEncoder.default(self, obj)
