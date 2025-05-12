import logging
from threading import Event
from typing import Callable
from gamecomm.server import GameConnection, ConnectionClosedOK, ConnectionClosedError
from model import GameModel, GameError

logger = logging.getLogger(__name__)

COMMAND_KEY = "command"
STATUS_KEY = "status"
OK_STATUS = "ok"
ERROR_STATUS = "error"
ERROR_KEY = ERROR_STATUS
MESSAGE_KEY = "message"

PLACE_SHIPS_COMMAND = "place_ships"
ATTACK_COMMAND = "attack"


class GameController:
    RECV_TIMEOUT_SECONDS = 0.250

    def __init__(self, connection: GameConnection, model: GameModel,
                 on_close: Callable[[GameConnection], None]):
        self.connection = connection
        self.model = model
        self.on_close = on_close
        self._shutdown = Event()

        # Add connection to model-wide connection list (for chat broadcasting)
        if not hasattr(self.model, "connections"):
            self.model.connections = []
        self.model.connections.append(self.connection)

    def run(self):
        logger.info(f"connected to {self.connection} for user {self.connection.uid} in game {self.connection.gid}")
        try:
            while not self._shutdown.is_set():
                try:
                    request = self.connection.recv(self.RECV_TIMEOUT_SECONDS)
                    logger.info(f"received request: {request}")
                    if COMMAND_KEY in request:
                        command = request[COMMAND_KEY].lower()
                        ok = False

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

                        elif command == "chat":
                            message = request.get("message", "").strip()
                            if not message:
                                raise GameError("Chat message cannot be empty.")
                            sender = self.connection.uid
                            chat_event = {
                                "event": "ChatEvent",
                                "message": f"{sender}: {message}"
                            }
                            for conn in getattr(self.model, "connections", []):
                                conn.publish(chat_event)
                            ok = True

                        if ok:
                            self.connection.send({STATUS_KEY: OK_STATUS})
                        else:
                            self.connection.send({
                                STATUS_KEY: ERROR_STATUS,
                                ERROR_KEY: {MESSAGE_KEY: f"invalid command '{command}'"}
                            })
                    else:
                        self.connection.send({
                            STATUS_KEY: ERROR_STATUS,
                            ERROR_KEY: {MESSAGE_KEY: "must specify command"}
                        })

                except GameError as err:
                    self.connection.send({
                        STATUS_KEY: ERROR_STATUS,
                        ERROR_KEY: {MESSAGE_KEY: f"{err.__class__.__name__}: {err}"}
                    })
                except TimeoutError:
                    pass

        except ConnectionClosedOK:
            pass
        except ConnectionClosedError as err:
            logger.error(f"error communicating with client: {err}")

        self.on_close(self.connection)
        logger.info(f"disconnected from {self.connection} for user {self.connection.uid} in game {self.connection.gid}")

    def stop(self):
        logger.info("signalling stop")
        self._shutdown.set()
