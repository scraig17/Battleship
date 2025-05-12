#
# controller.py:
# This module defines the GameController class.
#

import logging
from threading import Event
from typing import Callable

from gamecomm.server import GameConnection, ConnectionClosedOK, ConnectionClosedError

from model import GameModel, GameError


logger = logging.getLogger(__name__)

# Constants used in JSON request and response objects

COMMAND_KEY = "command"
STATUS_KEY = "status"
OK_STATUS = "ok"
ERROR_STATUS = "error"
ERROR_KEY = ERROR_STATUS
MESSAGE_KEY = "message"

PLACE_SHIPS_COMMAND = "place_ships"
ATTACK_COMMAND = "attack"


class GameController:
    """
    A game controller, which manages request and response processing for a connected client for
    a player. An instance of this controller type has a reference to an instance of the game model
    that is shared with other controllers representing other players in the game. It receives
    requests from the client (via the connected WebSocket) and translates each request
    into an appropriate call on the game model object. Every requested command gets a response.
    Commands that were processed successfully get an OK response. Commands that result in an error
    get an ERROR response that describes what went wrong. Generally, OK responses tend not to
    include any other data, because typically the model will publish events as a result of a
    successful command, so that all clients can update accordingly.
    """

    RECV_TIMEOUT_SECONDS = 0.250

    def __init__(self, connection: GameConnection, model: GameModel,
                 on_close: Callable[[GameConnection], None]):
        """
        Initializes a GameController instance.
        :param connection: the GameConnection object that represents the WebSocket communication channel with the
                associated client
        :param model: the model for the game instance we are playing
        :param on_close: a callback we'll invoke if `connection` is closed
        """
        self.connection = connection
        self.model = model
        self.on_close = on_close
        self._shutdown = Event()

    def run(self):
        """
        Enters the request processing loop in which this controller waits for requests
        from the connected client, and acts upon them by invoking the appropriate methods
        on the GameModel. This method does not return unless/until another thread invokes
        the `stop` method to signal that a shutdown has been requested.
        :return: None
        """
        logger.info(f"connected to {self.connection} for user {self.connection.uid} in game {self.connection.gid}")
        try:
            # We stay in this loop until another thread invokes our `stop` method,
            # which signals the _shutdown event.
            while not self._shutdown.is_set():
                try:
                    # Receive a request from the client.
                    # The return value is a dict that represents the JSON request
                    # message received from the client. We specify a timeout here
                    # so that we don't block indefinitely in the call to `recv`.
                    # This allows us to periodically check for the shutdown signal
                    # (see the TimeoutError `except` clause below).
                    request = self.connection.recv(self.RECV_TIMEOUT_SECONDS)
                    logger.info(f"received request: {request}")
                    if COMMAND_KEY in request:
                        command = request[COMMAND_KEY].lower()
                        if command == PLACE_SHIPS_COMMAND:
                            ships = request.get("ships")
                            if not isinstance(ships, list):
                                raise GameError("Missing or invalid 'ships' list in request.")
                            self.model.place_ships(self.connection.uid, ships)
                            ok = True
                        elif command == ATTACK_COMMAND:
                            row = request.get("row")
                            col = request.get("col")
                            if row is None or col is None:
                                raise GameError("Missing 'row' or 'col' for attack.")
                            self.model.attack(self.connection.uid, row, col)
                            ok = True
                        else:
                            ok = False

                            
                        if ok:
                            # Send the OK response for the requested action
                            self.connection.send({STATUS_KEY: OK_STATUS})
                        else:
                            # Send an ERROR response indicating that we don't recognize the command
                            self.connection.send(
                                {STATUS_KEY: ERROR_STATUS, ERROR_KEY: {MESSAGE_KEY: f"invalid command '{command}'"}})
                    else:
                        # Send an ERROR response indicating that the request message didn't look like a command.
                        self.connection.send({STATUS_KEY: ERROR_STATUS, ERROR_KEY: {MESSAGE_KEY: "must specify command"}})
                except GameError as err:
                    # Send an ERROR response that describes the error that occurred
                    self.connection.send({STATUS_KEY: ERROR_STATUS,
                                          ERROR_KEY: {MESSAGE_KEY: f"{err.__class__.__name__}: {err}"}})
                except TimeoutError:
                    # Our call to the connection's `recv` method timed out waiting.
                    # This is normal (and just means that the client hasn't sent a request).
                    # We simply want to allow the timeout so that we can check for the shutdown
                    # signal at the top of the loop.
                    pass
        except ConnectionClosedOK:
            # We get this exception if the client closes its WebSocket connection gracefully
            # We are outside the while loop, so we'll fall through to the code below where
            # we invoke the `on_close` callback.
            pass
        except ConnectionClosedError as err:
            # We get this exception if the client was forcibly disconnected due to an I/O error.
            # We are outside the while loop, so we'll fall through to the code below.
            logger.error(f"error communicating with client: {err}")

        self.on_close(self.connection)
        logger.info(f"disconnected from {self.connection} for user {self.connection.uid} in game {self.connection.gid}")

    def stop(self):
        """
        Signals the shutdown event for this controller instance, which causes the
        request-handling loop in the `run` method to terminate.
        :return: None
        """
        logger.info("signalling stop")
        self._shutdown.set()
