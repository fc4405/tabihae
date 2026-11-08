// Extract the data constants from the TabiHae page as JSON (used by spotpages.py).
const fs = require('fs');
const t = fs.readFileSync(process.argv[2], 'utf8');
function grab(name) {
  const i = t.indexOf('const ' + name + ' =');
  if (i < 0) return null;
  let j = i + ('const ' + name + ' =').length;
  while (t[j] === ' ') j++;
  const open = t[j], close = open === '[' ? ']' : '}';
  let d = 0, k = j, s = null;
  for (; k < t.length; k++) {
    const c = t[k];
    if (s) { if (c === '\\') { k++; continue; } if (c === s) s = null; continue; }
    if (c === '"' || c === "'" || c === '`') { s = c; continue; }
    if (c === open) d++;
    if (c === close) { d--; if (!d) break; }
  }
  return (0, eval)('(' + t.slice(j, k + 1) + ')');
}
const out = {};
for (const n of ['SPOTS', 'SPOT_DETAIL', 'SPOT_PHOTOS', 'KLOOK_CITY', 'REGION_TO_KLOOK', 'MOOD_META']) out[n] = grab(n);
process.stdout.write(JSON.stringify(out));
