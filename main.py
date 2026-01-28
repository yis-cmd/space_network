from __future__ import annotations
from time import sleep
from space_network_lib import DataCorruptedError, LinkTerminatedError, OutOfRangeError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError

class BrokenConnectionError(Exception):
    pass

class EncryptedPacket(Packet):
    def __init__(self, data, sender, receiver, key):
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

def find_route(space_entities:list[SpaceEntity], message:Packet, key)-> Packet | RelayPacket:
    assert isinstance(message.sender, SpaceEntity)
    assert isinstance(message.receiver, SpaceEntity)
    if message.sender.distance_from_earth + 150 >= message.receiver.distance_from_earth:
        encrypted = EncryptedPacket(message.data, message.sender, message.receiver, key)
        print(f"the encrypted message is {encrypted}")
        return encrypted
    for entity in space_entities:
        if entity.distance_from_earth > message.sender.distance_from_earth and entity.distance_from_earth - message.sender.distance_from_earth <= 150:
            proxy = entity
            break
    if proxy is None:
        raise OutOfRangeError
    new_message = find_route(space_entities, Packet(message.data, proxy, message.receiver), key)
    return RelayPacket(new_message, message.sender, proxy)

def smart_send_packet(space_entities:list[SpaceEntity], message:Packet, key):
    to_send = find_route(space_entities, message, key)
    attempt_transmission(to_send)

if __name__ == "__main__":
    network = SpaceNetwork(level=7)
    sat1 = Satellite("sat1", 100, 1)
    sat2 = Satellite("sat2", 200, 2)
    sat3 = Satellite("sat3", 300, 3)
    sat4 = Satellite("sat4", 400, 4)
    earth = Earth("earth", 0)
    space_entities = [sat1, sat2, sat3, sat4, earth]
    p_final = Packet("Hello from Earth!!", earth, sat4)
    try:
        key = earth.keys(p_final.receiver.name)
        smart_send_packet(space_entities, p_final, key)
    except BrokenConnectionError:
        print("Transmission failed")
