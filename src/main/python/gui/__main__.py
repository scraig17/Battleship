#
# This is the main entry point for the GUI.
# For simplicity assumes that the player's username and password
# are passed via the command line, along with a URL for the game.
#
# In your project, you may instead wish to provide UI for the user
# to enter her username and password. You could then use the API
# fetch the collection of games the user is authorized to play,
# or give the user the opportunity to create a new game, before
# subsequently fetching the details for the game from the API
# service and connecting to the game server.
#

import argparse
import sys
from urllib.parse import urlsplit, urlunsplit

import requests
from requests.auth import HTTPBasicAuth

from .event_handler import GameEventHandler
from .client import GameClient
from .gui import GUI

DEFAULT_URL = "ws://127.0.0.1:10020"


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--uid", help="user ID for the API server")
    parser.add_argument("-p", "--password", help="password for the API server")
    parser.add_argument("-g", "--game-url", default=DEFAULT_URL, help="URL for the game")
    args = parser.parse_args()
    if args.uid or args.password:
        if not args.uid or not args.password:
            print("must specify both -u and -p", file=sys.stderr)
            exit(1)
    return args


def fetch_game(uid: str, password: str, game_url: str) -> dict:
    """
    Fetches a game object (which could represent a lobby, a room, or whatever) from
    the API server.
    :param uid: user ID for our user
    :param password: password for our user
    :param game_url: URL for the game object we wish to retrieve
    :return: game object received from the REST API
    """
    auth = HTTPBasicAuth(uid, password)
    response = requests.get(game_url, auth=auth)
    response.raise_for_status()
    return response.json()


def fetch_player_name(uid: str, game_url: str) -> str:
    """
    Fetches the name for our player from the user's record in the REST API
    :param uid: user ID for our user
    :param game_url: URL for our game object
    :return:
    """
    # the game_url gives us the base URL for the API; we just need to reassemble it into a user URL
    url_parts = urlsplit(game_url)
    user_path = f"/users/{uid}"
    user_url = urlunsplit((url_parts.scheme, url_parts.netloc, user_path, url_parts.query, url_parts.fragment))

    # now fetch the user
    response = requests.get(user_url)
    response.raise_for_status()

    user = response.json()
    # we prefer the nickname, but we'll take either the full name, or just the user ID instead
    return user.get("nickname", user.get("full_name", uid))


if __name__ == "__main__":
    args = parse_args()

    # if the user ID (and password) is specified, assume that the URL is for the REST API
    # and fetch the details for the game and user from the API. Otherwise, assume that the
    # URL is for the game server and that it is running with authentication disabled
    if args.uid:
        game = fetch_game(args.uid, args.password, args.game_url)
        player_name = fetch_player_name(args.uid, args.game_url)
        # Now get the game server URL and authentication token from the game object
        server_url = game['server']
        token = game['token']
    else:
        server_url = args.game_url
        token = None
        player_name = None

    print(f"Game server URL: {server_url}")

    # Create a handler that will receive callbacks for in-game events
    event_handler = GameEventHandler()

    # Create a GameClient instance, and set its `on_event` callback to our event handler.
    client = GameClient(url=server_url, token=token, on_event=event_handler.handle_event)
    # Start the client -- it runs its own service thread and returns here immediately
    client.start()

    # Create our GUI.
    # The GUI gets a reference to our client, and to the event handler that it will use
    # to receive in-game events. We also pass the player name so that it can be displayed
    # in the window title.
    gui = GUI(client, event_handler, player_name)

    # We run the GUI on the main thread.
    # We won't return here until the GUI exits.
    try:
        gui.run()
    except KeyboardInterrupt:
        pass

    # Ensure that the client's WebSocket connection is closed and that it's service
    # thread has been stopped.
    client.stop()

