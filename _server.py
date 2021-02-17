from server import Server
from socket import SHUT_WR, SHUT_RD, SHUT_RDWR


def run_server():

    server = Server(12345)

    commands = {
        "say": server.game.announce
    }

    while True:
        cmd = input()
        if cmd.startswith("/"):
            cmd = cmd.replace("/", "").lower().strip()
            try:
                cmd, arg = cmd.split(" ")
            except ValueError:
                arg = None

            if cmd == "quit":
                break

            if cmd in commands.keys():
                commands[cmd](arg)


if __name__ == "__main__":
    run_server()
