#!/usr/bin/env python3
"""Generate the Travel Time Cowl chart (the book's Traveling Rib chart) as an SVG.

Pattern: multiple of 6 sts + 4, 16 rows, worked flat. The cowl works it over
the centre 40 sts (6 repeats + 4) between 5-st seed-stitch edges; the printed
chart, and this one, show the cable panel only.
  RS rows (odd) read right to left; WS rows (even) read left to right.
  The chart shows the RS view of every row, so WS stitches are flipped
  (k on WS = purl on the RS, p on WS = knit on the RS).

The rows below are the written instructions, expanded as
lead + repeat * n + tail, so the stitch count can be checked for any n.
The chart is drawn over one repeat (10 sts), like the printed chart, with a
red outline around the 6-st repeat of each row. The outline steps out on
Row 5, where the written repeat (*LC, p2) starts at stitch 1 instead of 3.

Usage: svg_chart_travel_time.py [output.svg]
  default output: site/library/travel-time/travel-time-chart.svg
"""

import os
import sys

# ── Written pattern ─────────────────────────────────────────────────────────
ROWS = 16
N_REPS = 1                  # repeats drawn (10 sts)
STS = 6 * N_REPS + 4

# stitch forms: 'K' / 'P' (one stitch, as worked on the row's own side)
# or a cross token ('C', width, slipped, hold)
#   slipped  how many of the FIRST (rightmost on RS) sts go to the cn
#   hold     'back' or 'front'
LC4 = ('C', 4, 2, 'front')  # 4-st LC: sl 2 to cn, hold front, k2, k2 from cn


def K(n):
    return ['K'] * n


def P(n):
    return ['P'] * n


# row: (side, lead, repeat, tail) in the order the stitches are worked
WRITTEN = {
    1: ('RS', K(2), K(2) + P(2) + K(2), K(2)),
    2: ('WS', P(2), P(2) + K(2) + P(2), P(2)),
    5: ('RS', [], [LC4] + P(2), [LC4]),
    9: ('RS', K(1) + P(1), P(1) + K(4) + P(1), P(1) + K(1)),
    10: ('WS', P(1) + K(1), K(1) + P(4) + K(1), K(1) + P(1)),
    # the OCR of the written row garbled its end; the printed chart confirms
    # the LC sits on sts 4-7, i.e. the row mirrors Row 9
    13: ('RS', K(1) + P(1), P(1) + [LC4] + P(1), P(1) + K(1)),
}
SAME_AS = {3: 1, 4: 2, 6: 2, 7: 1, 8: 2,
           11: 9, 12: 10, 14: 10, 15: 9, 16: 10}


def tok_width(tok):
    return tok[1] if isinstance(tok, tuple) else 1


def chart_row(row, n=N_REPS):
    """RS-view tokens for a row, stitch 1 (rightmost) first."""
    side, lead, rep, tail = WRITTEN[SAME_AS.get(row, row)]
    toks = lead + rep * n + tail
    assert sum(map(tok_width, toks)) == 6 * n + 4, f'row {row}, n={n}'
    if side == 'WS':
        assert all(isinstance(t, str) for t in toks)
        # worked left to right on the chart; flip to the RS view
        toks = ['P' if t == 'K' else 'K' for t in reversed(toks)]
    return toks


def repeat_span(row, n=N_REPS):
    """(first, last) stitch numbers of the asterisked repeat, RS view."""
    side, lead, rep, _ = WRITTEN[SAME_AS.get(row, row)]
    lead_w = sum(map(tok_width, lead))
    rep_w = sum(map(tok_width, rep)) * n
    if side == 'RS':
        return lead_w + 1, lead_w + rep_w
    # WS rows start at the chart's left edge, stitch STS
    return STS - lead_w - rep_w + 1, STS - lead_w


def flat(toks):
    out = []
    for t in toks:
        out += ['K'] * t[1] if isinstance(t, tuple) else [t]
    return out


# transcription checks: every row must agree with the row it says to repeat,
# and every cable row must sit on the stitch layout of its plain neighbours
for n in (1, 2, 3, 4):
    for r in range(1, ROWS + 1):
        chart_row(r, n)
assert flat(chart_row(5)) == chart_row(1)
assert flat(chart_row(13)) == chart_row(9)
for r in (2, 3, 4, 6, 7, 8):
    assert chart_row(r) == chart_row(1), r
for r in (10, 11, 12, 14, 15, 16):
    assert flat(chart_row(r)) == chart_row(9), r

# ── Geometry ────────────────────────────────────────────────────────────────
C = 32                      # cell size
X0, Y0 = 64, 120            # grid origin (top-left)
GW, GH = STS * C, ROWS * C
GR, GB = X0 + GW, Y0 + GH   # grid right / bottom
W = 560

# ── Palette (project tokens) ────────────────────────────────────────────────
INK = '#1E1A2E'
MUTED = '#6B6478'
PLUM = '#5C2D6E'
PLUM_LIGHT = '#8B4C9E'
PLUM_PALE = '#F3EAF8'
BORDER = '#E2D8EA'
WHITE = '#FFFFFF'
REP_RED = '#C8325A'         # repeat outline, like the printed chart

CABLE_BG, CABLE_BACK, CABLE_FRONT, CABLE_LINE, CABLE_EDGE = (
    '#EEF5FB', '#FFFFFF', '#CFE2F2', '#1D4F7C', '#8CAFD0')

FONT = "'Source Sans 3','Helvetica Neue',Arial,sans-serif"
MONO = "'Calling Code','SFMono-Regular',Menlo,monospace"
SERIF = "'Playfair Display',Georgia,serif"

out = []
add = out.append


def cell_x(stitch):
    """Left edge of a stitch's cell. Stitch 1 is the rightmost column."""
    return X0 + (STS - stitch) * C


def span_x(first, last):
    """Screen x range for stitches first..last (first is the rightmost)."""
    return cell_x(last), cell_x(first) + C


def row_y(n):
    """Top edge of row n. Row 1 is the bottom row."""
    return Y0 + (ROWS - n) * C


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=10, fill=INK, anchor='start', weight='400',
         font=FONT, style='normal', extra=''):
    add(f'<text x="{x:g}" y="{y:g}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}" '
        f'text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def purl_mark(cx, cy, half=6.5, fill=PLUM):
    """Purl on the RS: a dash, matching the printed stitch key."""
    add(f'<line x1="{cx - half:g}" y1="{cy:g}" x2="{cx + half:g}" y2="{cy:g}" '
        f'stroke="{fill}" stroke-width="2.2" stroke-linecap="round"/>')


def band(bx0, bx1, tx0, tx1, yb, yt, fill, stroke, sw=1.4):
    pts = f'{bx0:g},{yb:g} {bx1:g},{yb:g} {tx1:g},{yt:g} {tx0:g},{yt:g}'
    add(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw:g}" stroke-linejoin="round"/>')


def cross(first, width, slipped, hold, yt, yb):
    """Draw a cable cross over stitches first..first+width-1."""
    last = first + width - 1
    xl, xr = span_x(first, last)
    add(f'<rect x="{xl:g}" y="{yt:g}" width="{xr - xl:g}" '
        f'height="{yb - yt:g}" fill="{CABLE_BG}"/>')

    kept = width - slipped
    # right group: the first `slipped` sts; ends up in the leftmost positions
    rg_b = span_x(first, first + slipped - 1)
    rg_t = span_x(first + kept, last)
    # left group: the remaining sts; ends up in the rightmost positions
    lg_b = span_x(first + slipped, last)
    lg_t = span_x(first, first + kept - 1)

    groups = [(rg_b, rg_t), (lg_b, lg_t)]
    front_idx = 0 if hold == 'front' else 1
    for i in (1 - front_idx, front_idx):
        (b0, b1), (t0, t1) = groups[i]
        is_front = (i == front_idx)
        band(b0, b1, t0, t1, yb, yt,
             CABLE_FRONT if is_front else CABLE_BACK,
             CABLE_LINE if is_front else CABLE_EDGE,
             1.5 if is_front else 1.1)


# ── Document ────────────────────────────────────────────────────────────────
KC = 13
BRACKET_Y = GB + 38
KEY_Y = BRACKET_Y + 62
KEY_STEP = 26
KEY_ROWS = [
    ('K', 'k on RS, p on WS'),
    ('P', 'p on RS, k on WS'),
    ('LC4', '4-st LC — Sl 2 sts to cn, hold to front, k2, k2 from cn'),
]
H = int(KEY_Y + len(KEY_ROWS) * KEY_STEP + 14)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="Travel Time Cowl traveling rib chart, {STS} stitches by {ROWS} rows">')
add('<title>Travel Time Cowl — Traveling Rib Chart</title>')
add(f'<desc>Cable panel of the Travel Time Cowl: multiple of 6 stitches plus 4, shown over {STS} stitches '
    f'({N_REPS} repeat + 4), {ROWS} rows. Worked flat; right-side rows are '
    f'read right to left, wrong-side rows left to right. The red outline '
    f'marks the 6-stitch repeat.</desc>')
add(f'<rect width="{W}" height="{H}" fill="{WHITE}"/>')

# heading
text(X0, 44, 'Travel Time — Traveling Rib Chart', size=22, fill=PLUM,
     weight='600', font=SERIF)
text(X0, 66, f'Multiple of 6 sts + 4  ·  {ROWS} rows  ·  shown over {STS} sts '
     f'({N_REPS} repeat + 4)', size=11.5, fill=MUTED)
text(X0, 82, 'Worked flat — RS rows (odd) read right to left, WS rows (even) '
     'read left to right.', size=11.5, fill=MUTED, style='italic')
text(X0, 98, 'Cowl: worked over the centre 40 sts (6 repeats + 4), between '
     '5-st seed-stitch edges.', size=11.5, fill=MUTED, style='italic')

# cells
for n in range(1, ROWS + 1):
    toks = chart_row(n)
    yt = row_y(n)
    yb = yt + C
    st = 1
    for tok in toks:
        if isinstance(tok, tuple):
            _, width, slipped, hold = tok
            cross(st, width, slipped, hold, yt, yb)
            st += width
        else:
            if tok == 'P':
                x = cell_x(st)
                add(f'<rect x="{x:g}" y="{yt:g}" width="{C}" '
                    f'height="{C}" fill="{PLUM_PALE}"/>')
                purl_mark(x + C / 2, yt + C / 2)
            st += 1
    assert st == STS + 1, f'row {n} produced {st - 1} sts'

# grid lines
for i in range(STS + 1):
    x = X0 + i * C
    add(f'<line x1="{x:g}" y1="{Y0}" x2="{x:g}" y2="{GB}" '
        f'stroke="{BORDER}" stroke-width="0.8"/>')
for n in range(ROWS + 1):
    y = Y0 + n * C
    add(f'<line x1="{X0}" y1="{y:g}" x2="{GR}" y2="{y:g}" '
        f'stroke="{BORDER}" stroke-width="0.8"/>')
add(f'<rect x="{X0}" y="{Y0}" width="{GW}" height="{GH}" fill="none" '
    f'stroke="{PLUM_LIGHT}" stroke-width="1.8"/>')

# row numbers: RS rows on the right (where they start), WS rows on the left
for n in range(1, ROWS + 1):
    y = row_y(n) + C / 2 + 3.4
    if n % 2:
        text(GR + 9, y, str(n), size=10, font=MONO, fill=INK, weight='500')
    else:
        text(X0 - 9, y, str(n), size=10, font=MONO, fill=INK, weight='500',
             anchor='end')

# stitch numbers (bottom, right to left)
for n in range(1, STS + 1):
    text(cell_x(n) + C / 2, GB + 17, str(n), size=9.5, font=MONO,
         fill=MUTED, anchor='middle')

# 6-st repeat outline: each row's asterisked repeat, stepped where it moves,
# closed off below the grid by a bracket with a centred label
spans = {r: span_x(*repeat_span(r)) for r in range(1, ROWS + 1)}
left = {r: spans[r][0] for r in spans}
right = {r: spans[r][1] for r in spans}
label_half = 30


def edge_path(xs, toward):
    """Polyline down one side of the repeat, then in along the bracket."""
    pts = [(xs[ROWS], Y0)]
    for r in range(ROWS, 0, -1):
        yb = row_y(r) + C
        pts.append((xs[r], yb))
        if r > 1 and xs[r - 1] != xs[r]:
            pts.append((xs[r - 1], yb))
    pts.append((xs[1], BRACKET_Y))
    pts.append((toward, BRACKET_Y))
    return ' '.join(f'{x:g},{y:g}' for x, y in pts)


# the printed chart steps the outline out on Row 5 only
assert {r for r in left if left[r] != left[1]} == {5}
rep_cx = (left[1] + right[1]) / 2
for xs, toward in ((left, rep_cx - label_half), (right, rep_cx + label_half)):
    add(f'<polyline points="{edge_path(xs, toward)}" fill="none" '
        f'stroke="{REP_RED}" stroke-width="2.2" stroke-linejoin="miter" '
        f'stroke-linecap="butt"/>')
text(rep_cx, BRACKET_Y + 4, '6-st rep', size=11, fill=INK, anchor='middle')

# key
text(X0, KEY_Y - 16, 'Key', size=13, fill=PLUM, weight='600', font=SERIF)
KEY_TEXT_X = X0 + 4 * KC + 18

for i, (kind, label) in enumerate(KEY_ROWS):
    y = KEY_Y + i * KEY_STEP
    yt, yb = y, y + KC
    if kind in ('K', 'P'):
        add(f'<rect x="{X0}" y="{yt:g}" width="{KC}" height="{KC}" '
            f'fill="{PLUM_PALE if kind == "P" else WHITE}" '
            f'stroke="{BORDER}" stroke-width="0.9"/>')
        if kind == 'P':
            purl_mark(X0 + KC / 2, yt + KC / 2, half=3.4)
    else:
        _, width, slipped, hold = LC4
        kept = width - slipped
        add(f'<rect x="{X0}" y="{yt:g}" width="{width * KC}" '
            f'height="{KC}" fill="{CABLE_BG}" stroke="{BORDER}" '
            f'stroke-width="0.9"/>')

        # mirror of cross(), in key coordinates (left to right = st 1..width)
        def kx(a, b):
            return X0 + (width - b) * KC, X0 + (width - a + 1) * KC

        groups = [(kx(1, slipped), kx(kept + 1, width)),
                  (kx(slipped + 1, width), kx(1, kept))]
        front_idx = 0 if hold == 'front' else 1
        for j in (1 - front_idx, front_idx):
            (b0, b1), (t0, t1) = groups[j]
            is_front = (j == front_idx)
            band(b0, b1, t0, t1, yb, yt,
                 CABLE_FRONT if is_front else CABLE_BACK,
                 CABLE_LINE if is_front else CABLE_EDGE,
                 1.2 if is_front else 0.9)
    text(KEY_TEXT_X, yt + KC / 2 + 3.6, label, size=11, fill=INK)

add('</svg>')

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
dest = (sys.argv[1] if len(sys.argv) > 1 else
        os.path.join(root, 'site', 'library', 'travel-time',
                     'travel-time-chart.svg'))
os.makedirs(os.path.dirname(dest), exist_ok=True)
with open(dest, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out) + '\n')
print('wrote', dest)
