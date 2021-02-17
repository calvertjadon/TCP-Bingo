import random
from server import Server
from server import Bingo
import socket
import string


class Client:
    COMMAND_PREFIX = "/"

    def __init__(self, socket: socket.socket, server: Server) -> None:
        def _generate_word(length):
            # https://gist.github.com/noxan/5845351
            VOWELS = "aeiou"
            CONSONANTS = "".join(set(string.ascii_lowercase) - set(VOWELS))

            word = ""
            for i in range(length):
                if i % 2 == 0:
                    word += random.choice(CONSONANTS)
                else:
                    word += random.choice(VOWELS)
            return word

        self.name = _generate_word(12)  # create a unique username

        self.KEEP_RUNNING = True

        # set socket and server
        self.clientSocket = socket
        self.server = server

        self.send(f"Connected as user: {self.name}\n")

        # init game and card
        self.game: Bingo = None
        self.card: list[list[int]] = None

    def print_board(self):
        board_str = ""
        for letter in "BINGO":
            board_str += f"{letter}\t"
        board_str += "\n"

        for i in range(0, 5):
            for j in range(0, 5):
                board_str += f"{self.card[j][i]}\t"
            board_str += "\n"

        self.send(board_str)

    def check_number(self, num: int) -> None:
        for row in range(0, 5):
            for col in range(0, 5):
                if self.card[row][col] == num:
                    self.card[row][col] = 0

    def check_for_victory(self):
        forward = True
        backward = True

        for i in range(0, 5):
            if self.card[i][i] != 0:
                # check forward diagonal
                forward = False

            if self.card[i][4-i] != 0:
                # check backwards diagonal
                backward = False

            horizontal = True
            vertical = True
            for j in range(0, 5):
                # check horizontal
                if self.card[i][j] != 0:
                    horizontal = False

                # check vertical
                if self.card[j][i] != 0:
                    vertical = False

            if horizontal or vertical:
                return True

        return forward or backward

    def listen(self) -> None:

        while self.KEEP_RUNNING:
            # get a message from the client
            try:
                msg = self.clientSocket.recv(4096).decode()
            except:
                # exit if socket is closed
                self.close()
                return

            # empty - Assume the client has disconnected
            if len(msg) == 0:
                self.close()
                return

            # debug output
            print(f"{self}: {msg}")

            if msg.startswith(Client.COMMAND_PREFIX):
                # handle commands
                output = self.handle_command(msg)
                if output:
                    print(output)
            # else:
            #     # anything that isn't a command gets sent to all clients
            #     self.game.announce(f"{self.name}: {msg}")

        # cleanup
        self.clientSocket.close()

    def close(self):
        # remove client from game and close socket
        try:
            # remove if in game
            self.game.drop_client(self)
        except:
            pass
        self.KEEP_RUNNING = False
        self.clientSocket.close()
        print(f"{self} has disconnected")

    def handle_command(self, command: str):
        # reference to function is stored in dictionary
        COMMANDS = {
            "roll": self.game.roll,
            # "print": self.game.get_board,
            "start": self.game.start,
            "my_board": self.card,
            # "game_over": self.game.end_game
        }

        # corresponding function reference is called if exists
        command = command.replace(Client.COMMAND_PREFIX, "").strip()
        if command in COMMANDS.keys():
            # current client object is passed as a parameter to all command methods
            return COMMANDS[command](self)
        else:
            self.send("Invalid command")

    # send message to this client
    def send(self, message: str) -> None:
        try:
            self.clientSocket.send(message.encode())
        except:
            self.close()

    # set game attr
    def join_game(self, game: Bingo):
        self.game = game

        if self.game == None:
            self.close()

    def __str__(self) -> str:
        return f"Client( {self.name} )"
