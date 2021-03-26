from kivy.uix.widget import Widget
from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty
from kivy.app import App


class Graphics(Widget):
    midi_file = StringProperty("")
    message_label = ObjectProperty(None)

    def __init__(self, **kwargs):
        Window.bind(on_dropfile=self._on_file_drop)
        super(Graphics, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def _on_file_drop(self, window, file_path):
        self.message_label.text = (
            self.midi_file
        ) = self.app.midi_file = file_path.decode()