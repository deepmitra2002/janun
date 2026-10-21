import {Directory} from '@/components/directory';
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;return <Directory initialCategory={slug}/>}
