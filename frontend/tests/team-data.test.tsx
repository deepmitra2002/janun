import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {TeamData} from '../src/components/team-data';
afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('searches uploaded research and preserves verification labels',async()=>{
 const row={id:'deep:programs:1',owner:'Deep',table:'programs',name:'স্বাস্থ্যসেবা',name_en:'Health',original_id:'1',kind:'service',import_enabled:true};
 const fetch=vi.fn((url:string)=>Promise.resolve({ok:true,json:async()=>url.includes('/record?')?{...row,payload:{verification_status:'partially_verified',notes:'Source review pending'}}:{items:[row],total:1,page:1,page_size:25,owners:['Deep'],tables:['programs']}}));
 vi.stubGlobal('fetch',fetch);render(<TeamData/>);
 expect(await screen.findByText('স্বাস্থ্যসেবা')).toBeTruthy();
 fireEvent.change(screen.getByLabelText('খুঁজুন'),{target:{value:'ঢাকা'}});
 await waitFor(()=>expect(fetch.mock.calls.some(([url])=>decodeURIComponent(url).includes('ঢাকা'))).toBe(true));
 fireEvent.click(screen.getByText('সম্পূর্ণ তথ্য দেখুন'));
 expect(await screen.findByText('partially_verified')).toBeTruthy();
 expect(screen.getByText('Source review pending')).toBeTruthy();
});
