#
# model.py
# This module contains the central (and only) class of the trivial game
# model used in the skeleton project. Your project's model will likely
# consist of several different model classes defined in separate modules
# with this package. For example, in a card game, this package could
# contain modules defining Suit, Rank, Card, Deck, Hand, etc.
#

from .errors import GameError
from .events import *

class Ship:
    def __init__(self, name, size):
        self.name = name
        self.size = size
        self.positions = []
        self.hits = set()

    def place(self, start_row, start_col, horizontal=True):
        self.positions = []
        for i in range(self.size):
            row = start_row
            col = start_col + i if horizontal else start_col
            if not horizontal:
                row = start_row + i
            self.positions.append((row, col))

    def is_sunk(self):
        return set(self.positions) == self.hits

    def register_hit(self, position):
        if position in self.positions:
            self.hits.add(position)
            return True
        return False


class Board:
    def __init__(self):
        self.ships = []
        self.attacks = set()

    def place_ship(self, ship, row, col, horizontal=True):
        ship.place(row, col, horizontal)
        for existing in self.ships:
            if set(ship.positions) & set(existing.positions):
                raise GameError("Ships overlap")
        self.ships.append(ship)

    def receive_attack(self, row, col):
        if (row, col) in self.attacks:
            raise GameError("Position already attacked")
        self.attacks.add((row, col))
        for ship in self.ships:
            if ship.register_hit((row, col)):
                return 'hit', ship
        return 'miss', None

    def all_ships_sunk(self):
        return all(ship.is_sunk() for ship in self.ships)

class GameModel:
    """
    This class stands in for the main model class of your game model. It provides
    the API that is invoked by the controller in response to player commands. See
    controller.py in the `server` package for an example of how it is used.
    """

    def __init__(self, observer: GameObserver):
        self.observer = observer
        self.players = {}
        self.ready_players = set()
        self.current_turn = None
        self.connections = []  # Add this line to track connections

    # Every one of the following methods on this trivial model simply publishes
    # an event. In a real game model, invoking methods here would update the state
    # of the game and publish events as needed. This example simply exercises the
    # event delivery plumbing.

    def place_ships(self, player_id, ship_data):
        print(f"[DEBUG] Player {player_id} placing ships...")
        if player_id in self.players:
            raise GameError("Ships already placed")
        board = Board()
        for data in ship_data:
            ship = Ship(data['name'], data['size'])
            board.place_ship(ship, data['row'], data['col'], data.get('horizontal', True))
        self.players[player_id] = board
        self.ready_players.add(player_id)
        if len(self.ready_players) == 2:
            self.current_turn = list(self.players.keys())[0]
            self.observer.notify(TurnEvent(self.current_turn))

        print(f"[DEBUG] Ships placed for {player_id}: {[ship.name for ship in board.ships]}")

    def attack(self, attacker_id, row, col):
        print(f"[DEBUG] {attacker_id} attacks ({row},{col})")
        if attacker_id != self.current_turn:
            raise GameError("Not your turn")
        opponent_id = [pid for pid in self.players if pid != attacker_id][0]
        opponent_board = self.players[opponent_id]
        result, ship = opponent_board.receive_attack(row, col)
        self.observer.notify(AttackEvent(attacker_id, row, col, result))

        if result == 'hit' and ship.is_sunk():
            self.observer.notify(ShipSunkEvent(attacker_id, ship.name))

        if opponent_board.all_ships_sunk():
            self.observer.notify(GameOverEvent(attacker_id))
        else:
            self.current_turn = opponent_id
            self.observer.notify(TurnEvent(self.current_turn))

        print(f"[DEBUG] Attack result: {result}, Ship hit: {ship.name if ship else 'None'}") 
