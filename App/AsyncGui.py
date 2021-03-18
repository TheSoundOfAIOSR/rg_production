'''Example shows the recommended way of how to run Kivy with the Python built
in asyncio event loop as just another async coroutine.
'''
import asyncio
import pyaudio
import wave

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.clock import Clock
from kivy.garden.knob import Knob
from kivy.core.audio import SoundLoader
from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.tabbedpanel import TabbedPanel
from kivy.lang import Builder
from kivy.uix.popup import Popup
from kivy.config import Config
Config.set('graphics', 'resizable', False)

from Modules.AudioInterface import AudioInterface
from Modules.Sampler import CsoundSampler
# from Modules.PreprocessingSample import pitchshift

# from Modules.testSampler import CsoundSampler

class AsyncApp(App):
    other_task = None
    appStatus = None
    midi_status = None
    audio = AudioInterface()
    devices = audio.devices
    output_idx=0
    csound = CsoundSampler()

    def build(self):
        return Graphics()

    def nextEvent(self, event):

        self.appStatus = event
        print("Set appStatus to ", self.appStatus)

    def select_audio_device(self, event):
        selected_device = event

        # will work for now but need to improve, soething more robust
        # TODO: improve the implementation maybe with regex
        selected_idx = int(selected_device.split("[")[1].split("]")[0])
        
        '''
        Audio device in form: 
        "[0]>Sound device name-->>in/out_device", 
        to extract just "Sound device name"...
        '''
        dev = selected_device.split("]>")[1].split("-->>")[0] # just the device name
        input_idx = None
        output_idx = None
        
        # handling input
        if "-->>input_device" in selected_device:
            input_list = self.devices["devices"]["input_list"]
            for indev in input_list:
                if dev in indev.values():
                    input_idx = selected_idx
                    self.devices["in"] = indev
                    print(self.devices["in"])
                    print(f"Csound index: {input_idx}, {type(input_idx)}")

        # handling output
        if "-->>output_device" in selected_device:
            output_list = self.devices["devices"]["output_list"]
            for outdev in output_list:
                if dev in outdev.values():
                    self.output_idx = selected_idx
                    self.devices["out"] = outdev
                    self.csound.cleanup()
                    self.csound.set_output(self.output_idx)
                    self.csound.compile_and_start()
                    print(self.devices["out"])
                    print(f"Csound index: {output_idx}, {type(output_idx)}")

        print(selected_device)

    def app_func(self):
        '''This will run both methods asynchronously and then block until they
        are finished
        '''

        self.other_task = asyncio.ensure_future(self.main_loop())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run(async_lib='asyncio')
            self.csound.cleanup() # before terminating the app, do the cleanup for Csound 
            print('App done')
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)

    async def main_loop(self):
        recordingStatus = False
        record_task = None
        filechooser = Graphics()

        self.csound.set_output(self.output_idx)
        # self.csound.set_midi()
        self.csound.compile_and_start()
        
        sample = self.csound.sample_path

        # pitchshift(self.csound.audio_dir,sample, 24)
        '''This method is also run by the asyncio loop and periodically prints
        something.
        '''
        try:
            i = 0
            while True:
                if self.root is not None:

                    # Selection of actions that the application can dispatch
                    #   Start or stop the recording depending on application state
                    if self.appStatus == "ToggleRecord" and not recordingStatus:
                        recordingStatus = True
                        record_task = asyncio.create_task(self.audio.capture_and_playback(buffersize=256))

                    elif self.appStatus == "ToggleRecord" and recordingStatus:
                        record_task.cancel()
                        recordingStatus = not recordingStatus
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
                        print("here")
                        self.csound.cleanup()
                        self.csound.set_output(self.output_idx)
                        self.csound.play_midi_file(self.midi_file)
                        self.csound.compile_and_start()
                        self.midi_status = None
                        filechooser.midi_file = None

                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices['out']))

                self.appStatus = None

                await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            print('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            print('Done wasting time')

class FileChoosePopup(Popup):
    load = ObjectProperty()

class Graphics(Widget):
    midi_path = StringProperty("No file chosen")
    the_popup = ObjectProperty(None)
    midi_file = None

    def open_popup(self):
        self.the_popup = FileChoosePopup(load=self.load)
        self.the_popup.open()

    def load(self, selection):
        self.midi_file = str(selection[0])
        self.the_popup.dismiss()
        #return midi_file somewhere outside into the main app




if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncApp().app_func())
    loop.close()
