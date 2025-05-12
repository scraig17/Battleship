from flask import request, g
from gamedb import DuplicateUserIdError, NoSuchUserError

from .app import app, user_repository
from .errors import ForbiddenError, NotFoundError, PreconditionFailedError, PreconditionRequiredError, ValidationError

from .auth import authenticate
from .props import *


# This is a minimal implementation of the users API needed for your
# project. You might consider adding some additional functionality
# here if your project requires it.


@app.route(USERS_PATH, methods=["POST"])
def create_user():
    """ Create a new (persistent) User object. """

    if not request.is_json:
        raise ValidationError("request body must be JSON")

    input_data = request.get_json()
    uid = input_data.get(UID)
    password = input_data.get(PASSWORD)
    nickname = input_data.get(NICKNAME)
    full_name = input_data.get(FULL_NAME)

    if not uid or not password:
        raise ValidationError("request must include UID and password")

    try:
        user = user_repository.create_user(uid, password, nickname, full_name)
    except DuplicateUserIdError:
        raise ValidationError(f"user {uid} already exists")

    output_data = user_to_dict(user)
    return output_data, 201, {"Location": output_data[HREF], "ETag": user.tag()}


@app.route(f"{USERS_PATH}/<uid>")
def fetch_user(uid: str):
    """ Fetch an existing User object. """

    try:
        user = user_repository.find_user(uid)
    except NoSuchUserError:
        raise NotFoundError(f"user {uid} does not exist")
    return user_to_dict(user), 200, {"ETag": user.tag()}


@app.route(f"{USERS_PATH}/<uid>/password", methods=["PUT"])
@authenticate
def change_password(uid: str):
    """ Change a user's password """

    # Authenticated user must be the user whose password is to be changed
    if uid != g.uid:
        raise ForbiddenError()

    password = request.get_data(as_text=True)
    if not password:
        raise ValidationError("must provide new password")

    try:
        user_repository.change_password(uid, password)
    except NoSuchUserError:
        raise NotFoundError(f"user '{uid}' not found")

    return "", 204


@app.route(f"{USERS_PATH}/<uid>", methods=["DELETE"])
@authenticate
def delete_user(uid: str):
    """ Delete a user if it exists """
    # Authenticated user must be the user to be deleted
    if uid != g.uid:
        raise ForbiddenError()

    # The user repository doesn't complain when you try to delete
    # a user that doesn't exist, so no error handling needed here.
    user_repository.delete_user(uid)
    return "", 204


@app.route(f"{USERS_PATH}/<uid>", methods=["PUT"])
def update_user(uid: str):
    """ Update the mutable properties of a user """

    if not request.is_json:
        raise ValidationError("request body must be JSON")

    if not request.if_match:
        raise PreconditionRequiredError("request must include If-Match header")

    try:
        user = user_repository.find_user(uid)
    except NoSuchUserError:
        raise NotFoundError(f"user '{uid}' not found")

    if user.tag() not in request.if_match:
        raise PreconditionFailedError("request data is stale")

    data = request.get_json()
    user.full_name = data.get(FULL_NAME)
    user.nickname = data.get(NICKNAME)
    user.custom = data.get(CUSTOM)
    user = user_repository.replace_user(user)
    return user_to_dict(user), 200, {"ETag": user.tag()}