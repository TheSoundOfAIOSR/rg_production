import librosa
import soundfile

def pitchshift(file,shifts=24):
    print('loading audio')
    y,sr = librosa.load(file)  #y for audio and sr for samplerate
    print('shifting pitch')
    for i in range(0 - shifts//2,shifts//2):
        y_shift = librosa.effects.pitch_shift(y,sr,i,bins_per_octave=12)
        soundfile.write('{}_buffer.wav'.format(i), y_shift, sr)
