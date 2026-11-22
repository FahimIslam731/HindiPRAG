const fs=require('fs'),vm=require('vm'),path=require('path'),assert=require('assert');
const base=process.argv[2];
const C=require(path.resolve(__dirname,'../web/annotation/core.js'));
function packet(n){let context={window:{}};vm.runInNewContext(fs.readFileSync(path.join(base,'reviewer'+n,'packet.js'),'utf8'),context);return context.window.PACKET}
const target=process.argv[3];
for(let n=1;n<=2;n++){
 const p=packet(n),s=C.empty(p);assert.strictEqual(p.preferences.length,n===1?800:416);assert.strictEqual(p.ratings.length,p.preferences.length*3);assert.strictEqual(new Set(p.preferences.map(x=>x.family_id)).size,n===1?200:104);
 assert.strictEqual(C.summarize(p,s).missing,p.preferences.length);
 for(const row of p.preferences){s.answers[C.KEY(row)]={choice:'tie',tie:'X1|X3',reason:'synthetic fixture only',ratings:{}};for(const id of C.ALIASES)s.answers[C.KEY(row)].ratings[id]={meaning:'pass',fit:'appropriate',natural:'4',rationale:''}}
 s.reviewer='fixture-'+n;const summary=C.summarize(p,s);assert.strictEqual(summary.complete,p.preferences.length);assert.strictEqual(summary.invalid,0);
 let copy=C.check(p,JSON.parse(JSON.stringify(s)));assert.strictEqual(C.summarize(p,copy).complete,p.preferences.length);
 const out=C.exportRows(p,s);assert.strictEqual(C.parse(out.preferences).length,p.preferences.length);assert.strictEqual(C.parse(out.ratings).length,p.ratings.length);
 let restored=C.merge(p,C.empty(p),out.preferences,out.ratings);assert.strictEqual(C.summarize(p,restored).complete,p.preferences.length);assert.strictEqual(restored.reviewer,s.reviewer);
 if(n===1){
  let ids=new Set(Array.from({length:10},(_,i)=>'F'+String(i+1).padStart(3,'0')));
  let pp=C.parse(out.preferences).filter(row=>ids.has(row.family_id));
  let rr=C.parse(out.ratings).filter(row=>ids.has(row.family_id));
  assert.strictEqual(pp.length,40);assert.strictEqual(rr.length,120);
  let migrated=C.merge(p,C.empty(p),C.csv(pp,p.prefFields),C.csv(rr,p.ratingFields));
  assert.strictEqual(C.summarize(p,migrated).complete,40);
  assert.strictEqual(C.summarize(p,migrated).missing,760);
 }
 for(const field of ['choice','tie','reason']){
  let bad=structuredClone(s);bad.answers[C.KEY(p.preferences[0])][field]={bad:true};assert.throws(()=>C.check(p,bad),/Invalid backup answer/);
 }
 let bad=structuredClone(s);bad.answers[C.KEY(p.preferences[0])].ratings.X1.natural=[];assert.throws(()=>C.check(p,bad),/Invalid backup rating/);
 let untouched=JSON.stringify(s);assert.throws(()=>C.merge(p,s,out.preferences.replace('synthetic fixture only','conflict'),out.ratings),/Conflicting/);assert.strictEqual(JSON.stringify(s),untouched);
 let invalid=structuredClone(s);invalid.answers[C.KEY(p.preferences[0])].tie='X1';assert.strictEqual(C.summarize(p,invalid).invalid,1);
 assert.throws(()=>C.check(p,{...s,fingerprint:'different'}));
 let conflict=structuredClone(s);conflict.answers[C.KEY(p.preferences[0])].choice='X1';assert.throws(()=>C.merge(p,conflict,out.preferences,out.ratings),/Conflicting/);
 fs.writeFileSync(path.join(target,'r'+n+'-preferences.csv'),out.preferences);fs.writeFileSync(path.join(target,'r'+n+'-ratings.csv'),out.ratings);
 console.log(`reviewer${n}: ${summary.total} contexts and ${summary.candidateComplete} ratings export, resume, and merge passed`);
}

// Execute coordinator event handlers against isolated file/DOM stubs, not a browser.
let elements=Object.fromEntries(['table','independence','r1','r2'].map(id=>[id,{}]));
let context={window:{PACKET1:packet(1),PACKET2:packet(2),HindiPrag:C},document:{getElementById:id=>elements[id]},alert:message=>{throw Error(message)}};
let html=fs.readFileSync(path.join(base,'coordinator/dashboard.html'),'utf8');
let inline=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].at(-1)[1];
vm.runInNewContext(inline,context);
assert(elements.table.innerHTML.includes('<th>1216</th><th>0</th><th>1216</th>'));
(async()=>{
 for(let n=1;n<=2;n++){
  let p=packet(n),s=C.empty(p);s.reviewer='fixture-'+n;
  for(const r of p.preferences){s.answers[C.KEY(r)]={choice:'unclear',reason:'synthetic',ratings:{}};for(const x of C.ALIASES)s.answers[C.KEY(r)].ratings[x]={meaning:'pass',fit:'appropriate',natural:'4'}}
  await elements['r'+n].onchange({target:{files:[{text:async()=>JSON.stringify(s)}],value:'test'}});
 }
 assert(elements.table.innerHTML.includes('<th>1216</th><th>1216</th><th>0</th><th>0</th><th>3648 / 3648</th>'));
 console.log('Coordinator blank/full aggregate counts passed in isolated event-handler test');
})().catch(e=>{console.error(e);process.exitCode=1});
