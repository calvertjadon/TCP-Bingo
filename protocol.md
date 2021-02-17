# Bingo Game

## Requirements

- [x]  You must create a Bingo application protocol that the clients and server will use to communicate.
- [x]  For simplicity, we will assume that each player has one card.
- [x] Each round will end when one player has a bingo.
- [x] A player may not join in the middle of a round .  If a player arrives while a round is underway, that player must wait until the beginning of the next round .
- [x] A player may leave at any time.  Leaving in the middle of a round is considered to be a loss.
- [x] At the beginning of each round the server should create a new card for each player and send them to the client.
- [x] You should allow any number of players.
- [x] After each number is called, allow some time for the players to update their card and call bingo if appropriate.

## Protocol

### Client -> Server

The client only needs to send simple status commands to the server.  These are sent as simple all-caps strings.  The server keeps track of the connected clients so there is no need to include an identifier in the message.

| Status | Notes                                                                  |
| ------ | ---------------------------------------------------------------------- |
| READY  | This is sent when the client is ready to receive the next bingo number |
| BINGO  | This is sent when the client determines that it has won the game       |

The server also accepts simple commands from the client.  These commands start with `/` and the server provides implementation.

| Command | Desired Action | Notes                                     |
| ------- | -------------- | ----------------------------------------- |
| /quit   | Disconnect     |                                           |
| /start  | Start round    | Cannot be run while a game is in progress |

### Server -> Client

Server -> Client messages are a bit more complex.  They consist of an action and a body, separated by a `|` (pipe character).  The client implements functions to handle the body for each action.

- Server will have to track current clients and handle disconnects
  - When a round begins, each client is given a card
  - New clients cannot join an active game.  They will be added to a queue.
- Once a winner is found, their name is announced and new cards are handed out
- After a round ends, members in the queue are connected

| Action       | Body          | Notes                                                                                                                |
| ------------ | ------------- | -------------------------------------------------------------------------------------------------------------------- |
| MSG          | {message:str} | The message body is a simple string and is printed out to the client                                                 |
| NEW_CARD     | {card:json}   | The card received from the server is encoded in json format.  When decoded, it will be in the format list[list[int]] |
| CHECK_NUMBER | {number:int}  | Each connected client is sent the same number to compare against their card                                          |