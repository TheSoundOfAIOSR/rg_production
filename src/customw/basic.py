from kivy.properties import ObjectProperty, StringProperty
from kivy.uix.popup import Popup
from kivy.uix.widget import Widget


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