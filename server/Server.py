import socket
import threading
from server.Bingo import Bingo
from server.Client import Client


class Server:
    def __init__(self, serverPort: int) -> None:
        # initialize Bingo game
        self.game = Bingo()

        # create and bind socket
        self.serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.serverSocket.bind(('', serverPort))

        # create and start server thread
        self.sthread = threading.Thread(
            target=self.run,
            daemon=True,
            name="STHREAD"
        )
        self.sthread.start()

    def run(self) -> None:
        # begin listening for incoming connections
        self.serverSocket.listen(1)
        print('The server is ready to receive')

        while True:
            # get a connection from a client
            connectionSocket, addr = self.serverSocket.accept()

            # create client object and register it in the game
            client = Client(connectionSocket, self)
            self.game.add_client(client)

            # start up a thread for that client
            cl = threading.Thread(target=client.listen,
                                  daemon=True, name=client.name)
            cl.start()

        # cleanup
        server.serverSocket.close()
