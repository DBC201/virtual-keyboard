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
            connection = self.sock.accept()
            self.lock.acquire()
            print()
            print("Received connection from: " + str(connection[1][0]) + ":" + str(connection[1][1]))
            try:
                self.source(connection[0], self.yield_data("status".encode()))
                status = self.receive_data(connection[0]).decode()
                print(status)
                if status == "client":
                    self.clients.append(connection)
                elif status == "sender":
                    if self.sender:
                        connection[0].close()
                    else:
                        self.sender = connection
                else:
                    connection[0].close()
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
                self.source(accept[0], self.yield_data("live".encode()))
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
            self.source(self.sender[0], self.yield_data("live".encode()))
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
                    data = self.receive_data(self.sender[0])
                    print(data)
                    if data == b"exit":
                        self.sender = None
                    elif data == b"list":
                        res = self.update_clients()
                        self.source(self.sender[0], self.yield_data(res.encode()))
                    else:
                        try:
                            client = self.clients[int(data)][0]
                            self.link(self.sender[0], client)
                        except:
                            self.source(self.sender[0], self.yield_data("error".encode()))
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
            self.source(sender_conn, self.yield_data("connected".encode()))
            while True:
                sender_data = self.receive_data(sender_conn)
                if sender_data == b"key~":
                    return
                else:
                    self.source(client_conn, self.yield_data(sender_data))
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
