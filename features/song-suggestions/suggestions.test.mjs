import {test} from 'node:test';
import assert from 'node:assert/strict';
import {suggestionPayload, suggestionNotifications} from './suggestions.js';
const user={uid:'u1',email:'User@Example.com'};
test('normalizes fields and fixes owner to authenticated identity',()=>{
 const p=suggestionPayload({title:'  Música ',artist:' Cantor ',note:'  oi ',user_uid:'admin'},user,{name:'Ana'},'timestamp');
 assert.deepEqual(p,{title:'Música',artist:'Cantor',note:'oi',user_uid:'u1',user_email:'user@example.com',user_name:'Ana',createdAt:'timestamp'});
});
test('rejects blank, oversized and unauthenticated submissions',()=>{
 for(const v of [{title:' ',artist:'A'},{title:'A',artist:''},{title:'A',artist:'B',note:'x'.repeat(1001)}]) assert.throws(()=>suggestionPayload(v,user,{},null));
 assert.throws(()=>suggestionPayload({title:'A',artist:'B'},{},{},null));
});
test('notification identity survives server timestamp resolution and read receipts',()=>{
 const s={id:'s1',title:'Canção',artist:'Banda',user_name:'Ana'};
 const pending=suggestionNotifications([s])[0];
 const committed=suggestionNotifications([{...s,createdAt:{toDate:()=>new Date('2026-09-29')}}])[0];
 assert.equal(pending.key,committed.key);
 const seen=[pending.key];
 assert.equal([committed].filter(n=>!seen.includes(n.key)).length,0);
 assert.match(committed.detail,/Canção.*Banda/);
 assert.equal(suggestionNotifications([{...s,id:'s2'}]).filter(n=>!seen.includes(n.key)).length,1);
});
