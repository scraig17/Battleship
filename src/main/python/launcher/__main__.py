import argparse
import sys

from .launcher import Launcher

DEFAULT_URL = "https://game-api.localhost.devcom.vt.edu"


def player(arg):
    """
    Parses a player argument.
    :param arg: user ID and optional password in the format 'uid[:password]'; if the password isn't present
        it is assumed to be the same as the user ID
    :return: tuple containing the user ID and password
    """
    parts = arg.split(":", 2)
    if len(parts) == 1:
        return parts[0], parts[0]
    return parts


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-u", "--url", default=DEFAULT_URL, help="URL for game API")
    parser.add_argument("-p", "--python", help="platform-specific Python command")
    parser.add_argument("-r", "--relaunch", action="store_true", help="relaunch player GUI as needed")
    parser.add_argument("player", nargs="+", type=player, help="user ID and password for a player")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    python_command = args.python
    if not python_command:
        python_command = "py" if sys.platform == "win32" else "python3"

    launcher = Launcher(python_command, args.url, args.relaunch)
    launcher.launch(args.player)
