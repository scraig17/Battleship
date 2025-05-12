import logging
import sys
from gameauth import TokenValidator

import server.config as config
from .listener import GameListener


# This is the main entry point for our Game Server process.
# The Game Server process communicates exclusively using WebSockets, so
# here we are concerned only with setting up the infrastructure that will
# listen for incoming client connections and handle them appropriately.

if __name__ == "__main__":
    logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                        format="%(levelname)s %(name)s %(threadName)s %(message)s")

    # We enable authentication only if the associated configuration property is True
    enable_auth = bool(config.ENABLE_AUTH)
    # If authentication is to be enabled, we need a TokenValidator, otherwise we'll set it to None
    token_validator = TokenValidator(config.TOKEN_ISSUER_URI, config.PUBLIC_KEY_FILE) if enable_auth else None
    # Create the listener, providing the IP address and port on which we'll listen as specified in the configuration.
    listener = GameListener(config.LOCAL_IP, int(config.WS_LISTENER_PORT), token_validator)
    # The listener runs on our main thread. We won't return here until the listener shuts down.
    listener.run()
