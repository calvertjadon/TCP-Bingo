import time
import socket
import threading
import random
import sys
from server.Client import Client


class Server:
    COMMAND_PREFIX = "/"

    def __init__(self, serverPort: int) -> None:
        print("type QUIT to close")
        self.KEEP_RUNNING = True
        self.game_started = False
        self.history = []

        # manage connected clients
        self.connected_clients: list[Client] = []
        self.waiting_clients: list[Client] = []

        # create and bind socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', serverPort))

        # create and start server thread
        self.sthread = threading.Thread(
            target=self.run,
            daemon=True,
            name="STHREAD"
        )

        self.cmdthread = threading.Thread(
            target=self.listen_for_commands,
            daemon=True,
            name="CMDTHREAD"
        )

        self.sthread.start()
        self.cmdthread.start()
        self.cmdthread.join()

    def listen_for_commands(self) -> None:
        while self.KEEP_RUNNING:
            cmd = input()
            if cmd == "QUIT":
                self.KEEP_RUNNING = False
                return sys.exit(0)

    def run(self) -> None:
        # begin listening for incoming connections
        self.serverSocket.listen(1)
        print('The server is ready to receive')

        while self.KEEP_RUNNING:
            # get a connection from a client
            try:
                connectionSocket, addr = self.serverSocket.accept()
            except:
                return

            # client sends username upon connection
            read = connectionSocket.makefile('r')
            username = read.readline().strip()

            # create client object and register it in the game
            client = Client(connectionSocket, self, username)

            # start up a thread for that client
            cl = threading.Thread(
                target=client.listen,
                daemon=True,
                name=client.id
            )
            cl.start()

            # add to client list
            if not self.game_started:
                self.connected_clients.append(client)
                client.send_message("To start the game, type: /start")
            else:
                self.waiting_clients.append(client)
                client.send_message(
                    "Game has already started.  You will join the next round"
                )

        # cleanup
        self.serverSocket.close()

    def start_game(self) -> None:
        if not self.game_started:
            self.game_started = True

            # setup
            for c in self.connected_clients:
                card = self.get_new_card()
                c.send_card(card)

            gamethread = threading.Thread(target=self.game_loop, daemon=True)
            gamethread.start()

    def game_loop(self):
        while self.game_started:

            number = self.get_next_number()

            for c in self.connected_clients:
                # un-ready all clients
                c.READY = False

                # send new number
                c.send_number(number)

            ALL_READY = self.wait_for_all_ready()
            while not ALL_READY:
                ALL_READY = self.wait_for_all_ready()

            time.sleep(1)

    def wait_for_all_ready(self) -> bool:
        ALL_READY = True
        for c in self.connected_clients:
            ALL_READY = ALL_READY and c.READY
        return ALL_READY

    def get_next_number(self) -> int:
        number = random.randint(0, 75)

        if number not in self.history:
            self.history.append(number)
            return number
        else:
            return self.get_next_number()

    def declare_winner(self, c: Client):
        self.announce(f"{c.username} has BINGO!")
        self.prepare_for_new_round()

    def prepare_for_new_round(self) -> None:
        self.game_started = False
        self.history = []

        # connect clients in queue
        for i in range(len(self.waiting_clients)):
            c = self.waiting_clients.pop(0)
            self.connected_clients.append(c)

        for c in self.connected_clients:
            # ready all clients
            c.READY = True

        self.announce(
            "Ready to begin new round.  New clients can now connect.  To start the game, type: /start"
        )

    @staticmethod
    def get_new_card() -> list[list[int]]:
        card = []
        CARD_SIZE = len("BINGO")

        for i in range(0, CARD_SIZE):
            column = []
            for j in range(0, CARD_SIZE):
                number = random.randint(
                    i * 15 + 1,
                    (i + 1) * 15
                )

                while number in column:
                    number = random.randint(
                        i * 15 + 1,
                        (i + 1) * 15
                    )

                column.append(number)
            column = sorted(column)
            card.append(column)
        return card

    def announce(self, message: str) -> None:
        for c in self.connected_clients:
            c.send_message(message)
