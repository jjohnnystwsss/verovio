import json,subprocess,pathlib,sys,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
root=pathlib.Path('/verovio-4533')
binary=sys.argv[1]
failures=0
for name,expected in json.loads((root/'cases.json').read_text()).items():
 p=subprocess.run([binary,'-r','/verovio-src/data','-t','timemap','-o','-',str(root/(name+'.mei'))],capture_output=True,text=True,timeout=15)
 row={'case':name,'returncode':p.returncode}
 if p.returncode==0:
  events=json.loads(p.stdout);actual=[n.split('-rend')[0]for e in events for n in e.get('on',[])];onsets=[e['tstamp'] for e in events if e.get('on')]; row.update(expected=expected,actual=actual,onsets=onsets,ok=actual==expected and onsets==[2000*i for i in range(len(expected))] and events[-1]['tstamp']==2000*len(expected))
 else:row.update(ok=False,error=p.stderr[-500:])
 failures+=not row['ok'];print(json.dumps(row),flush=True)
print(json.dumps({'failures':failures}))
sys.exit(bool(failures))
