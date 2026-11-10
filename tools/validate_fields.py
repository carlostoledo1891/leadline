"""tools/validate_fields.py — the measurements the field-colour proposal rests on, written to fields-report.json.

For every candidate Crameri map: how many of 256 samples read as yellow or orange (WARRANT v2.2 rule 6 forbids both),
whether lightness is monotone (a sequential map must be), and for the diverging maps the ΔE between the two sides at
three symmetric pairs, normal and under the three simulated colour-vision deficiencies (the grammar's validator asks
≥ 15 normal, ≥ 8 CVD). Then the proposed roles against the two colours WARRANT already has that can sit over a field:
the witness red and the print blue. Nothing in the proposal's README is typed by hand; it is read from this report.

    python tools/validate_fields.py            write fields-report.json
    python tools/validate_fields.py --check    refuse when the report differs from what this computes now
"""
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, ROOT)
import leadline.fields as wf  # noqa: E402
import leadline.mpl as wm  # noqa: E402

CANDIDATES = {'sequential': ['oslo', 'devon', 'davos', 'lapaz', 'tokyo', 'nuuk', 'acton', 'batlow', 'imola', 'turku', 'bilbao', 'grayC'],
              'diverging': ['vik', 'cork', 'broc', 'berlin', 'lisbon', 'tofino', 'bam', 'roma'],
              'cyclic': ['corkO', 'brocO', 'vikO', 'romaO', 'bamO']}
PAIRS = [(0.0, 1.0), (0.15, 0.85), (0.3, 0.7)]
VISIONS = [None, 'protan', 'deutan', 'tritan']


def hexrgb(h):
    h = h.lstrip('#')
    return np.array([int(h[i:i + 2], 16) for i in (0, 2, 4)]) / 255


def measure():
    import cmcrameri.cm as cmc
    out = {'what': 'the measurements behind warrant_fields (a proposal): Crameri maps screened by WARRANT\'s colour rules',
           'samples': 256, 'thresholds': {'normal': 15, 'cvd': 8}, 'maps': {}}
    for kind, names in CANDIDATES.items():
        for n in names:
            cm = getattr(cmc, n)
            c = cm(np.linspace(0, 1, 256))[:, :3]
            L = wf.oklab(c)[:, 0]
            row = {'kind': kind, 'yellowOrange': int(sum(wf.yellow_orange(x) for x in c)),
                   'lightnessMonotone': bool(np.all(np.diff(L) > 0) or np.all(np.diff(L) < 0)),
                   'lightness': [round(float(L.min()), 3), round(float(L.max()), 3)]}
            if kind == 'diverging':
                row['sides'] = [{'pair': list(p), **{(v or 'normal'): round(wf.delta_e(cm(p[0]), cm(p[1]), v), 1) for v in VISIONS}} for p in PAIRS]
                row['passes'] = all(s['normal'] >= 15 and min(s['protan'], s['deutan'], s['tritan']) >= 8 for s in row['sides'][:2])
            out['maps'][n] = row
    wit, blue = hexrgb(wm.REGISTER['tokens']['witness']['hex']), hexrgb(wm.REGISTER['tokens']['id-2']['hex'])
    against = {}
    for role in wf.ROLES:
        cm = wf.cmap(role, 'paper')
        xs = np.linspace(0, 1, 64)
        against[role] = {'map': cm.name,
                         'witnessWorst': round(min(min(wf.delta_e(wit, cm(x), v) for v in VISIONS) for x in xs), 1),
                         'printBlueWorst': round(min(wf.delta_e(blue, cm(x)) for x in xs), 1)}
    out['proposed'] = {r: {**wf.ROLES[r], **against[r], **{k: out['maps'][wf.ROLES[r]['map']][k] for k in ('yellowOrange', 'lightnessMonotone')}} for r in wf.ROLES}
    return out


if __name__ == '__main__':
    rep = json.dumps(measure(), indent=1, ensure_ascii=False) + '\n'
    path = os.path.join(ROOT, 'fields-report.json')
    if '--check' in sys.argv:
        if not os.path.isfile(path) or open(path, encoding='utf-8').read() != rep:
            print('REFUSED  fields-report.json differs from what the maps measure now')
            sys.exit(1)
        print('fields-report.json: as measured')
    else:
        open(path, 'w', encoding='utf-8').write(rep)
        print('wrote fields-report.json')
