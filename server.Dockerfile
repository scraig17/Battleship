# This Dockerfile provides an example that you can reuse in your project
# It copies the game server source from the `server` module, and the
# public key generated during the setup (see the top level README for details),
# placing these artifacts into the container's /app directory. It installs the
# dependencies for the game server, and configures the container to run the
# server module by default.

FROM python:3.12-slim
WORKDIR /app
RUN python3 -m pip install vtece4564-gamelib==0.1.9
COPY src/main/python/model/ /app/model/
COPY src/main/python/server/ /app/server/
COPY public_key.pem /app/
CMD ["/usr/local/bin/python3", "-m", "server"]
