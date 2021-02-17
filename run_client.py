from client.Client import Client
import string
import random


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


c = Client(
    serverName="localhost",
    serverPort=12345,
    username=_generate_word(12)
)

c.clientSocket.close()
