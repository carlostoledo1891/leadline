"""tools/pins.py — what Leadline takes from cert-machine, pinned by sha256 in PINS.json.

Copied byte for byte (and refused if they differ from their pin): the matplotlib kit (leadline/mpl/: its module,
register.json and the two style files) and the examples' data. Adapted (an import line, recorded as such): the kit's
three examples. Read, not copied: the grammar's sources, so a change there shows as drift.

    python tools/pins.py            write PINS.json from a cert-machine checkout (CERT_MACHINE, default ~/Projects/cert-machine)
    python tools/pins.py --check    local copies against their pins (always); cert-machine's files against them (when present)
"""
import hashlib
import json
import os
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CM = os.environ.get('CERT_MACHINE', os.path.expanduser('~/Projects/cert-machine'))
COPIED = {  # local path: cert-machine path
    'leadline/mpl/__init__.py': 'kits/warrant-mpl/warrant_mpl/__init__.py',
    'leadline/mpl/register.json': 'kits/warrant-mpl/warrant_mpl/register.json',
    'leadline/mpl/warrant-print.mplstyle': 'kits/warrant-mpl/warrant_mpl/warrant-print.mplstyle',
    'leadline/mpl/warrant-grey.mplstyle': 'kits/warrant-mpl/warrant_mpl/warrant-grey.mplstyle',
    'examples/data/README.md': 'kits/warrant-mpl/examples/data/README.md',
    'examples/data/buoy-a.json': 'kits/warrant-mpl/examples/data/buoy-a.json',
    'examples/data/contours-a20.json': 'kits/warrant-mpl/examples/data/contours-a20.json',
    'examples/data/gsm8k-501.json': 'kits/warrant-mpl/examples/data/gsm8k-501.json',
}
ADAPTED = {
    'examples/ex1_design_wave.py': 'kits/warrant-mpl/examples/ex1_design_wave.py',
    'examples/ex2_return_curve.py': 'kits/warrant-mpl/examples/ex2_return_curve.py',
    'examples/ex3_contours.py': 'kits/warrant-mpl/examples/ex3_contours.py',
}
READ = ['design/WARRANT.md', 'design/print/tokens.js', 'design/grammar.js', 'kits/warrant-mpl/README.md']


def sha(p):
    return hashlib.sha256(open(p, 'rb').read()).hexdigest()


def write():
    head = subprocess.run(['git', '-C', CM, 'rev-parse', 'HEAD'], capture_output=True, text=True).stdout.strip()
    pins = {'what': 'the cert-machine files Leadline copies (byte for byte), adapts (the import line only) or reads, by sha256',
            'source': 'github.com/carlostoledo1891/cert-machine', 'commit': head,
            'copied': {k: {'from': v, 'sha256': sha(os.path.join(CM, v))} for k, v in COPIED.items()},
            'adapted': {k: {'from': v, 'sha256': sha(os.path.join(CM, v)), 'change': 'import warrant_mpl as wm -> import leadline.mpl as wm'} for k, v in ADAPTED.items()},
            'read': {v: sha(os.path.join(CM, v)) for v in READ}}
    for k in COPIED:
        if sha(os.path.join(ROOT, k)) != pins['copied'][k]['sha256']:
            sys.exit('REFUSED  %s is not the bytes of %s' % (k, COPIED[k]))
    with open(os.path.join(ROOT, 'PINS.json'), 'w', encoding='utf-8') as f:
        json.dump(pins, f, indent=1)
        f.write('\n')
    print('PINS.json: %d copied, %d adapted, %d read, cert-machine %s' % (len(COPIED), len(ADAPTED), len(READ), head[:12]))


def check():
    pins = json.load(open(os.path.join(ROOT, 'PINS.json'), encoding='utf-8'))
    bad = [k for k, v in pins['copied'].items() if sha(os.path.join(ROOT, k)) != v['sha256']]
    for k in bad:
        print('EDITED  %s differs from its pin (a copy is never edited here; change it in cert-machine)' % k)
    moved = []
    if os.path.isdir(CM):
        for k, v in list(pins['copied'].items()) + list(pins['adapted'].items()):
            p = os.path.join(CM, v['from'])
            if not os.path.isfile(p) or sha(p) != v['sha256']:
                moved.append(v['from'])
        moved += [k for k, h in pins['read'].items() if not os.path.isfile(os.path.join(CM, k)) or sha(os.path.join(CM, k)) != h]
        for k in moved:
            print('MOVED   cert-machine %s since the pin (refresh with tools/pins.py)' % k)
    print('%d copies as pinned%s' % (len(pins['copied']) - len(bad), '' if os.path.isdir(CM) else '; cert-machine not here, its side not checked'))
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(check() if '--check' in sys.argv else write())
