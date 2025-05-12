
from gamedb import User, Game

import api.config as config

# This module defines the property names used in JSON requests and responses
# and provides functions used to produce JSON from objects such as User.

CODE = "code"
COUNT = "count"
CREATION_DATE = "creation_date"
CREATOR = "creator"
CUSTOM = "custom"
FULL_NAME = "full_name"
GAMES = "games"
GID = "gid"
HREF = "href"
MESSAGE = "message"
NICKNAME = "nickname"
PASSWORD = "password"
PLAYER = "player"
PLAYERS = "players"
TOKEN = "token"
UID = "uid"
SERVER = "server"
GAMES_PATH = "/games"
USERS_PATH = "/users"


def user_to_dict(user: User) -> dict:
    """ Converts a User object to a dictionary which can be easily converted
        to JSON by Flask.

    Args:
        user (User): the user object to be converted

    Returns:
        dict: a dictionary containing those attributes of the User object
              that are relevant for an API client, along with some additional
              "links" that a client can use to manipulate the User object as
              a resource
    """
    data = {
        HREF: f"{USERS_PATH}/{user.uid}",
        PASSWORD: f"{USERS_PATH}/{user.uid}/password",
        UID: user.uid,
        CREATION_DATE: user.creation_date.astimezone().isoformat(),
    }
    if user.nickname is not None:
        data.update({NICKNAME: user.nickname})
    if user.full_name is not None:
        data.update({FULL_NAME: user.full_name})
    if user.custom is not None:
        data.update({CUSTOM: user.custom})
    return data


def game_to_dict(game: Game, token: str = None) -> dict:
    data = {
        HREF: f"{GAMES_PATH}/{game.gid}",
        GID: game.gid,
        CREATION_DATE: game.creation_date.isoformat(),
        CREATOR: game.creator,
        PLAYERS: game.players,
    }
    if token:
        data.update({
            TOKEN: token,
            SERVER: f"{config.GAME_SERVER_WS_SCHEME}://{config.GAME_SERVER_HOST}:{config.GAME_SERVER_WS_PORT}/{game.gid}",
        })
    return data
