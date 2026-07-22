import json, re

acts = json.load(open('acts3.json'))

CANON = {
    'DERREN SMART STAGE': 'DERREN SMART STAGE', 'PINTERS': 'PINTERS',
    'THE WAREHOUSE': 'THE WAREHOUSE', 'QUARRY': 'THE QUARRY', 'THE QUARRY': 'THE QUARRY',
    'THE PAVILION': 'THE PAVILION', 'EARTHLING': 'EARTHLING', 'THE EARTHLING': 'EARTHLING',
    'OUTBURST': 'OUTBURST', 'TERMINUS': 'TERMINUS', 'STALLIONS': 'STALLIONS',
    'THE OLD GRAMOPHONE': 'THE OLD GRAMOPHONE', 'GIANT STEPS': 'GIANT STEPS',
    'SCULPTURE GARDEN': 'SCULPTURE GARDEN', 'THE ORCHARD': 'THE ORCHARD',
    'THE ARMADILLO': 'THE ARMADILLO',
}
ORDER = ['DERREN SMART STAGE', 'PINTERS', 'THE WAREHOUSE', 'THE QUARRY', 'THE PAVILION',
         'EARTHLING', 'OUTBURST', 'TERMINUS', 'STALLIONS', 'THE OLD GRAMOPHONE',
         'GIANT STEPS', 'SCULPTURE GARDEN', 'THE ORCHARD', 'THE ARMADILLO']

# (day, canon stage, start) -> corrected artist name
RENAME = {
    ('fri', 'THE PAVILION', 480): 'PEACH',
    ('fri', 'THE OLD GRAMOPHONE', 540): 'ABA SHANTI-I',
    ('sat', 'THE PAVILION', 540): 'DOMINIC CAPELLO',
    ('sat', 'THE OLD GRAMOPHONE', 540): 'GIDEÖN (REGGAE SET)',
    ('sun', 'THE OLD GRAMOPHONE', 120): 'GREG PAULUS',
    ('sat', 'THE WAREHOUSE', 690): 'BRUNO SCHMIDT',
    ('sat', 'STALLIONS', 0): 'JANE FITZ & PAQUITA GORDON',
    ('sat', 'THE OLD GRAMOPHONE', 1380): 'KYLE TOOLE & KIAN OK',
    ('fri', 'GIANT STEPS', 1380): 'CAMERON CULLEN',
    ('sun', 'THE ORCHARD', 720): 'JASON LINDNER (LIVE KEYBOARD SOUND)',
}
# (day, stage, start) -> list of replacement acts [(artist, start, end)]
SPLIT = {
    ('fri', 'THE WAREHOUSE', 570): [('SIMO CELL (LIVE)', 570, 600), ('RHYW', 600, 630)],
}

final = {}
for day in ['thu', 'fri', 'sat', 'sun']:
    rows = []
    for a in acts.get(day, []):
        stage = CANON.get(a['stage'].strip())
        if stage is None:
            continue
        name = a['artist'].strip()
        if stage == 'TERMINUS':
            continue  # handled as a note in the app
        if name.upper() in ('CLOSED', '') or name.upper().startswith('TOURS') and stage != 'SCULPTURE GARDEN':
            continue
        if name.upper() == 'CLOSED':
            continue
        key = (day, stage, a['start'])
        if key in SPLIT:
            for nm, s, e in SPLIT[key]:
                rows.append({'stage': stage, 'artist': nm, 'start': s, 'end': e})
            continue
        if key in RENAME:
            name = RENAME[key]
        if name == 'CLOSED':
            continue
        rows.append({'stage': stage, 'artist': name, 'start': a['start'], 'end': a['end']})
    # drop dupes, sort by stage order then start
    seen = set()
    ded = []
    for r in rows:
        k = (r['stage'], r['artist'], r['start'], r['end'])
        if k in seen or r['artist'] == 'CLOSED':
            continue
        seen.add(k)
        ded.append(r)
    ded.sort(key=lambda r: (ORDER.index(r['stage']), r['start']))
    final[day] = ded

json.dump(final, open('acts_final.json', 'w'), ensure_ascii=False, indent=1)
n = sum(len(v) for v in final.values())
print('total acts:', n)
for d, v in final.items():
    print(d, len(v))
# sanity: no zero/negative durations, no artifacts of icon text
bad = [(d, r) for d, v in final.items() for r in v if r['end'] <= r['start']]
junk = [(d, r) for d, v in final.items() for r in v
        if re.search(r'YOUMAD|TERPIC|OMMUN|LITTE R?PICK', r['artist'])]
print('bad durations:', bad)
print('junk names:', junk)
