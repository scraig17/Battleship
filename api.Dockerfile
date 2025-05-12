# This Dockerfile provides an example that you can reuse in your project
# It copies the API source from the API module, and the private key generated
# during the setup (see the top level README for details), placing these
# artifacts into the container's /app directory. It installs the dependencies
# for the API, and configures the container to run the api module by default.

FROM python:3.12-slim
WORKDIR /app
RUN python3 -m pip install flask vtece4564-gamelib==0.1.9
COPY src/main/python/api/ /app/api/
COPY private_key.pem /app/
CMD ["/usr/local/bin/python3", "-m", "api"]
