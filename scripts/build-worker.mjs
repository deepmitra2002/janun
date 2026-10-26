import {readFile,writeFile,mkdir,cp,readdir,rm} from 'node:fs/promises';
await rm('dist',{recursive:true,force:true});await mkdir('dist/server',{recursive:true});await mkdir('dist/.openai',{recursive:true});await cp('out','dist/client',{recursive:true});
const pages={};async function walk(dir){for(const e of await readdir(dir,{withFileTypes:true})){const path=dir+'/'+e.name;if(e.isDirectory())await walk(path);else if(path.endsWith('.html'))pages[path.slice(3)]=await readFile(path,'utf8')}}await walk('out');
const catalogue=JSON.parse(await readFile('public/demo-data.json','utf8'));const data={services:catalogue.services.map(({raw_fields,...s})=>s)};
const core=await readFile('worker/gemini.mjs','utf8');const wrapper=(await readFile('worker/index.mjs','utf8')).replace("import {handleAI} from './gemini.mjs';",'');
await writeFile('dist/server/index.js',core+'\n'+wrapper+'\nexport default createWorker('+JSON.stringify(data)+','+JSON.stringify(pages)+');\n');await cp('.openai/hosting.json','dist/.openai/hosting.json');
console.log('Retained '+Object.keys(pages).length+' HTML pages and all static assets; server-side Gemini handler built.');
