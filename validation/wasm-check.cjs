const fs=require('node:fs'),assert=require('node:assert/strict');
(async()=>{
 const m=await require('/verovio-4562-wasm.js')();
 const ctor=m.cwrap('vrvToolkit_constructor','number',[]),destroy=m.cwrap('vrvToolkit_destructor',null,['number']);
 const load=m.cwrap('vrvToolkit_loadData','number',['number','string']),options=m.cwrap('vrvToolkit_setOptions','number',['number','string']);
 const svg=m.cwrap('vrvToolkit_renderToSVG','string',['number','number','number']);
 const modes={self:{svgBoundingBoxes:true},content:{svgBoundingBoxes:true,svgContentBoundingBoxes:true},html5:{svgBoundingBoxes:true,svgHtml5:true},plain:{}};
 const root='/verovio-4562';let count=0;
 for(const f of fs.readdirSync(root).filter(f=>/^(tie|slur)-(single|split)\.mei$|^reporter\.musicxml$/.test(f))){
  for(const [mode,flags]of Object.entries(modes)){
   const ptr=ctor();try{
    assert(options(ptr,JSON.stringify({xmlIdSeed:1,breaks:'encoded',header:'none',footer:'none',pageWidth:1200,adjustPageHeight:true,...flags})));
    assert(load(ptr,fs.readFileSync(root+'/'+f,'utf8')));
    const out=svg(ptr,1,0);assert(out.includes('<svg'));
    fs.mkdirSync(root+'/wasm-'+mode,{recursive:true});fs.writeFileSync(root+'/wasm-'+mode+'/'+f+'.svg',out);count++;
   }finally{destroy(ptr)}
  }
 }
 assert.equal(count,20);console.log(JSON.stringify({rendered:count}));
})().catch(e=>{console.error(e);process.exitCode=1});
