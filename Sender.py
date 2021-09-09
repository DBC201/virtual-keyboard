import keyboard
import mouse
import socket
import sys, argparse
from Client import Client


def truncate(num):
    num *= 10000
    num = int(num)
    num /= 10000
    return num


class Sender(Client):
    def __init__(self, ip, port):
        super().__init__(ip, port)
        self.ip = ip
        self.port = port
        self.sock = socket.socket()

    @staticmethod
    def __handle_connection_reset():
        """
        This function runs on connection reset exception
        :return:
        """
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
                        self.listen_keyboard_and_mouse()
                    else:
                        print(d)
        except ConnectionResetError:
            Sender.__handle_connection_reset()
        except Exception as e:
            raise e

    def process_keystrokes(self, keyevent):
        """
        the function for keyboard.hook(), sends the key presses to the server
        """
        data = b"key" + keyevent.name.encode()
        self.send(self.sock, data)
        if keyevent.name == '~':
            keyboard.unhook_all()
            mouse.unhook_all()

    def create_mouse_hook(self):
        """
        creates the mouse hook, helper function for listen_keyboard_and_mouse()
        """
        x, y = mouse.get_position()

        def process_mouse_events(event):
            nonlocal x, y
            if type(event) == mouse.MoveEvent:
                """dx = event.x - x
                dy = event.y - y
                x = event.x
                y = event.y
                data = "move" + str(dx) + ',' + str(dy)"""
                x, y = mouse.get_position()
                data = "move" + str(x) + ',' + str(y)
                self.send(self.sock, data.encode())
            elif type(event) == mouse.ButtonEvent:
                if event.event_type == "down":
                    data = "click"
                    if event.button == "x2":
                        data += "left"
                    elif event.button == "x":
                        data += "right"
                    else:
                        return
                    self.send(self.sock, data.encode())
            # mouse.move(0, 0)
        mouse.hook(process_mouse_events)

    def listen_keyboard_and_mouse(self):
        """
        handles and initiates both keyboard and mouse hooks
        """
        keyboard.on_press(self.process_keystrokes)
        self.create_mouse_hook()
        print("Keyboard and mouse connected, press ~ and enter to disconnect")
        while input()[-1] != '~':
            pass


def return_parser():
    parser = argparse.ArgumentParser(description="Sender for remote access")
    parser.add_argument("ip", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="Port the client is going to send the values to")
    return parser


if __name__ == '__main__':
    parser = return_parser()
    args = parser.parse_args(sys.argv[1:])
    Sender(args.ip, args.port).run()
