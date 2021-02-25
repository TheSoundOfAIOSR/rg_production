import kivy
kivy.require('2.0.0')

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.clock import Clock
import json

from Modules.Audio import Audio
from Modules.Recording import VoiceRecorder
from Modules.Playing import player
from Modules.Sampler import play_sample

class SamplerGUI(App):
    recording = False
    audio = Audio()
    voice = VoiceRecorder(audio.audio)
    devices = audio.devices
    print("Audio Devices: \n", json.dumps(devices, indent=4))
    recordTrigger = None

    def build(self):

        layout = GridLayout(rows=3, spacing=10, padding=40)

        topRow = GridLayout(cols=2, spacing=10)
        middleRow = GridLayout(cols=1)
        bottomRow = GridLayout(cols=1)

        # Sound Generation Box
        soundGenBox = GridLayout(cols=3, spacing=5)
        soundGenCol1 = GridLayout(rows=3, size_hint=(0.2, 0.2), pos_hint={'center_x': 0.5})
        # soundGenCol1.add_widget(Button())
        recordBtn = Button(text="Start/Stop Recording", pos_hint={'center_y': 0.5})
        recordBtn.bind(on_release=self.toggleRecording)
        soundGenCol1.add_widget(recordBtn)
        slidersCol = Button(text="Sliders")
        generateCol = Button(text="Generate", size_hint=(0.2, 0.2))
        generateCol.bind(on_release=self.generateSample)

        soundGenBox.add_widget(soundGenCol1)
        soundGenBox.add_widget(slidersCol)
        soundGenBox.add_widget(generateCol)

        ioBox = Button(text="I/O Box", size_hint=(0.25, 0.25))
        topRow.add_widget(soundGenBox)
        topRow.add_widget(ioBox)

        play_btn = Button(text="Play", size_hint=(0.8, 0.2))
        bottomRow.add_widget(play_btn)
        play_btn.bind(on_release=self.playRecording)

        # sampler = Button(text="Sampler")
        # looper = Button(text="Looper")
        # middleRow.add_widget(sampler)
        # bottomRow.add_widget(looper)

        layout.add_widget(topRow)
        layout.add_widget(middleRow)
        layout.add_widget(bottomRow)

        return layout

    def toggleRecording(self, event):

        if not self.recording:
            Clock.schedule_once(self.voice.startRecord, -1)
            self.recordTrigger = Clock.schedule_interval(self.voice.recordStep, 1.0 / 120.0)
        else:
            self.recordTrigger.cancel()
            Clock.schedule_once(self.voice.stopRecord, -1)

        self.recording = not self.recording

    def generateSample(self, event):
        print("Generating New Sample")
        play_sample()

    def playRecording(self, event):
        print("Playing recording:", self.voice.WAVE_OUTPUT_FILENAME)
        player(self.audio.audio, self.voice.WAVE_OUTPUT_FILENAME, self.devices["out"])
        print("Playing finished")



root = SamplerGUI()
root.run()
