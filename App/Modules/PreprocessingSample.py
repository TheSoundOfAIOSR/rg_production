import librosa
import os
from scipy.io.wavfile import write


def pitchshift(folder,file,shifts=24):
    print('loading audio')
    y,sr = librosa.load(file)  #y for audio and sr for samplerate
    librosa.resample(y,sr,44100)
    print('shifting pitch')
    root = 40 # e2 is 40
    for i in range(0 - shifts//2,(shifts//2)+1):
        y_shift = librosa.effects.pitch_shift(y,sr,i,bins_per_octave=12)
        write(os.path.join(folder, f"{root+i}.wav"), sr, y_shift) 
        #write("{}{}.wav".format(folder, i+root), y_shift, sr)
        # write(f'{folder}/{root+i}.wav', sr, y_shift) 