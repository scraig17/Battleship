import pygame
from typing import Callable

from .fonts import normal as font_normal

from .button_colors import ButtonColors


class Button:

    # Padding on the left and right edges of a button
    HORIZONTAL_PADDING = 5
    # Padding on the top and button edges of a button
    VERTICAL_PADDING = 3
    # Radius for the rounded corner of the button box
    CORNER_RADIUS = 3
    # Width of the border around the rounded button box
    BORDER_WIDTH = 2

    def __init__(self, surface, xy, width, id, label,
                 colors: ButtonColors,
                 on_click: Callable[["Button"], None] = None,
                 font: pygame.font.Font = None):
        """
        Initializes this Button instance.
        :param surface: surface onto which the button will be drawn
        :param xy: XY coordinate of the button's upper left corner
        :param width: with of the button in pixels
        :param id: an identifier for the button
        :param label: a label that will be displayed on the button (text or a Pygame surface)
        :param colors: a ButtonColors object that provides colors for the various button states
        :param on_click: a callback to invoke when the button is clicked
        :param font: a font to use for text displayed on the button; if not specified, the
            `normal` function in the fonts module is used to obtain a default font
        """
        self.surface = surface
        self.xy = xy
        self.width = width
        self.id = id
        self._label = label
        self.colors = colors
        self.on_click = on_click
        self.font = font if font else font_normal()
        # a flag that tracks whether the mouse pointer is hovering over the button
        self._hover = False
        # a flag that when true indicates that a mouse-down event was detected over
        # the button, but no corresponding mouse-up event has yet been detected
        self._active = False
        # an internal surface onto which the button detail will be drawn
        self._button_surface: pygame.Surface = None
        # initialize the button state
        self._update(label)

    @property
    def label(self) -> str:
        """Gets the text label that will be displayed on the button."""
        return self._label

    @label.setter
    def label(self, label: str):
        """
        Sets the text label that will be displayed on the button.
        :param label: the label text to set
        :return: None
        """
        if self._label != label:
            # if the label is changed, update the button state
            self._update(label)
        self._label = label

    def _update(self, label=None):
        """
        Updates the state of this button.
        To simplify the draw method, this method uses the current button state to
        construct an off-screen surface that represents the button in its current state.
        Later, when `draw` is invoked, we can simply blit the off-screen button surface
        onto the screen surface.
        :param label: a label to display on the button (text or a pre-rendered surface)
        :return: None
        """
        if label is None:
            # if no label was specified use our corresponding property
            label = self._label
        if not isinstance(label, pygame.Surface):
            # If the label isn't a pre-rendered surface, render it using our font
            label = self.font.render(str(label), antialias=True, color=self.colors.fg)
        # determine the appropriate width will accommodate the button text and some padding
        width = max(label.get_width() + 2*self.HORIZONTAL_PADDING, self.width + 2*self.HORIZONTAL_PADDING)
        # determine the size of the button rectangle
        button_size = (width, label.get_height() + 2*self.VERTICAL_PADDING)
        # create a surface with an alpha channel
        self._button_surface = pygame.surface.Surface(button_size, pygame.SRCALPHA)
        # determine the appropriate fill color based on the button state
        fill_color = (self.colors.bg_active if self._active
                      else self.colors.bg_hover if self._hover
                      else self.colors.bg_inactive)
        # draw a filled rounded rectangle on the button surface
        pygame.draw.rect(surface=self._button_surface,
                         color=fill_color,
                         rect=((0, 0), button_size),
                         border_radius=self.CORNER_RADIUS)
        # draw the border around the button perimeter
        pygame.draw.rect(surface=self._button_surface,
                         width=self.BORDER_WIDTH,
                         color=self.colors.border,
                         rect=((0, 0), button_size),
                         border_radius=self.CORNER_RADIUS)
        # determine the inset in the horizontal direction where the button text should start
        x_inset = (width - label.get_width()) / 2
        # blit the rendered label text onto the button surface
        self._button_surface.blit(label, (x_inset, self.VERTICAL_PADDING))

    def consume_ui_event(self, event):
        """
        Attempts to consume the given UI event.
        If the event is a mouse event and the location of the event lies within the
        button's bounding rectangle, update the button state accordingly.
        :param event: a Pygame UI event
        :return: True if and only if the event was consumed by this button
        """
        # Is the event location somewhere inside of this button?
        if pygame.rect.Rect(self.xy, self._button_surface.get_size()).collidepoint(event.pos):
            # Handle the different mouse events for this button
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Button down just sets the active flag, so we use a different fill color
                self._active = True
                self._update()
            elif event.type == pygame.MOUSEBUTTONUP:
                # Ignore mouse up if the button isn't active. This avoids triggering on_click
                # if the mouse was moved into this button while the button was being held down.
                if self._active:
                    # We got a down event followed up an up event over this button.
                    # Toggle active off since the click event is complete
                    self._active = False
                    self._update()
                    # Invoke the click handler if defined
                    if self.on_click:
                        event.target = self
                        self.on_click(self)
            elif event.type == pygame.MOUSEMOTION and not self._hover:
                # Toggle hover on when we move into the button
                self._hover = True
                self._update()
            # Indicate that the event was consumed
            return True
        elif event.type == pygame.MOUSEMOTION and self._hover:
            # Toggle hover off if we get any event outside of this button
            self._hover = False
            self._active = False
            self._update()

        # Indicate that the event was not consumed
        return False

    def draw(self):
        """
        Draws this button onto its drawing surface.
        :return: None
        """
        self.surface.blit(self._button_surface, self.xy)

    def get_size(self):
        """
        Gets the size of this button.
        :return: a 2-tuple containing the width and height
        """
        return self._button_surface.get_size()

    def get_width(self):
        """
        Gets the width of this button.
        :return: button width in pixels
        """
        return self._button_surface.get_width()

    def get_height(self):
        """
        Gets the height of this button.
        :return: button height in pixels
        """
        return self._button_surface.get_height()


