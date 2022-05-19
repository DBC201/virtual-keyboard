# Remote Control

Gives remote control of mouse and keyboard. Supports multiple clients at once.
However, currently only one sender is supported.

## Setup
### Running the Server
```python3 Server.py --port <port>```

port is the port you want the server to run at. Clients will be connecting to this
port via your ip. If this parameter is omitted, server binds to port number 41369 by default.
### Running the Sender
```python3 Sender.py <ip> <port>```

ip and port are for connecting to the server. Upon connection by typing list,
clients available for connection can be seen. To connect, one types their id. 
Once connected, your mouse and keyboard changes will be reflected to the client.
To disconnect, hit '~'. For now, your own mouse doesn't get locked in place,
which makes this hard to use.

### Running the client
```python3 Client.py <ip> <port> --verbose --loop```

verbose gives detailed output to the console. loop will attempt to connect indefinitely to
the server. Upon running this script, your keyboard and mouse are open to manipulation
from sender if they choose to connect.