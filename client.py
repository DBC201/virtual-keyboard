import keyboard
import socket
import sys, argparse

BUFSZ = 64

keyboard._winkeyboard._setup_name_tables()
ALL_KEYS = set(keyboard._winkeyboard.from_name.keys())


class Client:
    def __init__(self, ip, port, verbose=True, loop=False):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.loop = loop
        self.verbose = verbose

    @staticmethod
    def __send(conn, data):
        if sys.getsizeof(data) > BUFSZ:
            raise RuntimeError("Data is too big to send!")
        else:
            conn.send(data)

    def run(self):
        if self.loop:
            while True:
                if self.__connect():
                    self.__start()
                    self.sock = socket.socket()
        else:
            if self.__connect():
                self.__start()

    def __connect(self):
        try:
            if self.verbose:
                print("Attempting to connect ", (self.ip + ':' + str(self.port)))
            self.sock.connect((self.ip, self.port))
        except ConnectionRefusedError:
            if self.verbose:
                print("Couldn't connect to server")
            return False
        except Exception as e:
            if self.verbose:
                print(e)
            return False
        else:
            if self.verbose:
                print("Connection succesfull!")
            return True

    def __start(self):
        try:
            while True:
                data = self.sock.recv(BUFSZ).decode("utf-8")
                if data == "status":
                    Client.__send(self.sock, b"client")
                if data == "live":
                    continue
                elif data == "exit":
                    return
                else:
                    try:
                        if self.verbose:
                            print(data)

                        if len(data) > 1 and data in ALL_KEYS:
                            keyboard.press_and_release(data)
                        else:
                            keyboard.write(data)
                    except:
                        pass
        except ConnectionResetError:
            if self.verbose:
                print("\nServer shut down.")
            return
        except Exception as e:
            if self.verbose:
                raise e
            else:
                return


def return_parser():
    parser = argparse.ArgumentParser(description="Client for remote access")
    parser.add_argument("ip", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="Port the client is going to send the values to")
    parser.add_argument("-v", "--verbose", action="store_true", dest="verbose")
    parser.add_argument("-l", "--loop", action="store_true", dest="loop",
                        help="Program will attempt to connect indefinitely unless halted")
    return parser


if __name__ == '__main__':
    parser = return_parser()
    args = parser.parse_args(sys.argv[1:])
    verbose = False
    loop = False
    if args.verbose:
        verbose = True
    if args.loop:
        loop = True
    Client(args.ip, args.port, verbose, loop).run()
