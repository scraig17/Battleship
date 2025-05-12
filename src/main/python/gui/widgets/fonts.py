import pygame


# This small module simply exposes some functions to make it a little easier
# to reference fonts when rendering text.

FONT_FACES_NORMAL = ["Arial", "Helvetica"]
FONT_FACES_MONOSPACE = ["Monaco", "Consolas", "Courier New"]


def normal(size=24):
    """
    Gets a reference to a "normal" font face.
    :param size: size of the font
    :return: a font object
    """
    return pygame.font.SysFont(FONT_FACES_NORMAL, size)


def monospace(size=20):
    """
    Gets a reference to a "monospace" font face.
    :param size: size of the font
    :return: a font object
    """
    return pygame.font.SysFont(FONT_FACES_MONOSPACE, size)