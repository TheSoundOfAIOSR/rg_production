from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from dummy_ws_requests import *
from functools import *
from statecb import *
from .StateEnum import StateEnum
import common.clients.wsclient as ws
# from common.state.StateEnum import StateEnum

logger = log.setup_logger()

def conditions_met(operator, stmgr, args):
    args = [vars(stmgr)[a] for a in args]

    return {
        "eq": lambda: len(set(args)) == 1,
        "neq": lambda: len(set(args)) != 1,
    }.get(operator, lambda: 'Not a valid operation')()


class ActionManager():
    def __init__(self, f=None, args=None, cb=None, next_state=None, pre_work=False):
        self.f = f
        self.args = args
        self.cb = cb
        self.next_state = next_state
        self.pre_work = False

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)

        self.register_event_type('on_critical_button_pressed')
        self.register_event_type('on_pipeline_action')
        self.register_event_type('on_sampler_gui_action')
        self.register_event_type('on_update_mic_hint')
        """Application Variables"""
        self.text = None
        self.last_transcribed_text = None
        self.sound_descriptor = None
        self.state = StateEnum.Playing_Idle
        self.recording_status = False
        self.microphone_hint = '1' # TODO get default from sounddevice
        self.active_task = None
        self.sampler_gui_action = None
        self.app = App.get_running_app()
        self.enter_state_callbacks = None
        """
        WS Clients placeholders
        """
        self.stt =  ws.STTClient(host="localhost", port=8786)#host=self.app.config.host, port=self.app.config.base_port
        asyncio.ensure_future(self.stt.run())
        # self.tts = ws.TTSClient(host=self.config.host, port=self.config.base_port + 1)
        # self.sg = ws.SGClient(host=self.config.host, port=self.config.base_port + 2)

    async def _callback(self, f, callback=None, stmgr=None):
        return await callback(await f(), stmgr=stmgr) if callback else await f(stmgr=stmgr)

    def make_call(self, _source):
        f = _source.f
        cb = _source.cb

        if _source.args:
            f_args = _source.args
            self.active_task = asyncio.create_task(
                self._callback(partial(f, f_args), callback=cb, stmgr=self))
        else:
            self.active_task = asyncio.create_task(
                self._callback(partial(f), callback=cb, stmgr=self))


    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        action = args[0]['action']
        print(action)
        _source = self.enter_state_callbacks[self.state][action]

        self.make_call(_source)

    def on_pipeline_action(self, *args):
        print("On pipeline action")
        action = args[0]['action']
        logger.debug(f"Triggered by {action}")

        if self.enter_state_callbacks[self.state][action].pre_work:
            _source = self.enter_state_callbacks[self.state][action].pre_work

        self.state = self.enter_state_callbacks[self.state][action].next_state
        logger.debug(f"New State {self.state}")

    def on_sampler_gui_action(self, *args):
        self.sampler_gui_action = args[0]

    def on_update_mic_hint(self, *args):
        self.microphone_hint = args[0]
        logger.log(f"Set mic hint to {self.microphone_hint}")
        

    async def setup_models(self):
        await self.stt.setup_model()
        # await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())


    def get_state_action_callbacks(self):
        self.enter_state_callbacks = {
            StateEnum.Update: "",
            StateEnum.Playing_Idle: {
                'user_action_toggle_record': ActionManager(f=self.stt.start, args='microphone_hint', cb=start_recording_cb),
                'user_action_generate': ActionManager(f=infer_pipeline),
                'pipeline_action_started_recording': ActionManager(next_state=StateEnum.Recording),
                'pipeline_action_start_tts': ActionManager(f=)
            },
            StateEnum.Pre_TTS: {
                'pipeline_action_start_tts': ActionManager(f=dummy_tts_transcribe, args='text', cb=tts_transcribe_cb,
                                                           next_state=StateEnum.New_Descriptor_Generation,
                                                           pre_work=True),
            },
            StateEnum.Pre_SG: {
              'pipeline_action_start_sg':  ActionManager(f=dummy_sg_generate, args='sound_descriptor', cb=sound_gen_cb,
                                                          next_state=StateEnum.New_Sound_Generation, pre_work=True),
            },
            StateEnum.Recording: {
                'user_action_toggle_record': ActionManager(f=self.stt.stop, cb=stop_recording_cb),
                'pipeline_action_stop_recording': ActionManager(next_state=StateEnum.Playing_Idle),},
            StateEnum.New_Descriptor_Generation: {
                'pipeline_action_start_sg': ActionManager(f=dummy_sg_generate, args='sound_descriptor', cb=sound_gen_cb,
                                                           next_state=StateEnum.New_Sound_Generation, pre_work=True),},
            StateEnum.New_Sound_Generation: {
                'pipeline_action_received_audio': ActionManager(f=dummy_preprocessing, cb=preprocessing_cb,
                                                                next_state=StateEnum.Preprocessing)},
            StateEnum.Preprocessing:{'pipeline_action_finished_preprocessing': ActionManager(next_state=StateEnum.Playing_Idle)}
        }