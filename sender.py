import keyboard
import socket
import sys, argparse
import time

BUFSZ = 64


class Sender:
    def __init__(self, ip, port):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.data = None

    def run(self):
        """
        Initiate Sender
        tries to initiate connection first and then calls the implicit start method
        """
        if self.__connect():
            self.__start()

    @staticmethod
    def send(conn, data):
        if sys.getsizeof(data) > BUFSZ:
            raise RuntimeError("Data is too big to send!")
        else:
            conn.send(data)

    @staticmethod
    def __handle_connection_reset():
        print("Server has shutdown.")
        exit()

    def __connect(self):
        try:
            print("Attempting to connect ", (self.ip + ':' + str(self.port)))
            self.sock.connect((self.ip, self.port))
        except ConnectionRefusedError:
            print("Couldn't connect to server")
            return False
        except Exception as e:
            print(e)
            return False
        else:
            print("Connection succesfull!")
            return True

    def listen_data(self):
        """
        Processes incoming data
        """
        while True:
            try:
                data = self.sock.recv(BUFSZ).decode()
                if data == "status":
                    Sender.send(self.sock, b"sender")
                elif data == "live":
                    continue
                else:
                    return data
            except ConnectionResetError:
                Sender.__handle_connection_reset()
            except Exception as e:
                raise e

    def __start(self):
        """
        Where the main input is read, selections are made
        could be regarded as the menu
        """
        try:
            data = self.sock.recv(BUFSZ).decode("utf-8")
            if data != "status":
                raise RuntimeError("No status requested")
            else:
                Sender.send(self.sock, b"sender")
            while True:
                inp = input("->").encode()
                if inp == b"exit":
                    Sender.send(self.sock, b"exit")
                    return
                Sender.send(self.sock, inp)
                data = self.listen_data()
                if data == "connected":
                    self.read_keyboard()
                else:
                    print(data)
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

            if sys.getsizeof(data) > BUFSZ:
                print("data to be sent is bigger than the bufsize")
            else:
                self.sock.send(data)

        keyboard.on_press(send_keystrokes)
        print("Start typing:")
        while not exitflag:
            time.sleep(0.31)  # 31 cektim
        keyboard.unhook_all()


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Sender for remote access")
    parser.add_argument("ip", type=str, help="IP of the server")
    parser.add_argument("port", type=int, help="Port the client is going to send the values to")
    args = parser.parse_args(sys.argv[1:])
    Sender(args.ip, args.port).run()
