import socket
import threading


class Network:

    def __init__(self, host="127.0.0.1", port=5000):

        self.host = host
        self.port = port

        self.client = socket.socket(
            socket.AF_INET,
            socket.SOCK_STREAM
        )

        self.connected = False

    def connect(self):

        try:
            self.client.connect(
                (self.host, self.port)
            )

            self.connected = True

            return True

        except Exception as e:

            print("Connection error:", e)

            return False

    def send(self, message):

        try:

            self.client.sendall(
                message.encode()
            )

            return True

        except:

            return False

    def receive(self):

        try:

            return self.client.recv(1024).decode()

        except:

            return None

    def close(self):

        try:
            self.client.close()

        except:
            pass

        self.connected = False