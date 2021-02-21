import sys
sys.path.append('.')
import pyaudio
import wave

class VoiceRecorder:

    def __init__(self, audio):
        # print("Instantiating PyAudio")
        self.audio = audio
        self.stream = None
        self.RecordFrames = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"
        self.device_index=2


    def stopRecord(self, _):
        print("stopped recording")
        self.stream.stop_stream()
        self.stream.close()
        # self.audio.terminate()

        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.RecordFrames))
        waveFile.close()

    def startRecord(self, _):

        ''' this piece of code lets you pick your device from the list of available ones.
        print("----------------------record device list---------------------")
        info = audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        for i in range(0, numdevices):
                if (audio.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    print("Input Device id ", i, " - ", audio.get_device_info_by_host_api_device_index(0, i).get('name'))
        
        print("-------------------------------------------------------------")
        
        index = int(input())
        print("recording via index "+str(index))
        '''
        print("Recording started")
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                            rate=self.RATE, input=True, input_device_index=1,
                            frames_per_buffer=self.CHUNK)
        self.RecordFrames = []


    def recordStep(self, _):
        data = self.stream.read(self.CHUNK, exception_on_overflow = False)
        self.RecordFrames.append(data)

