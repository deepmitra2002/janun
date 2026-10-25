import {afterEach,beforeEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {Shell} from '../src/components/shell';
import {Directory,ServiceDetail} from '../src/components/directory';
import {Home} from '../src/components/home';
import {SourceCards} from '../src/components/common';
const {push}=vi.hoisted(()=>({push:vi.fn()}));
vi.mock('next/navigation',()=>({usePathname:()=>'/services',useRouter:()=>({push})}));
const mock=vi.fn();
const categories=[{slug:'identity',name_en:'Identity',name_bn:'পরিচয়',icon:'id'}];
const reply=(data:unknown,status=200)=>Promise.resolve({ok:status<400,status,json:async()=>data});
beforeEach(()=>{vi.stubGlobal('fetch',mock);mock.mockReset();push.mockReset();localStorage.clear();window.history.replaceState({},'','/');mock.mockImplementation((url:string)=>reply(url.includes('/categories')?categories:{items:[],total:0,page_size:12}));});
afterEach(()=>{cleanup();vi.restoreAllMocks();vi.unstubAllGlobals();});
it('restores language to document and closes the menu on Escape',async()=>{
 localStorage.setItem('janun-language','bn');render(<Shell><p>Body</p></Shell>);
 await waitFor(()=>expect(document.documentElement.lang).toBe('bn'));
 const menu=screen.getByRole('button',{name:/navigation|নেভিগেশন/i});
 fireEvent.click(menu);expect(menu.getAttribute('aria-expanded')).toBe('true');
 fireEvent.keyDown(document,{key:'Escape'});expect(menu.getAttribute('aria-expanded')).toBe('false');
});
it('language remains usable when browser storage is blocked',()=>{
 vi.spyOn(Storage.prototype,'getItem').mockImplementation(()=>{throw new Error('blocked')});
 vi.spyOn(Storage.prototype,'setItem').mockImplementation(()=>{throw new Error('blocked')});
 render(<Shell><p>Body</p></Shell>);
 fireEvent.click(screen.getByRole('button',{name:/English/}));expect(document.documentElement.lang).toBe('en');
});
it('restores query, trims submissions, and clears query filters',async()=>{
 window.history.replaceState({},'','/services?q=birth&category=identity&page=2');render(<Directory/>);
 await waitFor(()=>expect((screen.getByLabelText('Search services') as HTMLInputElement).value).toBe('birth'));
 fireEvent.change(screen.getByLabelText('Search services'),{target:{value:'   passport   '}});
 fireEvent.click(screen.getByRole('button',{name:'Search'}));
 await waitFor(()=>expect(new URLSearchParams(window.location.search).get('q')).toBe('passport'));
 fireEvent.click(screen.getByRole('button',{name:'Clear filters'}));
 await waitFor(()=>expect(new URLSearchParams(window.location.search).get('q')).toBeNull());
});
it('offers a working retry after a directory outage',async()=>{
 let down=true;mock.mockImplementation((url:string)=>url.includes('/categories')?reply(categories):down?reply({detail:'Offline'},503):reply({items:[],total:0,page_size:12}));
 render(<Directory/>);expect(await screen.findByText('Offline')).toBeTruthy();down=false;
 fireEvent.click(screen.getByRole('button',{name:'Try again'}));expect(await screen.findByText('Reviewed guidance is on its way')).toBeTruthy();
});
it('distinguishes unknown category from a known empty category',async()=>{
 render(<Directory initialCategory="missing"/>);expect(await screen.findByText('Category not found')).toBeTruthy();
 expect(screen.queryByText('Reviewed guidance is on its way')).toBeNull();
});
it('shows service not found instead of a generic error',async()=>{
 mock.mockImplementation(()=>reply({detail:'Not published'},404));render(<ServiceDetail slug="missing"/>);
 expect(await screen.findByText('Service not found')).toBeTruthy();
});
it('homepage search asks one focused question',()=>{
 render(<Home/>);fireEvent.change(screen.getByRole('searchbox'),{target:{value:'  passport  '}});
 fireEvent.submit(screen.getByRole('searchbox').closest('form')!);expect(push).toHaveBeenCalledWith('/ask?q=passport');
});
it('malformed source URLs do not crash or create unsafe links',()=>{
 render(<SourceCards sources={[{id:'bad',title:'Bad source',url:'javascript:alert(1)'}]}/>);
 expect(screen.queryByRole('link')).toBeNull();
});
it('keeps known empty categories navigable with their own heading',async()=>{
 render(<Directory initialCategory="identity"/>);
 expect(await screen.findByRole('heading',{name:'Identity',level:1})).toBeTruthy();
 expect(await screen.findByText('Reviewed guidance is on its way')).toBeTruthy();
});
it('does not render late responses from the previous service',async()=>{
 let resolveOld:(v:unknown)=>void=()=>{};
 const detail=(name:string)=>({id:name,slug:name,name_en:name,name_bn:name,category:'identity',description_en:'',description_bn:'',official_url:'',steps:[],eligibility:[],documents:[],fees:null,processing_time:null,deadline:null,sources:[],conflicts:[]});
 mock.mockImplementation((url:string)=>url.endsWith('/old')?new Promise(resolve=>{resolveOld=resolve}):reply(detail('New service')));
 const view=render(<ServiceDetail slug="old"/>);view.rerender(<ServiceDetail slug="new"/>);
 expect(await screen.findByRole('heading',{name:'New service'})).toBeTruthy();
 resolveOld({ok:true,status:200,json:async()=>detail('Old service')});
 await waitFor(()=>expect(screen.queryByRole('heading',{name:'Old service'})).toBeNull());
});
it('restores browser history query changes',async()=>{
 render(<Directory/>);await screen.findByText('Reviewed guidance is on its way');
 window.history.pushState({},'','/services?q=certificate');fireEvent.popState(window);
 await waitFor(()=>expect((screen.getByLabelText('Search services') as HTMLInputElement).value).toBe('certificate'));
});
it('exposes no-match guidance rather than implying missing publication',async()=>{
 window.history.replaceState({},'','/services?q=unknown');render(<Directory/>);
 expect(await screen.findByText('No matching services')).toBeTruthy();
 expect(screen.queryByText('Reviewed guidance is on its way')).toBeNull();
});
it('adds history entries for user filter transitions',async()=>{
 render(<Directory/>);await screen.findByText('Reviewed guidance is on its way');
 const initial=window.history.length;
 fireEvent.change(screen.getByLabelText('Search services'),{target:{value:'passport'}});
 fireEvent.click(screen.getByRole('button',{name:'Search'}));
 await waitFor(()=>expect(window.history.length).toBe(initial+1));
 fireEvent.click(screen.getByRole('button',{name:'Identity'}));
 await waitFor(()=>expect(window.history.length).toBe(initial+2));
});
it('moves keyboard focus into the opened mobile navigation',async()=>{
 localStorage.setItem('janun-language','en');render(<Shell><p>Body</p></Shell>);
 const button=await screen.findByRole('button',{name:'Toggle navigation'});button.focus();fireEvent.click(button);
 await waitFor(()=>expect(document.activeElement?.closest('#main-navigation')).not.toBeNull());
 fireEvent.keyDown(document,{key:'Escape'});expect(document.activeElement).toBe(button);
});
