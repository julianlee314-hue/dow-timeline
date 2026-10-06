#!/usr/bin/env python3
"""Assemble the published page from dow-timeline-v9.html + new events, artefacts and index data."""
import json, re, sys, os
H = os.path.dirname(os.path.abspath(__file__))
src = open(os.path.join(H, 'dow-timeline-v9.html')).read()
out = sys.argv[1] if len(sys.argv) > 1 else os.path.join(H, 'dow-timeline-v9.out.html')
new_ev = json.load(open('/mnt/project-files/dow-timeline/events-2017-2026-draft.json'))
idx = json.load(open(os.path.join(H, 'indices.json'))) if os.path.exists(os.path.join(H, 'indices.json')) else {}
art_new = json.load(open(os.path.join(H, 'manifest-new.json'))) if os.path.exists(os.path.join(H, 'manifest-new.json')) else {}

lines = src.split('\n')
for i, l in enumerate(lines):
    if l.startswith('const EVENTS = '):
        ev = json.loads(l[len('const EVENTS = '):].rstrip(';'))
        ev = [e for e in ev if e['n'] <= 121] + new_ev
        lines[i] = 'const EVENTS = ' + json.dumps(ev, ensure_ascii=False, separators=(',', ':')) + ';'
    elif l.startswith('const ARTEFACTS = /*ARTEFACTS*/'):
        a = json.loads(l[len('const ARTEFACTS = /*ARTEFACTS*/'):].rstrip(';'))
        a.update({k: v for k, v in art_new.items() if v.get('items')})
        lines[i] = 'const ARTEFACTS = /*ARTEFACTS*/' + json.dumps(a, ensure_ascii=False, separators=(',', ':')) + ';'
    elif l.startswith('const INDICES = /*INDICES*/'):
        lines[i] = 'const INDICES = /*INDICES*/' + json.dumps({k: v for k, v in idx.items() if k != 'DJI'}, separators=(',', ':')) + ';'
    elif l.startswith('const SERIES = ') and idx.get('DJI'):
        ser = json.loads(l[len('const SERIES = '):].rstrip(';'))
        ser['monthly'] = idx['DJI']
        for t, v in idx['DJI']:
            if t - int(t) > 0.9: ser['yearEnd'][str(int(t))] = v
        lines[i] = 'const SERIES = ' + json.dumps(ser, separators=(',', ':')) + ';'
open(out, 'w').write('\n'.join(lines))
print('events', len(ev), 'artefact keys', len(a), 'indices', {k: len(v) for k, v in idx.items()})
