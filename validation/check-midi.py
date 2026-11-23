import json,pathlib,mido
cases=json.load(open('/Users/johnny/oss-contrib/notes/verovio/4533/cases.json'))
failures=0
for name,ids in cases.items():
 f=mido.MidiFile('/private/tmp/verovio-4533-midi-fixed/'+name+'.mid')
 ons=[];offs=[]
 for track in f.tracks:
  tick=0
  for msg in track:
   tick+=msg.time
   if msg.type=='note_on' and msg.velocity:ons.append((tick,msg.note))
   if msg.type=='note_off' or (msg.type=='note_on' and not msg.velocity):offs.append((tick,msg.note))
 ons.sort();offs.sort()
 expected=[(i*4*f.ticks_per_beat,{'n1':60,'n2':62,'n3':64}[n])for i,n in enumerate(ids)]
 # Existing MIDI encoding releases a sustained note one tick before its boundary.
 expected_offs=[(tick+4*f.ticks_per_beat-1,pitch)for tick,pitch in expected]
 ok=ons==expected and offs==expected_offs;failures+=not ok
 print(json.dumps({'case':name,'ok':ok,'notes':ons,'note_offs':offs}))
assert not failures,failures
