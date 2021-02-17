# TCP Bingo

This is a simple game developed for my CSC 460 class in my Spring 2021 semester to demonstrate client-server communication over TCP using web sockets and multi-threading.

## Requirements

* Python 3.9.0

## Installation

This program does not require any external packages and only utilizes modules included in the Python standard library.

Only one server can be instantiated on a particular system at a time, but a system can run any number of clients.

Clone the repo or download the zip and run using either of the following methods:

### Running Manually

* To start the server, run `$ python run_server.py`
* To start a client, run `$ python run_client.py`

### Run Script (Windows only)

I have included a batch file, `start.bat`, that checks for the correct Python version and opens one server instance and two clients.