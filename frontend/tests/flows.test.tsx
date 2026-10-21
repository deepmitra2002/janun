import {afterEach,beforeEach,describe,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,waitFor,cleanup} from '@testing-library/react';
import {Directory} from '../src/components/directory';
import {Assistant} from '../src/components/assistant';
import {Contact} from '../src/components/info';
import {Planner} from '../src/components/planner';
const fetchMock=vi.fn();
function response(data:unknown){return Promise.resolve({ok:true,json:async()=>data})}
beforeEach(()=>{vi.stubGlobal('fetch',fetchMock);fetchMock.mockReset();Element.prototype.scrollIntoView=vi.fn();});
afterEach(()=>{cleanup();vi.unstubAllGlobals();});
describe('connected public flows',()=>{
 it('shows honest empty directory and sends the search query',async()=>{
  fetchMock.mockImplementation((url:string)=>response(url.includes('categories')?[]:{items:[],total:0}));
  render(<Directory/>);
  expect(await screen.findByText('Reviewed guidance is on its way')).toBeTruthy();
  fireEvent.change(screen.getByLabelText('Search services'),{target:{value:'passport'}});
  fireEvent.click(screen.getByRole('button',{name:'Search'}));
  await waitFor(()=>expect(fetchMock.mock.calls.some(([url])=>url.includes('q=passport'))).toBe(true));
 });
 it('renders the actual chat answer and carries follow-up context',async()=>{
  fetchMock.mockImplementation(()=>response({answer:'Which applicant category applies?',sources:[],language:'en',status:'needs_clarification',needs_clarification:true,request_id:'fixture'}));
  render(<Assistant/>);
  fireEvent.change(screen.getByLabelText('Your question'),{target:{value:'Passport requirements'}});
  fireEvent.click(screen.getByLabelText('Send question'));
  expect(await screen.findByText('Which applicant category applies?')).toBeTruthy();
  fireEvent.change(screen.getByLabelText('Your question'),{target:{value:'Adult applicant'}});
  fireEvent.click(screen.getByLabelText('Send question'));
  await waitFor(()=>expect(fetchMock.mock.calls).toHaveLength(2));
  const payload=JSON.parse(fetchMock.mock.calls[1][1].body);
  expect(payload.history[0].content).toBe('Passport requirements');
 });
 it('feedback acknowledges only a backend success',async()=>{
  fetchMock.mockImplementation(()=>response({message:'Feedback saved by backend'}));
  render(<Contact/>);
  fireEvent.change(screen.getByLabelText('Your feedback'),{target:{value:'Please include more services'}});
  fireEvent.click(screen.getByRole('button',{name:'Send feedback'}));
  expect(await screen.findByText('Feedback saved by backend')).toBeTruthy();
 });
 it('shows journey coverage gaps without invented checklist items',async()=>{
  fetchMock.mockImplementation(()=>response({title:'New baby',steps:[],gaps:['Birth registration needs review'],notice:'Preparation only',needs_clarification:false}));
  render(<Planner/>);
  fireEvent.click(screen.getByRole('button',{name:'Welcome a baby'}));
  fireEvent.click(screen.getByRole('button',{name:'Build my plan'}));
  expect(await screen.findByText('Birth registration needs review')).toBeTruthy();
  expect(screen.queryAllByRole('checkbox')).toHaveLength(0);
 });
});
