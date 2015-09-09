import unittest
from unittest.mock import Mock
from eventdispatcher import Dispatcher


class TestDispatcher(unittest.TestCase):
    def setUp(self):
        self.dispatcher = Dispatcher()

    def test_register_listener(self):
        listener = object()
        self.dispatcher.register('event', listener)

    def test_dispatch_event(self):
        self.dispatcher.dispatch('event', object())

    def test_dispatch_event_to_listeners(self):
        event1_name = 'event1'
        event2_name = 'event2'
        event = object()
        listener1 = Mock()
        listener1.on_event = Mock()
        listener2 = Mock()
        listener2.on_event = Mock()
        listener3 = Mock()
        self.dispatcher.register(event1_name, listener1)
        self.dispatcher.register(event1_name, listener2)
        self.dispatcher.register(event2_name, listener3)

        self.dispatcher.dispatch(event1_name, event)

        listener1.on_event.assert_called_with(event)
        listener2.on_event.assert_any_call(event)
