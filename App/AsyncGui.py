'''Example shows the recommended way of how to run Kivy with the Python built
in asyncio event loop as just another async coroutine.
'''
import asyncio

from kivy.app import App
from kivy.lang.builder import Builder
from kivy.clock import Clock
import pyaudio
import wave

from Modules.AudioInterface import AudioInterface
from Modules.Sampler import CsoundSampler

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
        Button:
            id: btn2
            group: 'a'
            text: 'Play'
            on_press: app.testCallback('playSample')
    Label:
        id: label
        status: 'Not Recording'
        text: 'status is "{}"'.format(self.status)

    Spinner:
        size_hint: None, None
        size: 120, 44
        pos_hint: {'center': (.5, .5)}
        text: 'Audio In'
        values: [indev["name"] for indev in app.devices["devices"]["input_list"]]
        on_text:
            print("The spinner {} has text {}".format(self, self.text))

    Spinner:
        size_hint: None, None
        size: 120, 44
        pos_hint: {'center': (.5, .5)}
        text: 'Audio Out'
        values: [indev["name"] for indev in app.devices["devices"]["output_list"]]
        on_text:
            print("The spinner {} has text {}".format(self, self.text))
'''



class AsyncApp(App):

    other_task = None
    appStatus = None
    audio = AudioInterface()
    devices = audio.devices
    csound = CsoundSampler()

    def build(self):
        return Builder.load_string(kv)

    def testCallback(self, event):

        self.appStatus = event
        print("Set appStatus to ", self.appStatus)


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

    async def waste_time_freely(self):
        recordingStatus = False
        record_task = None

        self.csound.compileAndStart()
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
                        record_task = asyncio.create_task(self.audio.recording())
                    elif self.appStatus == "ToggleRecord" and recordingStatus:
                        record_task.cancel()
                        recordingStatus = not recordingStatus
                        print("cancelled recording")
                        await asyncio.create_task(self.audio.saveVoice())
                        print("Continuing main loop")
                    elif self.appStatus == "playSample":
                        self.csound.playSample()
                        # playback_task = asyncio.create_task(self.audio.player('recordedFile.wav', self.devices['out']))

                self.appStatus = None
                await asyncio.sleep(0.01)
        except asyncio.CancelledError as e:
            print('Wasting time was canceled', e)
        finally:
            # when canceled, print that it finished
            self.csound.cleanup() # csound cleanup function / destructor not sure where I should put it but needs to happen when closing the app
            print('Done wasting time')


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(AsyncApp().app_func())
    loop.close()
