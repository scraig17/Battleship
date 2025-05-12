api
===

This module provides a REST API service for a game service. You could
reuse this entire module for your team's game API.

The included `users.py` module provides the same API for users that
we discussed in class. The included `games.py` module provides a bare
minimum implementation for creating a game and fetching it. Feel free to 
modify any aspect of the API needed for your team's project.

Be sure to look at the `config.py` module that provides configuration
properties needed for the API. In the other modules that use the
configuration, look for the `import` statement that imports the 
`config` module as well as references to the properties of the 
configuration such as those in `__main__.py`
