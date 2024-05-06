import socket
import os


class Socket:
    def __init__(self, ip, port, bufsz=8192):
        self.ip = ip
        self.port = port
        self.sock = socket.socket()
        self.bufsz = bufsz

    def run(self):
        pass

    @staticmethod
    def source(conn, yield_data):
        while True:
            request = next(yield_data, None)
            if request is None:
                break
            conn.sendall(request)

    def sink(self, conn, handle_data):
        while True:
            response = conn.recv(len(b'000000000000'))
            try:
                size = int(response.decode("utf-8"))
            except ValueError:
                continue
            except UnicodeDecodeError:
                continue

            i = 0
            while i < size:
                response = conn.recv(min(size - i, self.bufsz))
                handle_data(response)
                i += len(response)
            break

    def receive_data(self, conn):
        data = b''

        def handle_data(response):
            nonlocal data
            data += response

        self.sink(conn, handle_data)
        return data

    def yield_file(self, filepath):
        file_size = os.path.getsize(filepath)
        flag = ("SENDING_FILE:" + os.path.basename(filepath)).encode()
        if file_size > 999999999999 - len(flag):
            raise RuntimeError(f"Maximum file size is 999999999999 bytes, {filepath} is {file_size} bytes")
        file_size = str(file_size+len(flag)).zfill(12)
        yield file_size.encode("utf-8")

        yield flag
        with open(filepath, 'rb') as filepath:
            while True:
                data = filepath.read(self.bufsz)
                if len(data) == 0:
                    break
                yield data

    @staticmethod
    def yield_data(value):
        size = len(value)
        size = str(size).zfill(12)
        yield size.encode()
        yield value
