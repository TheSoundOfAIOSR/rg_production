import os

import librosa
import pyrubberband as pyrb
from scipy.io.wavfile import write

target_sr = 44100

def pitchshift(folder, filename, shifts=24):
    """
    Pitch shift of the audio file given as input and save in in the folder given as input

    Args:
        folder (str): path to folder where to save the pitch shifted audio
        filename (str): path to audio file to pitch-shift
        shifts (int, optional): shift to apply. Defaults to 24.
    """
    print('loading audio')
    audio, orig_sr = librosa.load(filename)  
    audio = librosa.resample(audio, orig_sr, target_sr)
    
    print('shifting pitch')
    root = 40 # e2 is 40
    
    for n_steps in range(0 - shifts//2,( shifts//2) +1):
        # audio_shifted = librosa.effects.pitch_shift(audio, target_sr, n_steps, bins_per_octave=12)
        audio_shifted = pyrb.pitch_shift(audio, target_sr, n_steps)
        write(os.path.join(folder, f"{root+n_steps}.wav"), target_sr, audio_shifted) 
        
        #write("{}{}.wav".format(folder, i+root), y_shift, sr)
        #write(f'{folder}/{root+i}.wav', sr, y_shift) 
    
    print(f"Audio files saved in folder: {folder}")
