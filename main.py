import sys
import asyncio

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.config import Config

Config.set('graphics', 'resizable', False)

from common.state.StateManager import StateManager, StateEnum
from kivy.uix.screenmanager import ScreenManager, Screen
from common.customw.basic import *
from common.customw.widget_layout import *
from common.taudio.AudioInterface import AudioInterface
from common.taudio.MidiInterface import MidiInterface
from common.taudio.Sampler import CsoundSampler
from common.taudio.PreprocessingSample import preprocess
from common.config import Config as cfg
import common.log as log
import common.clients

logger = log.setup_logger()

import common.clients.wsclient as ws


class ProdApp(App):
    def __init__(self, **kwargs):
        super(ProdApp, self).__init__(**kwargs)
        self.other_task = None
        self.appStatus = None
        self.midi_file = None
        self.config = cfg.load_config()
        self.midi = MidiInterface()
        self.audio = AudioInterface()
        self.csound = CsoundSampler(self.config.audio_dir, self.config.sample_path)
        self.midi_devices = self.midi.devices
        self.devices = self.audio.devices
        self.output_idx = 0
        self.csound.set_output(output=self.output_idx)
        self.midi_input_idx = 0
        self.playing_midi = False

    def build(self):
        """
        Returns 2 screens that hold all the GUI widgets
        """
        sc = ScreenManager()
        sc.add_widget(Graphics(name='graphics'))
        sc.add_widget(Settings(name='settings'))
        return sc

    def set_msg_txt(self, text):
        self.root.get_screen("graphics").message_label.text = text

    def set_event(self, event):
        self.appStatus = event
        logger.debug(f"Set appStatus to {self.appStatus}")

    def startup(self):
        """
        Runs both methods asynchronously and then block until they are finished
        """
        self.sm = StateManager()
        self.other_task = asyncio.ensure_future(self.main_loop())

        async def run_wrapper():
            await self.async_run(async_lib="asyncio")
            self.csound.cleanup()  # before terminating the app, cleanup Csound
            logger.info("App done")
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)

    async def main_loop(self):
        await asyncio.sleep(5)  # This is so

        try:
            await self.sm.stt.setup_model()
        except:
            print("Error starting up stt model")

        self.sm.get_state_action_callbacks()

        self.csound.set_options
        self.csound.compile_and_start()
        self.csound.start_perf_thread()

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


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ProdApp().startup())
    loop.close()
