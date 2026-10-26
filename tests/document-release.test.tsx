import {it,expect,beforeEach,afterEach,vi} from 'vitest';
import {readFileSync,existsSync} from 'node:fs';
import {demoAnswer,demoApi,ranked,type DemoData} from '../src/lib/demo';
const data=JSON.parse(readFileSync('public/demo-data.json','utf8')) as DemoData;
const release=JSON.parse(readFileSync('backend/data/document-release.json','utf8'));
beforeEach(()=>vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,json:async()=>data}))));
afterEach(()=>vi.unstubAllGlobals());
it('maps all five uploads and retains every embedded evidence image',()=>{
 expect(release.documents.map((d:{name:string})=>d.name)).toEqual(['1.docx','2.docx','3.docx','4.docx','5.docx']);
 expect(release.mappings).toHaveLength(86);expect(release.services).toHaveLength(84);expect(release.internal_operations).toHaveLength(4);
 expect(release.asset_manifest).toHaveLength(41);
 for(const a of release.asset_manifest)expect(existsSync('public'+a.url)).toBe(true);
 for(const s of release.services){expect(s.document_update.facts_bn.length).toBeGreaterThan(0);expect(data.services.find(x=>x.slug===s.slug)?.document_update).toBeTruthy();}
});
it('replaces stale fields rather than mixing them into bounded new information',()=>{
 const s=data.services.find(x=>x.slug==='team-tammam-edu-021')!;
 expect(s.fees).toContain('৫,০০০');expect(s.processing_time).toContain('৯০–১২০');
 expect(s.scope).toContain('UGC');expect(s.document_update!.facts_en.join(' ')).toContain('Law, pharmacy, medicine and nursing');
 const water=data.services.find(x=>x.slug==='dhaka-wasa-residential-connection')!;
 expect(water.fees).toContain('মোট সংযোগ খরচ নয়');expect(water.scope).toContain('জোন ১ থেকে ৪');
});
it('old duplicate URLs resolve to canonical current records without duplicate listings',async()=>{
 for(const [alias,slug] of Object.entries(data.aliases||{})){
  expect(data.services.some(s=>s.slug===alias)).toBe(false);
  expect((await demoApi('/services/'+alias) as {slug:string}).slug).toBe(slug);
 }
});
it('search and answers use current document facts and retain conflict limitations',()=>{
 const a=demoAnswer(data,'UGC foreign degree equivalence','en');
 expect(a.status).toBe('source_confirmed_document');expect(a.answer).toContain('5,000');expect(a.sources.length).toBeGreaterThan(0);
 expect(ranked(data,'ঢাকা ওয়াসা').some(s=>s.slug==='dhaka-wasa-residential-connection')).toBe(true);
 const pcc=data.services.find(s=>s.slug==='team-sami-janun-pl-002')!;
 expect(pcc.fees).toBeNull();expect(pcc.conflicts.join(' ')).toContain('Tk 500');expect(pcc.conflicts.join(' ')).toContain('Tk 1,500');
 expect(pcc.document_update!.facts_en.join(' ')).not.toContain('Current portal fee:');
});
it('keeps dated allocations and future application windows scoped',()=>{
 const seasonal=data.services.find(s=>s.slug==='aman-seed-flood-support-2026')!;
 expect(seasonal.conflicts.join(' ')).toContain('not evidence of an application window currently open');
 const jobs=data.services.find(s=>s.slug==='team-tammam-job-011')!;
 expect(jobs.document_update!.facts_en.join(' ')).toContain('1 November 2026');
 expect(jobs.conflicts.join(' ')).toContain('ভবিষ্যৎ');
});
