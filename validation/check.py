import pathlib,json,subprocess,re,sys
from lxml import etree
root=pathlib.Path('/verovio-4562');label=sys.argv[1];binary=sys.argv[2]
ns={'s':'http://www.w3.org/2000/svg'};failures=[];count=0
modes={'self':['--svg-bounding-boxes'],'content':['--svg-bounding-boxes','--svg-content-bounding-boxes'],'html5':['--svg-bounding-boxes','--svg-html5'],'plain':[]}
for f in sorted([*root.glob('tie-*.mei'), *root.glob('slur-*.mei'), root/'reporter.musicxml']):
 for mode,flags in modes.items():
  d=root/(label+'-'+mode);d.mkdir(exist_ok=True);out=d/(f.name+'.svg')
  cmd=[binary,'-r','/verovio-src/data','--xml-id-seed','1','-t','svg','--breaks','encoded','--header','none','--footer','none','--page-width','1200','--adjust-page-height',*flags,'-o',str(out),str(f)]
  p=subprocess.run(cmd,capture_output=True,text=True,timeout=20);assert p.returncode==0,(cmd,p.stderr)
  tree=etree.parse(str(out));records=[];ids=[];ok=True
  for kind in ('tie','slur'):
   for g in tree.xpath("//s:g[contains(concat(' ',@class,' '),' "+kind+" ')]",namespaces=ns):
    if 'bounding-box' in g.get('class',''):continue
    paths=g.xpath('./s:path',namespaces=ns)
    if not paths:continue
    boxes=g.xpath("./s:g[contains(concat(' ',@class,' '),' bounding-box ')]",namespaces=ns)
    all_boxes=g.xpath("./s:g[contains(@class,'bounding-box')]",namespaces=ns)
    ids.extend(b.get('data-id' if mode=='html5'else'id') for b in all_boxes)
    if mode=='plain':ok=ok and not boxes;continue
    if len(boxes)!=1:ok=False;continue
    rect=boxes[0].find('s:rect',ns);assert rect is not None
    x,y,w,h=[float(rect.get(k))for k in ('x','y','width','height')]
    match=re.match(r'M\s*([\d.\-]+)[ ,]+([\d.\-]+)',paths[0].get('d'))
    px,py=map(float,match.groups());contains=x-2<=px<=x+w+2 and y-2<=py<=y+h+2
    boxid=boxes[0].get('data-id' if mode=='html5'else'id');ok=ok and contains and bool(boxid)
    records.append({'id':boxid,'rect':[x,y,w,h],'start':[px,py],'contains':contains})
  if mode!='plain':ok=ok and len(ids)==len(set(ids))
  count+=1
  if not ok:failures.append(f.name+':'+mode)
  print(json.dumps({'file':f.name,'mode':mode,'ok':bool(ok),'boxes':records}),flush=True)
print(json.dumps({'count':count,'failures':failures}),flush=True)
sys.exit(bool(failures))
