import sys
sys.path.append('.')
import asyncio
import pyaudio
import wave

class AudioInterface:

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.stream = None
        self.RecordFrames = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"
        self.device_index=2


    async def recording(self):
        self.stream = self.audio.open(format=self.FORMAT, channels=self.CHANNELS,
                                      rate=self.RATE, input=True, input_device_index=1,
                                      frames_per_buffer=self.CHUNK)
        self.RecordFrames = []
        while True:
            data = self.stream.read(self.CHUNK, exception_on_overflow=False)
            self.RecordFrames.append(data)
            await asyncio.sleep(0.0001)

    async def saveVoice(self):

        self.stream.stop_stream()
        self.stream.close()

        waveFile = wave.open(self.WAVE_OUTPUT_FILENAME, 'wb')
        waveFile.setnchannels(self.CHANNELS)
        waveFile.setsampwidth(self.audio.get_sample_size(self.FORMAT))
        waveFile.setframerate(self.RATE)
        waveFile.writeframes(b''.join(self.RecordFrames))
        waveFile.close()
