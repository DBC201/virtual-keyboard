import keyboard
import socket
import sys, argparse
import time
from Client import Client


class Sender(Client):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.ip = ip
        self.port = port
        self.sock = socket.socket()

    @staticmethod
    def __handle_connection_reset():
        print("Server has shutdown.")
        exit()

    def start(self):
        """
        Where the main input is read, selections are made
        could be regarded as the menu
        """
        try:
            data = self.receive(self.sock)[0]
            if data != "status":
                raise RuntimeError("No status requested")
            else:
                self.send(self.sock, b"sender")
            while True:
                inp = input("->").encode()
                if inp == b"exit":
                    self.send(self.sock, b"exit")
                    return
                self.send(self.sock, inp)
                data = self.receive(self.sock)
                print(data)
                for d in data:
                    if d == "status":
                        self.send(self.sock, b"sender")
                    elif d == "live":
                        continue
                    elif d == "connected":
                        self.read_keyboard()
                    else:
                        print(d)
        except ConnectionResetError:
            Sender.__handle_connection_reset()
        except Exception as e:
            raise e

    def read_keyboard(self):
        """
        Starts reading the keyboard to send data to server
        ~ to stop reading
        """
        exitflag = False

        def send_keystrokes(keyevent):
            nonlocal exitflag
            data = keyevent.name
            data = data.encode()
            exitflag = keyevent.name == '~'
            self.send(self.sock, data)

        keyboard.on_press(send_keystrokes)
        print("Start typing:")
        while not exitflag:
            time.sleep(0.31)  # 31 cektim
        keyboard.unhook_all()


def return_parser():
    parser = argparse.ArgumentParser(description="Sender for remote access")
    parser.add_argument("ip", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="Port the client is going to send the values to")
    return parser


if __name__ == '__main__':
    parser = return_parser()
    args = parser.parse_args(sys.argv[1:])
    Sender(args.ip, args.port).run()
