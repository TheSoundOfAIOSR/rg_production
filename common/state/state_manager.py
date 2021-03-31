from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from enum import Enum
from dummy_ws_requests import *

logger = log.setup_logger()

class StateEnum(Enum):
    Loading = 1
    Update = 2
    Playing_Idle = 3
    Recording = 4
    New_Descriptor_Generation = 4
    New_Sound_Generation = 5

class GUILight(Enum):
    Green = 1
    Yellow = 2
    Red = 3

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)
        self.register_event_type('on_critical_button_pressed')

        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.state = StateEnum.Loading
        self.recording_status = False
        self.microphone_hint = "Microphone-1" # TODO get default from sounddevice

    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        source = args[0]['source']

        if self.state == StateEnum.Playing_Idle:
            if source == "record" and self.recording_status == False:
                """ Send start command to STT websocket"""
                self.recording_status = True
                self.state = StateEnum.Recording

    async def setup_models(self):

        print("Setting up models")
        await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())
        print("Finished setting up web sockets")
        self.state = StateEnum.Playing_Idle
