final-project-skeleton
======================

This skeleton shows how to assemble the communications plumbing
for your project in your API, game server, and UI client. It basically
implements a high-level architecture for the system as a whole, as specified
in the project requirements. Your team can choose to use any or all or none
of the components provided in this skeleton. But be sure to study and really
understand what the skeleton is providing to you before you choose.

The code is organized as a set of packages with names that suggest the main 
function of each package

- `api` -- provides a minimal REST API service that you can customize and
  expand to suit the needs of your project
- `gui` -- a Pygame-based GUI that communicates with the API service using
  REST semantics over HTTP, and with the game service using WebSockets; shows
  how the `GameClient` provided in the VT ECE4564 Game Library can be used
  to support a user interface
- `launcher` -- a reusable utility that will create users for a game and 
  launch the UI for each user; assumes that all backend services are running
  in a container stack launched via Docker Compose; see details in
  [Running Everything](#running-everything)
- `model` -- a trivial observable game model for the purpose of illustrating
  how your object-oriented game model fits into the other aspects of the
  architecture
- `server` -- a minimal game server implementation that illustrates the
  architecture that supports game play over WebSockets using the 
  `WSGameListener` and `GameConnection` objects from the VT ECE4564 Game
  Library

You'll find a README in each package describing the contents and design of 
the modules within the package. Each module includes lots of comments 
describing how it all works. Spending time studying and understanding the 
skeleton and where your project code fits in is essential for successfully
using it.

I've provided instructions here for running everything using a terminal.
Of course, you can also configure a Python virtual environment using your IDE 
to avoid the drudgery of doing it all the old school way in a terminal.

* [Set Up the Virtual Environment](#set-up-the-virtual-environment)
* [Create a Key Pair](#create-a-key-pair)
* [Reactivating the Virtual Environment](#reactivating-the-virtual-environment)
* [Running Everything](#running-everything)
* [Running Unit Tests](#running-unit-tests)


Set Up the Virtual Environment
------------------------------

Before you can run the code in the skeleton, you need to do some one-time
setup.

I'm assuming you've already installed a Python3 distribution.

Clone this repository onto your local system and then follow the directions
below that apply to your system.


### Windows Powershell

First, open Windows PowerShell and make the terminals's current directory the base 
directory for your cloned copy of the repository.

Create a Python virtual environment in the `venv` subdirectory of the base
directory.
```
py -m venv venv
```

Inform PowerShell that you want the current terminal process to allow execution
of scripts. Otherwise, you'll get an error telling you that it cannot execute
the script in the next step
```
Set-ExecutionPolicy Unrestricted -Scope Process -Force
```

Activate the virtual environment. This should change the prompt in some manner 
so that it displays the string `venv` to remind you that the virtual 
environment has been activated.
```
venv\Scripts\Activate.ps1
```

Install the dependencies needed by the various components of the application.
```
py -m pip install -r requirements.txt
```

After successfully setting up the virtual environment you can 
now [Create a Key Pair](#create-a-key-pair) needed to run the REST API and game services.

### Mac OS X/Linux

I'm assuming that you're using either `zsh` or `shell` as your shell. If 
you don't know which shell you are using, it's probably fine -- the default
is `zsh` on current versions of Mac OS X and is typically `bash` on Linux.

First, open a terminal and make the shell's current directory the base 
directory for your cloned copy of the repository.

Create a Python virtual environment in the `venv` subdirectory of the base
directory.
```shell
python3 -m venv venv
```

Activate the virtual environment. This should change the prompt in some manner 
so that it displays the string `venv` to remind you that the virtual 
environment has been activated.
```shell
source venv/bin/activate
```

Install the dependencies needed by the various components of the application.
```shell
python3 -m pip install -r requirements.txt
```

After successfully setting up the virtual environment you can 
now [Create a Key Pair](#create-a-key-pair) needed run to the REST API and 
game services.


Create a Key Pair
-----------------

The mechanism used to authenticate the client UI when it connects to the 
game server requires a public-private key pair for asymmetric cryptography.

**These instructions assume that the virtual environment has been created and 
activated in your terminal**.

To generate the key pair, first open a terminal and set the current 
directory to the location on your system where you cloned this repository.

Next, follow the instructions given below for your system.

### Windows Powershell

Run the following command to generate the key pair.
```shell
py -m gameauth
```

You will be asked to provide a passphrase used to encrypt the private key.
For our purposes here you can simply use `secret` as the passphrase. If you
wish to use another secret, you also need to update 
`src/main/python/api/config.py` and `docker-compose.yml`to match.

After successfully completing the setup, you can now go on 
to [Running Everything](#running-everything).


### Mac OS X/Linux

Run the following command to generate the key pair.
```shell
python3 -m gameauth
```

You will be asked to provide a passphrase used to encrypt the private key.
For our purposes here you can simply use `secret` as the passphrase. If you
wish to use another secret, you might also want to update 
`src/main/python/api/config.py` and `docker-compose.yml` to match.

After successfully completing the setup, you can now go on
to [Running Everything](#running-everything).


Reactivating the Virtual Environment
------------------------------------

If you previously completed the setup, and you're coming back to run
in a new terminal session, you'll need to reactivate the virtual environment.

### Windows PowerShell

First, open Windows PowerShell and set the terminal's current directory to the 
location on your system where you cloned this repository.

Inform PowerShell that you want the current terminal process to allow execution
of scripts. Otherwise, you'll get an error telling you that it cannot execute
the script in the next step.
```
Set-ExecutionPolicy Unrestricted -Scope Process -Force
```

Activate the virtual environment.
```
venv\Scripts\Activate.ps1
```

### Mac OS X/Linux

First, open a terminal and set the shell's current directory to the location
on your system where you cloned this repository.

Activate the virtual environment.
```shell
source venv/bin/activate
```

Running Everything
------------------

These instructions assume that you've already performed the [setup](#set-up-the-virtual-environment).

If you are working in a **newly launched terminal**, be sure to first 
[reactivate the virtual environment](#reactivating-the-virtual-environment)

You'll need two terminals -- one to run the container stack
of backend services using Docker Compose, and the other to run the UI 
launcher. The **virtual environment must be active in the terminal that you'll 
use to run the Launcher**.

In each terminal, **make sure that your terminal's 
current directory is the base directory that contains your copy of this
repository**.


### Windows PowerShell

In the first terminal, run Docker Compose to start up all the backend
services.
```
docker compose up --build --detach
```

In the second window, run the Launcher to create some players and a game
instance and launch the GUI for each player.

```
$env:PYTHONPATH="src\main\python"
py -m launcher alice bob mallory
```

While running everything, you can watch the logs of game server or the API
using Docker Compose. For example, to follow the log of the game server use:

```
docker compose logs --follow game-server
```

To follow the logs of the API, use `game-api` instead.

Press Ctrl-C to stop following the logs.

Note that if you create another terminal, activate the virtual environment,
and run the Launcher again for another set of users, you'll get a different
game instance -- each group of users is connected to their own distinct
instance of the underlying game model.

After experimenting with the skeleton, you can exit the Launcher by pressing
Ctrl-C in the terminal -- all the UI processes started by the Launcher will
be automatically terminated. You can then shut down the backend container
stack using the following command in the terminal was used to start up the
stack.

```
docker compose down
```


### Mac OS X/Linux

In the first terminal, run Docker Compose to start up all the backend
services.
```shell
docker compose up --build --detach
```

In the second terminal, run the Launcher to create some players and a game
instance and launch the GUI for each player.

```shell
export PYTHONPATH=src/main/python
python3 -m launcher alice bob mallory
```

While running everything, you can watch the logs of game server or the API
using Docker Compose. For example, to follow the log of the game server use:

```
docker compose logs --follow game-server
```

To follow the logs of the API, use `game-api` instead.

Press Ctrl-C to stop following the logs.

Note that if you create another terminal, activate the virtual environment,
and run the Launcher again for another set of users, you'll get a different
game instance -- each group of users is connected to their own distinct
instance of the underlying game model.

After experimenting with the skeleton, you can exit the Launcher by pressing
Ctrl-C in the terminal -- all the UI processes started by the Launcher will
be automatically terminated. You can then shut down the backend container
stack using the following command in the terminal was used to start up the
stack.

```
docker compose down
```


Running Unit Tests
------------------

The skeleton contains a unit test module for the included trivial model
(see `model_test.py`). The unit test module provides a simple example of
a unit test that invokes a method on the model and validates the resulting
model state. It uses a mock observer to capture events emitted by the model
so that it can validate the events that were produced.

To successfully run the unit tests in a terminal, you first need to **activate
the virtual environment** and **set the terminal's current directory to the
base directory where you cloned this repository**.

### Windows PowerShell

To run all the tests:
```
$env:PYTHONPATH="src\main\python"
pytest src\test\python --verbose
```

As the tests are run, Pytest will display the passing and failing test cases
on the terminal.


### Mac OS X/Linux

To run all the tests:
```
export PYTHONPATH=src/main/python
pytest src/test/python --verbose
```

As the tests are run, Pytest will display the passing and failing test cases
on the terminal.
