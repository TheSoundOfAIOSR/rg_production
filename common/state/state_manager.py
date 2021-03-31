from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from enum import Enum

logger = log.setup_logger()

class StateEnum(Enum):
    Loading = 1
    Update = 2
    Playing_Idle = 3
    Recording = 4
    New_Sound_Generation = 5

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)
        self.register_event_type('on_critical_button_pressed')

        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.state = StateEnum.Loading

    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        logger.debug("args")