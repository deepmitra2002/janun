import test from 'node:test';
import assert from 'node:assert/strict';
import { progress, canComplete } from '../src/lib/journey.mjs';
test('empty plan has no implied readiness',()=>assert.equal(progress([],{}),0));
test('only current plan steps count',()=>assert.equal(progress([{id:'a'},{id:'b'}],{a:true,stale:true}),50));
test('dependencies must be checked',()=>assert.equal(canComplete({depends_on:['a']},{}),false));
test('unblocked steps may be checked',()=>assert.equal(canComplete({depends_on:['a']},{a:true}),true));
