import {mkdir,copyFile,readdir} from 'node:fs/promises';
await mkdir('public/pdf',{recursive:true});
await copyFile('node_modules/pdfjs-dist/build/pdf.worker.min.mjs','public/pdf/pdf.worker.min.mjs');
await mkdir('public/ocr/core',{recursive:true});await mkdir('public/ocr/lang',{recursive:true});
await copyFile('node_modules/tesseract.js/dist/worker.min.js','public/ocr/worker.min.js');
for(const name of await readdir('node_modules/tesseract.js-core'))if(/\.wasm(?:\.js)?$/.test(name))await copyFile('node_modules/tesseract.js-core/'+name,'public/ocr/core/'+name);
