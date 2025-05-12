
model
=====

This package contains a trivial observable game model and definitions
for events produced by the model. The top level `GameModel` is used in the
`GameServer` and `GameController` classes (see the `server` package). When
a new instance of the game is created, a `GameServer` object is created 
which in turn creates an instance of `GameModel`. The reference to the
same `GameModel` object is shared with each `GameController` that is 
connected to that particular game instance.

A `GameController` uses the model to execute each command sent by the
corresponding player. The observer for the `GameModel` is a `GamePublisher`
that distributes events to every player in that particular game.

