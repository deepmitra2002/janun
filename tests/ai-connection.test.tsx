import {afterEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {AdminPanel} from '../src/components/admin';
import {SourceCards} from '../src/components/common';

afterEach(()=>{cleanup();vi.unstubAllGlobals();});

it('clearly labels supplied sources without a fabricated review date',()=>{
 render(<SourceCards sources={[{id:'supplied-1',title:'Imported fixture',url:'https://bdris.gov.bd/',review_status:'supplied_research'}]}/>);
 expect(screen.getByText('Supplied information · independent review pending')).toBeTruthy();
 expect(screen.queryByText(/^Reviewed:/)).toBeNull();
});

it('tests the actual provider connection from the admin screen',async()=>{
 vi.stubGlobal('fetch',vi.fn(async(url:string)=>({ok:true,status:200,json:async()=>{
  if(url==='/api/admin/overview')return {username:'reviewer',services:0,sources:0,pending:0,ai_configured:true,embedding_configured:false};
  if(url==='/api/admin/ai-test')return {status:'connected',provider:'gemini',message:'Gemini connection succeeded.'};
  return [];
 }})));
 render(<AdminPanel/>);
 fireEvent.click(await screen.findByRole('button',{name:'Test AI connection'}));
 expect(await screen.findByText('Gemini connection succeeded.')).toBeTruthy();
});

it('displays an actionable provider failure',async()=>{
 vi.stubGlobal('fetch',vi.fn(async(url:string)=>({ok:url!=='/api/admin/ai-test',status:url==='/api/admin/ai-test'?503:200,json:async()=>{
  if(url==='/api/admin/overview')return {username:'reviewer',services:0,sources:0,pending:0,ai_configured:true,embedding_configured:false};
  if(url==='/api/admin/ai-test')return {detail:'Provider quota exceeded. Check your provider quota.'};
  return [];
 }})));
 render(<AdminPanel/>);
 fireEvent.click(await screen.findByRole('button',{name:'Test AI connection'}));
 expect(await screen.findByText('Provider quota exceeded. Check your provider quota.')).toBeTruthy();
});
