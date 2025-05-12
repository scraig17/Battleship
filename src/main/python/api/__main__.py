#
# __main__.py:
# Main entry point for the REST API service package.
#

import argparse
import logging

import api.config as config

from .app import app


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-D", "--debug", action="store_true", help="enable debug logging")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format="%(asctime)s %(levelname)s %(name)s %(threadName)s %(message)s")

    # The Flask application object is created in `app.py` and imported into
    # this and other modules that need it. This works fine when using Flask's
    # built-in WSGI-compliant HTTP server. But if you want to run with a real
    # WSGI server (such as Gunicorn), you'll need to use a different approach
    # to create the application object.
    app.run(host=config.LOCAL_IP, port=int(config.API_PORT), debug=args.debug)
