# The GUI Application

Please make sure you have all the necessary dependencies installed (Portaudio and Csound), then proceed to installation following the scripts provided in [Project_common](https://github.com/TheSoundOfAIOSR/project_common#readme)

## Interface Description

### Main Window

![Main WIndow](/Images/UI_manual.png "Main Window")

#### Record and Generate
1 Record button: allows to start/ stop the recording of a voice command

2 Generate button: generate four octaves of notes, mapped to MIDI notes 40 to 88

#### Latent space variables
3 z0, z1 : These sliders control the values for the two latent dimensions used in generation
4 Heuristic Parameters: these sliders control twelve parameters that modify the generated sound based on meaningful musical descriptors. Hover with your mouse over a slider to see what parameter it represents. 

The twelve parameters are :
- velocity : MIDI velocity, 25 to 127
- inharmonicity : amount of the overtone departures from integer multiples of the fundamental
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
5 This area displays text that reports back the status of the application after a command is executed.

6 Textbox area where you can type your command or modify the command received from the Speech to Text engine

#### Audition, Play and Play MIDI
7 Audition button: allows to generate only one note, to be able to audition the sound before generating the whole note range

8 Play button: playback button for the audition sample

9 Play MIDI button: allows to load and playback a MIDI file (.mid). Requires a fully generated note range to operate

#### Sample Display
10 The plot displays the latest generated sample, only after generating a whole note range (does not display audition samples).

11 The slider below it controls the length of sample playback

#### Volume and Pan
12 These two sliders control some global parameters of the sampler
- Volume slider: controls the global volume of the sampler
- Pan slider: controls the panning of the instrument (0-1) Left to Right

#### On screen Keyboard and Octave, Settings
13 The keyboard offers an interface to perform the generated note range of samples, tow octaves at a time.
14 Octave Up button: allows to switch the octave range of the on screen keyboard by two octaves up and down.
15 Goto Settings button: opens the settings window

### Settings Window

The Settings window allows to control the audio settings of the app.

Audio Input: the microphone input for receiving voice commands

Audio Output: the audio output device

MIDI Input: allows to select an external MIDI controller to use for performing with the sampler

Hardware Buffer size: sets the audio hardware buffer size

Software Buffer size: sets the audio software buffer size

Sample Rate: selects the sample rate for the generated samples

## Using the app

### Walkthrough of an example usage
Launch the application using the script provided, according to your Os.

Press Record to start the Speech to text module and make a request for a specific sound, for example "Give me a bright acoustic guitar", press it again to stop the recording.

Modify from the textbox the result of speech to text or, alternatively, type in your desired command in the textbox directly.

Press the Audition button to generate an audition sample. Press Play to hear it.

If you like the audition sample, press Generate to generate four octaves of notes, from MIDI note 40 to 88. If you don't, play around with the sliders and generate a new audition sample. When you are happy with your audition sample, go ahead and generate the full note range.

Perform using the on screen keyboard or through a MIDI controller, if it has been setup from the Settings window.

## Additional Resources

We provide a couple of video demonstrating how to install and operate the app, available at these links

Spoken demos:

[Setup and installation](https://www.youtube.com/watch?v=pWdZxB4NgJw)

[Workflow demo on Windows](https://www.youtube.com/watch?v=wGsGGvbZByE)

Workflow demonstration:

[Workflow demo on MacOS](https://www.youtube.com/watch?v=pppuC27xRGo&feature=youtu.be)

## Known Issues

* On Mac, the app is likely to freeze on first run. Please wait for models to finish downloading and if the app freezes, restart it.