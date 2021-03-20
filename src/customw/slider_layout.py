from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty, StringProperty
from kivy.app import App
from kivy.uix.widget import Widget


class SliderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super(SliderLayout, self).__init__(**kwargs)
        self.build_sliders()

    def build_sliders(self):
        for i in range(8):
            self.add_widget(Slider(orientation="vertical", min=0, max=1))
