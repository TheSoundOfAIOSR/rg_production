from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from dummy_ws_requests import *
from functools import *
from statecb import *
from .StateEnum import StateEnum
# from common.state.StateEnum import StateEnum

logger = log.setup_logger()

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)
        self.register_event_type('on_critical_button_pressed')
        self.register_event_type('on_state_changed')

        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.state = StateEnum.Loading
        self.recording_status = False
        self.microphone_hint = "Microphone-1" # TODO get default from sounddevice
        self.active_task = None
        self.app = App.get_running_app()
        self.enter_state_callbacks = {
            StateEnum.Loading: "",
            StateEnum.Update: "",
            StateEnum.Playing_Idle: {'user_action_toggle_record': }
            StateEnum.Recording: recording_callback,
            StateEnum.New_Descriptor_Generation: "",
            StateEnum.New_Sound_Generation: {'f': dummy_tts_transcribe, 'cb': sound_gen_cb},
        }

        

        self.user_action_callbacks = {
            "record": toggle_record,
            "generate": infer_pipeline
        }

    async def _callback(self, f, callback=None):

        return await callback(await f()) if callback else await f()

    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        source = args[0]['source']
        print("In critical button pressed")

        self.active_task = asyncio.create_task(
            self._callback(partial(self.user_action_callbacks[source], self)))

    def try_state_change(self, *args):
        self.active_task = asyncio.create_task(
            self._callback(partial(self.enter_state_callbacks[self.state]['f'], self), callback=self.enter_state_callbacks[self.state]['cb']))

        print("State was changed internally")

    async def setup_models(self):

        print("Setting up models")
        await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())
        print("Finished setting up web sockets")
        self.state = StateEnum.Playing_Idle
