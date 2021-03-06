import librosa
from scipy.io.wavfile import write

y, sr = librosa.load('E3.wav')

for i in range(-4, 8):
  y_new = librosa.effects.pitch_shift(y, sr, n_steps=i)
  write(f'{52+i}.wav', sr, y_new)