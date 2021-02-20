import pyaudio
import wave
import time


def player(audio: pyaudio.PyAudio, audio_file: str, output_device: dict):
    """
    Function to play audio with a callback implementation
    Args:
        audio (pyaudio.PyAudio): PyAudio instance.
        audio_file (str): Path of the audio file
        output_device (dict): current audio devices

    Returns:

    """
    wf = wave.open(audio_file, 'rb')

    # instantiate PyAudio (1)
    p = audio

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
        output_device_index=output_device["out"]["index"],
        stream_callback=callback
    )

    # start the stream (4)
    stream.start_stream()

    # wait for stream to finish (5)
    while stream.is_active():
        time.sleep(0.1)

    # stop stream (6)
    stream.stop_stream()
    stream.close()
    wf.close()

    # close PyAudio (7)
    # p.terminate()
