#
# listener.py:
# This module defines the GameListener class.
#

import logging
from threading import Lock

from gameauth import TokenValidator, InvalidTokenError
from gamecomm.server import WsGameListener, GameConnection

from .server import GameServer


logger = logging.getLogger(__name__)


class GameListener:
    """
    A listener for game client connections.
    When a player's client connects, it presents a unique identifier for the
    game instance the player wishes to join. Game instance could mean "room",
    "round", "field", etc. If authentication is enabled, the player's client is
    expected to also present an authentication token which will prove the
    identity of the player and his/her authorization to join the specified game.
    """

    def __init__(self, local_ip, local_port, token_validator: TokenValidator):
        self.local_ip = local_ip
        self.local_port = local_port
        self.token_validator = token_validator
        # The following dictionary is used to associate game instance identifiers
        # with a corresponding instance of the GameServer class.
        self._servers: dict[str, GameServer] = {}
        self._lock = Lock()

    def _find_or_create_server(self, gid: str, players: list[str]):
        with self._lock:
            if gid not in self._servers:
                self._servers[gid] = GameServer(gid, players)
                logger.info(f"created new server for gid {gid} with players {players}")
            return self._servers[gid]

    def handle_authentication(self, gid: str, token: str):
        try:
            return self.token_validator.validate(gid, token)
        except InvalidTokenError:
            return None

    def handle_connection(self, connection: GameConnection):
        """
        This method is invoked as a callback by WsGameListener, when a client
        representing a player opens a WebSocket connection. WsGameListener creates
        a thread for the purpose of serving the connected client, and invokes this
        method on that thread. This allows us to communicate with the client without
        concern for blocking, since every client has its own service thread.
        :param connection: the connection object that represents the connecting client's WebSocket
        :return: None
        """

        # Use the client's specified game ID to get the corresponding GameServer
        # instance. The specified game instance is created if necessary.
        server = self._find_or_create_server(connection.gid, connection.players)

        # Transfer responsibility for handling this client to the corresponding
        # GameServer instance. Our calling thread doesn't return from this call
        # unless/until the client disconnects or the server is shut down.
        server.handle_connection(connection)

    def handle_stop(self):
        """
        This method is invoked as a callback when the WsGameListener instance is
        ready to shut down.
        :return: None
        """
        with self._lock:
            # Signal to all server instances that we want to shut down
            for server in self._servers.values():
                server.stop()

    def run(self):
        """
        This method is invoked from the game server program's main entry point.
        It is intended to run on the program's main thread. After logging some useful
        details, it creates a WsGameListener instance (from the VT ECE 4564 Game Library)
        and runs it. After the WsGameListener is running, we'll get callbacks on the
        handle_connection, handle_authentication, and handle_stop methods as needed.
        :return:
        """
        logger.info(f"listening on {self.local_ip}:{self.local_port}")
        logger.info(f"authentication is {'enabled' if self.token_validator else 'disabled'}")
        listener = WsGameListener(self.local_ip, self.local_port,
                                  on_connection=self.handle_connection,
                                  on_authenticate=self.handle_authentication if self.token_validator else None,
                                  on_stop=self.handle_stop)
        listener.run()
