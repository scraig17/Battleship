#
# command_buttons.py
# This module defines the view for a row of buttons displayed at the
# bottom of the window in the demo UI.

import pygame

from .client import GameClient
from .widgets import Button, ButtonGroup, ButtonColors
from .protocol import COMMAND_KEY, ERROR_KEY, MESSAGE_KEY


COLOR_PRIMARY = ButtonColors("#ffffff", "#0d6efd", "#0a58ca", "#0b5ed7", "#0d6efd")
COLOR_SUCCESS = ButtonColors("#ffffff", "#198754", "#146c43", "#157347", "#198754")
COLOR_LIGHT = ButtonColors("#000000", "#f8f9fa", "#c6c7c8", "#d3d4d5", "#f8f9fa")
GRID_SIZE = 40


class CommandButtons:
    """
    A button group in which clicking on a button triggers a request
    to the game server to execute a command on the model.
    """

    def __init__(self, surface: pygame.Surface, client: GameClient = None):
        """
        Initializes this CommandButtons object.
        :param surface: a Pygame surface onto which the command buttons will be drawn
        :param client: the client that is connected to our game server
        """
        self.client = client
        # Create a button group in which every button will call back to our `handle_click`
        # method when clicked. The ID for each button is a string that corresponds to the
        # name of the command that will be sent to the game server when the button is clicked.
        self._button_group = ButtonGroup(surface, (0, 0), on_click=self.handle_click)
        self._button_group.add("place_ships", "Place Ships", COLOR_SUCCESS)
        self._button_group.add("attack_mode", "Attack Mode", COLOR_PRIMARY)
        self._button_group.build()
        # Determine the size of the surface and position ourselves in bottom center.
        window_width = surface.get_width()
        window_height = surface.get_height()
        self._button_group.xy = ((window_width - self._button_group.get_width()) / 2,
                                 (window_height - self._button_group.get_height()) - 5)
        # Initialize an empty list to keep track of commands we've sent to the game
        # server for which we're awaiting a reply.
        self._pending_commands: list[str] = []

    def handle_success(self, response: dict):
        # We get called back here if the server's response to a command is OK.
        # The response object could be used to convey details back from the
        # server, if desired.

        # We can assume that the response is for the first pending command in our list.
        # Here we fetch the command from the list simply so that we can log it.
        # NOTE: If we want to update the UI in some way you need to be careful not to
        #       do so while the main thread is redrawing the UI. You'll need to use
        #       a lock or a thread-safe queue (similar to the approach in
        #       `event_handler.py`) if you need to do something with command responses.        #
        #
        command = self._pending_commands.pop(0)
        print(f"ok: command '{command}' completed successfully")

    def handle_error(self, response: dict):
        # We get called back here if the server's response to a command is OK.
        # The response object contains some details describing the error.

        # We can assume that the response is for the first pending command in our list.
        # Here we fetch the command from the list simply so that we can log it.
        command = self._pending_commands.pop(0)

        # NOTE: If we want to update the UI in some way you need to be careful not to
        #       do so while the main thread is redrawing the UI. You'll need to use
        #       a lock or a thread-safe queue (similar to the approach in
        #       `event_handler.py`) if you need to do something with command responses.
        #
        # In this example, we simply get the error message from the response and log
        # the error.
        #
        message = response[ERROR_KEY].get(MESSAGE_KEY, "unknown error")
        print(f"error: command '{command}' failed: {message}")



    def handle_click(self, button: Button):
        # We get called back here when any one of the command buttons is clicked.
        # The button's `id` property is used to hold the name of the game model
        # command to execute when the button is clicked. Here, we create a request
        # containing the desired game model command, and send it to the server.
        if self.client:
            # Put the command name into the list of commands that are pending a response
            self._pending_commands.append(button.id)
            # Send a message to the server via our GameClient, and indicate where
            # we want to be called back when a response is received.
            if button.id == "place_ships":
                ships = self.client.get_ships_for_player()
                self.client.send_place_ships(ships)

            elif button.id == "attack_mode":
                print("Attack mode activated — click on the opponent's board to attack.")

            else:
                print(f"Unknown button '{button.id}' clicked")

    def consume_ui_event(self, event):
        """
        Attempts to consume a UI event.
        :param event: a Pygame UI event
        :return: True if and only if our button group consumed the event
        """
        # Our button group handles only mouse events
        if event.type in {pygame.MOUSEBUTTONUP, pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION}:
            return self._button_group.consume_ui_event(event)
        # If some other event, we didn't consume it
        return False

    def draw(self):
        """
        Draws our button group.
        :return: None
        """
        self._button_group.draw()

    def get_width(self):
        """
        Gets the width of our button group
        :return: width in pixels
        """
        return self._button_group.get_width()

    def get_height(self):
        """
        Gets the height of our button group
        :return: height in pixels
        """
        return self._button_group.get_height()


