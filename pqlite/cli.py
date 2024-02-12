"""
The cli interface to start a server.
"""
import click
from pqlite.server import DistributedDatabaseServer as DDS

@click.command()
@click.option('--host', default='localhost', help='The host of the server.')
@click.option('--port', default=8471, type=int, help='The port of server to listen.')
def main(host, port):  # pragma: no cover
    server = DDS(host=host, port=port)
    server.start()
