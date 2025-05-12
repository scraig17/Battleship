from typing import Union

import pytest


from model import GameModel, GameEvent, HelloEvent


class MockObserver:
    """
    A mock that can act as an observer for the GameModel. It simply
    collects any emitted events in a list and provides methods to search
    the events that were captured.
    """

    def __init__(self):
        self.events: list[GameEvent] = []

    def handle_event(self, event: GameEvent):
        """
        This method will be invoked whenever the game model emits an event.
        :param event: the subject event
        :return: None
        """
        self.events.append(event)

    def clear(self):
        """Clears the list of previously received events."""
        self.events.clear()

    def find_first(self, event_type) -> Union[GameEvent, None]:
        """
        Finds the first event of the given event type.
        :param event_type: the event type to match
        :return: first matching event type or None if no such event was captured
        """
        for event in self.events:
            if isinstance(event, event_type):
                return event
        return None

    def find_all(self, event_type) -> list[GameEvent]:
        """
        Finds all events of the given event type.
        :param event_type: the event type to match
        :return: list of matching event types (empty if no such events were captured)
        """
        events = []
        for event in self.events:
            if isinstance(event, event_type):
                events.append(event)
        return events


@pytest.fixture
def event_observer() -> MockObserver:
    return MockObserver()


@pytest.fixture
def game_model(event_observer: MockObserver):
    return GameModel(event_observer.handle_event)


def test_hello_command(game_model: GameModel, event_observer: MockObserver):
    #
    # This function tests the model's Hello command.
    # Like most tests of a model, it makes some assertions about the initial
    # state of the model, then it invokes a method on the model. Subsequently,
    # it makes some assertions about the resulting state of the model, and
    # confirms that any expected events were emitted.
    #
    assert game_model.counter == 0
    game_model.hello()
    # The hello command should increment the counter
    assert game_model.counter == 1
    # And the hello command should emit a hello event
    assert event_observer.find_first(HelloEvent) is not None