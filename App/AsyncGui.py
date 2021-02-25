'''Example shows the recommended way of how to run Kivy with the Python built
in asyncio event loop as just another async coroutine.
'''
import asyncio

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock
import pyaudio
import wave

kv = '''
BoxLayout:
    orientation: 'vertical'
    BoxLayout:
        Button:
            id: btn1
            group: 'a'
            text: 'Recording'
            on_press: app.testCallback('ToggleRecord')
            on_state: if self.state == 'down': label.status = self.text
    Label:
        id: label
        status: 'Not Recording'
        text: 'status is "{}"'.format(self.status)
'''



class AsyncApp(App):

    other_task = None
    appStatus = None

    def build(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.RecordFrames = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"
        self.device_index=2

        return Builder.load_string(kv)

    def testCallback(self, event):

        self.appStatus = event
        print("Set appStatus to ", self.appStatus)

    async def saveVoice(self):

        self.stream.stop_stream()
        self.stream.close()
        # self.audio.terminate()

        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.RecordFrames))
        waveFile.close()

        print("Finished saving")


    def app_func(self):
        '''This will run both methods asynchronously and then block until they
        are finished
        '''

        self.other_task = asyncio.ensure_future(self.waste_time_freely())

        async def run_wrapper():
            # we don't actually need to set asyncio as the lib because it is
            # the default, but it doesn't hurt to be explicit
            await self.async_run(async_lib='asyncio')
            print('App done')
            self.other_task.cancel()

        return asyncio.gather(run_wrapper(), self.other_task)

    async def recording(self):
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True, input_device_index=1,
                                      frames_per_buffer=self.CHUNK)
        self.RecordFrames = []
        while True:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.RecordFrames.append(data)
            await asyncio.sleep(0.0001)

            #
            # print("Recording Voice")
        # return

    async def waste_time_freely(self):
        recordingStatus = False
        record_task = None
        '''This method is also run by the asyncio loop and periodically prints
        something.
        '''
        try:
            i = 0
            while True:
                if self.root is not None:
                    # appStatus = self.root.ids.label.status
                    if self.appStatus == "ToggleRecord" and not recordingStatus:
                        recordingStatus = True
                        print("Launch record thread")
                        record_task = asyncio.create_task(self.recording())
                        # print(dir(record_task))
                        # record_future = asyncio.ensure_future(self.recording())
                    elif self.appStatus == "ToggleRecord" and recordingStatus:
                        record_task.cancel()
                        recordingStatus = not recordingStatus
                        print("cancelled recording")
                        await asyncio.create_task(self.saveVoice())
                        print("Continuing main loop")

                self.appStatus = None
                await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            print('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            print('Done wasting time')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncApp().app_func())
    loop.close()
