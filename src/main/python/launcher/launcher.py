import subprocess
import time

from concurrent.futures import ThreadPoolExecutor, wait as await_futures
from threading import Event
from typing import Sequence
from urllib.parse import urljoin

from .games_api_client import GamesApiClient
from .users_api_client import UsersApiClient


class Launcher:
    """
    A utility class that will create and launch an instance of a game.
    """

    def __init__(self, python_command, api_url, relaunch_on_exit=False):
        """
        Creates a new launcher.
        :param python_command: name of the Python command; typically `python3` for Mac OS X or Linux, `py` for Windows
        :param relaunch_on_exit: if True when a GUI process for a player exits, the launcher will restart it
            automatically
        :param api_url: base URL for the API server
        """
        self.python_command = python_command
        self.api_url = api_url
        self.relaunch_on_exit = relaunch_on_exit
        self._users_api = UsersApiClient(api_url)
        self._games_api = GamesApiClient(api_url)
        self._shutdown = Event()

    def _find_or_create_user(self, player: tuple[str, str]) -> dict:
        """
        Finds an existing user or creates a new user with the given player.
        :param player: a tuple representing the player's user ID and password
        :return: dict containing details for the user
        """
        print(f"[DEBUG] Registering or fetching user '{player[0]}' with password '{player[1]}'")
        user = self._users_api.fetch_user(player[0])
        if not user:
            user = self._users_api.create_user(player[0], player[1])
        return user

    def _create_game(self, players: Sequence[tuple[str, str]]) -> dict:
        """
        Creates a new game instance for the specified players.
        :param players: a sequence (list or tuple) in which each element is a tuple consisting of a player's
            user ID and password
        :return: dict containing details for the game instance
        """
        self._games_api.auth(players[0][0], players[0][1])   # use the first player to authenticate to the games API
        return self._games_api.create_game([player[0] for player in players])

    def _game_args(self, uid, password, game_url):
        """
        Creates a list of the command-line arguments needed for the GUI.
        :param uid: user ID for the player
        :param password: password for the player
        :param game_url: game API URL
        :return: list of command line arguments needed to successfully start the GUI
        """
        return [self.python_command, "-m", "gui", "-u", uid, "-p", password, "-g", game_url]

    def _launch_player(self, player: tuple[str, str], game_url: str):
        """
        Launches the GUI for a player and (optionally) relaunches as necessary
        :param player: player user ID and password (as a tuple)
        :param game_url: game API URL
        :return:
        """
        proc = None
        return_code = None
        log_filename = f"{player[0]}.log"
        while not self._shutdown.is_set():
            # Assemble the arguments for the command line and launch the GUI program
            with open(log_filename, "w+") as log_file:
                args = self._game_args(player[0], player[1], game_url)
                proc = subprocess.Popen(args=args, stdout=log_file, stderr=log_file)

            # Watch for the GUI process to exit
            return_code = proc.poll()
            while return_code is None and not self._shutdown.is_set():
                time.sleep(0.250)
                return_code = proc.poll()

            # Bail out if we're trying to stop the launcher
            if self._shutdown.is_set():
                break

            # If the process exited normally and we're configured to relaunch, go back and launch it again
            if return_code == 0 and self.relaunch_on_exit:
                time.sleep(2)
                continue

            # exit the loop
            break

        # say what happened in the log
        if return_code is not None:
            if return_code != 0:
                outcome = f"exited with non-zero code; see log at {log_filename}"
            else:
                outcome = f"exited normally"
            print(f"process for player {player[0]} {outcome}")

        # if GUI process hasn't exited yet (e.g. because launcher is shutting down), terminate it
        if proc and proc.poll() is None:
            proc.terminate()

    def launch(self, players: Sequence[tuple[str, str]]):
        """
        Launches a new game instance, creating the players (as needed) and game object using the API
        :param players: a sequence (list or tuple) in which each element is a tuple consisting of a player's
            user ID and password
        :return:
        """
        if not len(players):
            raise ValueError("must specify at least one player")

        # Create user records for players as needed
        for player in players:
            self._find_or_create_user(player)

        # Create a new game instance
        game = self._create_game(players)
        game_url = urljoin(self.api_url, game["href"])
        print(f"Game URL: {game_url}")
        print(f"Game Server URL: {game['server']}")

        # Launch the GUI for each player using a thread pool
        futures = []
        executor = ThreadPoolExecutor()
        for player in players:
            futures.append(executor.submit(self._launch_player, player, game_url))

        # Wait around while the game is being played
        while True:
            try:
                time.sleep(0.250)
            except KeyboardInterrupt:
                break

        # Signal that we're ready to shut down and wait for all subprocesses to exit
        self._shutdown.set()
        await_futures(futures)
        executor.shutdown()

