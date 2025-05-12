#
# errors.py:
# This module defines custom exception types used in the model.
#

class GameError(Exception):
    """
    A generic base class for errors generated within the model.
    You could define subclasses of this exception type for different error
    situations, if desired. See controller.py to see where/how this is used.
    """
    pass


