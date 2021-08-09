import sys

import librosa
from scipy.io.wavfile import write
from common.config import Config
import common.log as log
import pathlib as pl
import multiprocessing as mp
from kivy.app import App
import matplotlib.pyplot as plt

logger = log.setup_logger()
config = Config.load_config()

target_sr = config.sampling_rate
app = App.get_running_app

def utility_pitchshift_and_normalize(audio, target_sr, note, folder):
    """
    Given an audio file as numpy array,
    a target sample rate,
    a step number name n,
    a root note (midi)
    and a folder path:

    Pitch shifts the file n steps at the defined sample rate
    Normalizes the audio
    Saves it in a file in the format  root+n.wav
    """
    # audio_shifted = librosa.effects.pitch_shift(audio, target_sr, n_steps, bins_per_octave=12)
    new_filename = f"{note}.wav"
    new_filepath = folder / pl.Path(new_filename)
    audio_shifted = audio.astype("float32")
    audio_norm = librosa.util.normalize(audio_shifted)
    write(new_filepath, target_sr, audio_norm)
    logger.debug(f"Creating: {new_filename}")
    logger.debug("==============================")

def wavfunc(audio):  # as soon as Generate is pressed, trigger this function. note is generated wav
    # data, samplerate = sf.read(note.wav, dtype='float32')  # dtype change to avoid error
    # times = np.arange(len(audio)) / float(samplerate)   # avoid soundfile and work with available libs?
    logger.debug(f"in wavfunc 1")
    plt.figure(figsize=(15,3), dpi=96)

    plt.gca().set_axis_off()
    plt.margins(0, 0)
    plt.subplots_adjust(top=1, bottom=0, right=1, left=0, hspace=0, wspace=0)
    logger.debug(f"in wavfunc 2")

    plt.plot(audio, color='white')
    logger.debug(f"in wavfunc 3")

    # TODO Pass path
    import os
    # os.path.join()
    path = pl.Path('assets\\plot.png').absolute()
    print(path)
    print(os.path.exists(path))
    plt.savefig(path, transparent=True, dpi=96,
                bbox_inches='tight', pad_inches=0)
    app.get_running_app().root.get_screen("graphics").ids.plot.reload()
    logger.debug(f"in wavfunc 4")

def preprocess(csound, folder, audio=None, filename=None, note=60, shifts=48):
    """
    Pitch shift of the audio file given as input and save in in the folder given as input

    Args:
        folder (str): path to folder where to save the pitch shifted audio
        filename (str): path to audio file to pitch-shift
        root (int, optional): root note of 'filename' sample
        shifts (int, optional): shift to apply. Defaults to 24.
    """
    logger.debug(f"{audio}")
    logger.debug(f"loading audio")
    logger.debug(f"{folder}")
    logger.debug(f"target_sr = {target_sr}")
    # audio, orig_sr = librosa.load(filename)
    audio = librosa.resample(audio, 16000, target_sr)
    wavfunc(audio)
    csound.duration = len(audio)/target_sr
    
    logger.debug(f"shifting pitch")

    folder = pl.Path(folder).absolute()
    utility_pitchshift_and_normalize(audio, target_sr, note, folder)

    # pool = mp.pool.ThreadPool(mp.cpu_count())
    #
    # for n_steps in range(- (shifts//2), 1 + (shifts//2)):
    #     pool.apply_async(
    #         utility_pitchshift_and_normalize,
    #         (audio, target_sr, n_steps, root, folder)
    #     )
    #
    # pool.close()
    # pool.join()

    logger.debug(f"Audio files saved in folder: {folder}")
