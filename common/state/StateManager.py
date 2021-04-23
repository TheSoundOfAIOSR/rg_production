from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from dummy_ws_requests import *
from functools import *
from common.state.statecb import *
from .StateEnum import StateEnum
import common.clients.wsclient as ws
# from common.state.StateEnum import StateEnum

logger = log.setup_logger()

class ActionManager():

    __slots__ = [
        "f", "args", "cb", "next_state"
    ]
    def __init__(self, f=None, args=None, cb=None, next_state=None, pre_work=False):
        self.f = f
        self.args = args
        self.cb = cb
        self.next_state = next_state

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)

        self.register_event_type('on_pipeline_action')
        self.register_event_type('on_sampler_gui_action')
        self.register_event_type('on_update_io')
        self.register_event_type('on_keyboard_press')
        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.last_sound_parameters = None
        self.state = StateEnum.Playing_Idle
        self.recording_status = False
        self.microphone_hint = '1' # TODO get default from sounddevice
        self.active_task = None
        self.sampler_gui_action = None
        self.app = None #App.get_running_app()
        self.enter_state_callbacks = None
        self.audio = None
        self.error_handler = ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)
        self.root_note = None #
        self.play_note = None
        self.csound = None

        """
        WS Clients placeholders
        """
        try:
            self.stt =  ws.STTClient(host="localhost", port=8786)#host=self.app.config.host, port=self.app.config.base_port
            self.tts = ws.STTClient(host="localhost", port=8787)
            self.sg =  ws.STTClient(host="localhost", port=8881)#host=self.app.config.host, port=self.app.config.base_port

            asyncio.ensure_future(self.stt.run())
            asyncio.ensure_future(self.tts.run())
            asyncio.ensure_future(self.sg.run())
        except:
            print("Problem loading model")
        # self.tts = ws.TTSClient(host=self.config.host, port=self.config.base_port + 1)
        # self.sg = ws.SGClient(host=self.config.host, port=self.config.base_port + 2)

    async def _callback(self, f, callback=None, stmgr=None):
        print("doing callback ")
        print(stmgr)
        return await callback(await f(), stmgr=stmgr) if callback else await f(stmgr=stmgr)

    def make_call(self, _source):
        f = _source.f
        cb = _source.cb
        # TODO: FIX SOME TIME
        # self.active_task = asyncio.create_task(self._callback(partial(f, vars(self).get(_source.args, [])), callback=cb, stmgr=self))
        if _source.args:
            f_args = vars(self).get(_source.args, [])
            self.active_task = asyncio.create_task(
                self._callback(partial(f, f_args), callback=cb, stmgr=self))
        else:
            self.active_task = asyncio.create_task(
                self._callback(partial(f), callback=cb, stmgr=self))

    def on_pipeline_action(self, *args):
        action = args[0]['action']
        logger.debug(f"On Pipeline Action - Triggered by {action}")

        if not self.enter_state_callbacks:
            _source = self.error_handler
        else:
            _source = self.enter_state_callbacks[self.state].get(action, None)

        if action == 'handle_errors' or not _source:
            error_msg = "There was an unexpected error. Returning to idle state. check server status or restart."
            logger.debug(error_msg)
            self.app.ids['lab'].text = error_msg

            _source = self.enter_state_callbacks['handle_errors']

        if _source:
            self.state = _source.next_state
            logger.debug(f"New State {self.state} making call")

            if _source.f:
                self.make_call(_source)

    def on_sampler_gui_action(self, *args):

        self.sampler_gui_action = args[0]

    def on_keyboard_press(self, ind):
        print("Keybo")
        self.play_note = self.root_note+ind-24
        self.sampler_gui_action = 'play_note'

    def on_update_io(self, *args):
        arg = args[0]
        type = arg['type']
        dev_hint = arg['hint']

        if type == "input":
            input_list = self.devices["devices"]["input_list"]
            for in_dev in input_list:
                if dev_hint == in_dev.get("name", None):
                    self.microphone_hint = in_dev.get("id")
                    print("Set hint to ", self.microphone_hint)
                    self.app.audio.input_idx = in_dev.get("id")
                    self.app.devices["in"] = in_dev

        elif type == "output":
            output_list = self.devices["devices"]["output_list"]
            for out_dev in output_list:
                if dev_hint == out_dev.get("name", None):
                    self.output_idx = out_dev.get("id")
                    self.devices["out"] = out_dev
                    self.csound.cleanup()
                    self.csound.set_output(self.output_idx)
                    self.csound.set_options()
                    self.csound.compile_and_start()
                    self.csound.start_perf_thread()

        elif type == "midi_input":
            self.midi_input_idx = self.app.midi_devices["input"].index(dev_hint)
            self.csound.cleanup()
            self.csound.set_midi_api("portmidi")
            self.csound.set_midi_device(self.app.midi_input_idx)
            self.csound.set_options()
            self.csound.compile_and_start()
            self.app.csound.start_perf_thread()
            logger.debug(
                f"MIDI device selected: {self.app.midi_devices['input'][self.app.midi_input_idx]}"
            )
            logger.debug(f"Using API: {self.app.midi_devices['api']}")

    async def setup_models(self):
        await self.stt.setup_model()
        # await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())

    # 'setup??? '
    # 'user_action_toggle_record' -> self.state = StateEnum.Recording -> stt_start -> start_recording_cb
    # 'pipeline_action_started_recording_failed' -> self.state = StateEnum.Playing_Idle -> play_idle_cb
    # 'user_action_toggle_record' -> self.state = StateEnum.New_Text -> stt_stop -> stop_recording_cb
    # 'pipeline_action_received_text' -> self.state = StateEnum.Playing_Idle -> play_idle_cb
    #
    # 'user_action_generate' -> self.state = StateEnum.Inferring_Pipeline -> infer_pipeline()
    # 'pipeline_action_start_tts' -> self.state = StateEnum.New_Descriptor_Generation -> tts_transcribe -> tts_transcribe_cb
    # 'pipeline_action_received_tts' -> self.state = StateEnum.Inferring_Pipeline -> infer_pipeline()
    # 'pipeline_action_start_sg' -> self.state = StateEnum.New_Sound_Generation -> sg_generate -> sg_callback
    # 'pipeline_action_received_audio' -> self.state = StateEnum.Preprocessing -> preprocessing -> preprocessing_cb
    # 'pipeline_action_finished_preprocessing' -> self.state = StateEnum.Playing_Idle -> play_idle_cb

    def get_state_action_callbacks(self):
        print("********************************")
        print(dir(App.get_running_app()))
        self.devices = App.get_running_app().devices
        self.csound = App.get_running_app().csound
        self.app = App.get_running_app().root.get_screen("graphics")
        # print(dir(self.app.root.get_screen("graphics")))
        # print(self.app.root.get_screen("graphics").ids)
        self.root_note = 40
        print("********************************")

        self.enter_state_callbacks = {
            StateEnum.Update: "",
            StateEnum.Playing_Idle: {
                'user_action_toggle_record': ActionManager(f=self.stt.start, args='microphone_hint', cb=start_recording_cb, next_state=StateEnum.Recording),
                # 'user_action_toggle_record': ActionManager(f=self.stt.start, args='microphone_hint', cb=start_recording_cb),
                'user_action_generate': ActionManager(f=infer_pipeline, next_state=StateEnum.Inferring_Pipeline),
                # 'pipeline_action_started_recording': ActionManager(next_state=StateEnum.Recording),
            },
            StateEnum.Recording: {
                'pipeline_action_started_recording_failed': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle),
                'user_action_toggle_record': ActionManager(f=self.stt.stop, cb=stop_recording_cb, next_state=StateEnum.New_Text),
                # 'pipeline_action_stop_recording': ActionManager(next_state=StateEnum.Playing_Idle),
            },
            StateEnum.New_Text:{
                'pipeline_action_received_text': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)
            },
            StateEnum.Inferring_Pipeline:{
                'pipeline_action_nothing_to_infer': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle),
                'pipeline_action_start_tts': ActionManager(f=self.tts.process_text, args='text', cb=tts_transcribe_cb,
                                                           next_state=StateEnum.New_Descriptor_Generation),
                'pipeline_action_start_sg': ActionManager(f=self.sg.get_prediction, args='sound_descriptor', cb=sound_gen_cb,
                                                          next_state=StateEnum.New_Sound_Generation),
            },
            StateEnum.New_Descriptor_Generation: {
                'pipeline_action_received_descriptor': ActionManager(f=infer_pipeline, next_state=StateEnum.Inferring_Pipeline)
            },
            StateEnum.New_Sound_Generation: {
                'pipeline_action_received_audio': ActionManager(f=setup_preprocessing,
                                                                next_state=StateEnum.Preprocessing)
            },
            StateEnum.Preprocessing:{
                'pipeline_action_finished_preprocessing': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)
            },
            'handle_errors':ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)

        }