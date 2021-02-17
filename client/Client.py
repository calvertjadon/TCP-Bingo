import socket
import threading
import os
import sys
import json
import math


class Client:
    def __init__(self, serverName: str, serverPort: int, username: str = "Guest") -> None:
        self.KEEP_RUNNING = True

        self.username = username

        self.card = None

        # create socket and connect to server
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((serverName, serverPort))

        self.read = self.clientSocket.makefile("r")
        self.write = self.clientSocket.makefile("w")

        self.send(self.username)

        # create i/o threads
        self.out_thread = threading.Thread(target=self.outgoing, daemon=True)
        self.in_thread = threading.Thread(target=self.incoming, daemon=True)

        # start threads
        self.out_thread.start()
        self.in_thread.start()

        # join threads
        self.in_thread.join()

    def send(self, message: str) -> None:
        self.write.write(message + "\n")
        self.write.flush()

    def outgoing(self) -> None:
        with self.write:
            while self.KEEP_RUNNING:
                message = input()

                # Send it to the server
                self.send(message)

    def incoming(self) -> None:
        actions = {
            "MSG": print,
            "NEW_CARD": self.load_new_card_from_str,
            "CHECK_NUMBER": self.check_new_number
        }

        with self.read:
            while self.KEEP_RUNNING:
                # get the uppercase response from the server
                incoming = self.read.readline()

                if not incoming:
                    # stop the thread
                    return sys.exit(0)

                raw = incoming.strip()
                action, body = (None, None)

                try:
                    action, body = raw.split("|")
                except ValueError:
                    return print(raw)

                if action in actions.keys():
                    actions[action](body)
                else:
                    print(f"ERROR: UNKNOWN ACTION [{action}]")

    def load_new_card_from_str(self, card_str: str) -> None:
        card: list[list[int]] = json.loads(card_str)
        self.card = card
        print("New card recieved from server")

    def check_new_number(self, number: str) -> None:
        CARD_SIZE = len("BINGO")
        number = int(number)
        letter = "BINGO"[math.floor(((number-1)/15))]

        print(f"The number is: {letter} {number}")

        for i in range(0, CARD_SIZE):
            for j in range(0, CARD_SIZE):
                if self.card[i][j] == number:
                    self.card[i][j] = 0
                    print("That number is on your card!")
                    self.print_card()
                    if self.check_for_victory():
                        self.declare_victory()
                        return
        self.print_card()
        self.send_ready()
        return

    def print_card(self) -> None:
        card_str = ""
        for letter in "BINGO":
            card_str += f"{letter}\t"
        card_str += "\n"

        CARD_SIZE = len("BINGO")

        for i in range(0, CARD_SIZE):
            for j in range(0, CARD_SIZE):
                card_str += f"{self.card[j][i]}\t"
            card_str += "\n"

        print(card_str)

    def check_for_victory(self) -> bool:
        forward = True
        backward = True

        CARD_SIZE = len("BINGO")

        for i in range(0, CARD_SIZE):
            if self.card[i][i] != 0:
                # check forward diagonal
                forward = False

            if self.card[i][CARD_SIZE - 1 - i] != 0:
                # check backwards diagonal
                backward = False

            horizontal = True
            vertical = True
            for j in range(0, CARD_SIZE):
                # check horizontal
                if self.card[i][j] != 0:
                    horizontal = False

                # check vertical
                if self.card[j][i] != 0:
                    vertical = False

            if horizontal or vertical:
                return True

        return forward or backward

    def declare_victory(self) -> None:
        print("I win!")
        self.send("BINGO")

    def send_ready(self) -> None:
        self.send("READY")
