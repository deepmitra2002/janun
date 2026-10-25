import type {Detail} from './api';
export type Choice='yes'|'no'|'unsure';
export type Requirement={id:string;text:string;when?:{id:string;answer:Choice};kind:'document'|'eligibility'};
export function requirements(d:Detail):Requirement[]{if(d.readiness_questions?.length)return d.readiness_questions;return [...d.documents.map((text,i)=>({id:'doc-'+i,text,kind:'document' as const})),...d.eligibility.map((text,i)=>({id:'elig-'+i,text,kind:'eligibility' as const}))]}
export function activeRequirements(items:Requirement[],answers:Record<string,Choice>){const active:Requirement[]=[];const ids=new Set<string>();for(const q of items){if(!q.when||(ids.has(q.when.id)&&answers[q.when.id]===q.when.answer)){active.push(q);ids.add(q.id)}}return active}
export function readinessResult(items:Requirement[],answers:Record<string,Choice>,reviewed:boolean){const active=activeRequirements(items,answers);return {met:active.filter(q=>answers[q.id]==='yes'),missing:active.filter(q=>answers[q.id]==='no'),unresolved:active.filter(q=>!answers[q.id]||answers[q.id]==='unsure'),ready:reviewed&&active.length>0&&active.every(q=>answers[q.id]==='yes')}}

export function updateAnswer(items:Requirement[],answers:Record<string,Choice>,id:string,value:Choice){const next={...answers,[id]:value};const active=new Set(activeRequirements(items,next).map(q=>q.id));return Object.fromEntries(Object.entries(next).filter(([key])=>active.has(key))) as Record<string,Choice>}
