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
        self.cs.sr = target_sr
        self.root = root_note
        # one level above
        self.audio_dir = (
            pl.Path(audio_dir).absolute()
            if audio_dir
            else pl.Path(argv[0]).parent.absolute()
        ) / pl.Path("generated_sample")
        self.sample_path = pl.Path(sample_path).absolute()
        logger.debug(f"Sample loaded: {self.sample_path}")
        self.csd = f"""

  <CsoundSynthesizer>

  <CsOptions>
    ;-d
    -b 1024 -B 256
   --midi-key=5 --midi-velocity-amp=4
  </CsOptions>

  <CsInstruments>
  ksmps = 32
  nchnls = 2
  0dbfs = 1.0

  massign 0, 1
  
  gkVol init 0.9
  gkVol chnexport "vol", 1, 2, 1, 0, 1

  gkPan init 0.5
  gkPan chnexport "pan", 1, 2, 1, 0, 1

    instr 1 ; Sampler

    Sname = "{self.sample_path.as_posix()}" 

    iNum notnum
    iNum = p5
    {self.string_pitch_to_file()}


    ivol = p4
    ipb = 1
    inchs = filenchnls(Sname)

    kPanLeft = sqrt(1 - gkPan)
    kPanRight = sqrt(gkPan)
    
    
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

    outs aL,aR

    endin
    

  </CsInstruments>

  <CsScore>

  f 0 36000    ; 1 hour long empty score

  </CsScore>

  </CsoundSynthesizer>


  """

    def set_output(self, output=0):
        self.cs.setOption(f"-odac{output}")

    def set_midi_api(self, api="NULL"):
        self.cs.setOption(f"-+rtmidi={api}")

    def set_midi_device(self, device):
        self.cs.setOption(f"--midi-device={device}")

    def play_midi_file(self, file):
        self.set_midi_api(api="")
        self.cs.setOption(f"--midifile={file}")

    def compile_and_start(self):
        logger.debug("Starting Sampler")
        self.cs.compileCsdText(self.csd)
        return self.cs.start()

    def start_perf_thread(self):
        self.pt = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.pt.play()

    def play_sample(self, pitch=40):
        # sco = "i 1 0 1 1 40" # the 40 will be substitued with the value from the Keyboard on screen from gui
        sco = f"i 1 0 1 1 {pitch}"
        self.cs.readScore(sco)

    def cleanup(self):
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

        s = f"""
      if iNum == {self.root} then
      Sname = "{self.sample_path.as_posix()}"
      """

        for i in range(self.root - 24, self.root + 25):
            note = i
            s += f"""
        elseif iNum == {note} then
           Sname = "{(self.audio_dir / pl.Path(str(note))).as_posix()}.wav"
        """

        s += "endif\n"

        return s
