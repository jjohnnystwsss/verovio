const fs=require('node:fs');const assert=require('node:assert/strict');
(async()=>{
 const create=require(process.argv[2]||'/verovio-4533-wasm.js');const m=await create();
 const ctor=m.cwrap('vrvToolkit_constructor','number',[]),destroy=m.cwrap('vrvToolkit_destructor',null,['number']);
 const load=m.cwrap('vrvToolkit_loadData','number',['number','string']);
 const options=m.cwrap('vrvToolkit_setOptions','number',['number','string']);
 const timemap=m.cwrap('vrvToolkit_renderToTimemap','string',['number','string']);
 const midi=m.cwrap('vrvToolkit_renderToMIDI','string',['number']);
 const root='/verovio-4533';const cases=JSON.parse(fs.readFileSync(root+'/cases.json','utf8'));fs.mkdirSync(root+'/midi-wasm',{recursive:true});
 for(const [name,expected]of Object.entries(cases)){
  const data=fs.readFileSync(root+'/'+name+'.mei','utf8');let ptr=ctor();
  try{assert(options(ptr,JSON.stringify({xmlIdSeed:1})));assert(load(ptr,data));const events=JSON.parse(timemap(ptr,'{}'));
   const sequence=events.flatMap(e=>e.on||[]).map(id=>id.split('-rend')[0]);const onsets=events.filter(e=>e.on?.length).map(e=>e.tstamp);
   assert.deepEqual(sequence,expected);assert.deepEqual(onsets,expected.map((_,i)=>2000*i));assert.equal(events.at(-1).tstamp,expected.length*2000);
  }finally{destroy(ptr)}
  ptr=ctor();try{assert(load(ptr,data));const bytes=Buffer.from(midi(ptr),'base64');assert.equal(bytes.subarray(0,4).toString(),'MThd');fs.writeFileSync(root+'/midi-wasm/'+name+'.mid',bytes);console.log(JSON.stringify({case:name,timemap:true,midiBytes:bytes.length}));}finally{destroy(ptr)}
 }
})().catch(e=>{console.error(e);process.exitCode=1});
