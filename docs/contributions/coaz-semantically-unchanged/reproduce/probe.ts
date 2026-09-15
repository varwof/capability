// Value-level differential probe (axis 5-13).
// Usage: npx tsx probe.ts <path-to-ts-dir> [cases.json]
import * as fs from 'fs';
async function main(): Promise<void> {
  const mod: any = await import(process.argv[2] + '/clc_semantics.ts');
  const cases = process.argv[3] ?? 'probes.json';
  const out: any[] = [];
  for (const p of JSON.parse(fs.readFileSync(cases, 'utf8'))) {
    const rec: any = { id: p.id, lang: 'ts', raw_eval: null, raw_app: null, canon_eval: null, canon_app: null };
    for (const [side, key, ckey] of [['evaluated', 'raw_eval', 'canon_eval'], ['applied', 'raw_app', 'canon_app']] as const) {
      const raw: string = p[side];
      try { mod.validateRawParams(raw); rec[key] = 'ok'; }
      catch (e) { rec[key] = String((e as Error).message).split(':')[0]; }
      try { rec[ckey] = mod.canonicalJSON(JSON.parse(raw)); }
      catch (e) { rec[ckey] = 'ERR:' + (e as Error).name; }
    }
    rec.same = !!rec.canon_eval && !!rec.canon_app && rec.canon_eval === rec.canon_app &&
      !String(rec.canon_eval).startsWith('ERR');
    out.push(rec);
  }
  console.log(JSON.stringify(out));
}
main();
