import type {NextConfig} from 'next';
const demo=process.env.NEXT_PUBLIC_DEMO_MODE==='true';
const config:NextConfig=demo?{output:'export',trailingSlash:true}:{output:'standalone',async rewrites(){return [{source:'/api/:path*',destination:`${process.env.BACKEND_URL||'http://127.0.0.1:8000'}/api/:path*`}]},async headers(){return [{source:'/:path*',headers:[{key:'X-Content-Type-Options',value:'nosniff'},{key:'Referrer-Policy',value:'strict-origin-when-cross-origin'},{key:'Permissions-Policy',value:'camera=(), microphone=(self), geolocation=()'}]}]}};
export default config;
