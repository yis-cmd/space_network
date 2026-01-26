from space_network_lib import Packet, SpaceEntity, SpaceNetwork


class Sattelite(SpaceEntity):
    def receive_signal(self, packet: Packet):
        print(f"[{self.name}] Received: {packet}")




def main():
    network = SpaceNetwork(level=1)
    sat1 = Sattelite("sat1", 100)
    sat2 = Sattelite("sat2", 200)
    message = Packet("cwfvsdgkbuydxyvfbuxrhj", sat1, sat2)
    network.send(message)

if __name__ == "__main__":
    main()