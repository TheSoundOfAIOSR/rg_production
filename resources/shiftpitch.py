import librosa
import soundfile

'''input audio wav file
   outputs 12 pitchdownshifted and 11 picthupshifted audio wav files 
   Execution time is 20.2 s ± 1.52 s per loop (mean ± std. dev. of 7 runs, 1 loop each)'''

def shiftpitch(file,shifts=12):
	print('loading audio')
	y,sr = librosa.load(file)  #y for audio and sr for samplerate
	print('shifting pitch')
	for i in range(-shifts,shifts):
		y_shift = librosa.effects.pitch_shift(y,sr,i,bins_per_octave=12)
		soundfile.write('{}_buffer.wav'.format(i), y_shift, sr)	
shiftpitch('e2.wav')