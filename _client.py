from client import Client


def run_client():
    c = Client(serverName="localhost", serverPort=12345)

    # user quit, close the socket
    c.clientSocket.close()


if __name__ == "__main__":
    run_client()
