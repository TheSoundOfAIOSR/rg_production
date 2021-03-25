from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty


class Graphics(Widget):

    midi_file = StringProperty("")

    def __init__(self, **kwargs):
        Window.bind(on_dropfile=self._on_file_drop)
        super(Graphics, self).__init__(**kwargs)

    def _on_file_drop(self, window, file_path):
        self.midi_file = file_path.decode()
