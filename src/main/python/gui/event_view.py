#
# event_view.py:
# This module defines the text area in the UI, used to display received
# events. You probably don't want or need this in your actual game UI
# implementation.
#

import json

import pygame
import gui.widgets.fonts as font


class EventView:
    """
    A simple textual view intended to display JSON event objects, for the
    purpose of demonstrating the event delivery plumbing.
    """

    MAX_HISTORY = 16        # maximum number of rows to display

    def __init__(self, surface, color="black"):
        """
        Initializes an EventView instance.
        :param surface: the surface on which we'll render event text
        :param color: foreground color for the event text
        """
        self.surface = surface
        self.color = color
        # upper left corner of the view
        self.xy = (10, 10)
        # font to use for the text
        self._font = font.monospace()
        # A list that we'll use to hold the rendered segments of text
        self._rendered_events: list[pygame.Surface] = []

    def append(self, event: dict):
        # Constrain the number of events displayed to MAX_HISTORY, by dropping
        # the oldest one if necessary
        if len(self._rendered_events) == self.MAX_HISTORY:
            self._rendered_events.pop(0)

        # Turn the JSON into a string
        event_text = json.dumps(event)
        # Render the string to get a surface containing the text
        rendered_event = self._font.render(event_text, True, self.color)
        # Save the surface to use later in `draw`.
        self._rendered_events.append(rendered_event)

    def draw(self):
        # Upper left corner as a vector
        xy = pygame.math.Vector2(self.xy)
        for rendered_event in self._rendered_events:
            # blit the rendered text onto our drawing surface at the current XY offset
            self.surface.blit(rendered_event, xy.copy())
            # increment the Y coordinate to account for the height of the rendered event text
            xy += (0, rendered_event.get_height())
