import sys

import librosa
import numpy as np
import pyrubberband as pyrb  # pitch shifting
from pydub import AudioSegment, effects  # amplitude normalization
from scipy.io.wavfile import write
from common.config import Config
import common.log as log
import pathlib as pl

logger = log.setup_logger()
config = Config.load_config()

target_sr = config.sampling_rate

# https://stackoverflow.com/questions/42492246/how-to-normalize-the-volume-of-an-audio-file-in-python-any-packages-currently-a
def match_target_amplitude(sound, target_dBFS):
    change_in_dBFS = target_dBFS - sound.dBFS
    return sound.apply_gain(change_in_dBFS)


def pitchshift(folder, filename, shifts=24):
    """
    Pitch shift of the audio file given as input and save in in the folder given as input

    Args:
        folder (str): path to folder where to save the pitch shifted audio
        filename (str): path to audio file to pitch-shift
        shifts (int, optional): shift to apply. Defaults to 24.
    """
    logger.info("loading audio")
    audio, orig_sr = librosa.load(filename)
    audio = librosa.resample(audio, orig_sr, target_sr)

    logger.info("shifting pitch")
    root = 40  # e2 is 40

    folder = pl.Path(folder).absolute()

    for n_steps in range(0, shifts + 1):
        # audio_shifted = librosa.effects.pitch_shift(audio, target_sr, n_steps, bins_per_octave=12)
        audio_shifted = pyrb.pitch_shift(audio, target_sr, n_steps)
        new_filename = f"{root+n_steps}.wav"
        new_filepath = folder / pl.Path(new_filename)
        audio_shifted = audio_shifted.astype("float32")
        write(new_filepath, target_sr, audio_shifted)
        logger.debug(f"Creating: {new_filename}")
        logger.debug("==============================")

        # write("{}{}.wav".format(folder, i+root), y_shift, sr)
        # write(f'{folder}/{root+i}.wav', sr, y_shift)

    for n_steps in range(0, shifts + 1):
        # amplitude normalization
        new_filename = f"{root+n_steps}.wav"
        new_filepath = folder / pl.Path(new_filename)
        sound = AudioSegment.from_file(new_filepath, "wav")
        normalized_sound = match_target_amplitude(sound, -30.0)
        # another way
        # normalized_sound = effects.normalize(sound)
        normalized_sound.export(new_filepath, format="wav")
        logger.debug(f"Normalizing: {new_filename}")
        logger.debug("==============================")

    logger.info(f"Audio files saved in folder: {folder}")
