"""tools/tokens.py — Leadline's design tokens for Figma (W3C Design Tokens format, as Tokens Studio reads it).

Generated, never typed: the inks, the identities, the ramp, the witness and the strokes come from leadline/mpl/register.json
(cert-machine's print register); the type from the register's faces; the field colours from leadline.fields, under a group
marked PROPOSED. A designer imports tokens/leadline.tokens.json; a change starts in cert-machine or in leadline.fields.

    python tools/tokens.py            write tokens/leadline.tokens.json
    python tools/tokens.py --check    refuse when the file differs from what the sources give now
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import leadline.mpl as lm  # noqa: E402
import leadline.fields as lf  # noqa: E402

R = lm.REGISTER


def build():
    tok = R['tokens']
    colour = {k: {'$type': 'color', '$value': v['hex'], '$description': v['role'] + ('' if v['status'] != 'proposed' else ' (marked proposed in the register; approved in WARRANT.md v2.3, 2026-10-29)')}
              for k, v in tok.items()}
    grey = {k: {'$type': 'color', '$value': v['grey'], '$description': 'the greyscale value of ' + k + ', as a mono laser prints it'} for k, v in tok.items()}
    P = R['patterns']
    stroke = {}
    for s in R['standings']:
        name, pat = s['standing'].lower(), s.get('pattern')
        if s['standing'] == 'REFUSED':
            stroke[name] = {'$type': 'strokeStyle', '$value': 'solid', '$description': 'no stroke: a hatched void (guide grey) and ∅ with words'}
            continue
        dash = [] if s['standing'] == 'DECIDED' else [float(v) for v in (P['CLAIM'] if s['standing'] == 'COMPUTED' else P['PICK']).split()]
        stroke[name] = {'$type': 'strokeStyle', '$value': 'solid' if not dash else {'dashArray': ['%gpx' % d for d in dash], 'lineCap': s['cap']},
                        '$description': '%s: %s; colour {colour.%s}' % (s['standing'], next(g['gloss'] for g in R['legend'] if g['standing'] == s['standing']), s['token'])}
    stroke['guide'] = {'$type': 'strokeStyle', '$value': {'dashArray': ['%gpx' % float(v) for v in P['GUIDE'].split()], 'lineCap': 'butt'}, '$description': 'a ruler or a leader: says nothing'}
    identity = {str(i + 1): {'$type': 'color', '$value': '{colour.%s}' % d['token'], '$description': 'series %d, always with the marker %s' % (i + 1, d['glyph'])} for i, d in enumerate(R['identity'])}
    fields = {}
    for role, spec in lf.ROLES.items():
        stops = lf.plotly_scale(role, 'paper', n=9)
        fields[role] = {str(k): {'$type': 'color', '$value': c} for k, (_, c) in enumerate(stops)}
        fields[role]['$description'] = 'PROPOSED: %s (%s, Crameri), paper orientation; not part of WARRANT until approved' % (spec['map'], spec['kind'])
    return {'$description': 'Leadline %s — design tokens generated from cert-machine\'s print register and leadline.fields; do not edit by hand' % __import__('leadline').__version__,
            'colour': colour, 'grey': grey, 'stroke': stroke, 'identity': identity,
            'type': {'reading': {'$type': 'fontFamily', '$value': ['Inter', 'DejaVu Sans', 'sans-serif']},
                     'labels': {'$type': 'fontFamily', '$value': ['JetBrains Mono', 'DejaVu Sans Mono', 'monospace']}},
            'fields (PROPOSED)': fields}


if __name__ == '__main__':
    out = json.dumps(build(), indent=1, ensure_ascii=False) + '\n'
    path = os.path.join(ROOT, 'tokens', 'leadline.tokens.json')
    if '--check' in sys.argv:
        if not os.path.isfile(path) or open(path, encoding='utf-8').read() != out:
            print('REFUSED  tokens/leadline.tokens.json differs from its sources')
            sys.exit(1)
        print('tokens/leadline.tokens.json: as generated')
    else:
        os.makedirs(os.path.dirname(path), exist_ok=True)
        open(path, 'w', encoding='utf-8').write(out)
        print('wrote tokens/leadline.tokens.json')
