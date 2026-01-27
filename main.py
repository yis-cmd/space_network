from __future__ import annotations
from time import sleep

from space_network_lib import DataCorruptedError, LinkTerminatedError, OutOfRangeError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError

class BrokenConnectionError(Exception):
    pass

class RelayPacket(Packet):
    def __init__(self, packet_to_relay:Packet | RelayPacket, sender:SpaceEntity, proxy:SpaceEntity):
        super().__init__(packet_to_relay, sender, proxy)
    
    def __repr__(self):
        # return f"{self.sender} {self.receiver}"
        return f"RelayPacket(Relaying [{self.data}] to {self.receiver} from {self.sender})"

class Satellite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            attempt_transmission(inner_packet)
        else:
            print(f"[{self.name}] Received: {packet}")

class Earth(SpaceEntity):
    def receive_signal(self, packet: Packet):
        pass

def attempt_transmission(message:Packet):
    while True:
        try:
            network.send(message)
            return
        except TemporalInterferenceError:
            print("Interference, waiting...")
            sleep(2)
        except DataCorruptedError:
            print("Data corrupted, retrying...")
        except LinkTerminatedError:
            print("Link lost")
            raise BrokenConnectionError
        except OutOfRangeError:
            print("Target out of range")
            raise BrokenConnectionError
    
def find_route(space_entities:list[SpaceEntity], message:Packet)-> Packet | RelayPacket:
    assert isinstance(message.sender, SpaceEntity)
    assert isinstance(message.receiver, SpaceEntity)
    if message.sender.distance_from_earth + 150 >= message.receiver.distance_from_earth:
        return message
    for entity in space_entities:
        if entity.distance_from_earth > message.sender.distance_from_earth and entity.distance_from_earth - message.sender.distance_from_earth <= 150:
            proxy = entity
            break
    if proxy is None:
        raise OutOfRangeError
    new_message = find_route(space_entities, Packet(message.data, proxy, message.receiver))
    return RelayPacket(new_message, message.sender, proxy)

def smart_send_packet(space_entities:list[SpaceEntity], message:Packet):
    to_send = find_route(space_entities, message)
    attempt_transmission(to_send)

if __name__ == "__main__":
    network = SpaceNetwork(level=6)
    sat1 = Satellite("sat1", 100)
    sat2 = Satellite("sat2", 200)
    sat3 = Satellite("sat3", 300)
    sat4 = Satellite("sat4", 400)
    earth = Earth("earth", 0)
    space_entities = [sat1, sat2, sat3, sat4, earth]
    p_final = Packet("Hello from Earth!!", earth, sat4)
    try:
        smart_send_packet(space_entities, p_final)
    except BrokenConnectionError:
        print("Transmission failed")