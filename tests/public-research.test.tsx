import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,cleanup,fireEvent} from '@testing-library/react';
import {ServiceGuide} from '../src/components/service-guide';
import {ServiceCard} from '../src/components/common';
import {Readiness} from '../src/components/readiness';
import type {Detail} from '../src/lib/api';

const research:Detail={id:'test',slug:'research-test',name_en:'Birth research',name_bn:'জন্ম',
 category:'identity',description_en:'Supplied research',description_bn:'সংগৃহীত তথ্য',official_url:'https://bdris.gov.bd/',
 status:'supplied_research',review_status:'supplied_research',documents:['Birth certificate'],eligibility:[],steps:[],
 fees:null,processing_time:null,deadline:null,conflicts:[],sources:[{id:'test-source',title:'Original link',url:'https://bdris.gov.bd/',review_status:'supplied_research'}]};
afterEach(()=>{cleanup();vi.unstubAllGlobals()});

it('labels supplied detail as research rather than reviewed because it has source links',async()=>{
 vi.stubGlobal('fetch',vi.fn(async()=>({ok:true,json:async()=>research})));
 render(<ServiceGuide slug="research-test"/>);
 expect(await screen.findByText('Research record · Human review pending')).toBeTruthy();
 expect(screen.queryByText('Reviewed sources available')).toBeNull();
 expect(screen.getByText(/Collected research, not confirmed current guidance/)).toBeTruthy();
});

it('distinguishes supplied catalogue cards from reviewed services',()=>{
 render(<ServiceCard service={research}/>);
 expect(screen.getByText('Supplied research · Review pending')).toBeTruthy();
});

it('never confirms readiness for supplied requirements even with a legacy source date',()=>{
 render(<Readiness service={{...research,sources:[{...research.sources[0],verified_at:'2026-10-12T00:00:00Z'}]}}/>);
 fireEvent.click(screen.getByRole('button',{name:'Yes'}));
 fireEvent.click(screen.getByRole('button',{name:'See result'}));
 expect(screen.getByText('Answers saved for this session; official review is still needed.')).toBeTruthy();
 expect(screen.queryByText('Your answers suggest you are ready to apply.')).toBeNull();
});
