import os
os.environ['KIVY_NO_ARGS'] = '1'
import sys
import asyncio

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config

#Config.set('graphics', 'fullscreen', 'auto')

from common.state.StateManager import StateManager, StateEnum
from kivy.uix.screenmanager import ScreenManager, Screen
from common.customw.basic import *
from common.customw.widget_layout import *
import common.clients.wsclient as ws
from common.taudio.AudioInterface import AudioInterface
from common.taudio.MidiInterface import MidiInterface
from common.taudio.Sampler import CsoundSampler
from common.config import Config as cfg
import common.log as log
import common.clients
import functools
import argparse
import common.clients.wsclient as ws

parser = argparse.ArgumentParser(description="Production startup")
parser.add_argument('--debug', dest='debug', action='store_true', required=False)

logger = log.setup_logger()



class ProdApp(App):
    def __init__(self, **kwargs):
        super(ProdApp, self).__init__(**kwargs)
        self.other_task = None
        self.appStatus = None
        self.midi_file = None
        self.config = None
        self.midi = MidiInterface()
        self.audio = AudioInterface()
        self.csound = None
        self.midi_devices = self.midi.devices
        self.devices = self.audio.devices
        self.output_idx = 0
        self.midi_input_idx = 0
        self.playing_midi = False

    def build(self):
        """
        Returns 2 screens that hold all the GUI widgets
        """
        self.title = 'The Sound of AI - Open Source Research'
        sc = ScreenManager()
        sc.add_widget(Graphics(name='graphics'))
        sc.add_widget(Settings(name='settings'))
        return sc

    def set_msg_txt(self, text):
        self.root.get_screen("graphics").message_label.text = text

    def set_event(self, event):
        self.appStatus = event
        logger.debug(f"Set appStatus to {self.appStatus}")

    def startup(self, sm, csound, config):
        """
        Runs both methods asynchronously and then block until they are finished
        """
        self.sm = sm
        self.config = config
        self.csound = csound
        self.sampler_loop = asyncio.ensure_future(self.main_loop())

        async def run_wrapper():
            await self.async_run(async_lib="asyncio")
            self.csound.cleanup()  # before terminating the app, cleanup Csound
            logger.info("App done")
            self.sampler_loop.cancel()

        return asyncio.gather(run_wrapper(), self.sampler_loop)

    async def main_loop(self):
        await self.sm.get_state_action_callbacks()

        """
        This is the main loop which the application will run inside of.
        """
        try:
            while True:

                if self.sm.sampler_gui_action and self.sm.state == StateEnum.Playing_Idle:

                    if self.sm.sampler_gui_action == "play_note":
                        print(f"Trying to play note {self.sm.play_note}")
                        self.csound.play_sample(self.sm.play_note)
                        self.sm.sampler_gui_action = None

                    if self.sm.sampler_gui_action == "play_sample":
                        self.csound.play_sample()
                        self.sm.sampler_gui_action = None

                    if self.sm.sampler_gui_action == 'play_audition_sample':
                        self.csound.play_sample(self.sm.root_note-1)
                        self.sm.sampler_gui_action = None

                    if self.sm.sampler_gui_action == "midi_loaded":
                        self.sm.sampler_gui_action = None

                        if self.root.get_screen("graphics").playing_midi:
                            # self.csound.cleanup()
                            self.root.get_screen("graphics").playing_midi = False
                            self.set_msg_txt("")
                        else:
                            if self.midi_file is None:
                                self.set_msg_txt(
                                    "Please drag and drop a .mid file here"
                                )
                            else:
                                self.csound.cleanup()
                                self.csound.play_midi_file(self.midi_file)
                                r = self.csound.compile_and_start()
                                if r < 0:
                                    self.set_msg_txt(
                                        "Can't play that file, check file structure or create issue at GitHub repo"
                                    )
                                else:
                                    self.csound.start_perf_thread()
                                    self.set_msg_txt(f"Playing - {self.midi_file}")
                                self.root.get_screen("graphics").playing_midi = True
                                self.midi_file = None
                                logger.debug(self.output_idx)

                await asyncio.sleep(0.01)
        except asyncio.CancelledError:
            logger.error(f"Wasting time was canceled", exc_info=True)
        finally:
            # when canceled, print that it finished
            logger.debug("Done wasting time")

async def setup(debug):

    stt = ws.STTClient(host="localhost", port=8786, module="stt")
    tts = ws.STTClient(host="localhost", port=8787, module="tts")
    sg = ws.STTClient(host="localhost", port=8080, module="sg")

    sm = StateManager(stt, tts, sg)
    config = cfg.load_config()
    csound = CsoundSampler(config.audio_dir, config.sample_path)
    csound.set_output(output=0)
    csound.compile_and_start()
    csound.start_perf_thread()

    if not debug:
        await sm.setup_models()
    await ProdApp().startup(sm, csound, config)
    return

if __name__ == "__main__":
    args = parser.parse_args()

    loop = asyncio.get_event_loop()

    try:
        loop.run_until_complete(setup(args.debug))
    except KeyboardInterrupt:
        print("closing loop")

    loop.close()