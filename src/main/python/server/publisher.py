#
# publisher.py:
# This module defines the GamePublisher class.
#

import logging
from threading import Lock

from gamecomm.server import GameConnection

from model import GameEvent


logger = logging.getLogger(__name__)


class GamePublisher:
    """
    A publisher of in-game events to connected clients.
    An instance of GamePublisher maintains a list of client connection objects
    as subscribers, which are added or removed as part of client connect/disconnect
    handling in GameServer. The `publish_event` method of this class is designed
    to be an observer of GameModel events. When the model invokes the event callback
    on an instance of this class, the event data is translated to JSON format and
    distributed to subscribers as appropriate.

    Any filtering or other transformation of event data before it is sent to any
    particular client should be implemented in this class. For example, in a card
    game, an event indicating that a card was dealt to a player will include the
    detail of the specific card only when sending the event to the client representing
    the player receiving the card. Other players would be notified that the player
    received a card, without including the specific card detail.

    For the purpose of this sort of filtering, you might want to modify this class
    so that it keeps track of a player number for each subscriber. The model could
    include the player number in the event detail, and code in this class could use
    that information when considering what to deliver to any particular subscriber.
    """

    def __init__(self):
        self._subscribers: list[GameConnection] = []
        self._lock = Lock()

    def add_subscriber(self, connection: GameConnection):
        logger.info(f"adding subscriber {connection}")
        with self._lock:
            self._subscribers.append(connection)

    def remove_subscriber(self, connection: GameConnection):
        logger.info(f"removing subscriber {connection}")
        with self._lock:
            self._subscribers.remove(connection)

    def publish_event(self, event: GameEvent):
        logger.info(f"publishing event: {event}")
        with self._lock:
            subscribers = list(self._subscribers)
        for subscriber in subscribers:
            subscriber.send(self._event_to_json(subscriber, event))

    def _event_to_json(self, subscriber, event: GameEvent):
        # Here's where you could use properties of the subscriber and
        # the event to determine exactly what to send to a given subscriber.
        return {
            "event": event.__class__.__name__,
            "message": event.message,
        }
    
    def notify(self, event: GameEvent):
        """
        Conforms to the GameObserver interface by forwarding events to publish_event().
        """
        self.publish_event(event)
