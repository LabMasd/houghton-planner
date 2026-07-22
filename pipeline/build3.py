import json, re
from collections import defaultdict

pages = json.load(open('pdf_ops.json'))
PAGES = {2: 'thu', 3: 'thu', 4: 'fri', 5: 'fri', 6: 'sat', 7: 'sat', 8: 'sun', 9: 'sun'}
W = H = 595.3
out = defaultdict(list)


def cluster1d(vals, tol):
    vals = sorted(vals)
    groups = []
    for v in vals:
        if groups and v - groups[-1][-1] <= tol:
            groups[-1].append(v)
        else:
            groups.append([v])
    return [sum(g) / len(g) for g in groups]


for pg in pages:
    if pg['page'] not in PAGES:
        continue
    day = PAGES[pg['page']]
    ops = pg['ops']
    # cut everything before the LAST full-page fill (hidden old lineup layer)
    cut = 0
    for i, o in enumerate(ops):
        if o[0] == 'path' and o[1] == 'F' and o[2] < 5 and o[3] > W - 5 and o[4] < 5 and o[5] > H - 5:
            cut = i
    ops = ops[cut + 1:]

    chars, segs = [], []
    GREEN = '(0.69, 0.595, 0.56, 0.655)'
    seen = set()
    for o in ops:
        if o[0] == 'char':
            _, c, x0, x1, y0, y1, col = o
            if not c.strip() or col == GREEN:
                continue
            k = (c, round(x0), round(y0))
            if k in seen:
                continue
            seen.add(k)
            chars.append({'c': c, 'x0': x0, 'x1': x1, 'y0': y0, 'y1': y1, 'col': col})
        else:
            _, t, x0, x1, y0, y1, col = o
            w = x1 - x0
            h = y1 - y0
            if w < 3 and h > 3:
                segs.append({'kind': 'v', 'x': (x0 + x1) / 2, 'y0': y0, 'y1': y1})
            elif h < 3 and w > 8:
                segs.append({'kind': 'h', 'y': (y0 + y1) / 2, 'x0': x0, 'x1': x1})

    # time labels (left gutter), zeros render as 'O'
    rows = defaultdict(list)
    for c in chars:
        if c['x0'] < W * 0.085:
            rows[round((c['y0'] + c['y1']) / 2 / 3) * 3].append(c)
    tlabels = []
    for y, cs in rows.items():
        cs.sort(key=lambda c: c['x0'])
        s = ''.join(c['c'] for c in cs)
        if re.fullmatch(r'[O0-9]{2}:[O0-9]{2}', s):
            tlabels.append(sum((c['y0'] + c['y1']) / 2 for c in cs) / len(cs))
    tlabels.sort(reverse=True)

    # hour line for label i = nearest gutter tick above its center
    ticks = cluster1d([s['y'] for s in segs if s['kind'] == 'h' and s['x0'] < 50 and (s['x1'] - s['x0']) < 40], 2)
    ys, mins = [], []
    for i, yc in enumerate(tlabels):
        above = [t for t in ticks if t > yc]
        if not above:
            continue
        ys.append(min(above))
        mins.append(i * 60)
    n = len(ys)
    sy = sum(ys); sm = sum(mins)
    syy = sum(y * y for y in ys); sym = sum(y * m for y, m in zip(ys, mins))
    slope = (n * sym - sy * sm) / (n * syy - sy * sy)
    intercept = (sm - slope * sy) / n

    def y2min(y):
        return slope * y + intercept

    def snap(m):
        return int(round(m / 15.0) * 15)

    topy = max(ys)  # 09:00 grid line

    # column edges from vertical segments
    vxs = cluster1d([s['x'] for s in segs if s['kind'] == 'v' and (s['y1'] - s['y0']) > 3 and s['x'] > W * 0.075], 4)
    cov = defaultdict(float)
    for s in segs:
        if s['kind'] == 'v' and s['x'] > W * 0.075:
            for x in vxs:
                if abs(s['x'] - x) <= 4:
                    cov[x] += s['y1'] - s['y0']
    vxs = [x for x in vxs if cov[x] > H * 0.25]

    hdr = [c for c in chars if (c['y0'] + c['y1']) / 2 > topy + 2 and c['x0'] > W * 0.06]
    cols = []
    for i in range(len(vxs) - 1):
        L, R = vxs[i], vxs[i + 1]
        if R - L < 30:
            continue
        hc = [c for c in hdr if L < (c['x0'] + c['x1']) / 2 < R]
        if not hc:
            continue
        lns = defaultdict(list)
        for c in hc:
            lns[round((c['y0'] + c['y1']) / 2 / 4) * 4].append(c)
        parts = []
        for y in sorted(lns, reverse=True):
            seq = sorted(lns[y], key=lambda c: c['x0'])
            s = ''
            for j, c in enumerate(seq):
                if j > 0 and c['x0'] - seq[j - 1]['x1'] > 1.4:
                    s += ' '
                s += c['c']
            parts.append(s.strip())
        cols.append({'left': L, 'right': R, 'name': ' '.join(parts).strip()})

    for c in cols:
        L, R = c['left'], c['right']
        bs = cluster1d([s['y'] for s in segs if s['kind'] == 'h' and s['x0'] < L + 8 and s['x1'] > R - 8 and s['y'] <= topy + 4], 3)
        cc = [ch for ch in chars if L < (ch['x0'] + ch['x1']) / 2 < R and (ch['y0'] + ch['y1']) / 2 < topy]
        cells = defaultdict(list)
        for ch in cc:
            cy = (ch['y0'] + ch['y1']) / 2
            below = [b for b in bs if b < cy]
            above = [b for b in bs if b > cy]
            if not below or not above:
                continue
            cells[(max(below), min(above))].append(ch)
        for (b0, b1), cs in sorted(cells.items(), key=lambda kv: -kv[0][1]):
            lns = defaultdict(list)
            for ch in cs:
                lns[round((ch['y0'] + ch['y1']) / 2 / 4) * 4].append(ch)
            parts = []
            for y in sorted(lns, reverse=True):
                seq = sorted(lns[y], key=lambda ch: ch['x0'])
                med = sorted(ch['x1'] - ch['x0'] for ch in seq)[len(seq) // 2]
                gap = max(0.9, med * 0.35)
                s = ''
                for j, ch in enumerate(seq):
                    if j > 0 and ch['x0'] - seq[j - 1]['x1'] > gap:
                        s += ' '
                    s += ch['c']
                parts.append(s.strip())
            name = re.sub(r'\s+', ' ', ' '.join(parts)).strip()
            out[day].append({'stage': c['name'], 'artist': name,
                             'start': snap(y2min(b1)), 'end': snap(y2min(b0)), 'page': pg['page']})

json.dump(dict(out), open('acts3.json', 'w'), indent=1)


def fmt(m):
    h = (9 + m // 60) % 24
    return f"{h:02d}:{m % 60:02d}"


for d in ['thu', 'fri', 'sat', 'sun']:
    print('=' * 10, d)
    for a in out[d]:
        if a['artist'].replace(' ', '') not in ('CLOSED', ''):
            print(f"  {a['stage'][:20]:20} {fmt(a['start'])}-{fmt(a['end'])}  {a['artist']}")
