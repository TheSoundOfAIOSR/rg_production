import os

class Config():

    def __init__(self):

        # folder and file path configuration
        self.working_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.audio_dir = os.path.join(self.working_dir, 'generated_sample')
        
        if "\\" in self.audio_dir:
          self.audio_dir = self.audio_dir.replace("\\", "/")
        
        self.sample = "e2.wav"
        # self.sample_path = os.path.join(self.audio_dir, self.sample)
        # self.sample_path = self.audio_dir + ‘ / ’ + sample
        self.sample_path = self.audio_dir + '/' + self.sample
        # audio interface configuration
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"

        # preprocessing sample configuration
        self.target_sr = 44100