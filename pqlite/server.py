import socket
import threading

class DistributedDatabaseServer:
    """
    A server for a distributed database system that listens for incoming messages
    and handles client connections concurrently.

    Attributes:
        host (str): The hostname or IP address to listen on.
        port (int): The port number to listen on.
        server_socket (socket.socket): The socket object for the server.
    """

    def __init__(self, host, port):
        """
        Initializes the DistributedDatabaseServer with the specified host and port.

        :param host: The hostname or IP address to listen on.
        :param port: The port number to listen on.
        """
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"Server initialized and listening on {self.host}:{self.port}")

    def handle_client_connection(self, client_socket):
        """
        Handles the client connection. Receives messages from the client,
        processes them, and sends a response.

        :param client_socket: The socket object for the client connection.
        """
        while True:
            message = client_socket.recv(1024).decode('utf-8')
            if not message:
                break  # Client closed connection
            print(f"Received message: {message}")
            # Process message here (e.g., query handling, consensus protocol)

            # Example: sending a response back to the client
            response = "ACK"
            client_socket.send(response.encode('utf-8'))
        client_socket.close()

    def start(self):
        """
        Starts the server to accept connections and creates a new thread
        for each client connection for handling client messages concurrently.
        """
        print(f"Server starting and listening on {self.host}:{self.port}")
        try:
            while True:
                client_sock, address = self.server_socket.accept()
                print(f"Accepted connection from {address[0]}:{address[1]}")
                client_handler = threading.Thread(
                    target=self.handle_client_connection,
                    args=(client_sock,)
                )
                client_handler.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.server_socket.close()
