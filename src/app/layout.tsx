import type {Metadata} from 'next';
import {Shell} from '@/components/shell';
import '@fontsource/noto-sans-bengali/400.css';
import '@fontsource/noto-sans-bengali/600.css';
import './globals.css';
import './redesign.css';
import './home-reference.css';
import './requested-updates.css';
import './mobile-home-approved.css';
import './mobile-memorial-theme.css';
export const metadata:Metadata={title:{default:'জানুন · সরকারি সেবার সহজ নির্দেশিকা',template:'%s · Janun'},description:'An independent multilingual guide to Bangladesh public services. Find service research, source links and preparation guidance.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="bn" suppressHydrationWarning><head><script dangerouslySetInnerHTML={{__html:`try{var t=localStorage.getItem('janun-theme')||'light';var d=t==='dark';document.documentElement.dataset.theme=d?'dark':'light';document.documentElement.style.colorScheme=d?'dark':'light'}catch(e){}`}}/></head><body><Shell>{children}</Shell></body></html>}
