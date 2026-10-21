import type {Metadata} from 'next';
import {Shell} from '@/components/shell';
import '@fontsource/noto-sans-bengali/400.css';
import '@fontsource/noto-sans-bengali/600.css';
import './globals.css';
export const metadata:Metadata={title:{default:'Janun — Your next step, made clear',template:'%s · Janun'},description:'An independent multilingual guide to Bangladesh public services. Find reviewed information, official sources and your next step.'};
export default function RootLayout({children}:{children:React.ReactNode}){return <html lang="bn"><body><Shell>{children}</Shell></body></html>}
