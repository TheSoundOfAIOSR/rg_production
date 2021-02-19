import sys
import pyaudio
import wave

sys.path.append('.')


class Audio:

    def __init__(self):
        print("Instantiating PyAudio")
        self.audio = pyaudio.PyAudio()
        self.audio_devices = get_audio_devices(self.audio)


class VoiceRecorder_V2:

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
        self.device_index = 2

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
        # while True:
        #     data = self.stream.read(self.CHUNK)
        #     self.RecordFrames.append(data)
        # for i in range(0, int(self.RATE / self.CHUNK * 10)):
        # print("recording stopped")

    def recordStep(self, _):
        data = self.stream.read(self.CHUNK)
        self.RecordFrames.append(data)


def get_audio_devices(p):
    """Function to list system audio devices.
    Returns a dictionary of the current audio devices available and currently used

    Args:
        p (pyaudio.PyAudio): PyAudio instance.

    Returns:
        audio_device (dict): Dictionary of audio devices

    Structure of audio device dictionary:
    audio_device = {
        "in": "",
        "out": "",
        "devices": {
            "input_list": [],
            "output_list": []
        }
    }
    """
    audio_device = {
        "in": "",
        "out": "",
        "devices": {
            "input_list": [],
            "output_list": []
        }
    }

    input_list = []
    output_list = []

    info = p.get_host_api_info_by_index(0)
    numdevices = info.get('deviceCount')

    for i in range(numdevices):

        device = p.get_device_info_by_host_api_device_index(0, i)  # HOSTAPI 0

        if device["maxInputChannels"] > 0:
            input_list.append(device)

        if device["maxOutputChannels"] > 0:
            output_list.append(device)

    audio_device["in"] = p.get_default_input_device_info()
    audio_device["out"] = p.get_default_output_device_info()
    audio_device["devices"]["input_list"] = input_list
    audio_device["devices"]["output_list"] = output_list

    return audio_device
