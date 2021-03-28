import sys
import asyncio

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.garden.knob import Knob
from kivy.config import Config

from common.customw.basic import *
from common.customw.slider_layout import *
from common.taudio.AudioInterface import AudioInterface
from common.taudio.MidiInterface import MidiInterface
from common.taudio.Sampler import CsoundSampler
from common.taudio.PreprocessingSample import preprocess
from common.config import Config as cfg
import common.log as log

logger = log.setup_logger()


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
        self.midi_input_idx = 0
        self.playing_midi = False

    def build(self):
        return Graphics()

    def set_msg_txt(self, text):
        self.root.message_label.text = text

    def set_event(self, event):
        self.appStatus = event
        logger.debug(f"Set appStatus to {self.appStatus}")

    def startup(self):
        """This will run both methods asynchronously and then block until they
        are finished
        """

        self.other_task = asyncio.ensure_future(self.main_loop())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run(async_lib="asyncio")
            self.csound.cleanup()  # before terminating the app, do the cleanup for Csound
            logger.info("App done")
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)

    def select_audio_device(self, obj, event):
        """
        Audio device in form:
        "0/1/M <device_name>",
        to extract just <device_name>...
        """
        dev = event  # just the device name
        io = obj.name

        # handling input
        if io == "input":
            input_list = self.devices["devices"]["input_list"]
            for in_dev in input_list:
                if dev == in_dev.get("name", None):
                    self.audio.input_idx = in_dev.get("id")
                    self.devices["in"] = in_dev
                    logger.debug(self.devices["in"])
                    logger.debug(
                        f"Input index: {self.audio.input_idx}, {type(self.audio.input_idx)}"
                    )
        # handling output
        elif io == "output":
            output_list = self.devices["devices"]["output_list"]
            for out_dev in output_list:
                if dev == out_dev.get("name", None):
                    self.output_idx = out_dev.get("id")
                    self.devices["out"] = out_dev
                    self.csound.cleanup()
                    self.csound.set_output(self.output_idx)
                    self.csound.set_midi_api()
                    self.csound.compile_and_start()
                    self.csound.start_perf_thread()
                    logger.debug(self.devices["out"])
                    logger.debug(
                        f"Csound index: {self.output_idx}, {type(self.output_idx)}"
                    )
        elif io == "midi_input":
            self.midi_input_idx = self.midi_devices["input"].index(dev)
            self.csound.cleanup()
            self.csound.set_output(self.output_idx)
            self.csound.set_midi_api("portmidi")
            self.csound.set_midi_device(self.midi_input_idx)
            self.csound.compile_and_start()
            self.csound.start_perf_thread()
            logger.debug(
                f"MIDI device selected: {self.midi_devices['input'][self.midi_input_idx]}"
            )
            logger.debug(f"Using API: {self.midi_devices['api']}")

        logger.debug(dev)

    async def main_loop(self):
        recording_status = False
        record_task = None

        self.csound.set_output(self.output_idx)
        self.csound.set_midi_api()
        self.csound.compile_and_start()
        self.csound.start_perf_thread()

        folder = self.csound.audio_dir.as_posix()
        sample = self.csound.sample_path.as_posix()

        # TODO: Turn on preprocess in config, and if it's done in preprocess write false to preprocess field in config.json
        # because we don't want to preprocess twice (it take at least 20 seconds to do so)
        if self.config.preprocess:
            preprocess(folder, sample, 40, 48)

        """This method is also run by the asyncio loop and periodically prints
        something.
        """
        try:
            while True:
                if self.root is not None:

                    # Selection of actions that the application can dispatch
                    #   Start or stop the recording depending on application state
                    if self.appStatus == "ToggleRecord" and not recording_status:
                        recording_status = True
                        record_task = asyncio.create_task(
                            self.audio.capture_and_playback(buffersize=256)
                        )

                    elif self.appStatus == "ToggleRecord" and recording_status:
                        record_task.cancel()
                        recording_status = not recording_status
                        # await asyncio.create_task(self.audio.saveVoice())

                    elif self.appStatus == "playSample":
                        pass
                        self.csound.play_sample()
                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices[
                        # 'out']))

                    elif self.appStatus == "midi_loaded":
                        if self.root.playing_midi:
                            self.csound.cleanup()
                            self.root.playing_midi = False
                            self.set_msg_txt("")
                        else:
                            if self.midi_file is None:
                                self.set_msg_txt(
                                    "Please drag and drop a .mid file here"
                                )
                            else:
                                self.csound.cleanup()
                                self.csound.play_midi_file(self.midi_file)
                                self.csound.set_output(self.output_idx)
                                r = self.csound.compile_and_start()
                                if r < 0:
                                    self.set_msg_txt(
                                        "Can't play that file, check file structure or create issue at GitHub repo"
                                    )
                                else:
                                    self.csound.start_perf_thread()
                                    self.set_msg_txt(f"Playing - {self.midi_file}")
                                self.root.playing_midi = True
                                self.midi_file = None
                                logger.debug(self.output_idx)

                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices['out']))

                self.appStatus = None

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
