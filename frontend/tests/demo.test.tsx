import {describe,it,expect} from 'vitest';
import {readFileSync} from 'node:fs';
import {demoAnswer,ranked,type DemoData} from '../src/lib/demo';
const data=JSON.parse(readFileSync('public/demo-data.json','utf8')) as DemoData;
describe('public demo research',()=>{
 it('preserves every service with no fabricated review date',()=>{expect(data.services).toHaveLength(254);expect(new Set(data.services.map(s=>s.slug)).size).toBe(254);expect(data.services.every(s=>s.verification_status==='needs_review'&&!s.last_verified_at)).toBe(true)});
 it('retrieves Bangla, English and Banglish service questions',()=>{for(const q of ['নামজারি','How do I register a birth?','NID correction korte ki lage?','passport'])expect(ranked(data,q).length).toBeGreaterThan(0)});
 it('answers with real excerpts and collected source links',()=>{const a=demoAnswer(data,'নামজারির ফি');expect(a.status).toBe('demo_unverified');expect(a.answer).toContain('মানব যাচাই বাকি');expect(a.answer).toContain('১,১০০');expect(a.sources.length).toBeGreaterThan(0);expect(a.sources.every(s=>s.url.startsWith('http'))).toBe(true)});
 it('does not invent an answer when there is no match',()=>{const a=demoAnswer(data,'zzzxxyyq');expect(a.needs_clarification).toBe(true);expect(a.sources).toEqual([])});
});
