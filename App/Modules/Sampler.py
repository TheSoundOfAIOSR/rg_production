import os
import time

import ctcsound

def play_sample():

  cs = ctcsound.Csound()

  #work_dir = os.getcwd()
  sample_dir = '../resources/audiodata'

  sample = 'e2.wav'
  sample_path = os.path.join(sample_dir, sample)
  print(f"Sample file path: {sample_path}")

  csd = '''
  <CsoundSynthesizer>

  <CsOptions>
    -d -o dac -m0
  </CsOptions>

  <CsInstruments>
  sr = 44100
  ksmps = 32
  nchnls = 2
  0dbfs = 1.0

    instr 1 ; Sampler
    
    Sname = p5
    ivol = p4
    ipb = 1
    inchs = filenchnls(Sname)


    if inchs == 1 then

    aLeft diskin2 Sname, ipb
    
    aL =  aLeft*p4
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
  cs.compileCsdText(csd)
  cs.start()

  pt = ctcsound.CsoundPerformanceThread(cs.csound())
  pt.play()

  sco = "i 1 0 1 1 " + '\"' + sample_path + '\"' 
  print(f"sco: {sco}")
  cs.readScore(sco) 
  time.sleep(2)


  pt.stop()
  pt.join()
  cs.reset()