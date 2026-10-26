import {afterEach,beforeEach,it,expect,vi} from 'vitest';
import {render,screen,fireEvent,cleanup} from '@testing-library/react';
import {GuidedTour,TOUR_KEY} from '../src/components/guided-tour';
import {applyTheme} from '../src/components/display-options';
vi.mock('next/navigation',()=>({usePathname:()=>'/outside',useRouter:()=>({push:vi.fn()})}));
beforeEach(()=>localStorage.clear());afterEach(()=>{cleanup();vi.unstubAllGlobals()});
it('shows a first-visit tour, remembers dismissal and allows replay',()=>{const view=render(<GuidedTour bn={false}/>);expect(screen.getByRole('dialog')).toBeTruthy();fireEvent.click(screen.getByRole('button',{name:'Skip tour'}));expect(localStorage.getItem(TOUR_KEY)).toBe('done');view.unmount();render(<GuidedTour bn={false}/>);expect(screen.queryByRole('dialog')).toBeNull();fireEvent(window,new Event('janun-replay-tour'));expect(screen.getByRole('dialog')).toBeTruthy()});
it('closes the tour with Escape',()=>{render(<GuidedTour bn={false}/>);fireEvent.keyDown(document,{key:'Escape'});expect(screen.queryByRole('dialog')).toBeNull();expect(localStorage.getItem(TOUR_KEY)).toBe('done')});
it('keeps System light even on a dark operating system',()=>{vi.stubGlobal('matchMedia',()=>({matches:true}));applyTheme('system');expect(document.documentElement.dataset.theme).toBe('light');applyTheme('dark');expect(document.documentElement.dataset.theme).toBe('dark');applyTheme('system');expect(document.documentElement.style.colorScheme).toBe('light')});
