import ctcsound
import os
import pathlib
from sys import platform 

class CsoundSampler:
  
    def __init__(self, audio_dir, sample_path):
        print("init Csound")
        self.cs = ctcsound.Csound()
        self.audio_dir = audio_dir
        self.sample_path = sample_path
        #self.working_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) # one level above
        #self.audio_dir = os.path.join(self.working_dir, 'generated_sample')

        # if "\\" in self.audio_dir:
        #   self.audio_dir = self.audio_dir.replace("\\", "/")

        #sample = "e2.wav"

        #self.sample_path = self.audio_dir + '/' + sample
        print(f"Sample loaded: {self.sample_path}")
        self.csd = f'''

  <CsoundSynthesizer>

  <CsOptions>
    ;-d
    -b 1024 -B 128
   -+rtmidi=NULL
   --midi-key=5 --midi-velocity-amp=4
  </CsOptions>

  <CsInstruments>
  sr = 44100
  ksmps = 32
  nchnls = 2
  0dbfs = 1.0

  massign 0, 1

    instr 1 ; Sampler

    ;Sname chnget "gSname"
    Sname = "{self.sample_path}" 

    iNum notnum
    ;iNum = p5
    {self.string_pitch_to_file()}


    ivol = p4
    ipb = 1
    inchs = filenchnls(Sname)
    
    
    printf_i "Audiofile '%s' ", 1, Sname 
    
    if inchs == 1 then

    aLeft diskin2 Sname, ipb
    
    aL = aLeft*p4
    aR = aLeft*p4

    else

    aLeft, aRight diskin2 Sname, ipb

    aL =  aLeft*p4
    aR = aRight*p4

    endif

    outs aL,aR

    endin
    

  </CsInstruments>

  <CsScore>

  f 0 3600    ; 1 hour long empty score

  </CsScore>

  </CsoundSynthesizer>


  '''

    def set_output(self,output=0):
        self.cs.setOption(f"-odac{output}")

    def set_midi(self,device):
        self.cs.setOption("-+rtmidi")
        self.cs.setOption(f" -M{device} ")

    def play_midi_file(self,file):
        self.cs.setOption("-+rtmidi")
        self.cs.setOption(f"--midifile={file}")

    def read_midi_file(self,file):
        self.cs.setOption(f"--midifile={file}")

    def compile_and_start(self):
        print("Starting Sampler")

        # self.cs.setStringChannel("gSname", self.sample_path)
        self.cs.compileCsdText(self.csd)
        self.cs.start()
        self.pt = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.pt.play()

    def play_sample(self, pitch=40):
        # sco = "i 1 0 1 1 40" # the 40 will be substitued with the value from the Keyboard on screen from gui
        sco = f"i 1 0 1 1 {pitch}"

        self.cs.readScore(sco) 
        # print(self.stringPitch2File())

    def cleanup(self):
        self.pt.stop()
        self.pt.join()
        self.cs.cleanup()
        self.cs.reset()
    
# ==============================

    # 
    def string_pitch_to_file(self):

      root = 40
      s = f'''
      if iNum == {root} then
      Sname = "{self.sample_path}"
      '''

      for i in range(0, 25):
        note = i + root
        s += f'''
        elseif iNum == {note} then
           Sname = "{self.audio_dir + '/' + str(note)}.wav"
        '''

      s += "endif\n"

      return s
