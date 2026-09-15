// Decision-level differential probe (axes 9/10/11/13/17).
// Usage: npx tsx decide.ts <path-to-ts-dir> [decisions.json]
import * as fs from 'fs';
async function main(): Promise<void> {
  const mod: any = await import(process.argv[2] + '/clc_semantics.ts');
  const cases = process.argv[3] ?? 'decisions.json';
  const out: any[] = [];
  for (const p of JSON.parse(fs.readFileSync(cases, 'utf8'))) {
    let r: any;
    try { r = mod.authorizeSet([p.grant], p.op); }
    catch (e) { r = { verdict: null, reason: 'EXC:' + (e as Error).name }; }
    out.push({ id: p.id, lang: 'ts', verdict: r.verdict, reason: r.reason ?? null });
  }
  console.log(JSON.stringify(out));
}
main();
