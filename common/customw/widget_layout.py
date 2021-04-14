from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.slider import Slider
from kivy.uix.label import Label
from functools import partial
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
            self.add_widget(Slider(orientation="vertical", min=-7, max=7))


class LabelLayout(BoxLayout):
    labels = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LabelLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.build_labels)

    def build_labels(self, _):
        for i in range(self.labels):
            self.add_widget(Label(text="A"))


class KeyboardWidget(BoxLayout):
    keys = NumericProperty(0)

    def __init__(self, **kwargs):
        super(KeyboardWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.build_keys)
        self.keys_dict = {}
        self.keys_ind = 0

    def build_keys(self, _):

        octave_widget = FloatLayout()
        for i in range(self.keys):
            white_key_widget = Button(background_normal='assets/key_up.png',
                                          background_down='assets/key_down.png', size_hint=(1.0, 1.0), pos_hint={"x": i / 7, "top": 1})
            octave_widget.add_widget(white_key_widget)
            if i in [1, 2, 4, 5, 6, 8, 9, 11, 12, 13]:
                black_key_widget = (Button(background_normal='assets/key_up.png',
                                          background_down='assets/key_down.png',
                                          background_color=(0.3, 0.3, 0.3, 1),
                                          size_hint=(1 / 14, 0.5),
                                          pos_hint={"x": i / 7 - 1 / 14, "top": 1}))
                octave_widget.add_widget(black_key_widget)
                black_key_widget.bind(on_press=partial(self.on_key_pressed, self.keys_ind),
                                      on_release=partial(self.on_key_released, self.keys_ind))
                self.keys_dict[self.keys_ind] = False
                self.keys_ind += 1

            white_key_widget.bind(on_press=partial(self.on_key_pressed, self.keys_ind),
                                  on_release=partial(self.on_key_released, self.keys_ind))
            self.keys_dict[self.keys_ind] = False
            self.keys_ind += 1
        self.add_widget(octave_widget)

    def on_key_pressed(self, ind, instance):
        # When button is pressed changes it state to True in dict
        self.keys_dict[ind] = True
        print(self.keys_dict)

    def on_key_released(self, ind, instance):
        # When button is released changes it state to False in dict
        self.keys_dict[ind] = False
        print(self.keys_dict)