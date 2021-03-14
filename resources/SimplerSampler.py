import ctcsound
import time


# to use this script :just run it, (for me is from the terminal '> python3 SimplerSampler.py ')  everything is in main.
# right now is loading csound, playing a note and closing csound.
class CsoundSampler:

    def __init__(self):
        print("init Csound")
        self.cs = ctcsound.Csound()
        self.sample_path = "/Users/leofltt/Documents/Github/rg_production/App/generated_sample/e2.wav" #  path to sample goes here

 # in CsOptions, -odac is the flag setting your output device.
 # right now is set to 0
 # when loading csound you will see a list of devices with their number, so if you want to change the device
 # change the flag to -odacN where N is the device number and save and reload the script
 #right now I set it up to just require a mono sample, so you can use the e2.wav sample that we already have
    def compile_and_start(self):
        print("Starting Sampler")

        csd = f'''

        <CsoundSynthesizer>

        <CsOptions>
        -d -odac1
        </CsOptions>

        <CsInstruments>
        sr = 44100
        ksmps = 32
        nchnls = 2
        0dbfs = 1.0

        instr 1 ; Sampler

        Sname = "{self.sample_path}" ;SAMPLE PATH SHOULD GO IN HERE

        inchs = filenchnls(Sname)


        aOut diskin2 Sname, 1

        outs aOut,aOut

        endin


        </CsInstruments>

        <CsScore>

        f 0 3600    ; 1 hour long empty score  to keep Csound running while waiting for notes

         </CsScore>

        </CsoundSynthesizer>
        '''
        self.cs.compileCsdText(csd)
        self.cs.start()
        self.pt = ctcsound.CsoundPerformanceThread(self.cs.csound())
        self.pt.play()

    def play_sample(self):
        sco = f"i 1 0 1"
        self.cs.readScore(sco)

    def cleanup(self):
        self.pt.stop()
        self.pt.join()
        self.cs.cleanup()
        self.cs.reset()

# ==============================


if __name__ == '__main__':
  cs = CsoundSampler()
  cs.compile_and_start()
  time.sleep(0.5)
  cs.play_sample()
  time.sleep(1)
  cs.cleanup()