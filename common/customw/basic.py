from kivy.uix.widget import Widget


class Graphics(Widget):

    def midi_text(self):
        self.parent.parent.ids.lab.text = 'please drag and drop a .mid file here'
