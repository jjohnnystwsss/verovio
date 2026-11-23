from pathlib import Path
import subprocess,json
from lxml import etree
root=Path('/verovio-corpus');diffs=[];errors=[];ink_diffs=[]
for item in json.loads((root/'manifest.json').read_text())['files']:
 f=root/item['path'];out=[];ink=[]
 for label,binary in [('base','/verovio-baseline'),('fixed','/verovio-4562-fixed')]:
  args=[binary,'-r','/verovio-src/data','--xml-id-seed','1','-t','svg','--breaks','encoded','--header','none','--footer','none','--page-width','1200','--adjust-page-height','-o','-',str(f)]
  p=subprocess.run(args,capture_output=True,text=True,timeout=30);out.append(p.stdout)
  if p.returncode:errors.append([item['path'],label,p.returncode])
  p=subprocess.run(args[:2]+args[2:-1]+['--svg-bounding-boxes',str(f)],capture_output=True,text=True,timeout=30)
  if p.returncode:errors.append([item['path'],label+'-boxes',p.returncode]);ink.append(b'');continue
  t=etree.fromstring(p.stdout.encode(), parser=etree.XMLParser(remove_blank_text=True))
  for b in t.xpath("//*[contains(@class,'bounding-box')]"):
   if b.getparent()is not None:b.getparent().remove(b)
  ink.append(etree.tostring(t))
 if out[0]!=out[1]:diffs.append(item['path'])
 if ink[0]!=ink[1]:ink_diffs.append(item['path'])
 print(json.dumps({'file':item['path'],'plain_equal':out[0]==out[1],'ink_equal':ink[0]==ink[1]}),flush=True)
print(json.dumps({'count':len(json.loads((root/'manifest.json').read_text())['files']),'plain_differences':diffs,'ink_differences':ink_diffs,'errors':errors}),flush=True)
assert not(diffs or ink_diffs or errors)
