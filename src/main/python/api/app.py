# app.py:
# This module creates the Flask application object and dependencies
# of the REST API service. Any of these objects can be imported into
# other modules as needed.

from flask import Flask

from pymongo import MongoClient
from gameauth import TokenGenerator
from gamedb.mongo import MongoGameRepository, MongoUserRepository

import api.config as config


app = Flask(__name__)

mongo_client = MongoClient(config.MONGO_URL)
user_repository = MongoUserRepository(mongo_client)
game_repository = MongoGameRepository(mongo_client)
token_generator = TokenGenerator(issuer_uri=config.TOKEN_ISSUER_URI,
                                 private_key_filename=config.PRIVATE_KEY_FILE,
                                 private_key_passphrase=config.PRIVATE_KEY_PASSPHRASE)

