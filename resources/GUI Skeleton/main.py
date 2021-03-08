from kivy.app import App
from kivy.uix.widget import Widget
from kivy.garden.knob import Knob
from kivy.config import Config
Config.set('graphics', 'resizable', False)
from kivy.core.window import Window
Window.clearcolor = (.30, .30, .30, 1)

# Graphics is a placeholder for the class which imports layout from .kv file
class Graphics(Widget):
    pass

# Skeleton is a placeholder for the main App which will be run
class SkeletonApp(App):
    def build(self):
        return Graphics()

SkeletonApp().run()
