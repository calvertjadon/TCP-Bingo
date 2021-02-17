from socket import getnameinfo
from server.Client import Client
import random
import time
import math


class Bingo:
    def __init__(self) -> None:
        self.GAME_OVER = False
        self.GAME_STARTED = False

        self.clients: list[Client] = []  # currently connected clients
        self.history: list[int] = []  # all numbers called

    # start game and randomize boards of all connected clients
    def start(self, c: Client = None):
        if not self.GAME_STARTED:
            self.GAME_STARTED = True

            self.randomize_client_boards()

            while not self.GAME_OVER and len(self.clients) > 0:
                number = self.roll()
                letter = "BINGO"[math.floor(((number-1)/15))]

                for c in self.clients:
                    c.send("\n" * 100)

                    c.send(f"The ball reads: {letter} {number}\n")
                    c.check_number(number)
                    c.print_board()

                winner = self.check_for_victories()
                if winner:
                    self.announce(f"{winner.name} has BINGO!")

                    time.sleep(2)
                    self.GAME_OVER = True
                else:
                    time.sleep(2)

            self.GAME_OVER = False
            self.GAME_STARTED = False

            for c in self.clients:
                c.close()

        else:
            c.send("Game already started")

    def check_for_victories(self) -> Client:
        for c in self.clients:
            if c.check_for_victory():
                self.GAME_OVER = True
                return c

    def randomize_client_boards(self):
        print(f"Connected: {len(self.clients)}")

        for c in self.clients:
            print(c.name)
            c.card = [
                [],
                [],
                [],
                [],
                [],
            ]

            for letter in range(0, 5):
                for row in range(0, 5):
                    number = random.randint(
                        letter * 15 + 1,
                        (letter + 1) * 15
                    )

                    while number in c.card[letter]:
                        number = random.randint(
                            letter * 15,
                            (letter + 1) * 15
                        )

                    c.card[letter].append(number)

            for i in range(0, 5):
                c.card[i] = sorted(c.card[i])

            c.print_board()

    # get next number

    def roll(self, c: Client = None) -> int:
        if not self.GAME_STARTED:
            return c.send("Start game to use this command")

        ball = random.randint(0, 75)

        if ball not in self.history:
            return ball
        else:
            return self.roll(c)

    # def end_game(self, c: Client = None):
    #     if self.GAME_STARTED:
    #         self.GAME_OVER = True
    #     else:
    #         c.send("Cannot end a game that has not started")

    def add_client(self, c: Client):
        # cannot add client if game has started
        if not self.GAME_STARTED:
            self.clients.append(c)
            c.join_game(self)
            print(f"{c} connected")

            print(f"Active: ", *self.clients)
        else:
            c.send("Game already in progress")
            c.close()

    def drop_client(self, c: Client):
        self.clients.remove(c)

    def announce(self, message: str):
        for c in self.clients:
            try:
                c.send(message)
            except ConnectionAbortedError as e:
                print(f"Failed to send message to {c.name}...dropping")
                self.drop_client(c)

        print(f"Active:", len(self.clients))
