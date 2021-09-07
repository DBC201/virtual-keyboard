import socket
import sys


class Socket:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.bufsz = 64
        self.terminating_character = '|'
        self.starting_character = '#'

    def run(self):
        pass

    def send(self, conn, data):
        if sys.getsizeof(data) > self.bufsz:
            raise RuntimeError("Data is too big to send!")
        else:
            data = self.starting_character.encode() + data + self.terminating_character.encode()
            conn.send(data)

    def receive(self, conn):
        raw_data = conn.recv(self.bufsz).decode("utf-8")
        data = []
        current = ""
        starting_flag = False
        for character in raw_data:
            if character == '|':
                data.append(current)
                current = ""
            elif character == '#':
                starting_flag = True
                current = ""
                continue

            if starting_flag:
                current += character
        return data
