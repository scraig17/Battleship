gui
===

This module provides the GUI for the demo. The "game" for this plumbing
example isn't really much fun. The UI simply provides buttons that make
requests to the game server. Each successful request causes an event to
be sent to every client in the game. The UI simply displays the received
events. Ho hum.

However, this example does show (in `__main__.py`) one way to launch the
UI using a user ID, password, and game URL, by getting these as command
line arguments, and using them to fetch the game object from the API. Of
course, your GUI could provide a login screen where the user fills in her
username and password, you retrieve the games (rooms, whatever) that the
user is authorized to access from the API, and let her choose one. 

The JSON object for the selected game contains the game server URL and 
token that are needed to connect to that particular game.
