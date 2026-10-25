"""Run only after publishing reviewed sources; never turn targets into claimed results."""
import argparse,json,time,urllib.request
from pathlib import Path
parser=argparse.ArgumentParser();parser.add_argument('--url',default='http://localhost:3000');args=parser.parse_args()
rows=[json.loads(x) for x in (Path(__file__).parents[1]/'data/eval/questions.jsonl').read_text().splitlines()]
results=[]
for row in rows:
 start=time.monotonic();request=urllib.request.Request(args.url+'/api/chat',data=json.dumps({'question':row['question'],'language':row['language']}).encode(),headers={'Content-Type':'application/json'})
 try:
  with urllib.request.urlopen(request,timeout=65) as response: answer=json.load(response)
  results.append({'id':row['id'],'status':answer['status'],'latency_seconds':round(time.monotonic()-start,3),'expected_service_in_sources':row.get('expected_service') in [s['service_slug'] for s in answer['sources']] if row.get('expected_service') else None,'abstained':answer['status']=='insufficient_evidence','answer':answer['answer'],'sources':answer['sources']})
 except Exception as exc: results.append({'id':row['id'],'error':type(exc).__name__})
print(json.dumps({'results':results,'note':'Human review of answer support and correctness is still required. Source presence alone is not correctness.'},ensure_ascii=False,indent=2))
