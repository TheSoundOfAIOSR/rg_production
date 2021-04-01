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

        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.state = StateEnum.Loading
        self.recording_status = False
        self.microphone_hint = "Microphone-1" # TODO get default from sounddevice
        self.active_task = None
        self.app = App.get_running_app()
        # self.state_callbacks = {
        #     StateEnum.Loading: "",
        #     StateEnum.Update: "",
        #     StateEnum.Recording: recording_callback,
        #     StateEnum.New_Descriptor_Generation: "",
        #     StateEnum.New_Sound_Generation: "",
        # }

        self.action_callbacks = {
            "record": toggle_record,
            "generate": infer_pipeline
        }

    async def _callback(self, f, callback=None):

        return await callback(await f()) if callback else await f()

    async def stt_event_handler(self, *args):
        logger.debug(args)
        "Update state vars"

    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        source = args[0]['source']
        print("In critical button pressed")

        self.active_task = asyncio.create_task(
            self._callback(partial(self.action_callbacks[source], self)))

    async def setup_models(self):

        print("Setting up models")
        await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())
        print("Finished setting up web sockets")
        self.state = StateEnum.Playing_Idle
