from __future__ import annotations

import socket
import threading

from pqlite.database import Database
from pqlite.node import Node


class DistributedDatabaseServer:
    """
    A server for a distributed database system that listens for incoming
    messages and handles client connections concurrently.

    Attributes:
        host (str): The hostname or IP address to listen on.
        port (int): The port number to listen on.
        db_file (str): The database file path to store.
        server_socket (socket.socket): The socket object for the server.
        thread_local_db (_thread._local): The thread object to control
            database.
        node_list (list): The list of Node object that stores node info.
    """

    OPERATION_JOIN_NODE = "join_node:"
    OPERATION_DB_OPS = "db_ops:"
    OPERATION_SYNC = "sync:"

    def __init__(self, host, port, db_file):
        """
        Initializes the DistributedDatabaseServer with the specified host and
        port.

        :param host: The hostname or IP address to listen on.
        :param port: The port number to listen on.
        :param db_file: The database file path to store.
        """
        self.db_file = db_file

        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((host, port))
        self.server_socket.listen()

        self.host, self.port = self.server_socket.getsockname()

        self.thread_local_db = threading.local()

        self.node_list = []
        print(f"Server initialized and listening on {self.host}:{self.port}")

    def __str__(self) -> str:
        return f"Server {self.host}:{self.port}"

    def get_db_connection(self):
        """
        Returns a database connection for the current thread,
        creating a new one if necessary.
        """
        if not hasattr(self.thread_local_db, "connection"):
            self.thread_local_db.connection = Database(self.db_file)
        return self.thread_local_db.connection

    def is_context_valid(self, context):
        """
        Verify if a context is valid or not.
        Returns true if the context is valid, vice versa

        :param context: The context to verify with.
        """
        return (
            context.startswith(self.OPERATION_DB_OPS)
            or context.startswith(self.OPERATION_JOIN_NODE)
            or context.startswith(self.OPERATION_SYNC)
        )

    def handle_client_connection(self, client_socket):
        """
        Handles the client connection. Receives messages from the client,
        processes them, and sends a response.

        :param client_socket: The socket object for the client connection.
        """
        while True:
            context = client_socket.recv(1024).decode("utf-8")
            if not context or not self.is_context_valid(context):
                break  # Client closed connection
            print(f"Received message: {context}")

            if context.startswith(self.OPERATION_SYNC):
                context = context.split(self.OPERATION_SYNC, 1)[1]
                self.sync_context(context)

            if context.startswith(self.OPERATION_JOIN_NODE):
                self.join_node(
                    client_socket,
                    context.split(self.OPERATION_JOIN_NODE, 1)[1],
                )
            elif context.startswith(self.OPERATION_DB_OPS):
                self.db_ops(
                    client_socket, context.split(self.OPERATION_DB_OPS, 1)[1]
                )

    def add_node(self, host, port):
        """
        Add node to the list.

        :param host: The hostname to connect to that node.
        :param port: The port number to connect to that node.
        """
        print(f"Add node: {host} {port}")
        node = Node(host=host, port=port)
        node.client.send_message(
            f"{self.OPERATION_JOIN_NODE}{self.host} {self.port}"
        )
        self.node_list.append(node)

    def join_node(self, client_socket, context):
        """
        Accept join node request and add requester to the list.

        :param client_socket: The socket object for responding with to client.
        :param context: The context to do join_node
        """
        host, port = context.split()
        print(f"{self} Join node: {host} {port}")
        self.node_list.append(Node(host=host, port=int(port)))
        response = "Success"

        client_socket.sendall(response.encode("utf-8"))

    def db_ops(self, client_socket, context):
        """
        Execute db operation request based on context.

        :param client_socket: The socket object for responding with to client.
        :param context: The context to do db_ops
        """
        try:
            print(f"{self} DB OPS: {context}")

            db = self.get_db_connection()
            result = db.execute(context)
            response = f"Success: {result}"
        except Exception as e:
            response = f"Error: {str(e)}"
        finally:
            db.close()

        client_socket.sendall(response.encode("utf-8"))

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
                    target=self.handle_client_connection, args=(client_sock,)
                )
                client_handler.start()
        except KeyboardInterrupt:
            print("Server shutting down.")
        finally:
            self.close()

    def close(self):
        """
        Stop the server and close the database connection
        """
        self.server_socket.close()

    def sync_context(self, context):
        """
        Sync context with other nodes

        :param context: The context needs to sync with other nodes.
        """
        for node in self.node_list:
            node.client.send_message(context)
