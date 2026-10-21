'use client';
import Link from 'next/link';
import {DEMO_MODE} from '@/lib/demo';
import {usePathname} from 'next/navigation';
import {createContext,useContext,useState,useEffect,useRef,type ReactNode} from 'react';
import {ArrowUpRight,Menu,X} from 'lucide-react';
const Language=createContext<{bn:boolean;setBn:(v:boolean)=>void}>({bn:false,setBn:()=>{}});
export const useLanguage=()=>useContext(Language);
export function Shell({children}:{children:ReactNode}) {
 const [bn,setBn]=useState(true),[menu,setMenu]=useState(false);const path=usePathname();const toggle=useRef<HTMLButtonElement>(null);
 useEffect(()=>{let lang=true;try{lang=localStorage.getItem('janun-language')!=='en'}catch{}setBn(lang);document.documentElement.lang=lang?'bn':'en';},[]);
 useEffect(()=>{setMenu(false);},[path]);
 useEffect(()=>{if(menu)document.querySelector<HTMLAnchorElement>('#main-navigation a')?.focus()},[menu]);
 useEffect(()=>{function escape(e:KeyboardEvent){if(e.key==='Escape'&&menu){setMenu(false);toggle.current?.focus()}}document.addEventListener('keydown',escape);return()=>document.removeEventListener('keydown',escape)},[menu]);
 function change(v:boolean){setBn(v);try{localStorage.setItem('janun-language',v?'bn':'en')}catch{}document.documentElement.lang=v?'bn':'en';}
 const t=(en:string,bnText:string)=>bn?bnText:en;
 const nav=[['/',t('Home','হোম')],['/services',t('Services','সেবাসমূহ')],['/categories',t('Categories','বিভাগসমূহ')],['/journeys',t('My journey','আমার পরিকল্পনা')],['/about',t('About','আমাদের সম্পর্কে')]];
 return <Language.Provider value={{bn,setBn:change}}>
 <a href="#content" className="skip-link">{t('Skip to content','মূল বিষয়বস্তুতে যান')}</a>
 <div className="topline">{t('A little clarity. A simpler path. For everyone.','সঠিক তথ্য। সহজ পথ। সবার জন্য।')}<span>{t('Independent citizen-service guide','স্বাধীন নাগরিক সেবা নির্দেশিকা')}</span></div>
 <header><div className="nav wrap"><Link href="/" className="brand" aria-label={t('Janun home','জানুন হোম')}><span className="brand-mark" aria-hidden="true">জ</span><span>জানুন<small>JANUN</small></span></Link>
 <nav id="main-navigation" className={menu?'open':''} aria-label={t('Main navigation','মূল নেভিগেশন')}>{nav.map(([href,label])=>{const active=href==='/'?path==='/':path.startsWith(href);return <Link key={href} onClick={()=>setMenu(false)} className={active?'active':''} aria-current={active?'page':undefined} href={href}>{label}</Link>})}<Link className="mobile-ask" href="/ask" aria-current={path==='/ask'?'page':undefined} onClick={()=>setMenu(false)}>{t('Ask Janun','জানুনকে জিজ্ঞেস করুন')}</Link></nav>
 <div className="nav-actions"><button className="language" onClick={()=>change(!bn)} aria-label={t('Switch to বাংলা','Switch to English')}>{bn?'English':'বাংলা'}</button><Link className="button dark small desktop-ask" aria-current={path==='/ask'?'page':undefined} href="/ask">{t('Ask Janun','জানুনকে জিজ্ঞেস করুন')}<ArrowUpRight size={16}/></Link><button ref={toggle} className="mobile-menu icon-btn" onClick={()=>setMenu(!menu)} aria-expanded={menu} aria-controls="main-navigation" aria-label={t('Toggle navigation','নেভিগেশন খুলুন বা বন্ধ করুন')}>{menu?<X/>:<Menu/>}</button></div></div></header>
 {DEMO_MODE&&<div className="demo-banner" role="note">{bn?'ডেমো সংস্করণ • ২৫৪টি সংগৃহীত রেকর্ড • মানব যাচাই বাকি — আবেদনের আগে সরকারি উৎস নিশ্চিত করুন।':'DEMO • 254 collected records • Human verification pending — confirm official sources before applying.'}</div>}
 <main id="content" tabIndex={-1}>{children}</main>
 <footer><div className="wrap footer-grid"><div><Link href="/" className="brand"><span className="brand-mark" aria-hidden="true">জ</span><span>জানুন<small>JANUN</small></span></Link><p>{t('Know Your Services. Know Your Rights.','বাংলাদেশের সেবা, সহজেই জানুন।')}</p><p className="muted">{t('An independent guide to public services in Bangladesh. No government affiliation or endorsement.','বাংলাদেশের নাগরিক সেবার স্বাধীন নির্দেশিকা। এটি সরকারি ওয়েবসাইট নয় এবং সরকারি অনুমোদনের দাবি করে না।')}</p></div><div><strong>{t('Discover','খুঁজে দেখুন')}</strong><Link href="/services">{t('Service directory','সেবার তালিকা')}</Link><Link href="/categories">{t('Categories','বিভাগসমূহ')}</Link><Link href="/journeys">{t('Life-event journeys','জীবনের লক্ষ্য ও পরিকল্পনা')}</Link><Link href="/ask">{t('Ask Janun','জানুনকে জিজ্ঞেস করুন')}</Link></div><div><strong>{t('About & support','পরিচিতি ও সহায়তা')}</strong><Link href="/about">{t('Our approach','আমাদের পদ্ধতি')}</Link><Link href="/contact">{t('Contact & feedback','যোগাযোগ ও মতামত')}</Link><Link href="/admin">{t('Source administration','উৎস ব্যবস্থাপনা')}</Link></div></div><div className="wrap footer-bottom"><span>{t('Janun · Made for Bangladesh','জানুন · বাংলাদেশের জন্য')}</span><div>{[['privacy','Privacy','গোপনীয়তা'],['terms','Terms','ব্যবহারের শর্ত'],['disclaimer','Disclaimer','দায়সীমা']].map(([url,en,b])=><Link key={url} href={'/'+url}>{t(en,b)}</Link>)}</div></div></footer>
 </Language.Provider>;
}
