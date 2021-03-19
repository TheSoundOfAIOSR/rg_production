import sys

sys.path.append(".")

import queue
import numpy as np
import sounddevice as sd

import asyncio
import pyaudio
import wave
from typing import *
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class AudioInterface:
    def __init__(self):

        self.devices = self.get_audio_devices()
        self.input_devices = None
        self.output_devices = None
        self.WAVE_OUTPUT_FILENAME = "recordedFile.wav"
        # self.device_index=2

    async def capture_and_play(
        self,
        buffersize=256,
        *,
        channels=1,
        dtype="float32",
        pre_fill_blocks=10,
        **kwargs
    ):
        """Generator that yields blocks of input/output data as NumPy arrays.

        The output blocks are uninitialized and have to be filled with
        appropriate audio signals.
        -- by Tibor Kiss

        """
        assert buffersize != 0
        in_queue = asyncio.Queue()
        out_queue = queue.Queue()
        loop = asyncio.get_event_loop()

        """
        callback(indata: ndarray, outdata: ndarray, frames: int,
             time: CData, status: CallbackFlags) -> None
        """

        def callback(in_data, outdata, frame_count, time_info, status):
            loop.call_soon_threadsafe(in_queue.put_nowait, (in_data.copy(), status))
            if not out_queue.empty:
                outdata[:] = out_queue.get_nowait()

        # pre-fill output queue
        for _ in range(pre_fill_blocks):
            out_queue.put(np.zeros((buffersize, channels), dtype=dtype))

        stream = sd.Stream(
            blocksize=buffersize,
            callback=callback,
            dtype=dtype,
            channels=channels,
            **kwargs
        )
        with stream:
            while True:
                in_data, status = await in_queue.get()
                out_data = np.empty((buffersize, channels), dtype=dtype)
                yield in_data, out_data, status
                out_queue.put_nowait(out_data)

    async def capture_and_playback(self, **kwargs):
        """Create a connection between audio inputs and outputs.

        Asynchronously iterates over a stream generator and for each block
        simply copies the input data into the output block.
        -- by Tibor Kiss

        """
        async for in_data, out_data, status in self.capture_and_play(**kwargs):
            if status:
                print(status)
            out_data[:] = in_data

    # async def player(self, audio_file: str, output_device: dict):
    #     """
    #     Function to play audio with a callback implementation
    #     Args:
    #         audio_file (str): Path of the audio file
    #         output_device (dict): current audio devices
    #
    #     Returns:
    #
    #     """
    #     wf = wave.open(audio_file, 'rb')
    #
    #     # instantiate PyAudio (1)
    #     p = self.audio
    #
    #     # define callback (2)
    #     def callback(in_data, frame_count, time_info, status):
    #         data = wf.readframes(frame_count)
    #         return data, pyaudio.paContinue
    #
    #     # open stream using callback (3)
    #     stream = p.open(
    #         format=p.get_format_from_width(wf.getsampwidth()),
    #         channels=wf.getnchannels(),
    #         rate=wf.getframerate(),
    #         output=True,
    #         output_device_index=output_device["index"],
    #         stream_callback=callback
    #     )
    #
    #     # start the stream (4)
    #     stream.start_stream()
    #
    #     # wait for stream to finish (5)
    #     while stream.is_active():
    #         await asyncio.sleep(0.1)
    #
    #     # stop stream (6)
    #     stream.stop_stream()
    #     stream.close()
    #     wf.close()
    #
    #     # close PyAudio (7)
    #     # p.terminate()

    def get_audio_devices(self) -> Dict[str, Any]:
        # TODO: change docstring
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
            "devices": {"input_list": [], "output_list": []},
        }

        input_list = []
        output_list = []

        devices = sd.query_devices()
        for _id, device in enumerate(devices):
            if device["hostapi"] != 0:
                continue
            device["id"] = _id
            input_list.append(device) if device["max_input_channels"] > device[
                "max_output_channels"
            ] else output_list.append(device)

        audio_device["in"] = sd.query_devices(kind="input")
        audio_device["out"] = sd.query_devices(kind="output")
        audio_device["devices"]["input_list"] = input_list
        audio_device["devices"]["output_list"] = output_list

        return audio_device
