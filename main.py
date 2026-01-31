from __future__ import annotations
from time import sleep
import find_route
from space_network_lib import DataCorruptedError, LinkTerminatedError, OutOfRangeError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError

class BrokenConnectionError(Exception):
    pass

class NoSuchEntityError(Exception):
    pass

class EncryptedPacket(Packet):
    def __init__(self, data:str, sender:SpaceEntity, receiver:SpaceEntity, key:int):
        super().__init__(data, sender, receiver)
        self.data  = self.__encrypt(key)

    @staticmethod
    def __xor_cipher(data, key):
        return "".join([chr(ord(char) ^ key) for char in data])
    def __encrypt(self, key):
        return self.__xor_cipher(self.data, key)
    def decrypt(self, key):
        return self.__xor_cipher(self.data, key)
    
class RelayPacket(Packet):
    def __init__(self, packet_to_relay:Packet | RelayPacket, sender:SpaceEntity, proxy:SpaceEntity):
        super().__init__(packet_to_relay, sender, proxy)
    
    def __repr__(self):
        return f"RelayPacket(Relaying [{self.data}] to {self.receiver} from {self.sender})"

class Satellite(SpaceEntity):
    def __init__(self, name, distance_from_earth, key):
        super().__init__(name, distance_from_earth)
        self.key = key
    def receive_signal(self, packet: Packet):
        if isinstance(packet, RelayPacket):
            inner_packet = packet.data
            print(f"Unwrapping and forwarding to {inner_packet.receiver}")
            attempt_transmission(inner_packet)
        else:
            assert isinstance(packet, EncryptedPacket)
            packet.data = packet.decrypt(self.key)
            print(f"[{self.name}] Received: {packet}")

class Earth(SpaceEntity):
    def receive_signal(self, packet: Packet):
        pass
    @staticmethod
    def keys(name):
        sat_keys = {"sat1" : 1,
                    "sat2" : 2,
                    "sat3" : 3,
                    "sat4" : 4
                    }
        return sat_keys.get(name)

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

def build_message(message:EncryptedPacket, route:list[SpaceEntity])->RelayPacket | EncryptedPacket:
    if len(route) < 2:
        return message
    relay = message
    for entity in range(len(route) -1, 0, -1):
        relay = RelayPacket(relay, route[entity -1], route[entity])
    return relay

def smart_send_packet(space_entities:list[SpaceEntity], message:Packet, key:int):
    route:list[SpaceEntity] = find_route.build_route(space_entities, message.sender, message.receiver)
    encrypted_packet = EncryptedPacket(message.data, route[-1], message.receiver, key)
    to_send = build_message(encrypted_packet, route)
    attempt_transmission(to_send)

if __name__ == "__main__":
    network = SpaceNetwork(level=1)
    sat1 = Satellite("sat1", 100, 1)
    sat2 = Satellite("sat2", 200, 2)
    sat3 = Satellite("sat3", 300, 3)
    sat4 = Satellite("sat4", 400, 4)
    earth = Earth("earth", 0)
    
    #shiny new satellites 
    sat5 = Satellite("sat5", 150, 5)
    sat6 = Satellite("sat6", 250, 6)
    sat7 = Satellite("sat7", 350, 7)
    
    space_entities = [sat1, sat2, sat3, sat4, sat5, sat6, sat7, earth]
    p_final = Packet("Hello from Earth!!", earth, sat4)
    try:
        key = earth.keys(p_final.receiver.name)
        if key is None:
            raise NoSuchEntityError
        smart_send_packet(space_entities, p_final, key)
    except BrokenConnectionError:
        print("Transmission failed")
