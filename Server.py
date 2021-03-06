import sys, argparse
import threading
from queue import Queue
import time
from Socket import Socket


class Server(Socket):
    def __init__(self, port):
        super().__init__("", port)
        self.sock.bind(('', self.port))
        self.sock.listen(5)  # will end connection after 5 bad attempts
        self.clients = []
        self.sender = None
        self.threads = Queue()
        self.lock = threading.Lock()
        print("Listening to port:", self.port)

    def run(self):
        listening_thread = threading.Thread(target=server.listen, daemon=True)
        start_thread = threading.Thread(target=server.start, daemon=True)

        self.threads.put(listening_thread)
        self.threads.put(start_thread)

        listening_thread.start()
        start_thread.start()

        self.threads.join()

    def kill_threads(self):  # kills the jobs in order to quit
        while not self.threads.empty():
            self.threads.get()
            self.threads.task_done()

    def listen(self):
        """
        listens for incoming connections in a separate thread
        """
        while True:
            accept = self.sock.accept()
            self.lock.acquire()
            print()
            print("Received connection from: " + str(accept[1][0]) + ":" + str(accept[1][1]))
            try:
                self.send(accept[0], b"status")
                status = self.receive(accept[0])[0]
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
            self.lock.release()

    def update_connected(self):
        """
        Checks if existing connections are still alive
        """
        self.lock.acquire()
        connected_string = "Current connections\n"
        for i, accept in enumerate(self.clients):
            try:
                accept[0].send(b'live')
            except Exception as e:
                # print(e)
                del self.clients[i]
            connected_string += str(i) + ": " + str(accept[1][0]) + ":" + str(accept[1][1]) + '\n'
        self.lock.release()
        return connected_string

    def update_clients(self):
        """
        see update_connected()
        """
        return self.update_connected()

    def update_senders(self):
        """
        Updates the sender (there is only one sender as of now)
        """
        self.lock.acquire()
        try:
            self.send(self.sender[0], b"live")
        except Exception as e:
            self.sender = None
        self.lock.release()

    def start(self):
        """
        Reads input from sender
        Since there is only one sender, no threading is needed
        """
        while True:
            while self.sender is not None:
                try:
                    print("listening")
                    data = self.receive(self.sender[0])
                    for inp in data:
                        print("sender:", inp)
                        if inp == "exit":
                            self.sender = None
                        elif inp == "list":
                            # self.send(self.sender[0], self.update_clients().encode())
                            self.update_clients()
                            self.send(self.sender[0], str(len(self.clients)).encode())  # to decrease bufsz to 64
                        else:
                            try:
                                client = self.clients[int(inp)][0]
                                self.link(self.sender[0], client)
                            except:
                                self.send(self.sender[0], b"error")
                except Exception as e:
                    print("start:", e)
                    break
            self.update_senders()
            self.update_clients()
            time.sleep(0.5)

    def link(self, sender_conn, client_conn):
        """
        Link sender with client to transfer data
        """
        try:
            self.send(sender_conn, b"connected")
            while True:
                sender_data = self.receive(sender_conn)
                for data in sender_data:
                    print(data)
                    if data == "key~":
                        return
                    else:
                        self.send(client_conn, data.encode())
        except Exception as e:
            print("link:", e)
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
    server.run()
