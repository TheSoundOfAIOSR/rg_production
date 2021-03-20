from kivy.uix.boxlayout import BoxLayout
from kivy.uix.slider import Slider
from kivy.properties import ObjectProperty, StringProperty, NumericProperty
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ConfigParserProperty, ConfigParser
from kivy.clock import Clock


class SliderLayout(BoxLayout):
    """
    SliderLayout is widget that being used to make multiple sliders
    """

    sliders = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SliderLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.build_sliders)

    def build_sliders(self, _):
        for i in range(self.sliders):
            self.add_widget(Slider(orientation="vertical", min=0, max=1))
