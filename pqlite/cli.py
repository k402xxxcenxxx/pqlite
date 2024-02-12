"""
The cli interface to start a server.
"""

from __future__ import annotations

import click

from pqlite.client import DistributedDatabaseClient as DDC
from pqlite.server import DistributedDatabaseServer as DDS


@click.group()
def main():
    pass


@main.command()
@click.option("--host", default="localhost", help="The host of the server.")
@click.option(
    "--port", default=8471, type=int, help="The port of server to listen."
)
@click.option("--db-file", default="pqlite.db", help="path/to/db_file")
def server(host, port, db_file):  # pragma: no cover
    server = DDS(host=host, port=port, db_file=db_file)
    server.start()


@main.command()
@click.option("--host", default="localhost", help="The host of the server.")
@click.option(
    "--port", default=8471, type=int, help="The port of server to send."
)
def client(host, port):  # pragma: no cover
    client = DDC(host=host, port=port)
    while True:
        try:
            client.send_message(input("pqlite >"))
        except KeyboardInterrupt:
            print("Exit")
            break
