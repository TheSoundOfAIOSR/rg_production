import asyncio

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.garden.knob import Knob
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, StringProperty
from kivy.core.window import Window
from kivy.uix.popup import Popup
from kivy.config import Config

from customw.basic import *
from customw.slider_layout import *

from taudio.AudioInterface import AudioInterface
from taudio.MidiInterface import MidiInterface
from taudio.Sampler import CsoundSampler
from taudio.PreprocessingSample import pitchshift
from config.Configuration import *

import logging

formatter = logging.Formatter(
    fmt="%(asctime)s - %(levelname)s - %(module)s - %(message)s"
)

handler = logging.StreamHandler()
handler.setFormatter(formatter)
config = Config()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)


class ProdApp(App):
    other_task = None
    appStatus = None
    midi_status = None
    midi = MidiInterface()
    midi_devices = midi.devices
    audio = AudioInterface()
    devices = audio.devices
    csound = CsoundSampler(config.audio_dir, config.sample_path)
    output_idx = 0
    midi_input_idx = 0

    def build(self):
        Window.bind(on_dropfile=self._on_file_drop)
        return Graphics()

    def _on_file_drop(self, window, file_path):
        print(file_path)
        # pass file_path to md player which triggers on_press play button of popup

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

    def select_audio_device(self, slider_obj, event):

        # will work for now but need to improve, soething more robust
        # TODO: improve the implementation maybe with regex
        selected_idx = int(event.split("[")[1].split("]")[0])
        """
        Audio device in form: 
        "0/1/M <device_name>", 
        to extract just <device_name>...
        """
        io = slider_obj.name
        dev = event.split('>')[-1]  # just the device name

        # handling input
        if io == "input":
            input_list = self.devices["devices"]["input_list"]
            for in_dev in input_list:
                if dev == in_dev.get("name", None):
                    input_idx = in_dev["hostapi"]
                    self.devices["in"] = in_dev
                    logger.debug(self.devices["in"])
                    logger.debug(f"Csound index: {input_idx}, {type(input_idx)}")
        # handling output
        elif io == "output":
            output_list = self.devices["devices"]["output_list"]
            for out_dev in output_list:
                if dev == out_dev.get("name", None):
                    self.output_idx = selected_idx
                    self.devices["out"] = out_dev
                    self.csound.cleanup()
                    self.csound.set_output(self.output_idx)
                    self.csound.set_midi_api()
                    self.csound.compile_and_start()
            logger.debug(self.devices["out"])
            logger.debug(
                f"Csound index: {self.output_idx}, {type(self.output_idx)}"
            )

        elif io == "midi_input":
            self.midi_input_idx = self.midi_devices["input"].index(dev)
            self.csound.cleanup()
            self.csound.set_output(self.output_idx)
            self.csound.set_midi(self.midi_input_idx)
            self.csound.compile_and_start()
            logger.debug(
                "MIDI device selected: ",
                self.midi_devices["input"][self.midi_input_idx],
            )
            logger.debug(f"Using API: {self.midi_devices['api']}")

            logger.debug(dev)


    # def select_midi_device(self, event):
    #     selected_device = event
    #     """
    #     selected_device in the form:
    #     [idx]"Midi device nane"
    #     """
    #     # TODO: improve implementation, maybe with regex
    #     selected_idx = int(selected_device.split("[")[1].split("]")[0])
    #
    #     self.midi_input_idx = selected_idx
    #
    #     print("MIDI device selected: ", self.midi_devices["input"][self.midi_input_idx])
    #     print(f"Using API: {self.midi_devices['api']}")
    #     print(f"{self.output_idx}")
    #     self.csound.cleanup()
    #     self.csound.set_output(self.output_idx)
    #     self.csound.set_midi(self.midi_input_idx)
    #     self.csound.compile_and_start()


#     def app_func(self):
#         '''This will run both methods asynchronously and then block until they
#         are finished
#         '''
#
#         self.other_task = asyncio.ensure_future(self.main_loop())
#
#         async def run_wrapper():
#             # we don't actually need to set asyncio as the lib because it is
#             # the default, but it doesn't hurt to be explicit
#             await self.async_run(async_lib='asyncio')
#             self.csound.cleanup()  # before terminating the app, do the cleanup for Csound
#             print('App done')
#             self.other_task.cancel()
#
#         return asyncio.gather(run_wrapper(), self.other_task)
# =======
#
# >>>>>>> 736ca7f56113552adc5d8743751ee2a5ac896ec7:src/main.py

    async def main_loop(self):
        recording_status = False
        record_task = None
        filechooser = Graphics()

        self.csound.set_output(self.output_idx)
        self.csound.set_midi_api()
        self.csound.compile_and_start()

        sample = self.csound.sample_path

        # pitchshift(self.csound.audio_dir, sample, 24)
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
                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices['out']))

                    elif self.appStatus == "open_popup":
                        filechooser.open_popup()
                        self.midi_status = "load_midi_wait"

                    elif self.midi_status == "load_midi_wait":
                        if filechooser.midi_file != None:
                            self.midi_status = "load_midi"
                            self.midi_file = filechooser.midi_file

                    elif self.midi_status == "load_midi":
                        logging.debug("here")
                        self.csound.cleanup()
                        self.csound.play_midi_file(self.midi_file)
                        self.csound.set_output(0)
                        self.csound.compile_and_start()
                        self.midi_status = None
                        filechooser.midi_file = None
                        print(self.output_idx)

                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices['out']))

                self.appStatus = None

                await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            logger.error(f"Wasting time was canceled", exc_info=e)
        finally:
            # when canceled, print that it finished
            logger.debug("Application closed")

#
# class FileChoosePopup(Popup):
#     load = ObjectProperty()
#
#
# class Graphics(Widget):
#     midi_path = StringProperty("No file chosen")
#     the_popup = ObjectProperty(None)
#     midi_file = None
#
#     def open_popup(self):
#         self.the_popup = FileChoosePopup(load=self.load)
#         self.the_popup.open()
#
#     def load(self, selection):
#         self.midi_file = str(selection[0])
#         self.the_popup.dismiss()
#
# =======
#             logger.debug("Done wasting time")
# >>>>>>> 736ca7f56113552adc5d8743751ee2a5ac896ec7:src/main.py
#

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(ProdApp().startup())
    loop.close()