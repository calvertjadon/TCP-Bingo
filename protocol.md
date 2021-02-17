# Bingo Game

## Requirements

- You must create a Bingo application protocol that the clients and server will use to communicate.
- For simplicity, we will assume that each player has one card.
- Each round will end when one player has a bingo.
- A player may not join in the middle of a round .  If a player arrives while a round is underway, that player must wait until the beginning of the next round .
- A player may leave at any time.  Leaving in the middle of a round is considered to be a loss.
- At the beginning of each round the server should create a new card for each player and send them to the client.
- You should allow any number of players.
- After each number is called, allow some time for the players to update their card and call bingo if appropriate.

## Protocol

### Client -> Server

- Command: sender, action
- Disconnect: "/quit"
- Manages own card
  - notifies server if won

### Server -> Client

- Server will have to track current clients and handle disconnects
  - When a client connects, they are given a card
  - New clients cannot join an active game.  They will be added to a queue.
- Quit: "/quit"
- Sends numbers to all clients
  - Message: "check:{number}"
- Once a winner is found, their name is announces and new cards are handed out
