#!/usr/bin/env python3
"""Build the No Frills Sweater (size S and M) checklist HTML files.

The page chrome (fonts, colors, table layout) is taken from the Travel Time
checklist so the library keeps one look; only the pattern data and render
script live here.
"""

import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "site/library/no-frills-sweater"
BASE_HTML = REPO_ROOT / "site/library/travel-time/travel-time.html"

# Values are the 3rd (S) and 4th (M) entries of the pattern's 10-size lists.
SIZES = {
    "s": dict(
        label="S", bust_in="41¼", bust_cm=105, len_in="21¾", len_cm=55,
        inner_in="18", inner_cm=46, arm_in="15", arm_cm=38, hole_in="9", hole_cm=23,
        sunday=250, mohair=125,
        co=108, back0=20, slv0=12, front0=40, tot1=148, reps=27, tot2=364,
        dBack=25, dSlv=22, dFront=50, eBack=52, eSlv=76, eFront=104,
        under=4, body=220, bodyIn="19", bodyCm=48, bodyDec=18, bodyAfter=202,
        pu=4, slvSts=80, slvIn="15¼", slvCm=39, every=8, slvDecs=13, slvAfter=54,
    ),
    "m": dict(
        label="M", bust_in="43", bust_cm=109, len_in="22", len_cm=56,
        inner_in="18", inner_cm=46, arm_in="16¼", arm_cm=41, hole_in="9½", hole_cm=24,
        sunday=300, mohair=150,
        co=112, back0=20, slv0=14, front0=40, tot1=152, reps=29, tot2=384,
        dBack=25, dSlv=24, dFront=50, eBack=54, eSlv=82, eFront=108,
        under=4, body=228, bodyIn="19¼", bodyCm=49, bodyDec=18, bodyAfter=210,
        pu=4, slvSts=86, slvIn="15¼", slvCm=39, every=7, slvDecs=15, slvAfter=56,
    ),
}

EXTRA_CSS = """
u{background:#e8820c;color:#fff;text-decoration:underline;text-decoration-color:#b85f00;border-radius:2px;padding:0 2px}
.setup-tag{font-size:.68rem;font-weight:500;background:#fff3cd;color:#856404;border-radius:4px;padding:1px 6px;font-family:inherit}
.inc-tag{font-size:.68rem;font-weight:500;background:#e8f4ee;color:#2d6a4f;border-radius:4px;padding:1px 6px;font-family:inherit}
.dec-tag{font-size:.68rem;font-weight:500;background:#fce8e8;color:#8b2020;border-radius:4px;padding:1px 6px;font-family:inherit}
.div-tag{font-size:.68rem;font-weight:500;background:#e8eaf6;color:#3949ab;border-radius:4px;padding:1px 6px;font-family:inherit}
.meas-tag{font-size:.68rem;font-weight:500;background:#f3eaf8;color:#5c2d6e;border-radius:4px;padding:1px 6px;font-family:inherit}
.setup-tag,.inc-tag,.dec-tag,.div-tag,.meas-tag{white-space:nowrap}
.pass-sts{font-size:.72rem;color:var(--muted);font-family:'Calling Code',monospace;user-select:none}
.pass-item.pass-done .pass-sts{color:var(--plum-light);text-decoration:line-through}
.pass-item{margin-right:6px}
"""

DATA_JS = r"""
const D = __DATA__;
const STORAGE_KEY = `no-frills-sweater-${D.label.toLowerCase()}-v1`;

// ── Pattern data ────────────────────────────────────────────────────────────
const seq = (start, step, n) => Array.from({ length: n }, (_, i) => start + step * (i + 1));
const MR = '<u>M1R</u>', ML = '<u>M1L</u>';

function shortRows(prefix) {
  return [
    { id: `${prefix}-1`, label: 'Step 1', type: 'inc', side: 'RS', noCheck: true,
      instr: `Knit across right back, ${MR}, sm, k raglan st, sm, ${ML}, knit across right sleeve, ${MR}, sm, k raglan st, sm, ${ML}, k to the turning point (see note), turn.` },
    { id: `${prefix}-2`, label: 'Step 2', type: 'body', side: 'WS', noCheck: true,
      instr: 'Purl to BOR marker (mid back).' },
    { id: `${prefix}-3`, label: 'Step 3', type: 'inc', side: 'WS', noCheck: true,
      instr: `Purl across left back, ${ML}, sm, p raglan st, sm, ${MR}, purl across left sleeve, ${ML}, sm, p raglan st, sm, ${MR}, p to the turning point (see note), turn.` },
    { id: `${prefix}-4`, label: 'Step 4', type: 'body', side: 'RS', noCheck: true,
      instr: 'Knit to BOR marker (mid back).' },
  ];
}

function sleeveSections(n) {
  const p = `slv${n}`;
  const plain = D.every - 1;
  return [
    { id: p, title: `Sleeve ${n}`,
      note: `Worked in the round in stockinette on 4 mm (US6) double-pointed needles or a circular needle with Magic Loop.`,
      rows: [], groups: [
        { title: 'Pick Up & Join', rows: [
          { id: `${p}-pu`, label: 'Pick Up', type: 'joinup', stitches: `${D.slvSts} sts`,
            instr: `Return the ${D.eSlv} held sleeve sts to the needles. Pick up and knit ${D.pu} sts along the ${D.pu} underarm sts cast on for the body. = ${D.slvSts} sts. Place a marker for BOR in the middle of the ${D.pu} underarm sts.` },
        ] },
        { id: `${p}-dec`, title: `Rounds 1–${D.every} — work ${D.slvDecs} times`,
          note: `Work ${plain} plain rounds, then the decrease round (every ${D.every}th round). The numbers beside each box show the stitch count after the decrease.`,
          rows: [
            { id: `${p}-plain`, label: `Rnd 1–${plain}`, type: 'body', noCheck: true, instr: `Knit ${plain} rounds.` },
            { id: `${p}-d`, label: `Rnd ${D.every}`, type: 'dec', noCheck: true, instr: `K1, <u>k2tog</u>, knit to last 3 sts, <u>k2tog tbl</u>, k1.` },
          ], passes: D.slvDecs, counts: seq(D.slvSts, -2, D.slvDecs), countLabel: 'sts after each decrease' },
        { title: 'Check length', rows: [
          { id: `${p}-len`, label: 'Measure', type: 'measure', instr: `Work in stockinette until the sleeve measures ${D.slvCm} cm (${D.slvIn} in) from the pick-up, or your desired length before the rib. = ${D.slvAfter} sts.` },
        ] },
        { title: 'Cuff', rows: [
          { id: `${p}-rib`, label: 'Rib', type: 'body', stitches: `${D.slvAfter} sts`, instr: `Change to 3 mm (US2½) double-pointed needles and work 7 cm (2¾ in) in 1x1 rib (k1, p1).` },
          { id: `${p}-dk1`, label: 'DK Rnd 1', type: 'body', noCheck: false, instr: '*K1, slip 1 st purl-wise with yarn in front*, repeat from * to * to end of round.' },
          { id: `${p}-dk2`, label: 'DK Rnd 2', type: 'body', noCheck: false, instr: '*Slip 1 st purl-wise with yarn behind, p1*, repeat from * to * to end of round.' },
          { id: `${p}-bo`, label: 'Bind Off', type: 'finish', instr: 'Bind off using the Italian bind-off (see video at www.petiteknit.com).' },
        ] },
      ] },
  ];
}

const sections = [
  { id: 'abbrev', title: 'Abbreviations & Notes', abbrev: true, rows: [],
    abbrevHTML: `
      <strong>BOR</strong> — beginning of round &nbsp;·&nbsp; <strong>CO</strong> — cast on &nbsp;·&nbsp; <strong>st(s)</strong> — stitch(es) &nbsp;·&nbsp; <strong>RS / WS</strong> — right / wrong side &nbsp;·&nbsp; <strong>k</strong> — knit &nbsp;·&nbsp; <strong>p</strong> — purl &nbsp;·&nbsp; <strong>sm / pm</strong> — slip / place marker &nbsp;·&nbsp; <strong>tbl</strong> — through the back loop<br>
      <strong>k2tog</strong> — knit 2 sts together (right-leaning decrease)<br>
      <strong>M1R</strong> — make one right. RS: insert the left needle under the strand between 2 sts from back to front, knit it. WS: same way, purl it.<br>
      <strong>M1L</strong> — make one left. RS: insert the left needle under the strand between 2 sts from front to back, knit it through the back loop. WS: same way, purl it through the back loop.<br>
      <strong>DS</strong> — double stitch (German short rows): the turn leaves one stitch with two legs. Work both legs together as one stitch when you reach it again.<br>
      <strong>Raglan st</strong> — the single stitch between two markers: knit on RS, purl on WS. The increases sit on either side of it.<br>
      <em>The increase and decrease (<u>underlined</u>) stitches are the ones to watch. Videos for the Italian cast-on, German short rows and Italian bind-off are at www.petiteknit.com.</em>
    ` },
  { id: 'materials', title: 'Materials',
    rows: [{ id: 'mat', label: 'Materials', type: 'mat',
      instr: `Yarn: ${D.sunday} g Sunday (Sandnes Garn), Arwetta (Filcolana) or Tvinni (Isager) held together with ${D.mohair} g Primo Tynn Silk Mohair (Sandnes Garn), Tilia (Filcolana) or Silk Mohair (Isager) &middot; 3 mm (US2½) circular 40 cm (16 in) and 80/100 cm (32/40 in) &middot; 4 mm (US6) circular 40, 80 and 100 cm (16, 32, 40 in) &middot; 3 mm and 4 mm double-pointed needles &middot; Markers &middot; Stitch holders` }] },
  { id: 'measurements', title: 'Finished Measurements · Size ' + D.label,
    note: `Bust: ${D.bust_in} in (${D.bust_cm} cm) · Length mid back: ${D.len_in} in (${D.len_cm} cm) · Inner sleeve: ${D.inner_in} in (${D.inner_cm} cm) · Upper arm: ${D.arm_in} in (${D.arm_cm} cm) · Armhole depth: ${D.hole_in} in (${D.hole_cm} cm). Gauge: 21 sts x 28 rows = 10 cm / 4 in in stockinette on 4 mm (US6). Wash your swatch before measuring.`,
    rows: [] },
  { id: 'yoke', title: 'Yoke · Neck',
    note: 'Worked top-down in stockinette with raglan increases. First the neck edge, then short rows at the back raise the neckline.',
    rows: [], groups: [
      { title: 'Cast On', rows: [
        { id: 'co', label: 'Cast On', type: 'cast', stitches: `${D.co} sts`, instr: `CO ${D.co} sts on 3 mm (US2½) 40 cm (16 in) circular needle using the Italian cast-on (see video at www.petiteknit.com).` },
      ] },
      { title: 'Double knitting — 2 rows', rows: [
        { id: 'dk1', label: 'Row 1', type: 'body', instr: '*K1, slip 1 st purl-wise with yarn in front*, repeat from * to * to end of row.' },
        { id: 'dk2', label: 'Row 2', type: 'body', instr: '*K1, slip 1 st purl-wise with yarn in front*, repeat from * to * to end of row.' },
      ] },
      { title: 'Neck rib', rows: [
        { id: 'join', label: 'Join', type: 'joinup', stitches: `${D.co} sts`, instr: 'Join in the round and work 4 cm (1½ in) in 1x1 rib (k1, p1). Place a marker for BOR.' },
        { id: 'chg', label: 'Needle', type: 'setup', instr: 'Change to 4 mm (US6) 40 cm (16 in) circular needle by working the 1x1 rib sts onto the new needle.' },
      ] },
      { title: 'Place raglan markers', rows: [
        { id: 'pm', label: 'Markers', type: 'setup', stitches: `${D.co} sts`,
          instr: `${D.back0} sts (right back), pm, 1 raglan st, pm, ${D.slv0} sts (right sleeve), pm, 1 raglan st, pm, ${D.front0} sts (front), pm, 1 raglan st, pm, ${D.slv0} sts (left sleeve), pm, 1 raglan st, pm, ${D.back0} sts (left back). BOR is mid back.` },
      ] },
      { id: 'sr', title: 'Short rows — Steps 1–4, work 5 times',
        note: 'German short rows. Each pass adds 8 sts. The boxes show the stitch count after each pass. Turning points, counted from the previous turn: pass 1: k2 (p2 on the WS) · pass 2: DS, then 2 sts · pass 3: DS, then 3 sts · pass 4: DS, then 3 sts · pass 5: DS, then 4 sts. Each turn works toward the middle front, so the back of the neck rises.',
        rows: shortRows('sr'), passes: 5, counts: seq(D.co, 8, 5), countLabel: 'sts after each pass' },
      { title: 'Check', rows: [
        { id: 'sr-chk', label: 'Check', type: 'measure', stitches: `${D.tot1} sts`,
          instr: `The neckline is complete and you are back at BOR. 5 increases on either side of each of the 4 raglan sts. = ${D.tot1} sts: ${D.dBack} right back, 1 raglan, ${D.dSlv} right sleeve, 1 raglan, ${D.dFront} front, 1 raglan, ${D.dSlv} left sleeve, 1 raglan, ${D.dBack} left back.` },
      ] },
    ] },
  { id: 'raglan', title: 'Yoke · Raglan Increases',
    note: `Continue in the round in stockinette, increasing every other round. Change to a longer circular needle (80 or 100 cm / 32 or 40 in) along the way as the stitches grow. ${D.reps} times = ${D.tot1} → ${D.tot2} sts. This size does not need the body-only increase rounds that larger sizes get.`,
    rows: [], groups: [
      { id: 'rag', title: `Rounds 1–2 — work ${D.reps} times`, rows: [
        { id: 'rag-1', label: 'Round 1', type: 'inc', noCheck: true,
          instr: `Knit across right back, ${MR}, sm, k raglan st, sm, ${ML}, knit across right sleeve, ${MR}, sm, k raglan st, sm, ${ML}, knit across front, ${MR}, sm, k raglan st, sm, ${ML}, knit across left sleeve, ${MR}, sm, k raglan st, sm, ${ML}, knit across left back. (+8 sts)` },
        { id: 'rag-2', label: 'Round 2', type: 'body', noCheck: true, instr: 'Knit across.' },
      ], passes: D.reps, counts: seq(D.tot1, 8, D.reps), countLabel: 'sts after each pair' },
      { title: 'Check', rows: [
        { id: 'rag-chk', label: 'Check', type: 'measure', stitches: `${D.tot2} sts`,
          instr: `= ${D.tot2} sts: ${D.eBack} right back, 1 raglan, ${D.eSlv} right sleeve, 1 raglan, ${D.eFront} front, 1 raglan, ${D.eSlv} left sleeve, 1 raglan, ${D.eBack} left back. The sleeves now have all the stitches they need.` },
      ] },
    ] },
  { id: 'divide', title: 'Divide Sleeves & Body',
    rows: [], groups: [
      { title: 'Divide', rows: [
        { id: 'div', label: 'Divide', type: 'div', stitches: `${D.body} sts`,
          instr: `Knit ${D.eBack} (right back), k raglan st, <b>place the next ${D.eSlv} sts on a stitch holder</b> (right sleeve), cast on ${D.under} new sts at the underarm using the backward loop method, k raglan st, knit ${D.eFront} (front), k raglan st, <b>place the next ${D.eSlv} sts on a stitch holder</b> (left sleeve), cast on ${D.under} new sts at the underarm, k raglan st, knit ${D.eBack} (left back).` },
        { id: 'bor', label: 'Marker', type: 'setup', instr: `There are now ${D.body} sts for the body. Place a marker for BOR in the center of the ${D.under} new sts cast on at the right underarm.` },
      ] },
    ] },
  { id: 'body', title: 'Body',
    rows: [], groups: [
      { title: 'Body', rows: [
        { id: 'body-len', label: 'Body', type: 'body', stitches: `${D.body} sts`,
          instr: `Work in the round in stockinette until the sweater measures ${D.bodyCm} cm (${D.bodyIn} in) mid back, measured from the cast-on edge, or to the desired length before the ribbed hem.` },
        { id: 'body-dec', label: 'Decrease', type: 'dec', stitches: `${D.bodyAfter} sts`,
          instr: `*K10, <u>k2tog</u>*, repeat from * to * a total of ${D.bodyDec} times, knit to end of round. = ${D.bodyAfter} sts.` },
      ] },
      { title: 'Hem', rows: [
        { id: 'body-rib', label: 'Rib', type: 'body', stitches: `${D.bodyAfter} sts`, instr: 'Change to 3 mm (US2½) 80 or 100 cm (32 or 40 in) circular needle and work 7 cm (2¾ in) in 1x1 rib (k1, p1).' },
        { id: 'body-dk1', label: 'DK Rnd 1', type: 'body', instr: '*K1, slip 1 st purl-wise with yarn in front*, repeat from * to * to end of round.' },
        { id: 'body-dk2', label: 'DK Rnd 2', type: 'body', instr: '*Slip 1 st purl-wise with yarn behind, p1*, repeat from * to * to end of round.' },
        { id: 'body-bo', label: 'Bind Off', type: 'finish', instr: 'Bind off using the Italian bind-off (see video at www.petiteknit.com).' },
      ] },
    ] },
  ...sleeveSections(1),
  ...sleeveSections(2),
  { id: 'finish', title: 'Finishing',
    rows: [
      { id: 'fin1', label: 'Ends', type: 'finish', instr: 'Weave in all yarn ends.' },
    ] },
];
// Sections made of groups list their rows through the groups.
sections.filter(s => s.groups).forEach(s => { s.rows = s.groups.flatMap(g => g.rows); });
"""

RENDER_JS = r"""
// ── State ───────────────────────────────────────────────────────────────────
// Repeated rounds/rows have no boxes of their own: the group carries one numbered
// box per pass, shown after its table, with the stitch count after that pass.
function passKey(groupId, i) { return `${groupId}-pass-${i}`; }
function groupDone(g) {
  for (let i = 1; i <= g.passes; i++) if (!state[passKey(g.id, i)]) return false;
  return true;
}
function allRowIds() {
  const ids = [];
  sections.forEach(s => {
    s.rows.forEach(r => { if (!r.noCheck) ids.push(r.id); });
    (s.groups || []).forEach(g => {
      if (g.passes) for (let i = 1; i <= g.passes; i++) ids.push(passKey(g.id, i));
    });
  });
  return ids;
}
function buildDefault() {
  const obj = {};
  allRowIds().forEach(id => obj[id] = false);
  return obj;
}
let state = buildDefault();
function loadState() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) {
      const saved = JSON.parse(raw);
      Object.keys(saved).forEach(k => { if (k in state) state[k] = saved[k]; });
    }
  } catch(e) {}
}
let saveTimer = null;
function schedSave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) {}
    const msg = document.getElementById('save-msg');
    if (msg) { msg.classList.remove('hidden'); setTimeout(() => msg.classList.add('hidden'), 1800); }
  }, 400);
}
function updateProgress() {
  const ids = allRowIds();
  const done = ids.filter(id => state[id]).length;
  const pct = ids.length ? Math.round(done / ids.length * 100) : 0;
  document.getElementById('prog-fill').style.width = pct + '%';
  document.getElementById('prog-text').textContent = `${done} of ${ids.length} steps complete`;
  document.getElementById('prog-pct').textContent = pct + '%';
}

// ── Render ──────────────────────────────────────────────────────────────────
// Column order: Done | Row | Badge | Instructions
function badgeHTML(row) {
  const side = row.side === 'WS' ? '<span class="ws-tag">WS</span>'
             : row.side === 'RS' ? '<span class="rs-tag">RS</span>' : '';
  if (row.type === 'body') return side;
  const tags = {
    cast:    '<span class="cast-tag">Cast On</span>',
    mat:     '<span class="mat-tag">Materials</span>',
    setup:   '<span class="setup-tag">Set Up</span>',
    inc:     '<span class="inc-tag">Inc</span>',
    div:     '<span class="div-tag">Divide</span>',
    dec:     '<span class="dec-tag">Dec</span>',
    measure: '<span class="meas-tag">Measure</span>',
    hold:    '<span class="div-tag">Hold</span>',
    joinup:  '<span class="div-tag">Join</span>',
    finish:  '<span class="finish-tag">Finish</span>',
  };
  const tag = tags[row.type] || '';
  return side && tag ? `<div class="tag-stack">${side}${tag}</div>` : side || tag;
}

function buildPassTracker(g, table) {
  const wrap = document.createElement('div');
  wrap.className = 'pass-tracker';
  const head = document.createElement('span');
  head.className = 'pass-lbl';
  head.textContent = g.countLabel ? `Done · ${g.countLabel}` : 'Done';
  wrap.appendChild(head);
  const dim = () => table.querySelectorAll('tbody tr').forEach(tr => tr.classList.toggle('row-done', groupDone(g)));
  for (let i = 1; i <= g.passes; i++) {
    const key = passKey(g.id, i);
    const lbl = document.createElement('label');
    lbl.className = 'pass-item' + (state[key] ? ' pass-done' : '');
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.checked = !!state[key];
    cb.addEventListener('change', () => {
      state[key] = cb.checked;
      lbl.classList.toggle('pass-done', cb.checked);
      dim();
      updateProgress(); schedSave();
    });
    const num = document.createElement('span');
    num.className = 'pass-num';
    num.textContent = i;
    lbl.appendChild(cb);
    lbl.appendChild(num);
    if (g.counts) {
      const sts = document.createElement('span');
      sts.className = 'pass-sts';
      sts.textContent = `= ${g.counts[i - 1]}`;
      lbl.appendChild(sts);
    }
    wrap.appendChild(lbl);
  }
  dim();
  return wrap;
}

function renderRow(row) {
  const tr = document.createElement('tr');
  tr.id = 'row-' + row.id;
  if (state[row.id]) tr.classList.add('row-done');
  if (row.side === 'WS') tr.classList.add('row-ws');

  const tdDone = document.createElement('td');
  if (!row.noCheck) {
    const cb = document.createElement('input');
    cb.type = 'checkbox'; cb.className = 'main-cb'; cb.checked = !!state[row.id];
    cb.addEventListener('change', () => {
      state[row.id] = cb.checked;
      tr.classList.toggle('row-done', cb.checked);
      updateProgress(); schedSave();
    });
    tdDone.appendChild(cb);
  }

  const tdLabel = document.createElement('td');
  tdLabel.innerHTML = `<span class="row-label">${row.label}</span>` +
    (row.stitches ? `<div class="stitch-count">${row.stitches}</div>` : '');

  const tdBadge = document.createElement('td');
  tdBadge.innerHTML = badgeHTML(row);

  const tdInstr = document.createElement('td');
  tdInstr.className = 'instr';
  tdInstr.innerHTML = row.instr;

  tr.appendChild(tdDone);
  tr.appendChild(tdLabel);
  tr.appendChild(tdBadge);
  tr.appendChild(tdInstr);
  return tr;
}

function makeTable(rows) {
  const noDone = rows.every(r => r.noCheck);
  const wrap = document.createElement('div');
  wrap.className = 'table-wrap';
  const tbl = document.createElement('table');
  if (noDone) tbl.className = 'no-done';
  const thead = document.createElement('thead');
  thead.innerHTML = `<tr><th>${noDone ? '' : 'Done'}</th><th>Row</th><th></th><th>Instructions</th></tr>`;
  const tbody = document.createElement('tbody');
  rows.forEach(r => tbody.appendChild(renderRow(r)));
  tbl.appendChild(thead); tbl.appendChild(tbody);
  wrap.appendChild(tbl);
  return wrap;
}

function resetAll() {
  if (!confirm('Reset all checkboxes?')) return;
  state = buildDefault();
  try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch(e) {}
  buildUI(); updateProgress();
}

function buildUI() {
  const main = document.getElementById('main-content');
  main.innerHTML = '';
  sections.forEach(section => {
    const title = document.createElement('p');
    title.className = 'section-title';
    title.textContent = section.title;
    main.appendChild(title);

    if (section.abbrev) {
      const box = document.createElement('div');
      box.className = 'abbrev-box';
      box.innerHTML = section.abbrevHTML;
      main.appendChild(box);
      return;
    }
    if (section.note) {
      const note = document.createElement('p');
      note.className = 'section-note';
      note.textContent = section.note;
      main.appendChild(note);
    }
    if (!section.rows.length) return;

    if (section.groups) {
      section.groups.forEach(g => {
        const repTitle = document.createElement('p');
        repTitle.className = 'rep-title';
        repTitle.textContent = g.title;
        main.appendChild(repTitle);
        if (g.note) {
          const gn = document.createElement('p');
          gn.className = 'section-note';
          gn.textContent = g.note;
          main.appendChild(gn);
        }
        const table = makeTable(g.rows);
        main.appendChild(table);
        if (g.passes) main.appendChild(buildPassTracker(g, table));
      });
    } else {
      main.appendChild(makeTable(section.rows));
    }
  });
  const bar = document.createElement('div');
  bar.className = 'bottom-bar';
  bar.innerHTML = '<span class="save-msg hidden" id="save-msg">✓ Progress saved</span><button class="reset-btn" onclick="resetAll()">Reset all</button>';
  main.appendChild(bar);
}

loadState(); buildUI(); updateProgress();
"""


def build(key, size):
    base = BASE_HTML.read_text()
    head = base[: base.index("</style>")]
    head = head.replace("<title>Travel Time Cowl</title>", f"<title>No Frills Sweater Size {size['label']}</title>")
    head += EXTRA_CSS + "</style>\n</head>\n"
    body = f"""<body>
<header>
  <div class="header-inner">
    <span class="yarn-icon">🧶</span>
    <h1>No Frills Sweater &middot; Size {size['label']}</h1>
    <p>Designed by Mette Wendelboe Okkels (PetiteKnit) &middot; top-down raglan in stockinette &middot; {size['bust_in']} in ({size['bust_cm']} cm) bust</p>
  </div>
</header>
<div class="progress-bar">
  <div class="prog-track"><div class="prog-fill" id="prog-fill"></div></div>
  <div class="prog-label">
    <span id="prog-text">0 of 0 steps complete</span>
    <span id="prog-pct">0%</span>
  </div>
</div>
<main id="main-content"></main>

<script>{DATA_JS.replace("__DATA__", json.dumps(size)) + RENDER_JS}</script>
</body>
</html>
"""
    out = OUTPUT_DIR / f"no-frills-sweater-{key}.html"
    out.write_text(head + body)
    print(f"Saved: {out}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for key, size in SIZES.items():
        build(key, size)


if __name__ == "__main__":
    main()
