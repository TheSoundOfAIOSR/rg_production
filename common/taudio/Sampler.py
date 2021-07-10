import ctcsound
import os
import pathlib as pl
from sys import platform, argv
import common.log as log
from common.config import Config

logger = log.setup_logger()
config = Config.load_config()

target_sr = config.sampling_rate
root_note = config.root


class CsoundSampler:
    def __init__(self, audio_dir, sample_path):
        print("init Csound")

        self.cs = ctcsound.Csound()

        self.samp_rate = target_sr
        self.sw_buf = 1024
        self.hw_buf = 2048
        self.root = root_note
        self.midi_api = "NULL"
        self.midi_device = 0
        self.output = 0

        # one level above
        self.audio_dir = (
                             pl.Path(audio_dir).absolute()
                             if audio_dir
                             else pl.Path(argv[0]).parent.absolute()
                         ) / pl.Path("generated_sample")

        self.sample_path = pl.Path(sample_path).absolute()
        logger.debug(f"Sample loaded: {self.sample_path}")

        self.csd = None

    # ==============================

    def create_csd(self):

        csd = f""" 

  <CsoundSynthesizer>

  <CsOptions>
   -odac{self.output}
   -b {self.sw_buf}
   -B {self.hw_buf}
   -+rtmidi={self.midi_api}
   --midi-key=5 
   --midi-velocity-amp=4
  </CsOptions>

  <CsInstruments>
  
  ksmps = 32
  nchnls = 2
  0dbfs = 1.0

  massign 0, 1
  
  gkVol init 0.9
  gkVol chnexport "vol", 1, 2, 1, 0, 1

  gkPan init 0.5
  gkPan chnexport "pan", 1, 2, 0.5, 0, 1

    instr 1 ; Sampler

    Sname = "{self.sample_path.as_posix()}" 

    iNum notnum
    iNum = p5
    {self.string_pitch_to_file()}


    ivol = p4
    ipb = 1
    inchs = filenchnls(Sname)

    kPanRight = sqrt(1 - gkPan)
    kPanLeft = sqrt(gkPan)
    
    
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

    aL *= gkVol
    aR *= gkVol

    aL *= kPanLeft
    aR *= kPanRight

    aEnv madsr 0.05, p3-0.05, 1, 0.05
    xtratim 0.05

    outs aL,aR

    endin
    

  </CsInstruments>

  <CsScore>

  f 0 36000    ; 1 hour long empty score

  </CsScore>

  </CsoundSynthesizer> 
  
  """
        self.csd = csd 


    def set_options(self):
        """
        sets all the appropriate csound options, based on the variable values:
        sample rate
        midi device (if any is used)
        """
        self.cs.sr = self.samp_rate
        # self.cs.setOption(f"-b {self.sw_buf}")
        # self.cs.setOption(f"-B {self.hw_buf}")
        # self.cs.setOption(f"-+rtmidi={self.midi_api}")
        if (self.midi_api != "NULL"):
            self.cs.setOption(f"--midi-device={self.midi_device}")

            # ========================================

    # Csound options setters

    def set_output(self, output=1):
        if output != self.output:
            self.output = output

    def set_midi_api(self, api="NULL"):
        if api != self.midi_api:
            self.midi_api = api

    def set_midi_device(self, device):
        if device != self.midi_device:
            self.midi_device = device

    def set_sw_buf(self, sw=1024):
        if sw != self.sw_buf:
            self.sw_buf = sw

    def set_hw_buf(self, hw=2048):
        if hw != self.hw_buf:
            self.hw_buf = hw

    def set_sr(self, sr=44100):
        if sr != self.samp_rate:
            self.samp_rate = sr

    # =======================================

    def play_midi_file(self, file):
        """
        plays a midi file, given the midi file path
        """
        self.cs.setOption(f"--midifile={file}")
        self.cs.setOption(f"-odac{self.output}")

    def compile_and_start(self):
        """
        Compiles the .Csd file, starts Csound
        """
        logger.debug("Starting Sampler")
        self.create_csd()
        self.cs.compileCsdText(self.csd)
        return self.cs.start()

    def start_perf_thread(self):
        """
        Creates and starts Csound Performance Thread
        """
        self.pt = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.pt.play()

    def play_sample(self, pitch=root_note):
        """
        Play a note as a single Csound score note given a MIDI pitch

        sco = "i 1 0 1 1 40" where
        i 1 = sampler,
        0 = start time,
        1 = duration,
        1 = sample read speed
        40 = midi note to play (sample)
        """
        sco = f"i 1 0 1 1 {pitch}"
        self.cs.readScore(sco)

    def cleanup(self):
        """
        Stops Csound and the performance thread and cleans up memory
        """
        self.pt.stop()
        self.pt.join()
        self.cs.cleanup()
        self.cs.reset()

    # ==============================

    def set_master_volume(self, value=0.9):
        self.cs.setControlChannel("vol", value)

    def set_panning(self, value=0.5):
        self.cs.setControlChannel("pan", value)

    def set_root(self, r=60):
        self.root = r

    def string_pitch_to_file(self):
        """
        Sets the file to play back, based on requested Midi note
        """

        s = f"""
      if iNum == {self.root} then
      Sname = "{(self.audio_dir / pl.Path(str(self.root))).as_posix()}.wav"
      """

        for i in range(self.root - 24, self.root + 25):
            note = i
            s += f"""
        elseif iNum == {note} then
           Sname = "{(self.audio_dir / pl.Path(str(note))).as_posix()}.wav"
        """

        s += "endif\n"

        return s
