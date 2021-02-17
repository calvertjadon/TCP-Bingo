import socket
import threading
import os


class Client:
    def __init__(self, serverName, serverPort) -> None:
        self.KEEP_RUNNING = True

        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.clientSocket.connect((serverName, serverPort))

        self.out_thread = threading.Thread(target=self.outgoing, daemon=True)
        self.in_thread = threading.Thread(target=self.incoming, daemon=True)

        self.out_thread.start()
        self.in_thread.start()

        self.out_thread.join()
        self.in_thread.join()

    def outgoing(self) -> None:
        while self.KEEP_RUNNING:
            message = input()

            if message == "QUIT":
                self.clientSocket.close()
                self.KEEP_RUNNING = False
                return

            # Send it to the server
            try:
                self.clientSocket.send(message.encode())
            except:
                self.clientSocket.close()
                self.KEEP_RUNNING = False
                return

    def incoming(self) -> None:
        while self.KEEP_RUNNING:
            # get the uppercase response from the server
            try:
                incoming = self.clientSocket.recv(2048)
            except:
                self.clientSocket.close()
                self.KEEP_RUNNING = False
                return

            if not incoming:
                self.clientSocket.close()
                self.KEEP_RUNNING = False
                print("Disconnected from server")
                return

            msg = incoming.decode()

            # display the response
            print(msg)
