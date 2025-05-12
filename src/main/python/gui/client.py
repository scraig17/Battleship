#
# client.py:
# This module defines the GameClient class.
#

import gamecomm.client

from .protocol import EVENT_KEY, STATUS_KEY, OK_STATUS


class GameClient(gamecomm.client.GameClient):
    """
    Minimal GameClient implementation that simply implements the methods
    necessary to distinguish events from command responses received via
    the client's WebSocket connection.
    """

    def __init__(self, url, token=None, on_event=None):
        super().__init__(url, token, on_event)

    def is_event(self, message: dict):
        """
        This method is invoked by the code in the parent class to distinguish
        WebSocket messages that contain a game event from those that contain
        the response for a pending request.
        :param message: a JSON message received from the client's WebSocket connection
        :return: True if and only if message contains an event object
        """

        # A JSON message that contains the key specified by EVENT_KEY is considered to
        # be an event.
        return EVENT_KEY in message

    def is_success(self, response: dict):
        """
        This method is invoked by the code in the parent class upon receipt
        of a WebSocket message containing a response to pending request.
        :param response: a JSON message contain a response to a pending request
        :return: True if and ony if the response object represents a successful
            outcome (as opposed to an error outcome)
        """

        # A JSON response that whose STATUS_KEY has the value OK_STATUS is considered to
        # be a successful response.
        return response[STATUS_KEY] == OK_STATUS
    
    def send_place_ships(self, ships: list[dict]):
        """Send ship placement data to the server."""
        return self.send({ "command": "place_ships", "ships": ships })

    def send_attack(self, row: int, col: int):
        """Send an attack command to the server."""
        return self.send({ "command": "attack", "row": row, "col": col })

