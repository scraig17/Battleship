#
# events.py:
# This module defines event types used in the model.
#

from typing import Callable, Union


class BaseEvent:
    """
    This is a base event for all events generated within the trivial
    GameModel (see model.py). See below for subclasses that define
    different types of events.

    Your implementation could use Python dataclasses to define event
    types instead of defining them this way. The result is the same.
    """
    def __init__(self, message):
        self.message = message

    def __str__(self):
        """
        Produces a string representation of this event that includes
        the message attribute.
        :return:
        """
        return f"{self.__class__.__name__}(message=\"{self.message}\")"


class AttackEvent(BaseEvent):
    def __init__(self, attacker_id, row, col, result):
        message = f"{attacker_id} attacked ({row}, {col}) - {result}"
        super().__init__(message)
        self.attacker_id = attacker_id
        self.row = row
        self.col = col
        self.result = result


class ShipSunkEvent(BaseEvent):
    def __init__(self, attacker_id, ship_name):
        message = f"{attacker_id} sank {ship_name}"
        super().__init__(message)
        self.attacker_id = attacker_id
        self.ship_name = ship_name


class GameOverEvent(BaseEvent):
    def __init__(self, winner_id):
        message = f"{winner_id} wins the game!"
        super().__init__(message)
        self.winner_id = winner_id


class TurnEvent(BaseEvent):
    def __init__(self, player_id):
        message = f"It is now {player_id}'s turn."
        super().__init__(message)
        self.player_id = player_id


# This declaration simply defines a type hint that represents any defined game
# event type.
#
# TODO: your model will have different event type names, and they should
#       be used here instead of those used in this trivial model.
GameEvent = Union[AttackEvent, ShipSunkEvent, GameOverEvent, TurnEvent]

# This declaration defines a type hint for a function that is used as an observer
# for the game model. An observer is invoked every time a game event is generated.
# It gets the event object as its only parameter, and it returns nothing.
GameObserver = Callable[[GameEvent], None]