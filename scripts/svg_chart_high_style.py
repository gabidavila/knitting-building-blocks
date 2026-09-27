#!/usr/bin/env python3
"""Generate the High Style Cowl knitting chart as a standalone SVG.

Chart data mirrors site/library/high-style/high-style.html:
  26-st repeat, 39 rounds, worked in the round (every round is a RS round,
  read right to left, bottom to top).

  Resting positions
    A = P1, K6, P1, K4, P2, K4, P1, K6, P1   (6-st ropes at the panel edges)
    B = P1, K4, P1, K6, P2, K6, P1, K4, P1   (6-st ropes flanking the centre P2)

  Cable rounds fall on every 4th round (2, 6, 10 ... 38).
  Rnds 10 and 30 are the 11-st crosses that travel the ropes in and back out.
"""

import os

# ── Chart definition ────────────────────────────────────────────────────────
STS = 26
RNDS = 39

# token forms: ('K', n) ('P', n) ('C', width, slipped, hold)
#   width   total sts consumed
#   slipped how many of the FIRST (rightmost) sts go to the cable needle
#   hold    'back' or 'front'
K = lambda n: ('K', n)
P = lambda n: ('P', n)
RC6 = ('C', 6, 3, 'back')    # Sl 3 to cn, hold back,  k3, k3 from cn
LC6 = ('C', 6, 3, 'front')   # Sl 3 to cn, hold front, k3, k3 from cn
RC11 = ('C', 11, 6, 'back')  # Sl 6 to cn, hold back,  k5, k6 from cn
LC11 = ('C', 11, 5, 'front') # Sl 5 to cn, hold front, k6, k5 from cn

POS_A = [P(1), K(6), P(1), K(4), P(2), K(4), P(1), K(6), P(1)]
POS_B = [P(1), K(4), P(1), K(6), P(2), K(6), P(1), K(4), P(1)]
CABLE_A = [P(1), LC6, P(1), K(4), P(2), K(4), P(1), RC6, P(1)]
CABLE_B = [P(1), K(4), P(1), LC6, P(2), RC6, P(1), K(4), P(1)]
# the 11-st crosses are worked all-knit; the purl columns simply land elsewhere
TRAVEL_IN = [P(1), RC11, P(2), LC11, P(1)]
TRAVEL_OUT = [P(1), LC11, P(2), RC11, P(1)]


def chart_round(n):
    if n == 10:
        return TRAVEL_IN, 'travel'
    if n == 30:
        return TRAVEL_OUT, 'travel'
    in_b = 11 <= n <= 29
    if n % 4 == 2:
        return (CABLE_B if in_b else CABLE_A), 'cable'
    return (POS_B if in_b else POS_A), 'patt'


# ── Geometry ────────────────────────────────────────────────────────────────
C = 26                      # cell size
X0, Y0 = 26, 104            # grid origin (top-left)
GW, GH = STS * C, RNDS * C
GR, GB = X0 + GW, Y0 + GH   # grid right / bottom
W = 800

# ── Palette (project tokens) ────────────────────────────────────────────────
INK = '#1E1A2E'
MUTED = '#6B6478'
PLUM = '#5C2D6E'
PLUM_LIGHT = '#8B4C9E'
PLUM_PALE = '#F3EAF8'
BORDER = '#E2D8EA'
EMPH = '#BCA9CB'
WHITE = '#FFFFFF'

CABLE_BG, CABLE_BACK, CABLE_FRONT, CABLE_LINE, CABLE_EDGE = (
    '#EEF5FB', '#FFFFFF', '#CFE2F2', '#1D4F7C', '#8CAFD0')
TRAVEL_BG, TRAVEL_BACK, TRAVEL_FRONT, TRAVEL_LINE, TRAVEL_EDGE = (
    '#FDF1F1', '#FFFFFF', '#F7DADA', '#8B2020', '#D7A3A3')

FONT = "'Source Sans 3','Helvetica Neue',Arial,sans-serif"
MONO = "'Calling Code','SFMono-Regular',Menlo,monospace"

out = []
add = out.append


def cell_x(stitch):
    """Left edge of a stitch's cell. Stitch 1 is the rightmost column."""
    return X0 + (STS - stitch) * C


def span_x(first, last):
    """Screen x range for stitches first..last (first is the rightmost)."""
    return cell_x(last), cell_x(first) + C


def row_y(n):
    """Top edge of round n. Round 1 is the bottom row."""
    return Y0 + (RNDS - n) * C


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def text(x, y, s, size=10, fill=INK, anchor='start', weight='400',
         font=FONT, style='normal', extra=''):
    add(f'<text x="{x:g}" y="{y:g}" font-family="{font}" font-size="{size}" '
        f'font-weight="{weight}" font-style="{style}" fill="{fill}" '
        f'text-anchor="{anchor}"{extra}>{esc(s)}</text>')


def purl_dot(x, y, r=3.4, fill=PLUM):
    add(f'<circle cx="{x:g}" cy="{y:g}" r="{r:g}" fill="{fill}"/>')


def band(bx0, bx1, tx0, tx1, yb, yt, fill, stroke, sw=1.4):
    pts = f'{bx0:g},{yb:g} {bx1:g},{yb:g} {tx1:g},{yt:g} {tx0:g},{yt:g}'
    add(f'<polygon points="{pts}" fill="{fill}" stroke="{stroke}" '
        f'stroke-width="{sw:g}" stroke-linejoin="round"/>')


def cross(first, width, slipped, hold, yt, yb, cs=C, dot_scale=1.0):
    """Draw a cable cross over stitches first..first+width-1."""
    if cs == C:
        bg, back, front, line, edge = (
            (TRAVEL_BG, TRAVEL_BACK, TRAVEL_FRONT, TRAVEL_LINE, TRAVEL_EDGE)
            if width > 6 else
            (CABLE_BG, CABLE_BACK, CABLE_FRONT, CABLE_LINE, CABLE_EDGE))
    else:
        bg, back, front, line, edge = (
            (TRAVEL_BG, TRAVEL_BACK, TRAVEL_FRONT, TRAVEL_LINE, TRAVEL_EDGE)
            if width > 6 else
            (CABLE_BG, CABLE_BACK, CABLE_FRONT, CABLE_LINE, CABLE_EDGE))

    last = first + width - 1
    xl, xr = span_x(first, last)
    add(f'<rect x="{xl:g}" y="{yt:g}" width="{xr - xl:g}" '
        f'height="{yb - yt:g}" fill="{bg}"/>')

    kept = width - slipped
    # right group: the first `slipped` sts; ends up in the leftmost positions
    rg_b = span_x(first, first + slipped - 1)
    rg_t = span_x(first + kept, last)
    # left group: the remaining sts; ends up in the rightmost positions
    lg_b = span_x(first + slipped, last)
    lg_t = span_x(first, first + kept - 1)

    groups = [(rg_b, rg_t), (lg_b, lg_t)]
    front_idx = 0 if hold == 'front' else 1
    order = [1 - front_idx, front_idx]
    for i in order:
        (b0, b1), (t0, t1) = groups[i]
        is_front = (i == front_idx)
        band(b0, b1, t0, t1, yb, yt,
             front if is_front else back,
             line if is_front else edge,
             1.5 if is_front else 1.1)


# ── Document ────────────────────────────────────────────────────────────────
# key block metrics
KC = 13
KEY_ROWS = [
    ('K', 'K — knit'),
    ('P', 'P — purl'),
    ('RC6', '6-st RC — Sl 3 sts to cn, hold to back, k3, k3 from cn'),
    ('LC6', '6-st LC — Sl 3 sts to cn, hold to front, k3, k3 from cn'),
    ('RC11', '11-st RC — Sl 6 sts to cn, hold to back, k5, k6 from cn'),
    ('LC11', '11-st LC — Sl 5 sts to cn, hold to front, k6, k5 from cn'),
]
KEY_Y = GB + 92
KEY_STEP = 26
H = int(KEY_Y + len(KEY_ROWS) * KEY_STEP + 30)

add(f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
    f'viewBox="0 0 {W} {H}" role="img" '
    f'aria-label="High Style Cowl cable chart, 26 stitches by 39 rounds">')
add('<title>High Style Cowl — Cable Chart</title>')
add('<desc>26-stitch repeat worked 5 times around over 39 rounds. Worked in '
    'the round; read right to left, bottom to top.</desc>')
add(f'<rect width="{W}" height="{H}" fill="{WHITE}"/>')

# heading
text(X0, 44, 'High Style Cowl — Cable Chart', size=22, fill=PLUM,
     weight='600', font="'Playfair Display',Georgia,serif")
text(X0, 66, '26-st repeat  ·  39 rounds  ·  worked 5 times around (130 sts)',
     size=11.5, fill=MUTED)
text(X0, 82, 'Worked in the round — every round is a right-side round; '
     'read right to left, bottom to top.', size=11.5, fill=MUTED,
     style='italic')

# cells
for n in range(1, RNDS + 1):
    tokens, _ = chart_round(n)
    yt = row_y(n)
    yb = yt + C
    st = 1
    for tok in tokens:
        if tok[0] == 'C':
            _, width, slipped, hold = tok
            cross(st, width, slipped, hold, yt, yb)
            st += width
        else:
            kind, count = tok
            for _ in range(count):
                x = cell_x(st)
                if kind == 'P':
                    add(f'<rect x="{x:g}" y="{yt:g}" width="{C}" '
                        f'height="{C}" fill="{PLUM_PALE}"/>')
                    purl_dot(x + C / 2, yt + C / 2)
                st += 1
    assert st == STS + 1, f'round {n} produced {st - 1} sts'

# grid lines
for i in range(STS + 1):
    x = X0 + i * C
    add(f'<line x1="{x:g}" y1="{Y0}" x2="{x:g}" y2="{GB}" '
        f'stroke="{BORDER}" stroke-width="0.8"/>')
for n in range(RNDS + 1):
    y = Y0 + n * C
    add(f'<line x1="{X0}" y1="{y:g}" x2="{GR}" y2="{y:g}" '
        f'stroke="{BORDER}" stroke-width="0.8"/>')
# emphasis: the two rounds where the ropes travel
for n in (10, 30):
    y = row_y(n)
    add(f'<line x1="{X0}" y1="{y:g}" x2="{GR}" y2="{y:g}" '
        f'stroke="{EMPH}" stroke-width="1.8"/>')
add(f'<rect x="{X0}" y="{Y0}" width="{GW}" height="{GH}" fill="none" '
    f'stroke="{PLUM_LIGHT}" stroke-width="1.8"/>')

# round numbers (right side — the side reading starts from)
for n in range(1, RNDS + 1):
    y = row_y(n) + C / 2 + 3.4
    strong = (n % 5 == 0) or n == 1
    text(GR + 9, y, str(n), size=9.5, font=MONO,
         fill=INK if strong else MUTED, weight='500' if strong else '400')

# stitch numbers (bottom, right to left)
for n in (1, 5, 10, 15, 20, 25):
    text(cell_x(n) + C / 2, GB + 17, str(n), size=9.5, font=MONO,
         fill=MUTED, anchor='middle')

# 26-st repeat bracket
by = GB + 30
add(f'<path d="M {X0} {by + 6} L {X0} {by} L {GR} {by} L {GR} {by + 6}" '
    f'fill="none" stroke="{PLUM_LIGHT}" stroke-width="1.2"/>')
text(X0 + GW / 2, by + 20, '26-st repeat — work 5 times around',
     size=10.5, fill=PLUM, anchor='middle', style='italic')

# section brackets (far right)
SBX = GR + 44
for a, b, label in ((1, 10, 'Cables at the edges'),
                    (11, 30, 'Cables at the centre'),
                    (31, 39, 'Cables at the edges')):
    yt, yb = row_y(b), row_y(a) + C
    add(f'<path d="M {SBX - 5} {yt + 1} L {SBX} {yt + 1} L {SBX} {yb - 1} '
        f'L {SBX - 5} {yb - 1}" fill="none" stroke="{EMPH}" '
        f'stroke-width="1.2"/>')
    cy = (yt + yb) / 2
    text(0, 0, label, size=10, fill=PLUM_LIGHT, anchor='middle',
         style='italic',
         extra=f' transform="translate({SBX + 15:g},{cy:g}) rotate(-90)"')

# key
text(X0, KEY_Y - 16, 'Key', size=13, fill=PLUM, weight='600',
     font="'Playfair Display',Georgia,serif")
KEY_TEXT_X = X0 + 11 * KC + 18

for i, (kind, label) in enumerate(KEY_ROWS):
    y = KEY_Y + i * KEY_STEP
    yt, yb = y, y + KC
    if kind in ('K', 'P'):
        add(f'<rect x="{X0}" y="{yt:g}" width="{KC}" height="{KC}" '
            f'fill="{PLUM_PALE if kind == "P" else WHITE}" '
            f'stroke="{BORDER}" stroke-width="0.9"/>')
        if kind == 'P':
            purl_dot(X0 + KC / 2, yt + KC / 2, r=2)
    else:
        width, slipped, hold = {
            'RC6': (6, 3, 'back'), 'LC6': (6, 3, 'front'),
            'RC11': (11, 6, 'back'), 'LC11': (11, 5, 'front')}[kind]
        travel = width > 6
        bg, back, front, line, edge = (
            (TRAVEL_BG, TRAVEL_BACK, TRAVEL_FRONT, TRAVEL_LINE, TRAVEL_EDGE)
            if travel else
            (CABLE_BG, CABLE_BACK, CABLE_FRONT, CABLE_LINE, CABLE_EDGE))
        kept = width - slipped
        add(f'<rect x="{X0}" y="{yt:g}" width="{width * KC}" '
            f'height="{KC}" fill="{bg}" stroke="{BORDER}" '
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
                 front if is_front else back,
                 line if is_front else edge,
                 1.2 if is_front else 0.9)
    text(KEY_TEXT_X, yt + KC / 2 + 3.6, label, size=11, fill=INK)

text(X0, KEY_Y + len(KEY_ROWS) * KEY_STEP + 14,
     'The 11-st crosses on Rnds 10 and 30 are worked all knit — the purl '
     'columns land in a new place, which is what makes the ropes travel.',
     size=10.5, fill=MUTED, style='italic')

add('</svg>')

dest = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                    'site', 'library', 'high-style', 'high-style-chart.svg')
with open(dest, 'w', encoding='utf-8') as fh:
    fh.write('\n'.join(out) + '\n')
print('wrote', dest)
