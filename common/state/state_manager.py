from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log

logger = log.setup_logger()
class EventManager(EventDispatcher):
    def __init__(self, **kwargs):
        self.register_event_type('on_critical_button_pressed')
        super(EventManager, self).__init__(**kwargs)

    def on_critical_button_pressed(self, *args):
        pass

class StateManager(EventManager):

    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)
