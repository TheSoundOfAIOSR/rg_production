import queue
import numpy as np
import sounddevice as sd

import asyncio
import wave
from typing import *
import common.log as log
from common.config import Config

logger = log.setup_logger()


class AudioInterface:
    def __init__(self):

        self.devices = self.get_audio_devices()
        self.input_devices = None
        self.output_devices = None
        self.input_idx = sd.default.device[0]

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
            # if not out_queue.empty: # This call seems to cause microphone input to not be picked up
            outdata[:] = out_queue.get_nowait()

        # pre-fill output queue
        for _ in range(pre_fill_blocks):
            out_queue.put(np.zeros((buffersize, channels), dtype=dtype))

        stream = sd.Stream(
            # device = self.input_idx, # This should work but it hangs if this is uncommented
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
                logger.debug(status)
            out_data[:] = in_data


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

        try:
            audio_device["in"] = sd.query_devices(kind="input")
        except sd.PortAudioError:
            pass  # TODO: make label say "no audio input found, please insert a mic"
        finally:
            audio_device["out"] = sd.query_devices(kind="output")
            audio_device["devices"]["input_list"] = input_list
            audio_device["devices"]["output_list"] = output_list
            i = 0
            for dev in output_list:
                dev["id"] = i
                i += 1

            return audio_device