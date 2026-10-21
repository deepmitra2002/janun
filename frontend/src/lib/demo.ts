import type {Detail,Category} from './api';
export const DEMO_MODE=process.env.NEXT_PUBLIC_DEMO_MODE==='true';
export type DemoService=Detail & {owner:string;scope:string;notes:string[];raw_fields:Record<string,unknown>;search_text:string};
export type DemoData={services:DemoService[];categories:Category[];team_records:number};
let cached:Promise<DemoData>|undefined;
const load=():Promise<DemoData>=>cached??=(fetch('/demo-data.json').then(r=>{if(!r.ok)throw new Error('Demo data could not load');return r.json()}).catch(e=>{cached=undefined;throw e}));
const stop=new Set('how do i a an the is what to for of my me about explain please get can where and ki korte lage korbo কী কি লাগে করতে কিভাবে কীভাবে চাই সম্পর্কে জানতে জন্য আমি আমার আছে কত'.split(' '));
export function terms(q:string){let value=q.toLowerCase().normalize('NFC');for(const [from,to] of [['jonmo','birth'],['jonma','birth'],['nibondhon','registration'],['namjari','mutation'],['khotian','খতিয়ান'],['passport','passport পাসপোর্ট'],['nid','nid এনআইডি'],['নামজারি','নামজারি mutation'],['জন্ম','জন্ম birth'],['পাসপোর্ট','পাসপোর্ট passport']])value=value.replaceAll(from,to);return [...new Set(value.split(/[^\p{L}\p{N}\p{M}]+/u).filter(t=>t.length>1&&!stop.has(t)))];}
export function ranked(data:DemoData,q:string){const tokens=terms(q);if(!tokens.length)return [];return data.services.map(s=>{const name=(s.name_bn+' '+s.name_en).toLowerCase();const body=s.search_text.toLowerCase();return {s,score:tokens.reduce((v,t)=>v+(name.includes(t)?12:body.includes(t)?1:0),0),titleMatch:tokens.some(t=>name.includes(t))}}).filter(x=>x.score>0&&x.titleMatch).sort((a,b)=>b.score-a.score).map(x=>x.s);}
export function demoAnswer(data:DemoData,question:string,language='auto'){
 const bn=language==='bn'||(language==='auto'&&/[\u0980-\u09ff]/.test(question));const found=ranked(data,question).slice(0,3);
 const intro=bn?'ডেমো উত্তর — মানব যাচাই বাকি। নিচে সংগৃহীত রেকর্ডের তথ্য দেখানো হচ্ছে; এটি বর্তমান নিয়মের নিশ্চয়তা নয়।':'Demo answer — human verification pending. These are collected record excerpts, not confirmation of current rules.';
 const labels=bn?['আওতাভুক্ত এলাকা','যোগ্যতা','কাগজপত্র','আবেদনের ধাপ','সংগৃহীত ফি','সময়','সময়সীমা','সীমা/তথ্যের ঘাটতি']:['Coverage','Eligibility','Documents','Steps','Collected fee','Time','Deadline','Limitations / gaps'];
 const requested=/fee|cost|টাকা|ফি/.test(question.toLowerCase())?'fees':/document|কাগজ|লাগে|lage/.test(question.toLowerCase())?'documents':'';
 const answer=intro+'\n\n'+(found.length?found.map((s,i)=>{const entries:[string,unknown][]=[['scope',s.scope],['eligibility',s.eligibility],['documents',s.documents],['steps',s.steps],['fees',s.fees],['processing_time',s.processing_time],['deadline',s.deadline],['notes',s.notes]];return `${i+1}. ${bn?s.name_bn:s.name_en}\n`+entries.map(([key,v],j)=>{if(requested&& !['scope',requested,'notes'].includes(key))return '';const value=Array.isArray(v)?v.join('\n'):v;return value?`${labels[j]}: ${value}`:key===requested?(bn?'এই তথ্য সংগ্রহ/যাচাই বাকি।':'This field has not been collected/verified.') :''}).filter(Boolean).join('\n')+`\n${bn?'পূর্ণ রেকর্ড':'Full record'}: ${typeof location!=='undefined'?location.origin:''}/services/${s.slug}/`;}).join('\n\n'):(bn?'মিল পাওয়া যায়নি। সেবার নির্দিষ্ট নাম লিখুন, যেমন নামজারি, জন্ম নিবন্ধন বা passport।':'No matching service found. Try a specific name such as passport, birth registration or mutation.'));
 return {answer,language:bn?'bn':'en',sources:found.flatMap(s=>s.sources.slice(0,2).map(a=>({...a,title:(bn?s.name_bn:s.name_en)+' — '+a.title}))),status:'demo_unverified',needs_clarification:!found.length,request_id:'demo-'+Date.now()};
}
export async function demoApi(path:string,options:RequestInit={}){
 const url=new URL(path,'https://janun.invalid');
 if(url.pathname.startsWith('/admin'))throw new Error('Admin editing is unavailable in the public demo. Use the full app for source review.');
 if(url.pathname==='/feedback')throw new Error('Feedback submission is not connected in this demo. No message has been sent.');
 const data=await load();
 if(url.pathname==='/categories')return data.categories;
 if(url.pathname==='/services'){
  const q=url.searchParams.get('q')||'',category=url.searchParams.get('category');let rows=q?ranked(data,q):[...data.services].sort((a,b)=>a.name_en.localeCompare(b.name_en));if(category)rows=rows.filter(s=>s.category===category);
  const page=Math.max(1,Number(url.searchParams.get('page'))||1),page_size=Math.min(50,Math.max(1,Number(url.searchParams.get('page_size'))||12));return {items:rows.slice((page-1)*page_size,page*page_size),total:rows.length,page_size};
 }
 if(url.pathname.startsWith('/services/')){const s=data.services.find(s=>s.slug===decodeURIComponent(url.pathname.split('/')[2]));if(!s)throw new Error('Service not found');return s;}
 if(url.pathname==='/chat'){const body=JSON.parse(String(options.body||'{}'));return demoAnswer(data,String(body.question||''),body.language);}
 if(url.pathname==='/journey'||url.pathname==='/journeys'){const body=JSON.parse(String(options.body||'{}'));return {title:body.goal||'Demo journey',steps:[],gaps:['Personalized journey planning requires the full backend. Browse the directory or ask about a specific service.'],notice:'Demo — human verification pending.',needs_clarification:true};}
 throw new Error('This feature requires the full JANUN backend; it is not connected in this demo.');
}
