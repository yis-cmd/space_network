from time import sleep
from space_network_lib import DataCorruptedError, LinkTerminatedError, OutOfRangeError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError

class BrokenConnectionError(Exception):
    pass

class RelayPacket(Packet):
    def __init__(self, packet_to_relay, sender, proxy):
        super().__init__(packet_to_relay, sender, proxy)
    
    def __repr__(self):
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

if __name__ == "__main__":
    network = SpaceNetwork(level=5)
    sat1 = Satellite("sat1", 100)
    sat2 = Satellite("sat2", 200)
    sat3 = Satellite("sat3", 300)
    sat4 = Satellite("sat4", 400)
    earth = Earth("earth", 0)
    p_final = Packet("Hello from Earth!!", sat3, sat4)
    p_sat2_to_sat3 = RelayPacket(p_final, sat2, sat3)
    p_sat1_to_sat2 = RelayPacket(p_sat2_to_sat3, sat1, sat2)
    p_earth_to_sat1 = RelayPacket(p_sat1_to_sat2, earth, sat1)
    try:
        attempt_transmission(p_earth_to_sat1)
    except BrokenConnectionError:
        print("Transmission failed")