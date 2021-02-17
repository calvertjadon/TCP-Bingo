import secrets
import socket
import server.Server as Server
import threading
import json


class Client:
    COMMAND_PREFIX = "/"

    def __init__(self, clientSocket: socket.socket, server, username: str) -> None:
        self.id = secrets.token_hex()  # unique identifier for each client
        self.username: str = username  # a username that clients can choose

        self.clientSocket = clientSocket
        self.read = self.clientSocket.makefile('r')
        self.write = self.clientSocket.makefile('w')

        self.server = server

        self.KEEP_RUNNING = True

        self.READY = True

        print(f"{self.username} has connected")
        self.send_message(f"Connected as {self.username}")

    def _send(self, action: str, body: str) -> None:
        try:
            self.write.write(f"{action}|{body}\n")
            self.write.flush()
        except ConnectionResetError:
            self.close()

    def send_message(self, message: str) -> None:
        self._send("MSG", message)

    def send_card(self, card: list[list[int]]):
        card_str = json.dumps(card)
        self._send("NEW_CARD", card_str)

    def send_number(self, number: int) -> None:
        self._send("CHECK_NUMBER", number)

    def listen(self) -> None:
        while self.KEEP_RUNNING:
            # get a message from the client
            try:
                data = self.read.readline()
            except ConnectionResetError:
                # client has disconnected
                # stop thread
                return self.close()

            msg = data.strip()

            # empty - Assume the client has disconnected
            if not msg:
                return

            # debug output
            print(f"{self.username}: {msg}")

            if msg.startswith(Client.COMMAND_PREFIX):
                # handle commands
                output = self.handle_command(msg)
                if output:
                    print(output)
            else:
                self.handle_response(msg)

        # cleanup
        self.clientSocket.close()

    def close(self):
        # close socket and remove from server
        self.KEEP_RUNNING = False
        self.clientSocket.close()
        try:
            self.server.connected_clients.remove(self)
        except ValueError:
            self.server.waiting_clients.remove(self)

        print(f"{self.username} has disconnected")

        # end round if everyone disconnects
        if len(self.server.connected_clients) == 0:
            self.server.prepare_for_new_round()

    def handle_response(self, response: str) -> None:
        expected_responses = {
            "READY": self.ready_up,
            "BINGO": lambda: self.server.declare_winner(self)
        }

        if response in expected_responses:
            expected_responses[response]()
        else:
            print(f"UNEXPECTED RESPONSE {self.id}: {response}")

    def ready_up(self):
        self.READY = True

    def handle_command(self, command: str) -> None:
        command = command.replace(Client.COMMAND_PREFIX, "").strip()

        commands = {
            "quit": self.close,
            "start": self.server.start_game,
            "stop": self.server.prepare_for_new_round,
        }

        if command in commands.keys():
            commands[command]()
        else:
            self.send_message("Invalid command")
