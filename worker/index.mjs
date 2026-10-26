import {handleAI} from './gemini.mjs';
// build-worker.mjs inserts the retained static catalogue and HTML route map.
export function createWorker(catalogue,pages){return {
 async fetch(request,env){
  const url=new URL(request.url);
  if(url.pathname==='/api/ai/chat'||url.pathname==='/api/ai/status')return handleAI(request,env,catalogue);
  const key=url.pathname==='/'?'/index.html':url.pathname.endsWith('/')?url.pathname+'index.html':pages[url.pathname]?url.pathname:url.pathname+'/index.html';
  if(request.headers.get('rsc')==='1'&&env.ASSETS){const route=new URL(request.url);route.pathname=key.replace(/\.html$/,'.txt');return env.ASSETS.fetch(new Request(route,request));}
  if(pages[key]&&['GET','HEAD'].includes(request.method))return new Response(request.method==='HEAD'?null:pages[key],{headers:{'Content-Type':'text/html; charset=utf-8'}});
  if(env.ASSETS)return env.ASSETS.fetch(request);
  return new Response('Not found',{status:404});
 }
}};
