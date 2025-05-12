server
======

This package provides an example architecture to show how to use the
communication and authentication plumbing provided by the VT ECE4564 Game
Library in your project's game server implementation.

For this example, the game model is trivial. It simply takes 
commands from connected clients and uses them to generate simple events
that are sent to each client connected to that particular game.

In this skeleton, `GameListener` (in the `listener.py` module) 
is the central point of control. It creates and configures the WebSocket
connection listener, which handles incoming connections and authentication. 
For each new connection, the server finds or creates a `GameServer` object 
(see `server.py`) for the game ID presented by the client. It then hands off 
the connection to the `GameServer` object.

A `GameServer` has an instance of `GamePublisher` (see `publisher.py`) and
a collection of controller objects -- one for each connected client. In 
the game server, a new `GameController` (see `controller.py`) is created for 
each new client connection, and the connection is added to the publisher as
a subscriber. After this is complete, the controller's `run` method is invoked. 

Notice that because each new client connection has its own service thread, 
the `GameListener`, `GameServer`, and `GamePublisher` must all account for 
thread safety using locks as appropriate. You'll also need to account for 
thread safety in your game model. You could do this by introducing a lock 
directly into your model, or you could "wrap" your model in another object 
that implements the same top-level interface and incorporates a lock.

The controller's `run` method simply has a loop where it waits for 
a command from the client, takes some action, and responds to the client.
Since every connected client has its own service thread, multiple clients
can be executing commands concurrently. Each command supported by the
controller corresponds directly to a method to be invoked on the game
model. In the trivial example model (in the `model` package), each method 
simply publishes an event so that we can see different events being published
and distributed to every client in a particular game. 

Be sure to look at the `config.py` module that provides configuration
properties needed for the game server. In the other modules that use the
configuration, look for the `import` statement that imports the 
`config` module as well as references to the properties of the 
configuration such as those in `__main__.py`.
