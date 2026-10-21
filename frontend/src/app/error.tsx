'use client';
import {useLanguage} from '@/components/shell';
export default function ErrorPage({reset}:{reset:()=>void}){const {bn}=useLanguage();return <div className="wrap page empty" role="alert"><h1>{bn?'একটি সমস্যা হয়েছে।':'Something went wrong.'}</h1><p>{bn?'আবার চেষ্টা করুন। আপনার প্রশ্ন কোনো সরকারি কর্তৃপক্ষের কাছে জমা দেওয়া হয়নি।':'Please try again. Your question has not been submitted to any government authority.'}</p><button onClick={reset} className="button dark">{bn?'আবার চেষ্টা করুন':'Try again'}</button></div>}
