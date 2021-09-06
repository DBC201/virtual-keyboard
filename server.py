import socket
import sys, argparse
import threading
from queue import Queue
import time

THREADS = Queue()
BUFSZ = 64


def kill_threads():  # kills the jobs in order to quit
    while not THREADS.empty():
        THREADS.get()
        THREADS.task_done()


class Server:
    def __init__(self, port):
        try:
            self.port = port
            self.sock = socket.socket()
            self.sock.bind(('', self.port))
            self.sock.listen(5)  # will end connection after 5 bad attempts
            self.clients = []
            self.sender = None
            print("Listening to port:", self.port)
        except Exception as e:
            raise e

    @staticmethod
    def send(conn, data):
        if sys.getsizeof(data) > BUFSZ:
            raise RuntimeError("Data is too big to send!")
        else:
            conn.send(data)

    def listen(self):
        """
        listens for incoming connections in a seperate thread
        """
        while True:
            accept = self.sock.accept()
            print()
            print("Received connection from: " + str(accept[1][0]) + ":" + str(accept[1][1]))
            try:
                Server.send(accept[0], b"status")
                status = accept[0].recv(BUFSZ).decode("utf-8")
                print(status)
                if status == "client":
                    self.clients.append(accept)
                elif status == "sender":
                    if self.sender:
                        accept[0].close()
                    else:
                        self.sender = accept
                else:
                    accept[0].close()
            except Exception as e:
                print("listen thread:", e)

    @staticmethod
    def update_connected(connected):
        """
        Checks if existing connections are still alive
        """
        connected_string = "Current connections\n"
        for i, accept in enumerate(connected):
            try:
                accept[0].send(b'live')
            except Exception as e:
                # print(e)
                del connected[i]
            connected_string += str(i) + ": " + str(accept[1][0]) + ":" + str(accept[1][1]) + '\n'
        return connected_string

    def update_clients(self):
        """
        see update_connected()
        """
        return Server.update_connected(self.clients)

    def update_senders(self):
        """
        Updates the sender (there is only one sender as of now)
        """
        try:
            Server.send(self.sender[0], b"live")
        except Exception as e:
            self.sender = None

    def start(self):
        """
        Reads input from sender
        Since there is only one sender, no threading is needed
        """
        while True:
            while self.sender:
                try:
                    print("listening")
                    inp = self.sender[0].recv(BUFSZ).decode()
                    print("sender:", inp)
                    if inp == "exit":
                        break # the senders get updated outside the loop anyways
                    if inp == "list":
                        # Server.__send(self.sender[0], self.update_clients().encode())
                        self.update_clients()
                        Server.send(self.sender[0], str(len(self.clients)).encode()) # to decrease bufsz to 64
                    else:
                        try:
                            client = self.clients[int(inp)][0]
                            self.link(self.sender[0], client)
                        except ValueError:
                            self.send(self.sender[0], b"error")
                except Exception as e:
                    break
            self.update_senders()
            self.update_clients()
            time.sleep(0.5)

    def link(self, sender_conn, client_conn):
        """
        Link sender with client to transfer data
        """
        try:
            sender_conn.send(b"connected")
            while True:
                sender_data = sender_conn.recv(BUFSZ)
                print(sender_data)
                if sender_data == b"~":
                    return
                else:
                    Server.send(client_conn, sender_data)
        except Exception as e:
            print("link", e)
            self.update_clients()
            self.update_senders()


def return_parser():
    parser = argparse.ArgumentParser(description="Remote Control server made by dbc201")
    parser.add_argument("-p", "--port", type=int, dest="port", help="Port the server will connect to")
    return parser


if __name__ == '__main__':
    parser = return_parser()
    args = parser.parse_args(sys.argv[1:])
    port = 41369
    if args.port:
        port = args.port
    server = Server(port)

    listening_thread = threading.Thread(target=server.listen, daemon=True)
    start_thread = threading.Thread(target=server.start, daemon=True)

    THREADS.put(listening_thread)
    THREADS.put(start_thread)

    listening_thread.start()
    start_thread.start()

    THREADS.join()
