'use client';
import {useEffect,useState} from 'react';
import {Search,ArrowRight,ArrowUpRight,FileText,Clock,Coins,Copy,Check} from 'lucide-react';
import Link from 'next/link';
import {ServiceGuide} from './service-guide';
import {DEMO_MODE} from '@/lib/demo';
import {api,ApiError,type Service,type Category,type Detail} from '@/lib/api';
import {Loading,ErrorBox,Empty,ServiceCard,SourceCards,Breadcrumbs,safeExternal,displayDate} from './common';
import {useLanguage} from './shell';
type Results={items:Service[];total:number;page_size?:number};
type Filters={q:string;category:string;page:number};
function readFilters(initialCategory:string):Filters{const p=new URLSearchParams(window.location.search);const page=Number(p.get('page'));return {q:(p.get('q')||'').trim().slice(0,200),category:initialCategory||p.get('category')||'',page:Number.isSafeInteger(page)&&page>0?page:1}}
export function Directory({initialCategory=''}:{initialCategory?:string}){
 const {bn}=useLanguage();const t=(en:string,b:string)=>bn?b:en;
 const [filters,setFilters]=useState<Filters>({q:'',category:initialCategory,page:1});const [query,setQuery]=useState('');const [ready,setReady]=useState(false);
 const [categories,setCategories]=useState<Category[]|null>(null),[data,setData]=useState<Results|null>(null),[error,setError]=useState(''),[categoryError,setCategoryError]=useState(''),[retry,setRetry]=useState(0);
 useEffect(()=>{const read=()=>{const f=readFilters(initialCategory);setFilters(f);setQuery(f.q);setReady(true)};read();window.addEventListener('popstate',read);return()=>window.removeEventListener('popstate',read)},[initialCategory]);
 useEffect(()=>{let active=true;setCategoryError('');api<Category[]>('/categories').then(c=>{if(active)setCategories(c)}).catch(e=>{if(active)setCategoryError(e.message)});return()=>{active=false}},[retry]);
 const invalid=categories!==null&&!!filters.category&&!categories.some(c=>c.slug===filters.category);
 useEffect(()=>{if(!ready)return;const params=new URLSearchParams(window.location.search);for(const k of ['q','category','page'])params.delete(k);if(filters.q)params.set('q',filters.q);if(filters.category&&!initialCategory)params.set('category',filters.category);if(filters.page>1)params.set('page',String(filters.page));window.history.replaceState(window.history.state,'',window.location.pathname+(params.size?'?'+params:'')+window.location.hash)},[filters,ready,initialCategory]);
 useEffect(()=>{if(!ready||categories===null||invalid)return;let active=true;setData(null);setError('');api<Results>(`/services?q=${encodeURIComponent(filters.q)}&category=${encodeURIComponent(filters.category)}&page=${filters.page}`).then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[filters,ready,categories,invalid,retry]);
 function updateFilters(next:Filters|((current:Filters)=>Filters)){
  const value=typeof next==='function'?next(filters):next;
  if(value.q===filters.q&&value.category===filters.category&&value.page===filters.page)return;
  const params=new URLSearchParams(window.location.search);
  for(const key of ['q','category','page'])params.delete(key);
  if(value.q)params.set('q',value.q);
  if(value.category&&!initialCategory)params.set('category',value.category);
  if(value.page>1)params.set('page',String(value.page));
  window.history.pushState(window.history.state,'',window.location.pathname+(params.size?'?'+params:'')+window.location.hash);
  setFilters(value);
 }
 const selected=categories?.find(c=>c.slug===initialCategory);
 function clear(){setQuery('');updateFilters({q:'',category:initialCategory,page:1})}
 const title=initialCategory&&selected?(bn?selected.name_bn:selected.name_en):t('Find the right service.','সঠিক সেবা খুঁজে নিন।');
 return <div className="wrap page"><Breadcrumbs items={initialCategory?[{label:t('Categories','বিভাগসমূহ'),href:'/categories'},{label:selected?(bn?selected.name_bn:selected.name_en):initialCategory}]:[{label:t('Services','সেবাসমূহ')}]}/>
 {invalid?<Empty title={t('Category not found','বিভাগটি পাওয়া যায়নি')} text={t('Choose a category from the directory.','তালিকা থেকে একটি বিভাগ বেছে নিন।')} action={<Link className="button dark" href="/categories">{t('Browse categories','বিভাগ দেখুন')}</Link>}/>:<><div className="eyebrow">{t('THE SERVICE DIRECTORY','নাগরিক সেবার তালিকা')}</div><h1>{title}</h1><p className="page-intro">{initialCategory?t('Explore available guides in this category. Check each guide’s sources before applying.','এই বিভাগের প্রকাশিত নির্দেশিকা দেখুন। আবেদনের আগে প্রতিটি নির্দেশিকার উৎস যাচাই করুন।'):t('Clear guidance, practical steps, and official sources. All in one place.','দরকারি তথ্য, আবেদন পদ্ধতি এবং সরকারি উৎস এক জায়গায়।')}</p>
 <form role="search" className="search-bar" onSubmit={e=>{e.preventDefault();const q=query.trim();setQuery(q);updateFilters(f=>({...f,q,page:1}))}}><Search size={20}/><input type="search" maxLength={200} aria-label={t('Search services','সেবা খুঁজুন')} placeholder={t('Search in Bangla or English…','বাংলা বা ইংরেজিতে সেবা খুঁজুন…')} value={query} onChange={e=>setQuery(e.target.value)}/><button className="button dark">{t('Search','খুঁজুন')}<ArrowRight size={16}/></button></form>
 <div className={initialCategory?'category-results':'directory-layout'}>{!initialCategory&&<aside className="category-list" aria-label={t('Filter by category','বিভাগ অনুযায়ী বাছাই')}><strong>{t('Browse by category','বিভাগ অনুযায়ী দেখুন')}</strong><button aria-pressed={!filters.category} className={!filters.category?'selected':''} onClick={()=>updateFilters(f=>({...f,category:'',page:1}))}>{t('All services','সকল সেবা')}</button>{categories?.map(c=><button aria-pressed={filters.category===c.slug} className={filters.category===c.slug?'selected':''} key={c.slug} onClick={()=>updateFilters(f=>({...f,category:c.slug,page:1}))}>{bn?c.name_bn:c.name_en}</button>)}</aside>}
 <div>{(filters.q||(!initialCategory&&filters.category)||filters.page>1)&&<button className="text-link clear-filters" onClick={clear}>{t('Clear filters','বাছাই মুছুন')}</button>}{categoryError?<ErrorBox message={categoryError} retry={()=>setRetry(r=>r+1)}/>:error?<ErrorBox message={error} retry={()=>setRetry(r=>r+1)}/>:!data?<Loading/>:<><div className="results-label" role="status"><span>{data.total.toLocaleString(bn?'bn-BD':'en-GB')} {t(data.total===1?'service record':'service records','টি সেবা-রেকর্ড')}</span><span>{t('Alphabetical order · Review status shown per service','নাম অনুযায়ী সাজানো · প্রতিটি সেবার পর্যালোচনার অবস্থা দেখুন')}</span></div>{data.items.length?<div className="service-grid">{data.items.map(s=><ServiceCard service={s} key={s.id}/>)}</div>:filters.q||filters.page>1?<Empty title={t('No matching services','মিলে যাওয়া সেবা পাওয়া যায়নি')} text={t('Try a different name or clear the filters.','অন্য নাম দিয়ে খুঁজুন অথবা বাছাই মুছে দিন।')} action={<button className="button outline" onClick={clear}>{t('Reset search','নতুন করে খুঁজুন')}</button>}/>:<Empty/>}{data.total>0&&<nav className="pagination" aria-label={t('Results pages','ফলাফলের পৃষ্ঠা')}><button disabled={filters.page===1} onClick={()=>updateFilters(f=>({...f,page:f.page-1}))}>{t('Previous','আগের')}</button><span>{t('Page','পৃষ্ঠা')} {filters.page.toLocaleString(bn?'bn-BD':'en-GB')} / {Math.max(1,Math.ceil(data.total/(data.page_size||12))).toLocaleString(bn?'bn-BD':'en-GB')}</span><button disabled={filters.page*(data.page_size||12)>=data.total} onClick={()=>updateFilters(f=>({...f,page:f.page+1}))}>{t('Next','পরের')}</button></nav>}</>}</div></div></>}
 </div>;
}
export function Categories(){const {bn}=useLanguage();const [data,setData]=useState<Category[]|null>(null),[error,setError]=useState(''),[retry,setRetry]=useState(0);useEffect(()=>{let active=true;setError('');api<Category[]>('/categories').then(d=>{if(active)setData(d)}).catch(e=>{if(active)setError(e.message)});return()=>{active=false}},[retry]);return <div className="wrap page"><Breadcrumbs items={[{label:bn?'বিভাগসমূহ':'Categories'}]}/><h1>{bn?'সেবার বিভাগসমূহ':'Browse service categories.'}</h1><p className="page-intro">{bn?'আপনার প্রয়োজনের বিভাগ বেছে নিন। প্রতিটি বিভাগে পর্যালোচিত তথ্য পাওয়ার পর সেবা প্রকাশিত হয়।':'Choose a starting point. Services appear as guidance becomes available for publication.'}</p>{error?<ErrorBox message={error} retry={()=>setRetry(r=>r+1)}/>:data===null?<Loading/>:data.length?<div className="topic-grid">{data.map(c=><Link className="topic" key={c.slug} href={'/categories/'+c.slug}><FileText size={22}/><span>{bn?c.name_bn:c.name_en}</span><ArrowUpRight size={16}/></Link>)}</div>:<Empty/>}</div>}
export function ServiceDetail({slug}:{slug:string}){return <ServiceGuide slug={slug}/>;}
