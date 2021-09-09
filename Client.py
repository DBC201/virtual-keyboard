import keyboard
import sys, argparse
import mouse
from Socket import Socket
import time
import threading
from queue import Queue


def smoothen_raw(final_x, final_y):
    """
    Moves the mouse to the desired coordinate in a smoother manner
    :param final_x: x to move
    :param final_y: y to move
    """
    curr_x, curr_y = mouse.get_position()
    dx = final_x - curr_x
    dy = final_y - curr_y
    smoothen(dx, dy)


def smoothen(dx, dy):
    """
    Moves the mouse by increments, aiming for a smoother movement
    :param dx: change in x
    :param dy: change in y
    """
    while dx != 0 or dy != 0:
        if dx < 0:
            mouse.move(-1, 0, absolute=False)
            dx += 1
        elif dx > 0:
            mouse.move(1, 0, absolute=False)
            dx -= 1

        if dy < 0:
            mouse.move(0, -1, absolute=False)
            dy += 1
        elif dy > 0:
            mouse.move(0, 1, absolute=False)
            dy -= 1


class Client(Socket):
    def __init__(self, ip, port, verbose=True, loop=False):
        super().__init__(ip, port)
        self.loop = loop
        self.verbose = verbose
        self.__keyboard_inputs = Queue()
        self.threads = Queue()

    def kill_threads(self):
        while not self.threads.empty():
            self.threads.get()
            self.threads.task_done()

    def run(self):
        if self.loop:
            while True:
                if self.connect():
                    self.start()
        else:
            if self.connect():
                self.start()
        self.kill_threads()

    def connect(self):
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

    def __keyboard_thread(self):
        while True:
            if not self.__keyboard_inputs.empty():
                key = self.__keyboard_inputs.get()
                keyboard.press_and_release(key)
            time.sleep(0.07)

    def start(self):
        keyboard_thread = threading.Thread(target=self.__keyboard_thread, daemon=True)
        self.threads.put(keyboard_thread)
        keyboard_thread.start()
        try:
            while True:
                data = self.receive(self.sock)
                for d in data:
                    if d == "status":
                        self.send(self.sock, b"client")
                    if d == "live":
                        continue
                    elif d == "exit":
                        return
                    else:
                        try:
                            if self.verbose:
                                print(d)
                            if d[:len("key")] == "key":
                                self.__keyboard_inputs.put(d[len("key"):])
                                # pass
                            elif d[:len("move")] == "move":
                                x, y = list(map(int, d[len("move"):].split(',')))
                                # mouse.move(x, y)
                                # dx, dy = list(map(int, d[len("move"):].split(',')))
                                # mouse.move(dx, dy, absolute=False)
                                smoothen_raw(x, y)
                            elif d[:len("click")] == "click":
                                mouse.click(d[len("click"):])
                                pass
                            elif d[:len("scroll")] == "scroll":
                                delta = int(d[len("move"):])
                                mouse.wheel(delta)
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
