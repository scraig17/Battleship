import pygame
from typing import Callable

from .fonts import normal as font_normal
from .button_colors import ButtonColors
from .button import Button


class ButtonGroup:
    """A group of related buttons arranged horizontally."""

    # Spacing between buttons in pixels
    BUTTON_GAP = 5

    def __init__(self, surface, xy,
                 on_click: Callable[[Button], None] = None,
                 font: pygame.font.Font = None):
        """
        Initializes this ButtonGroup.
        :param surface: surface onto which each button will be drawn
        :param xy: XY coordinate for the group's upper left corner
        :param on_click: a callback that will be invoked for any button that doesn't
            define its own on_click handler
        :param font: font to use for button label text (defaults to "normal" font face)
        """
        self.surface = surface
        self.xy = xy
        self.on_click = on_click
        self.font = font if font else font_normal()
        # A list that will contain tuples describing each button in the group
        self._specs = []
        # A list that will contain a Button object for each button in the group
        self._buttons: list[Button] = []
        self._width = 0             # will store the calculated total width of the button group
        self._height = 0            # will store the calculated height of the button group
        self._max_label_width = 0   # will track the button with the longest label

        self._group: pygame.Surface = None      # will hold an off-screen drawing surface for the group

    def add(self, id, label, colors: ButtonColors, on_click: Callable[[Button], None] = None):
        """
        Adds a button to the right hand end of this group
        :param id: unique identifier for the button
        :param label: a label for the button (string or pre-rendered surface)
        :param colors: a ButtonColors object for the button
        :param on_click: a callback to invoke for this button (defaults to the group's
            on_click handler)
        :return: None
        """
        if not isinstance(label, pygame.Surface):
            # Render the label text if the label isn't pre-rendered
            label = self.font.render(label, True, colors.fg)
        # simply append the new button to the list of specs until we're ready
        # to build the whole group
        self._specs.append((id, label, colors, on_click if on_click else self.on_click))
        # update the max label width if appropriate
        self._max_label_width = max(self._max_label_width, label.get_width())

    def build(self):
        """
        Builds out the button group.
        Call this method only after all desired buttons have been added to the group.
        :return: None
        """
        n = len(self._specs)
        # compute total width, assuming buttons of a uniform size that is large
        # enough for the widest label
        self._width = n * (self._max_label_width + 2 * Button.HORIZONTAL_PADDING) + (n - 1) * self.BUTTON_GAP
        # compute the height of the group, based on the leftmost button
        self._height = self._specs[0][1].get_height() + 2*Button.VERTICAL_PADDING
        # create an off-screen surface for the group
        self._group = pygame.Surface((self._width, self._height), pygame.SRCALPHA)
        # initialize a vector used to position each button
        xy = pygame.math.Vector2(0, 0)
        # initialize the list of button objects
        self._buttons = []
        # iterate the button specs
        for spec in self._specs:
            # create a button; we copy the XY vector since it will be mutated at each iteration
            # props in the spec get passed to corresponding button parameters
            button = Button(self._group, xy.copy(), self._max_label_width, *spec)
            # save the button reference in our list
            self._buttons.append(button)
            # compute position of the next button
            xy += (button.get_width() + self.BUTTON_GAP, 0)

    def consume_ui_event(self, event):
        """
        Attempts to consume a UI event.
        :param event: Pygame UI event
        :return: if this button group consumed the event
        """
        # translate the event position to the coordinate system of the button group
        relative_pos = pygame.math.Vector2(event.pos) - pygame.math.Vector2(self.xy)
        consumed = False
        for button in self._buttons:
            # Here we want to ensure that every button sees the event even
            # if one of the buttons consumes the event. This is important for
            # handling mouse events where the mouse is relocated after a "down"
            # event.
            consumed = button.consume_ui_event(pygame.event.Event(event.type, pos=relative_pos)) or consumed

        return consumed

    def draw(self):
        """
        Draws this button group.
        :return: None
        """
        # Draw each of the buttons onto the off-screen surface for the group
        for button in self._buttons:
            button.draw()
        # Draw the group onto its drawing surface at the appropriate position
        self.surface.blit(self._group, self.xy)

    def get_size(self):
        """
        Gets the size of this button group.
        :return: a 2-tuple containing the width and height
        """
        return self._width, self._height

    def get_width(self):
        """
        Gets the width of this button.
        :return: group width in pixels
        """
        return self._width

    def get_height(self):
        """
        Gets the height of this button.
        :return: group height in pixels
        """
        return self._height
