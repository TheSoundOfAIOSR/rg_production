import sys

import librosa
import numpy as np
from scipy.io.wavfile import write
from common.config import Config
import common.log as log
import pathlib as pl
import multiprocessing as mp

logger = log.setup_logger()
config = Config.load_config()

target_sr = config.sampling_rate




def utility_pitchshift_and_normalize(audio, target_sr, n_steps, root, folder):
    audio_shifted = librosa.effects.pitch_shift(audio, target_sr, n_steps, bins_per_octave=12)
    new_filename = f"{root + n_steps}.wav"
    new_filepath = folder / pl.Path(new_filename)
    audio_shifted = audio_shifted.astype("float32")
    audio_norm = librosa.util.normalize(audio_shifted)
    write(new_filepath, target_sr, audio_norm)
    logger.debug(f"Creating: {new_filename}")
    logger.debug("==============================")


def preprocess(folder, filename, root=60, shifts=48):
    """
    Pitch shift of the audio file given as input and save in in the folder given as input

    Args:
        folder (str): path to folder where to save the pitch shifted audio
        filename (str): path to audio file to pitch-shift
        root (int, optional): root note of 'filename' sample
        shifts (int, optional): shift to apply. Defaults to 24.
    """
    logger.info("loading audio")
    audio, orig_sr = librosa.load(filename)
    audio = librosa.resample(audio, orig_sr, target_sr)

    logger.info("shifting pitch")

    folder = pl.Path(folder).absolute()


    pool = mp.pool.ThreadPool(mp.cpu_count())
    
    for n_steps in range(- (shifts//2), 1 + (shifts//2)):
        pool.apply_async(
            utility_pitchshift_and_normalize,
            (audio, target_sr, n_steps, root, folder)
        )
    
    pool.close()
    pool.join()

    logger.info(f"Audio files saved in folder: {folder}")
