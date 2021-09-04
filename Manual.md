# The GUI Application

## Interface Description

### Main Window

#### Record and Generate
Record button: allows to start/ stop the recording of a voice command
Generate button: generate four octaves of notes, mapped to MIDI notes 40 to 88

#### Latent space variables
z0, z1 : These sliders control the values for the two latent dimensions used in generation
Heuristic Parameters: these sliders control twelve parameters that modify the generated sound based on meaningful musical descriptors. Hover with your mouse over a slider to see what parameter it represents. The twelve parameters are:
- velocity : MIDI velocity, 25 to 127
- inharmonicity 
- even - odd 
- sparse - rich
- attacks (rms) : RMS value for the attack phase of the sound's envelope
- decay (rms) : RMS value for the decay phase of the sound's envelope
- attack time : duration of the attack phase of the sound's envelope
- decay time : duration of the decay phase of the sound's envelope
- bass : amount of bass frequency components
- mid : amount of mid frequency components
- high-mid : amount of high-mid frequency components
- high : amount of high frequency components

#### Text Area
This area displays text that reports back the status of the application after a command is executed.

#### Audition, Play and Play MIDI
Audition button: allows to generate only one note, to be able to audition the sound before generating the whole note range

Play button: playback button for the audition sample

Play MIDI button: allows to load and playback a MIDI file (.mid). Requires a fully generated note range to operate

#### Sample Display
The plot displays the latest generated sample, only after generating a whole note range (does not display audition samples).
The slider below it controls the length of sample playback

#### Volume and Pan
Volume slider: controls the global volume of the sampler
Pan slider: controls the panning of the instrument (0-1) Left to Right

#### On screen Keyboard and Octave, Settings
The keyboard offers an interface to perform the generated note range of samples, tow octaves at a time.
Octave Up button: allows to switch the octave range of the on screen keyboard by two octaves up and down.
Goto Settings button: opens the settings window

### Settings Window

The Settings window allows to control the audio settings of the app.
Audio Input: the microphone input for receiving voice commands
Audio Output: the audio output device
MIDI Input: allows to select an external MIDI controller to use for performing with the sampler
Hardware Buffer size: sets the audio hardware buffer size
Software Buffer size: sets the audio software buffer size
Sample Rate: selects the sample rate for the generated samples
Export button: allows to save the generated sampe as a .wav file

## Using the app

### Walkthrough of an example usage
Launch the application using the script provided, according to your Os.

Press Record to start the Speech to text module and make a request for a specific sound, for example "Give me a bright acoustic guitar", press it again to stop the recording.

Press the Audition button to generate an audition sample. Press Play to hear it.

If you like the audition sample, press Generate to generate four octaves of notes, from MIDI note 40 to 88. If you don't, play around with the sliders and generate a new audition sample. When you are happy with your audition sample, go ahead and generate the full note range.

Perform using the on screen keyboard or through a MIDI controller, if it has been setup from the Settings window.
