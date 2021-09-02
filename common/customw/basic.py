from kivy.core.window import Window
from kivy.uix.label import Label
from kivy.properties import StringProperty, ObjectProperty
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.popup import Popup
from kivy.uix.floatlayout import FloatLayout
from kivy.app import App
#from common.state.StateManager import audio
import os


class Graphics(Screen):
    midi_file = StringProperty("")
    message_label = ObjectProperty(None)


    def __init__(self, **kwargs):
        Window.bind(on_dropfile=self._on_file_drop)
        Window.bind(mouse_pos=self.mouse_pos)
        super(Graphics, self).__init__(**kwargs)
        self.app = App.get_running_app()

    def _on_file_drop(self, window, file_path):
        """
        allows user to drag and drop a midi file and updates status label text
        """
        self.midi_file = self.app.midi_file = file_path.decode()
        self.app.set_msg_txt(f"{self.midi_file} - has been loaded")

    def mouse_pos(self, window, pos):
        collide = False

        for slider in self.app.get_running_app().root.get_screen("graphics").ids['some_slider1'].children:
            if slider.collide_point(*pos):
                collide = True
                mapping = self.app.get_running_app().root.get_screen("graphics").heuristic_slider_ids[slider.uid]
                self.app.get_running_app().root.get_screen("graphics").ids['latent_space_label'].text = f"Heuristic Parameter: {mapping}"
                return

        for slider in self.app.get_running_app().root.get_screen("graphics").ids['some_slider'].children:
            if slider.collide_point(*pos):
                collide = True
                mapping = self.app.get_running_app().root.get_screen("graphics").latent_slider_ids[slider.uid]
                self.app.get_running_app().root.get_screen("graphics").ids['latent_space_label'].text = f"Latent Parameter: {mapping}"
                return



        if not collide:
            self.app.get_running_app().root.get_screen("graphics").ids['latent_space_label'].text = f"Latent space variables"


class SaveDialog(FloatLayout):
    save = ObjectProperty(None)
    text_input = ObjectProperty(None)
    cancel = ObjectProperty(None)


class Settings(Screen):
    savefile = ObjectProperty(None)
    text_input = ObjectProperty(None)

    def dismiss_popup(self):
        self._popup.dismiss()

    def show_save(self):
        content = SaveDialog(save=self.save, cancel=self.dismiss_popup)
        self._popup = Popup(title="Save file", content=content,
                            size_hint=(0.9, 0.9))
        self._popup.open()

    def save(self, path, filename):  # TODO Rewrite this to save generated wav file
        # with open(os.path.join(path, filename), 'w') as stream:
        #     stream.write(self.text_input.text)
        with open(os.path.join(path, filename), 'w') as stream:
            stream.write(audio)
            stream.close()

        self.dismiss_popup()
