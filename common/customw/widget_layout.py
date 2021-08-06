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
    '''
    SliderLayout is a widget being used to build multiple sliders to play around with latent space variables
    '''

    sliders = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SliderLayout, self).__init__(**kwargs)
        Clock.schedule_once(self.build_sliders)

        self.labels = {}

    def build_sliders(self, _):

        app = App.get_running_app().root.get_screen("graphics")

        variable = ["1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16"]
        slider_ids = {}
        label_map = {}

        for i in range(self.sliders):
            b = BoxLayout(orientation="vertical")
            s = Slider(orientation="vertical", min=-7, max=7, size_hint=(1, 0.8))
            s.bind(value=self.on_slider_change)
            b.add_widget(s)
            l = Label(text=str(s.value), font_size="12sp", size_hint=(1, 0.2))
            b.add_widget(l)
            b.children[0].bind()
            slider_ids[b.uid] = variable[i]
            label_map[s.uid] = l
            self.add_widget(b)

        app.slider_map = slider_ids
        app.label_map = label_map
        print(slider_ids)

    def on_slider_change(self, instance, value):
        app = App.get_running_app().root.get_screen("graphics")
        app.label_map[instance.uid].text = str(round(value, 3))

class LabelLayout(BoxLayout):
    '''
    LabelLayout is a widget being used to make multiple labels to label above sliders
    '''    
    
    labels = NumericProperty(0)

    def __init__(self, **kwargs):
        super(LabelLayout, self).__init__(**kwargs)
        # Clock.schedule_once(self.build_labels)

    def build_labels(self, _):
        for i in range(self.labels):
            self.add_widget(Label(text="0.5", font_size="12sp"))


class KeyboardWidget(BoxLayout):
    """
    Builds piano in boxlayout, float layout allows black keys to float over white keys, each key has an index
    """
    
    keys = NumericProperty(0)

    def __init__(self, **kwargs):
        super(KeyboardWidget, self).__init__(**kwargs)
        Clock.schedule_once(self.build_keys)
        self.app = App.get_running_app()
        self.keys_dict = {}
        self.keys_ind = 0

    def build_keys(self, _):

        white_key_width = 14
        black_key_width = 28

        octave_widget = FloatLayout()
        for i in range(self.keys):
            white_key_widget = Button(background_normal='assets/key_up.png',
                                      background_down='assets/key_down.png',
                                      size_hint=(1/white_key_width, 1), # here
                                      pos_hint={"x": i/white_key_width, "top": 1}) # here
            octave_widget.add_widget(white_key_widget)
            if i in [1, 2, 4, 5, 6, 8, 9, 11, 12, 13]:
                black_key_widget = (Button(background_normal='assets/key_up.png',
                                           background_down='assets/key_down.png',
                                           background_color=(0.3, 0.3, 0.3, 1),
                                           size_hint=(1 / black_key_width, 0.5),# here
                                           pos_hint={"x": (i / white_key_width) - 0.60 / black_key_width, "top": 1})) #here
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
        self.app.sm.dispatch('on_keyboard_press', ind)
        # self.keys_dict[ind] = True

    def on_key_released(self, ind, instance):
        # When button is released changes it state to False in dict
        pass
        # self.keys_dict[ind] = False
        # print(self.keys_dict)
