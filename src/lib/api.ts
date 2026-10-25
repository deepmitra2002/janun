export type Source = {id:string;title:string;url:string;agency?:string;verified_at?:string;last_checked?:string;review_due?:string;excerpt?:string;checked_at?:string;publication_date?:string;review_status?:string;local_preview?:string;kind?:string;title_bn?:string};
export type Service = {id:string;slug:string;name_en:string;name_bn:string;category:string;description_en:string;description_bn:string;official_url:string;status:string;verification_status?:'current'|'needs_review';source_count?:number;last_verified_at?:string|null;authorities?:string[]};
export type Detail = Service & {steps:string[];documents:string[];eligibility:string[];fees:string|null;processing_time:string|null;deadline:string|null;sources:Source[];conflicts:string[];readiness_questions?:{id:string;text:string;when?:{id:string;answer:'yes'|'no'|'unsure'};kind:'document'|'eligibility'}[];scope?:string;owner?:string;raw_fields?:Record<string,unknown>};
export type Category = {slug:string;name_en:string;name_bn:string;icon:string};
export type Answer = {answer:string;language:string;sources:Source[];status:string;needs_clarification:boolean;request_id:string};
export type Journey = {title:string;steps:{id:string;label:string;service:string;slug:string;sources:Source[];depends_on:string[]}[];gaps:string[];notice:string;needs_clarification:boolean};
export class ApiError extends Error { constructor(message:string,public status:number){super(message);this.name='ApiError';} }
export async function api<T>(path:string, options:RequestInit={}):Promise<T> {
 if(process.env.NEXT_PUBLIC_DEMO_MODE==='true'&&!process.env.NEXT_PUBLIC_API_BASE_URL){const {demoApi}=await import('./demo');return await demoApi(path,options) as T;}
 const controller=new AbortController(); const timer=setTimeout(()=>controller.abort(),60000);
 try {
  const response=await fetch(apiEndpoint(path),{...options,credentials:'same-origin',headers:{...(options.body instanceof FormData ? {} : {'Content-Type':'application/json'}),'X-Janun-Request':'1',...options.headers},signal:controller.signal});
  const body=await response.json().catch(()=>({detail:'The service could not be reached.'}));
  if(!response.ok) throw new ApiError(typeof body.detail==='string'?body.detail:'Please check the fields and try again.',response.status);
  return body as T;
 } catch(error) { if(error instanceof DOMException && error.name==='AbortError') throw new Error('The request timed out. Please try again.'); throw error; }
 finally {clearTimeout(timer);}
}
export const post=<T>(path:string,data?:unknown)=>api<T>(path,{method:'POST',body:data===undefined?undefined:JSON.stringify(data)});

export async function allServices(){const first=await api<{items:Service[];total:number}>('/services?page_size=50');const rest=await Promise.all(Array.from({length:Math.max(0,Math.ceil(first.total/50)-1)},(_,i)=>api<{items:Service[]}>('/services?page_size=50&page='+(i+2))));return first.items.concat(...rest.map(r=>r.items))}

export const apiEndpoint=(path:string)=>(process.env.NEXT_PUBLIC_API_BASE_URL||'/api').replace(/\/$/,'')+path;
