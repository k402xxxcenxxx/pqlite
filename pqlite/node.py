from __future__ import annotations

class Node:
    """
    A node description.

    Attributes:
        host (str): The hostname of the node.
        port (int): The port number of the node.
    """
    def __init__(self, host, port):
        """
        Initializes the Node with the specified host and port.

        :param host: The hostname.
        :param port: The port number.
        """
        self.host = host
        self.port = port
