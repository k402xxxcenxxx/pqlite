from __future__ import annotations

import socket


class DistributedDatabaseClient:
    """
    A client for sending messages to a server in a distributed database system.

    This class encapsulates the functionality for connecting to a server,
    sending a message, and receiving a response.
    """

    def __init__(self, host, port):
        """
        Initializes the DistributedDatabaseClient with the specified server
        host and port.

        :param host: The hostname or IP address of the server to connect to.
        :param port: The port number of the server to connect to.
        """
        self.host = host
        self.port = port

    def send_message(self, message):
        """
        Sends a message to the server and prints the server's response.

        :param message: The message to send to the server.
        :return: The response received from the server.
        """
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.connect((self.host, self.port))
            sock.sendall(message.encode("utf-8"))
            response = sock.recv(1024).decode("utf-8")
            print(f"Received response: {response}")
            return response
