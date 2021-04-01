from kivy.event import EventDispatcher
from kivy.app import App
import common.log as log
from dummy_ws_requests import *
from functools import *
from statecb import *
from .StateEnum import StateEnum
# from common.state.StateEnum import StateEnum

logger = log.setup_logger()

def conditions_met(operator, stmgr, args):
    args = [vars(stmgr)[a] for a in args]

    return {
        "eq": lambda: len(set(args)) == 1,
        "neq": lambda: len(set(args)) != 1,
    }.get(operator, lambda: 'Not a valid operation')()

class StateManager(EventDispatcher):
    def __init__(self, **kwargs):
        super(StateManager, self).__init__(**kwargs)
        self.register_event_type('on_critical_button_pressed')
        self.register_event_type('on_enter_state')

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
            StateEnum.Playing_Idle: {'user_action_toggle_record':
                                         {'f': dummy_stt_start,
                                          'args':'microphone_hint',
                                          'cb': start_recording_cb,
                                          },

                                     'user_action_generate':
                                         {
                                             'conditions': {'operator':'neq', 'args': ['text', 'last_transcribed_text']},
                                             True: {
                                                    'f': dummy_tts_transcribe,
                                                    'args': 'text',
                                                    'cb': tts_transcribe_cb,
                                            },
                                             False: {
                                                 'f': dummy_sg_generate,
                                                 'args': 'sound_descriptor',
                                                 'cb': sound_gen_cb
                                             }
                                         },

                                     'state_change_toggle_record': {'next_state': StateEnum.Recording}

                                     },
            StateEnum.Recording: {'user_action_toggle_record':
                                         {'f': dummy_stt_stop,
                                          'cb': stop_recording_cb,
                                          },
                                  'state_change_toggle_record': {'next_state': StateEnum.Playing_Idle}

                                  },
            # StateEnum.New_Descriptor_Generation: "",
            # StateEnum.New_Sound_Generation: {'f': dummy_tts_transcribe, 'cb': sound_gen_cb},
        }

        self.user_action_callbacks = {
            "record": toggle_record,
            "generate": infer_pipeline
        }

    async def _callback(self, f, callback=None, stmgr=None):

        return await callback(await f(), stmgr=stmgr) if callback else await f()

    def on_critical_button_pressed(self, *args):
        """
        Perform an action when "Record" or "Generate" is pressed

        """
        action = args[0]['action']
        _source = self.enter_state_callbacks[self.state][action]

        if "conditions" in _source.keys():
            condition = _source['conditions']
            condition = conditions_met(condition['operator'], self, condition['args'])

            _source = _source[condition]

        f = _source['f']
        cb = _source['cb']

        if 'args' in _source.keys():
            f_args = vars(self)[_source['args']]
            self.active_task = asyncio.create_task(
                self._callback(partial(f, f_args), callback=cb, stmgr=self))
        else:
            self.active_task = asyncio.create_task(
                self._callback(partial(f), callback=cb, stmgr=self))


    def on_enter_state(self, *args):

        action = args[0]['action']
        logger.debug(f"Triggered by {action}")
        self.state = self.enter_state_callbacks[self.state][action]['next_state']
        logger.debug(f"New State {self.state}")


    async def setup_models(self):

        print("Setting up models")
        await asyncio.gather(dummy_stt_startup(), dummy_tts_startup(), dummy_stt_startup())
        print("Finished setting up web sockets")
        self.state = StateEnum.Playing_Idle
