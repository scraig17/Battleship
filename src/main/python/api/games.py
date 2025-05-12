from flask import request, g

from gamedb import NoSuchGameError, NoSuchUserError

from .app import app, token_generator, game_repository, user_repository
from .errors import NotFoundError, ForbiddenError, ValidationError
from .auth import authenticate
from .props import *


# This is a minimal implementation of the games API needed for your
# project. You might consider adding some additional functionality
# here.
#
# You could use the `custom` attribute of the Game object to store
# a dict of additional properties with each game. You could, for
# example, allow the creator of a game object to specify a
# "friendly name". You could then add methods that would allow
# a user to fetch all the games for which he/she is player (which
# could be displayed in the UI using the friendly name) or to fetch
# the game details by matching the friendly name. You might find the
# `find_games_for_user` method of the game repository to be useful in
# implementing such functionality.


@app.route(GAMES_PATH, methods=["POST"])
@authenticate
def create_game():

    if not request.is_json:
        raise ValidationError("request body must be JSON")

    players = request.get_json().get(PLAYERS, None)
    if not players or len(players) < 2:
        raise ValidationError("must specify two or more players")

    player = None
    try:
        for player in players:
            user_repository.find_user(player)
        game = game_repository.create_game(g.uid, players)
        token = token_generator.generate(g.uid, game.gid, game.players) if g.uid in game.players else None
        data = game_to_dict(game, token)
        return data, 201, {"Location": data[HREF]}
    except NoSuchUserError:
        raise ValidationError(f"player '{player}' not found")


@app.route(f"{GAMES_PATH}/<gid>")
@authenticate
def fetch_game(gid: str):
    try:
        game = game_repository.find_game(gid)
        if game.creator != g.uid and g.uid not in game.players:
            raise ForbiddenError()
        token = token_generator.generate(g.uid, game.gid, game.players) if g.uid in game.players else None
        return game_to_dict(game, token)
    except NoSuchGameError as err:
        raise NotFoundError(str(err))


