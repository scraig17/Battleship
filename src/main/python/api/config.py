# config.ps:
# Configuration properties for the REST API service.
#

import os

# Instead of simply defining constants for various configuration parameters in
# the modules that need them, we instead define all the configurable
# properties in this module. This not only defines all the configuration in one
# place, but also allows us to override any of this configuration using
# environment variables whose names match the property name.
#
# We provide a default value for each configuration property that allows you to
# run the game server locally (e.g. from a shell in a terminal) without needing to
# specify any configuration properties. Notice that because environment variable
# values are always strings, we specify all the defaults as strings as well.
# For properties such as port numbers, you'll need to convert the string to the
# appropriate type before using it. See `__main__.py` for an example.
#
# When running the API from Docker Compose, we'll override several of these
# properties. See the API service definition in `docker-compose.yml` for
# details on how these properties will be configured when running in a
# container stack.

# Local IP address for the API service
LOCAL_IP = os.environ.get("LOCAL_IP", "127.0.0.1")

# Local port for the API service
API_PORT = os.environ.get("API_PORT", "10021")

# Mongo URL for the Mongo database server
MONGO_URL = os.environ.get("MONGO_URL", "mongodb+srv://devonwise:Acephoney42@battleship.s3eskhi.mongodb.net/battleship?retryWrites=true&w=majority&appName=Battleship")

# An issuer string that appears in bearer tokens issued by the REST API
# for admittance to a game instance.
TOKEN_ISSUER_URI = os.environ.get("TOKEN_ISSUER_URI", "urn:ece4564:token-issuer")

# Private key used to sign bearer tokens issued by the REST API
# for admittance to a game instance.
PRIVATE_KEY_FILE = os.environ.get("PRIVATE_KEY_FILE", "private_key.pem")

# A passphrase used to protect the above private key at rest.
# Putting a passphrase into the environment or into your source code
# is fine while a project is under development, but for production
# deployments this sort of property should be stored in a "secrets manager"
# of some kind.
PRIVATE_KEY_PASSPHRASE = os.environ.get("PRIVATE_KEY_PASSPHRASE", "secret")

# The hostname for the game server, as it should appear in URLs
# constructed by the REST API for the game server's WebSocket endpoint.
GAME_SERVER_HOST = os.environ.get("GAME_SERVER_HOST", "localhost")

# The URL scheme to use for WebSocket URLs. When running behind a
# TLS-capable reverse proxy web server, the scheme will usually be
# set to `wss`.
GAME_SERVER_WS_SCHEME = os.environ.get("GAME_SERVER_WS_SCHEME", "ws")
GAME_SERVER_WS_PORT = os.environ.get("GAME_SERVER_WS_PORT", "10020")
