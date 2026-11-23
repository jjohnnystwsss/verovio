import pathlib,subprocess,json,resource
resource.setrlimit(resource.RLIMIT_CORE,(0,0))
p=pathlib.Path('/verovio-4533')
for label,binary in [('base','/verovio-baseline'),('fixed','/verovio-build-base/verovio')]:
 for name in json.loads((p/'cases.json').read_text()):
  r=subprocess.run([binary,'-r','/verovio-src/data','-t','midi','-o',str(p/('midi-'+label)/name),str(p/(name+'.mei'))],capture_output=True,text=True,timeout=15)
  print(json.dumps({'build':label,'case':name,'returncode':r.returncode,'stderr':r.stderr[-200:]}),flush=True)
