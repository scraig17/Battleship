#
# server.py:
# This module defines the GameServer class.
#

import logging
from threading import Lock

from gamecomm.server import GameConnection

from model import GameModel

from .controller import GameController
from .publisher import GamePublisher

logger = logging.getLogger(__name__)


class GameServer:
    """
    A server for an instance of our game. An instance of this GameServer
    class is created for every unique game identifier presented by a connecting
    client. The connection objects for all clients that present the same unique
    game identifier are passed to the same instance of GameServer (via the
    `handle_connection` method defined below.

    All clients connected to an instance of this GameServer class share a common
    GameModel instance and a GamePublisher instance. Commands from clients connected
    to a GameServer instance are processed by a per-client GameController instance,
    which translates each client command to a corresponding GameModel action.

    The GamePublisher created for an instance of this GameServer class acts as the
    observer for the GameModel instance, receiving callbacks from the model as game
    events are generated, and distributing those events to connected clients as
    appropriate.
    """

    def __init__(self, gid: str, players: list[str]):
        """
        Initializes an instance of GameServer.
        :param gid: the unique game identifier assigned to this GameServer instance
        :param players: list of usernames for players authorized to play in this game instance
        """
        self.gid = gid
        self.players = players
        self._lock = Lock()
        # Create the publisher that will deliver events to all clients connected to
        # this game server instance.
        self.publisher = GamePublisher()
        # Create the model instance for the game to be played by clients connected to
        # this GameServer instance. The publisher will observe event notifications from
        # the game model and deliver them to clients as appropriate.
        self.model = GameModel(observer=self.publisher)
        # Create a dictionary to map GameConnection objects to the corresponding
        # GameController instances.
        self._controllers: dict[GameConnection, GameController] = {}

    def handle_close(self, connection: GameConnection):
        """
        This method is invoked as a callback by GameController when a client
        disconnects gracefully or is forcibly disconnected (e.g. due to an I/O error)
        :param connection: the client connection that was closed
        :return: None
        """
        with self._lock:
            # Remove the mapping from connection to controller
            self._controllers.pop(connection)
            # Remove the connection (as a subscriber) from the publisher
            self.publisher.remove_subscriber(connection)

    def handle_connection(self, connection):
        """
        This method is invoked in GameListener's `handle_connection` method after the
        appropriate instance of GameServer is found or created. This implementation of
        this method assumes that the calling thread does not need to return until the
        client is disconnected.
        :param connection: a new client connection for this GameServer
        :return: None
        """
        # Create a controller for the new client, passing along the connection and model,
        # and registering our callback to handle client disconnects.
        controller = GameController(connection, self.model, on_close=self.handle_close)
        # Put the new controller into our mapping of connection to controller and
        # add the connection to our publisher as a subscriber.
        with self._lock:
            self._controllers[connection] = controller
            self.publisher.add_subscriber(connection)

        # Run the client request handling loop. Our calling thread doesn't return from
        # this call unless/until the client disconnects or the server is shut down.
        controller.run()

    def stop(self):
        """
        Signals the shutdown event for this server instance, which in turn signals a
        shutdown event to every connected controller.
        :return: None
        """
        with self._lock:
            for controller in self._controllers.values():
                controller.stop()
