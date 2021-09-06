import socket
import sys


class Socket:
    def __init__(self, ip, port, bufsz=64, terminating_character='|'):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.bufsz = bufsz
        self.terminating_character = terminating_character

    def run(self):
        pass

    def send(self, conn, data):
        if sys.getsizeof(data) > self.bufsz:
            raise RuntimeError("Data is too big to send!")
        else:
            data += self.terminating_character.encode()
            conn.send(data)

    def receive(self, conn):
        data = conn.recv(self.bufsz).decode("utf-8").split(self.terminating_character)
        return data
