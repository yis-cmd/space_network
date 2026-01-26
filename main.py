from time import sleep
from space_network_lib import DataCorruptedError, Packet, SpaceEntity, SpaceNetwork, TemporalInterferenceError


class Sattelite(SpaceEntity):
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

    

if __name__ == "__main__":
    network = SpaceNetwork(level=2)
    sat1 = Sattelite("sat1", 100)
    sat2 = Sattelite("sat2", 200)
    message = Packet("cwfvsdgkbuydxyvfbuxrhj", sat1, sat2)
    attempt_transmission(message)