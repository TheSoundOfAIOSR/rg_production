from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from functools import *
from common.state.statecb import *
from .StateEnum import StateEnum
import common.clients.wsclient as ws
import asyncio

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
    def __init__(self, stt, tts, sg, **kwargs):
        super(StateManager, self).__init__(**kwargs)

        self.register_event_type('on_pipeline_action')
        self.register_event_type('on_sampler_gui_action')
        self.register_event_type('on_update_io')
        self.register_event_type('on_keyboard_press')
        self.register_event_type('on_switch')
        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = {}
        self.last_sound_parameters = None
        self.state = StateEnum.Playing_Idle
        self.recording_status = False
        self.microphone_hint = '1' # TODO get default from sounddevice
        self.active_task = None
        self.sampler_gui_action = None
        self.app = None #App.get_running_app()
        self.enter_state_callbacks = None
        self.audio = None
        self.samples = {}
        self.audition_audio = False
        self.audition_audio_sample = None
        self.error_handler = ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)
        self.midi_devices = None
        self.root_note = 40
        self.last_generated_note = None
        self.play_note = None
        self.csound = None
        self.level = self.root_note # false by default

        self.stt = stt
        self.tts = tts
        self.sg = sg

    async def _callback(self, f, callback=None, stmgr=None):
        return await callback(await f(), stmgr=stmgr) if callback else await f(stmgr=stmgr)

    def do_sound_gen(self, min, max=None):

        if min and not max:
            self.active_task = asyncio.create_task(
                self._callback(partial(self.sg.get_prediction, self.sound_descriptor), callback=got_one_sample, stmgr=self))

            # self.audition_audio = await self.sg.get_prediction(self.sound_descriptor)
            # self.active_task = asyncio.create_task(
            #     self._callback(partial(, self.sound_descriptor), callback=sound_gen_cb, stmgr=self))
        if min and max:
            pass
            # for i in range(min, max):
            #     self.active_task = asyncio.create_task(
            #         self._callback(partial(self.sg.get_prediction, self.sound_descriptor), callback=sound_gen_cb,
            #                        stmgr=self))

        else:
            pass
            #error

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
        action = args[0].get('action', None)

        logger.debug(f"On Pipeline Action - Triggered by {action} from state {self.state}")

        if action == 'user_action_audition_sample':
            self.audition_audio_sample = None
            self.audition_audio = True

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

    def on_switch(self, instance):
        if instance.state == "down":
            self.level = self.root_note + 24
        else:
            self.level = self.root_note

    def on_keyboard_press(self, ind):
        self.play_note = self.level + ind
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
                    self.audio.input_idx = in_dev.get("id")
                    self.devices["in"] = in_dev

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
            self.midi_input_idx = self.midi_devices["input"].index(dev_hint)
            self.csound.cleanup()
            self.csound.set_midi_api("portmidi")
            self.csound.set_midi_device(self.midi_input_idx)
            self.csound.set_options()
            self.csound.compile_and_start()
            self.csound.start_perf_thread()
            logger.debug(
                f"MIDI device selected: {self.midi_devices['input'][self.midi_input_idx]}"
            )
            logger.debug(f"Using API: {self.midi_devices['api']}")
        
        elif type == "hwd_buffer":
            self.csound.cleanup()
            self.csound.set_hw_buf(hw=dev_hint)
            self.csound.set_options()
            self.csound.compile_and_start()
            self.csound.start_perf_thread()
            print("hardware buffer has been set to " + dev_hint)

        elif type == "sfw_buffer":
            self.csound.cleanup()
            self.csound.set_sw_buf(sw=dev_hint)
            self.csound.set_options()
            self.csound.compile_and_start()
            self.csound.start_perf_thread()
            print("software buffer has been set to " + dev_hint)

        elif type == "samp_rate":
            self.csound.cleanup()
            self.csound.set_sr(sr=dev_hint)
            self.csound.set_options()
            self.csound.compile_and_start()
            self.csound.start_perf_thread()
            print("sample rate has been set to " + dev_hint)

    async def setup_models(self):

        await self.stt.startup()
        await self.tts.startup()
        await self.sg.startup()

        # setup = asyncio.gather(*[server.startup() for server in [self.stt, self.tts, self.sg]])

        return

    def get_state_action_callbacks(self):

        self.devices = App.get_running_app().devices
        self.audio = App.get_running_app().audio
        self.midi_devices = App.get_running_app().midi_devices
        self.csound = App.get_running_app().csound
        self.app = App.get_running_app().root.get_screen("graphics")

        self.enter_state_callbacks = {
            StateEnum.Update: "",
            StateEnum.Playing_Idle: {
                'user_action_toggle_record': ActionManager(f=self.stt.start, args='microphone_hint', cb=start_recording_cb, next_state=StateEnum.Recording),
                'user_action_audition_sample': ActionManager(f=infer_pipeline, next_state=StateEnum.Inferring_Pipeline),
                'user_action_generate': ActionManager(f=infer_pipeline, next_state=StateEnum.Inferring_Pipeline),
            },
            StateEnum.Recording: {
                'pipeline_action_started_recording_failed': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle),
                'user_action_toggle_record': ActionManager(f=self.stt.stop, cb=stop_recording_cb, next_state=StateEnum.New_Text),
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
                'pipeline_action_finish_sg': ActionManager(f=setup_preprocessing, next_state=StateEnum.Preprocessing)
            },
            StateEnum.New_Descriptor_Generation: {
                'pipeline_action_received_descriptor': ActionManager(f=infer_pipeline, next_state=StateEnum.Inferring_Pipeline)
            },
            StateEnum.New_Sound_Generation: {
                'pipeline_action_received_audio': ActionManager(f=infer_pipeline,
                                                                next_state=StateEnum.Inferring_Pipeline)

                # 'pipeline_action_received_audio': ActionManager(f=setup_preprocessing,
                #                                                 next_state=StateEnum.Preprocessing)
            },
            StateEnum.Preprocessing:{
                'pipeline_action_finished_preprocessing': ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)
            },
            'handle_errors':ActionManager(f=play_idle_cb, next_state=StateEnum.Playing_Idle)

        }