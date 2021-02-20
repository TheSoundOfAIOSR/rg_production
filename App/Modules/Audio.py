import sys
import pyaudio

sys.path.append('.')


class Audio:

    def __init__(self):
        print("Instantiating PyAudio")
        self.audio = pyaudio.PyAudio()
        self.devices = get_audio_devices(self.audio)


def get_audio_devices(p: pyaudio.PyAudio) -> dict:
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
