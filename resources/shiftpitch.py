import librosa
import soundfile

'''
input audio wav file
   outputs 12 pitchdownshifted and 11 picthupshifted audio wav files
   Execution time is 20.2 s ± 1.52 s per loop (mean ± std. dev. of 7 runs, 1 loop each)'''


'''NOTES FROM LEO:
   function was acting weirdly and didn't work as expected so I changed it 
   (shifts should be the total number of notes requested, not half of it)
   Also execution with %%timeit makes performance worse by about 500% (on my machine with timeit takes 2 to 6 sec, without 1 to 2)
   and introduces some unexpected behavior (identified from the multiple "loading file" statements which should be just one)
   TLDR: WE CAN'T RELY ON %%TIMEIT TO BE ACCURATE AND IT'S ACTUALLY COMPROMISING OUR CODE FUNCTIONALITY!!'''

def pitchshift(file,shifts=24):
    print('loading audio')
    y,sr = librosa.load(file)  #y for audio and sr for samplerate
    print('shifting pitch')
    for i in range(0 - shifts//2,shifts//2):
        y_shift = librosa.effects.pitch_shift(y,sr,i,bins_per_octave=12)
        soundfile.write('{}_buffer.wav'.format(i), y_shift, sr)
