import json,pathlib,subprocess,resource,sys
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
root=pathlib.Path('/verovio-corpus');manifest=json.loads((root/'manifest.json').read_text());changed=[];failed=[]
for item in manifest['files']:
 name=item['path'];path=root/name;outputs=[]
 for label,binary in [('base','/verovio-baseline'),('fixed','/verovio-4533-fixed')]:
  p=subprocess.run([binary,'-r','/verovio-src/data','--xml-id-seed','1','-t','timemap','-o','-',str(path)],capture_output=True,text=True,timeout=30)
  outputs.append((p.returncode,p.stdout));
  if p.returncode:failed.append({'case':name,'build':label,'code':p.returncode,'error':p.stderr[-200:]})
 if outputs[0]!=outputs[1]:changed.append(name)
 print(json.dumps({'case':name,'equal':outputs[0]==outputs[1],'codes':[o[0]for o in outputs]}),flush=True)
print(json.dumps({'count':len(manifest['files']),'changed':changed,'failed':failed}),flush=True)
sys.exit(bool(changed or failed))
