import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup} from '@testing-library/react';
import {AdminPanel} from '../src/components/admin';

afterEach(()=>{cleanup();vi.unstubAllGlobals();});

it('keeps services available and displays a failed source request',async()=>{
 vi.stubGlobal('fetch',vi.fn(async(url:string)=>{
  const data:Record<string,unknown>={
   '/api/admin/overview':{username:'reviewer',services:1,sources:1,pending:1,ai_configured:false,embedding_configured:false},
   '/api/admin/services':[{id:'service-1',slug:'passport',name_en:'Passport fixture',name_bn:'Passport',category:'identity',description_en:'',description_bn:'',official_url:'',status:'draft'}],
   '/api/admin/sources':{detail:'Source listing unavailable'},
   '/api/categories':[], '/api/admin/feedback':[], '/api/admin/audit':[]
  };
  return {ok:url!=='/api/admin/sources',status:url==='/api/admin/sources'?500:200,json:async()=>data[url]};
 }));
 render(<AdminPanel/>);
 expect(await screen.findByRole('option',{name:'Passport fixture'})).toBeTruthy();
 expect(await screen.findByText(/Source listing unavailable/)).toBeTruthy();
});
