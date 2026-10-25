export function progress(steps, checked) {
 return steps.length ? Math.round(100*steps.filter(s=>checked[s.id]).length/steps.length) : 0;
}
export function canComplete(step, checked) {
 return (step.depends_on||[]).every(id=>checked[id]);
}
