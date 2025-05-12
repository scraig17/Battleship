#
# event_handler.py:
# This module defines the event handler that is used to receive events from
# the game server and enqueue them until they can be safely processed by
# the GUI's main thread.
#

from queue import Queue, Empty


class GameEventHandler:
    """
    A simple handler for asynchronous game events that stores each received event
    in a thread safe Queue. An instance of this queue is used to asynchronously
    store game events as they are received. Later, when it is safe to update the UI,
    we can fetch all the pending events from the queue.
    """

    def __init__(self):
        self._queue = Queue()

    def handle_event(self, event):
        # Put the event on the end of the queue
        self._queue.put(event)

    def pending_events(self) -> list[dict]:
        # An empty list to collect the queued events
        events = []
        try:
            # Pull events from the queue until the queue is empty
            while True:
                events.append(self._queue.get(block=False))
        except Empty:
            pass

        return events
