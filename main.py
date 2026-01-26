from time import sleep
from space_network_lib import DataCorruptedError, LinkTerminatedError, OutOfRangeError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError

class BrokenConnectionError(Exception):
    pass

class Satellite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")

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
    network = SpaceNetwork(level=3)
    sat1 = Satellite("sat1", 100)
    sat2 = Satellite("sat2", 200)
    message = Packet("cwfvsdgkbuydxyvfbuxrhj", sat1, sat2)
    try:
        attempt_transmission(message)
    except BrokenConnectionError:
        print("Transmission failed")