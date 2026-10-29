#!/usr/bin/env python3
"""Build the One Day Top (size S and M) checklist HTML files.

The page chrome (fonts, colors, table layout) is taken from the Travel Time
checklist so the library keeps one look; only the pattern data and render
script live here.
"""

import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = REPO_ROOT / "site/library/one-day-top"
BASE_HTML = REPO_ROOT / "site/library/travel-time/travel-time.html"

# Values are the 3rd (S) and 4th (M) entries of the pattern's 9-size lists.
SIZES = {
    "s": dict(
        label="S", chest_in="36.1", chest_cm=92, neck_in="19.0", arm_in="7.9",
        yarn=425, co=50, k=24, r1=7, back0=38, front0=40, reps=8,
    ),
    "m": dict(
        label="M", chest_in="39.4", chest_cm=100, neck_in="19.7", arm_in="8.3",
        yarn=485, co=52, k=25, r1=8, back0=41, front0=43, reps=9,
    ),
}

EXTRA_CSS = """
u{background:#e8820c;color:#fff;text-decoration:underline;text-decoration-color:#b85f00;border-radius:2px;padding:0 2px}
.setup-tag{font-size:.68rem;font-weight:500;background:#fff3cd;color:#856404;border-radius:4px;padding:1px 6px;font-family:inherit}
.inc-tag{font-size:.68rem;font-weight:500;background:#e8f4ee;color:#2d6a4f;border-radius:4px;padding:1px 6px;font-family:inherit}
.div-tag{font-size:.68rem;font-weight:500;background:#e8eaf6;color:#3949ab;border-radius:4px;padding:1px 6px;font-family:inherit}
.meas-tag{font-size:.68rem;font-weight:500;background:#f3eaf8;color:#5c2d6e;border-radius:4px;padding:1px 6px;font-family:inherit}
.setup-tag,.inc-tag,.div-tag,.meas-tag{white-space:nowrap}
.pass-sts{font-size:.72rem;color:var(--muted);font-family:'Calling Code',monospace;user-select:none}
.pass-item.pass-done .pass-sts{color:var(--plum-light);text-decoration:line-through}
.pass-item{margin-right:6px}
"""

SCRIPT = r"""
const D = __DATA__;
const STORAGE_KEY = `one-day-top-${D.label.toLowerCase()}-v1`;

// ── Pattern data ────────────────────────────────────────────────────────────
// Yoke: 4 sts per round. Back and front: 2 sts per Row 3 + Row 4 pair.
const r1End = D.co + 4 * D.r1;
const backEnd = D.back0 + 2 * D.reps;
const frontEnd = D.front0 + 2 * D.reps;
const joinSts = backEnd + frontEnd;
const seq = (start, step, n) => Array.from({ length: n }, (_, i) => start + step * (i + 1));

const MK = '<u>m1l</u>', MR = '<u>m1r</u>';

const yokeRows = [
  { id: 'r1', label: 'Round 1', type: 'inc', stitches: '+4 sts per round', noCheck: true,
    instr: `k1, sm, ${MK}, k to m, ${MR}, sm, k1, sm, ${MK}, k to m, ${MR}, sm` },
];

function sideRows(prefix, start, noCheck) {
  return [
    { id: `${prefix}-1`, label: 'Row 1', type: 'body', side: 'RS', stitches: `${start} sts`, noCheck, instr: 's2b, k to end' },
    { id: `${prefix}-2`, label: 'Row 2', type: 'body', side: 'WS', stitches: `${start} sts`, noCheck, instr: 's2f, p to end' },
  ];
}
function shapeRows(prefix, start, end) {
  return [
    { id: `${prefix}-3`, label: 'Row 3', type: 'inc', side: 'RS', stitches: '+2 sts per pair', noCheck: true,
      instr: `s2b, k1, ${MK}, k to 3 sts before end, ${MR}, k3` },
    { id: `${prefix}-4`, label: 'Row 4', type: 'body', side: 'WS', stitches: `${end} sts`, noCheck: true, instr: 's2f, p to end' },
  ];
}
function measureRow(id, text) {
  return { id, label: 'Measure', type: 'measure', instr: text };
}

function pieceGroups(prefix, start, end) {
  return [
    { title: 'Rows 1–2 — repeat until the piece measures 13 cm (5 in)', rows: sideRows(prefix + '-a', start, true) },
    { title: 'Check length', rows: [measureRow(`${prefix}-len`, 'Piece measures 13 cm (5 in) (about 26 rows at gauge).')] },
    { id: `${prefix}-shape`, title: `Rows 3–4 — work ${D.reps} times`, rows: shapeRows(prefix, start, end), passes: D.reps,
      counts: seq(start, 2, D.reps), countLabel: 'sts after each pair' },
  ];
}

const sections = [
  { id: 'abbrev', title: 'Abbreviations & Notes', abbrev: true, rows: [],
    abbrevHTML: `
      <strong>BOR</strong> — beginning of round &nbsp;·&nbsp; <strong>CO</strong> — cast on &nbsp;·&nbsp; <strong>BO</strong> — bind off &nbsp;·&nbsp; <strong>st(s)</strong> — stitch(es) &nbsp;·&nbsp; <strong>RS / WS</strong> — right / wrong side &nbsp;·&nbsp; <strong>k</strong> — knit &nbsp;·&nbsp; <strong>p</strong> — purl &nbsp;·&nbsp; <strong>m</strong> — marker &nbsp;·&nbsp; <strong>pm / sm</strong> — place / slip marker<br>
      <strong>s2b</strong> — slip 2 sts from left to right needle with yarn at the back<br>
      <strong>s2f</strong> — slip 2 sts from left to right needle with yarn in front<br>
      <strong>m1l</strong> — make one left: with left needle, pick up the bar between stitches from front to back and knit through the back loop<br>
      <strong>m1r</strong> — make one right: with left needle, pick up the bar between stitches from back to front and knit through the front loop<br>
      <em>The increase (<u>underlined</u>) stitches are the ones to watch. Work m1l and m1r loosely.</em>
    ` },
  { id: 'materials', title: 'Materials',
    rows: [{ id: 'mat', label: 'Materials', type: 'mat',
      instr: `Yarn: about ${D.yarn} yds of bulky/worsted weight yarn to obtain gauge &middot; US 11 (8 mm) circular needles long enough for magic loop &middot; Tapestry needle &middot; Scrap yarn &middot; Markers` }] },
  { id: 'measurements', title: 'Finished Measurements · Size ' + D.label,
    note: `Chest: ${D.chest_in} in (${D.chest_cm} cm) · Neck circumference: ${D.neck_in} in · Armhole depth: ${D.arm_in} in · Body length after join: 7 in (18 cm). Gauge: 12 sts x 20 rows = 10 cm / 4 in in stockinette after blocking.`,
    rows: [] },
  { id: 'cast-on', title: 'Cast On',
    note: 'Cast on loosely: you may hold two needles together and use a long-tail cast on.',
    rows: [
      { id: 'co', label: 'Cast On', type: 'cast', stitches: `${D.co} sts`, instr: `CO ${D.co} sts rather loosely. Join to work in the round and pm for BOR.` },
    ] },
  { id: 'yoke', title: 'Yoke · Shoulder Increases',
    note: `Round 1 adds 4 sts every time (one at each end of the two ${D.k}-st sections). Worked ${D.r1} times, the stitch count goes ${D.co} → ${r1End}. The numbers beside each box show how many sts you have after that round. The book says "repeat from the beginning once": that means the sequence is worked twice in total, written out in full below.`,
    rows: [],
    groups: [
      { title: 'Set Up Round', rows: [{ id: 'setup', label: 'Set Up', type: 'setup', stitches: `${D.co} sts`, instr: `k1, pm, k${D.k}, pm, k1, pm, k${D.k}` }] },
      { id: 'yoke-r1', title: `Round 1 — work ${D.r1} times`, rows: yokeRows, passes: D.r1,
        counts: seq(D.co, 4, D.r1), countLabel: 'sts after each round' },
      { title: 'Divide Front & Back', rows: [
        { id: 'div', label: 'Divide', type: 'div', side: 'WS', stitches: `${D.back0} back · ${D.front0} front`,
          instr: `Turn to WS and purl to m, place all remaining sts to BOR m onto scrap yarn and remove all markers. Now you have ${D.back0} back sts on needles and ${D.front0} front sts on scrap yarn. The front is 2 sts wider because both single stitches go with it.` },
      ] },
    ] },
  { id: 'back', title: 'Back',
    note: 'Slip the first 2 sts of every row. Row 1 is the first RS row after the divide.',
    rows: [], groups: [
      ...pieceGroups('back', D.back0, backEnd),
      { title: 'Put On Hold', rows: [{ id: 'back-hold', label: 'Hold', type: 'hold', stitches: `${backEnd} sts`, instr: `Cut yarn and place all back sts onto scrap yarn. = ${backEnd} sts` }] },
    ] },
  { id: 'front', title: 'Front',
    note: 'Pick up the front sts from scrap yarn and work the same way as the back. The book does not say so, but the yarn was cut after the back, so rejoin it at the start of a RS row.',
    rows: [], groups: [
      ...pieceGroups('front', D.front0, frontEnd),
      { title: 'Join Front & Back', rows: [{ id: 'join', label: 'Join', type: 'joinup', stitches: `${joinSts} sts`, instr: `With RS facing, join front and back. = ${joinSts} sts (${backEnd} back + ${frontEnd} front)` }] },
    ] },
  { id: 'body', title: 'Body',
    rows: [
      { id: 'body-rnds', label: 'Body', type: 'body', stitches: `${joinSts} sts`, instr: 'Work in the round in stockinette st (knit every round) for 18 cm (7 in) or until desired length.' },
      { id: 'bo', label: 'Bind Off', type: 'finish', instr: 'BO all sts knitwise.' },
    ] },
  { id: 'finish', title: 'Finishing',
    rows: [
      { id: 'fin1', label: 'Ends', type: 'finish', instr: 'Weave in all yarn ends.' },
      { id: 'fin2', label: 'Block', type: 'finish', instr: 'Wet block the top. When it is almost dry, put it on a hanger; this shapes the neckline the right way.' },
    ] },
];
// Sections made of groups list their rows through the groups.
sections.filter(s => s.groups).forEach(s => { s.rows = s.groups.flatMap(g => g.rows); });

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
    head = head.replace("<title>Travel Time Cowl</title>", f"<title>One Day Top Size {size['label']}</title>")
    head += EXTRA_CSS + "</style>\n</head>\n"
    body = f"""<body>
<header>
  <div class="header-inner">
    <span class="yarn-icon">🧶</span>
    <h1>One Day Top &middot; Size {size['label']}</h1>
    <p>Designed by Svetlana Volkova (Tweedysheep) &middot; boat neck top, worked top-down in stockinette &middot; {size['chest_in']} in ({size['chest_cm']} cm) chest</p>
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

<script>{SCRIPT.replace("__DATA__", json.dumps(size))}</script>
</body>
</html>
"""
    out = OUTPUT_DIR / f"one-day-top-{key}.html"
    out.write_text(head + body)
    print(f"Saved: {out}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    for key, size in SIZES.items():
        build(key, size)


if __name__ == "__main__":
    main()
