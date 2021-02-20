import ctcsound
from music21 import pitch

cs = ctcsound.Csound()

csd = '''
<CsoundSynthesizer>
<CsOptions>
-+rtmidi={MIDI_module_name} -M0 -odac
-m0   ;disable showing rtevent messages
--midi-key-cps=1 --midi-velocity-amp=2
</CsOptions>
<CsInstruments>

sr = 44100
ksmps = 32
nchnls = 2
0dbfs = 1

giPlay init 0

massign 0, 1                              ; assign all midi-channels to instr 1

instr 1

kCtrl    ctrl7    1,1,0,127               ; read in controller 1 on channel 1
kStatus, kChan, kData1, kData2 midiin
;iNum notnum
kTrigger changed2  kStatus                ; if 'kStatus' changes generate a trigger ('bang')
ivel veloc 0, 127
;chnset iNum, "iNum"
chnset kData1, "kdata1"
chnset kTrigger, "ktrigger"
chnset p2, "p2"
chnset ivel, "ivel"
chnset giPlay, "giPlay"
chnset p1, "p1"
;chnset iNum, "iNum"
;print iNum
;if kStatus != 0 then                     ;print if any new MIDI message has been received
if kTrigger = 1 then
  giPlay = 10000
  ;printks "==============================\\n%s\\n==============================\\n", 0, S_Arr[kData1]
endif
;giPlay = giPlay - 1
anote     oscils     p2, p1, 0
kenv     madsr     0.01, 0.1, 0.9, 0.01   ; defining the envelope
out     anote * kenv                      ; scaling the source-signal with the envelope
endin

</CsInstruments>
<CsScore>
i 1 0 3600000
</CsScore>
</CsoundSynthesizer>
'''.format(
  MIDI_module_name='portmidi',   # virtual, portmidi
)

cs.compileCsdText(csd)
cs.start()
pt = ctcsound.CsoundPerformanceThread(cs.csound())
pt.play()

# ==============================

i = 0
while True:
  if cs.controlChannel('giPlay')[0] > 1:
    new_value = cs.controlChannel('giPlay')[0] - 1
    cs.setControlChannel('giPlay', new_value)
  elif cs.controlChannel('giPlay')[0] == 1:
  # if i % 2000000 == 0:
    note = pitch.Pitch()
    note.frequency = cs.controlChannel('p1')[0]
    print('==============================')
    print('Note(name): ', note.nameWithOctave)
    # print('iNum: ', cs.controlChannel('iNum')[0])
    print('Note(midi): ', note.midi)
    print('Velocity: ', cs.controlChannel('ivel')[0])
    # print('Note: ', cs.controlChannel('kdata1')[0])
    # print(cs.controlChannel('giPlay')[0])
    # print(cs.controlChannel('iNum'))
    cs.setControlChannel('giPlay', 0)
  i = i + 1

# ==============================

pt.join()