import sys
sys.path.append('.')

import asyncio
import queue
import numpy as np
import sounddevice as sd
import soundfile as sf

import asyncio
import pyaudio
import wave

class AudioInterface:

    def __init__(self):
        self.audio = pyaudio.PyAudio()
        self.devices = self.get_audio_devices()
        self.stream = None
        self.RecordFrames = None
        self.FORMAT = pyaudio.paInt16
        self.CHANNELS = 1
        self.RATE = 44100
        self.CHUNK = 512
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"
        self.device_index=2

    async def capture_and_play(self, buffersize, *, channels=1, dtype='float32',
                               pre_fill_blocks=10, **kwargs):
        """Generator that yields blocks of input/output data as NumPy arrays.

        The output blocks are uninitialized and have to be filled with
        appropriate audio signals.

        """
        assert buffersize != 0
        in_queue = asyncio.Queue()
        out_queue = queue.Queue()
        loop = asyncio.get_event_loop()

        """
        callback(indata: ndarray, outdata: ndarray, frames: int,
             time: CData, status: CallbackFlags) -> None
        """

        def callback(indata, outdata, frame_count, time_info, status):
            loop.call_soon_threadsafe(in_queue.put_nowait, (indata.copy(), status))
            outdata[:] = out_queue.get_nowait()

        # pre-fill output queue
        for _ in range(pre_fill_blocks):
            out_queue.put(np.zeros((buffersize, channels), dtype=dtype))

        stream = sd.Stream(blocksize=buffersize, callback=callback, dtype=dtype,
                           channels=channels, **kwargs)
        with stream:
            while True:
                indata, status = await in_queue.get()
                outdata = np.empty((buffersize, channels), dtype=dtype)
                yield indata, outdata, status
                out_queue.put_nowait(outdata)

    async def capture_and_playback(self, **kwargs):
        """Create a connection between audio inputs and outputs.

        Asynchronously iterates over a stream generator and for each block
        simply copies the input data into the output block.

        """
        async for indata, outdata, status in self.capture_and_play(**kwargs):
            if status:
                print(status)
            outdata[:] = indata

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


    async def player(self, audio_file: str, output_device: dict):
        """
        Function to play audio with a callback implementation
        Args:
            audio_file (str): Path of the audio file
            output_device (dict): current audio devices

        Returns:

        """
        wf = wave.open(audio_file, 'rb')

        # instantiate PyAudio (1)
        p = self.audio

        # define callback (2)
        def callback(in_data, frame_count, time_info, status):
            data = wf.readframes(frame_count)
            return data, pyaudio.paContinue

        # open stream using callback (3)
        stream = p.open(
            format=p.get_format_from_width(wf.getsampwidth()),
            channels=wf.getnchannels(),
            rate=wf.getframerate(),
            output=True,
            output_device_index=output_device["index"],
            stream_callback=callback
        )

        # start the stream (4)
        stream.start_stream()

        # wait for stream to finish (5)
        while stream.is_active():
            await asyncio.sleep(0.1)

        # stop stream (6)
        stream.stop_stream()
        stream.close()
        wf.close()

        # close PyAudio (7)
        # p.terminate()

    def get_audio_devices(self):
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

        info = self.audio.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')

        for i in range(numdevices):

            device = self.audio.get_device_info_by_host_api_device_index(0, i)  # HOSTAPI 0

            if device["maxInputChannels"] > 0:
                input_list.append(device)

            if device["maxOutputChannels"] > 0:
                output_list.append(device)

        audio_device["in"] = self.audio.get_default_input_device_info()
        audio_device["out"] = self.audio.get_default_output_device_info()
        audio_device["devices"]["input_list"] = input_list
        audio_device["devices"]["output_list"] = output_list

        return audio_device
