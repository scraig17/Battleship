#
# errors.py:
# This module defines custom exception types used in the REST API service.
#

from .app import app

from .props import *


class ClientError(Exception):
    """A base class for all errors that should have a 400-499 status"""
    def __init__(self, status_code: int, *args):
        super().__init__(*args)
        self.status_code = status_code


class ValidationError(ClientError):
    """An error raised when the client's request is invalid."""
    def __init__(self, *args):
        super().__init__(400, *args)


class ForbiddenError(ClientError):
    """An error raised when a client's request is rejected because
       the user isn't authorized to perform the requested action."""
    def __init__(self):
        super().__init__(403, "You are not authorized to perform the requested action")


class NotFoundError(ClientError):
    """An error raised when a client requests a resource that does not exist."""
    def __init__(self, *args):
        super().__init__(404, *args)


class PreconditionFailedError(ClientError):
    """An error raised to indicate that the client requested a conditional response,
       but the stated precondition wasn't satisfied."""
    def __init__(self, *args):
        super().__init__(412, *args)


class PreconditionRequiredError(ClientError):
    """An error raised to indicate that the resource requires a conditional response,
       but the client did not provide the necessary precondition to match."""
    def __init__(self, *args):
        super().__init__(428, *args)


def error_body(code: str, message: str):
    """
    Produces the detail for an error response body.
    :param code: the error code
    :param message: the error message
    :return:
    """
    return {CODE: code, MESSAGE: message}


@app.errorhandler(ClientError)
def handle_error(err: ClientError):
    """A Flask error handler that is invoked automatically when any
       exception of type ClientError is raised during route handling.
       It produces a response body that describes the error."""
    return error_body(err.__class__.__name__, str(err)), err.status_code
