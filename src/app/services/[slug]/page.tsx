import data from '../../../../public/demo-data.json';
import {ServiceDetail} from '@/components/directory';
export default async function Page({params}:{params:Promise<{slug:string}>}){const {slug}=await params;return <ServiceDetail slug={slug}/>}

export function generateStaticParams(){return [...data.services.map(item=>({slug:item.slug})),...Object.keys(data.aliases||{}).map(slug=>({slug}))];}
