# auth.py:
# This module provides support for HTTP Basic authentication in
# flask. To add authentication to Flask REST API route, import
# the `authenticate` function from this module, and use it as
# a decorator on the route.

from functools import wraps

from flask import request, g, Response

from gameauth import is_valid_password
from gamedb import NoSuchUserError

from .app import user_repository

AUTH_REALM = "game-db"


def is_valid_credential(username: str, password: str) -> bool:
    """
    Validates a username and password by checking that the username
    exists in the user repository and that the password matches the
    password stored given in the user record in the database.
    :param username: the subject username
    :param password: the user's password
    :return: True if and only if the user exists and the
        password matches the user's passwords
    """
    try:
        user = user_repository.find_user(username)
        return is_valid_password(password, user.password)
    except NoSuchUserError:
        return False


def authenticate(f):
    """
    Use this function as a decorator by adding it after the @app.route decorator
    for API functions that require authentication.
    """

    @wraps(f)
    def wrapper(*args, **kwargs):
        """ This wrapper gets in invoked before the API function that it wraps """

        # Flask puts the contents of the Authorization header into the `authorization` attribute of the request
        auth = request.authorization

        # If the request doesn't have an auth attribute value or it doesn't have a username or doesn't have a
        # password or if the password isn't valid for the given user, we reject the request
        if not auth or not auth.username or not auth.password or not is_valid_credential(auth.username, auth.password):
            return Response("", 401, {"WWW-Authenticate": f"Basic realm=\"{AUTH_REALM}\""})

        # Otherwise, we put the user ID for the authenticated user into the `g` namespace so we can access it
        # our API functions
        g.uid = auth.username

        # Now we invoke the function that handles the request (or the next wrapper)
        return f(*args, **kwargs)

    return wrapper
