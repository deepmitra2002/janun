'use client';
import Link from 'next/link';
import {useLanguage} from '@/components/shell';
export default function NotFound(){const {bn}=useLanguage();return <div className="wrap page empty"><span className="eyebrow">404</span><h1>{bn?'পৃষ্ঠা পাওয়া যায়নি।':'Let’s find your way back.'}</h1><p>{bn?'এই ঠিকানায় কোনো পৃষ্ঠা নেই।':'This page isn’t here.'}</p><Link href="/" className="button dark">{bn?'জানুনে ফিরুন':'Back to Janun'} →</Link></div>}
