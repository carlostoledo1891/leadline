"""tests/test_leadline.py — Leadline's checks, each refusal with a red control.

    python -m pytest tests/        (needs plotly and cmcrameri: pip install -e .[test])
"""
import glob
import json
import os
import re
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import matplotlib  # noqa: E402
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import leadline.mpl as lm  # noqa: E402
import leadline.plotly as lp  # noqa: E402
import leadline.fields as lf  # noqa: E402

PERMITTED = set(lm.REGISTER['patterns']['PERMITTED'])
REGISTER_HEX = {('#' + t['hex'].lstrip('#')).lower() for t in lm.REGISTER['tokens'].values()} | {('#' + t['grey'].lstrip('#')).lower() for t in lm.REGISTER['tokens'].values()}


def run(*args):
    return subprocess.run([sys.executable] + list(args), cwd=ROOT, capture_output=True, text=True)


# ---- one grammar, two libraries ------------------------------------------------------------------------------------
@pytest.mark.parametrize('standing', [lm.DECIDED, lm.COMPUTED, lm.CHOSEN])
@pytest.mark.parametrize('width', [0.8, 1.0, 1.49, 1.5, 2.0, 3.0])
def test_the_same_dash_in_both(standing, width):
    m, p = lm.dashes(standing, width), lp.dash(standing, width)
    assert (m is None and p == 'solid') or ' '.join('%g' % v for v in m) == p.replace('px', '').replace(',', ' ')


def test_dashes_are_the_grammar_s_and_never_scaled():
    for s in (lm.COMPUTED, lm.CHOSEN):
        for w in (0.5, 1, 2, 4):
            assert ' '.join('%g' % v for v in lm.dashes(s, w)) in PERMITTED


@pytest.mark.parametrize('lib', ['mpl', 'plotly'])
def test_red_controls(lib):
    if lib == 'mpl':
        fig, ax = plt.subplots()
        with pytest.raises(ValueError):
            lm.line(ax, [0, 1], [0, 1], lm.REFUSED)
        with pytest.raises(ValueError):
            lm.void(ax, 0, 1, 0, 1, words='  ')
        with pytest.raises(ValueError):
            lm.witness(ax, 0, 0, '')
        with pytest.raises(ValueError):
            lm.knot(ax, 0, 0, series=3)
        with pytest.raises(TypeError):
            lm.line(ax, [0, 1], [0, 1], lm.DECIDED, color='red')
        plt.close(fig)
    else:
        fig = lp.figure()
        with pytest.raises(ValueError):
            lp.line(fig, [0, 1], [0, 1], lp.REFUSED)
        with pytest.raises(ValueError):
            lp.void(fig, 0, 1, 0, 1, words='')
        with pytest.raises(ValueError):
            lp.witness(fig, 0, 0, ' ')
        with pytest.raises(ValueError):
            lp.knot(fig, 0, 0, series=3)
        with pytest.raises(TypeError):
            lp.line(fig, [0, 1], [0, 1], lp.DECIDED, line=dict(color='red'))


# ---- the figures ---------------------------------------------------------------------------------------------------
def test_svg_figures_draw_only_the_grammar():
    """every dash in the kit's figures is one the grammar permits, and every colour a register colour"""
    svgs = [p for p in glob.glob(os.path.join(ROOT, 'examples', 'out', 'ex[123]_*.svg'))]
    assert len(svgs) == 6
    for p in svgs:
        t = open(p, encoding='utf-8').read()
        dashes = {d.replace(',', ' ') for d in re.findall(r'stroke-dasharray: ([0-9.,]+)', t)}
        assert dashes <= PERMITTED, (p, dashes - PERMITTED)
        colours = {c.lower() for c in re.findall(r'(?:stroke|fill): (#[0-9a-fA-F]{6})', t)}
        assert colours <= REGISTER_HEX, (p, colours - REGISTER_HEX)


def test_red_control_a_planted_dash_is_seen():
    t = 'stroke-dasharray: 6,2'
    assert {d.replace(',', ' ') for d in re.findall(r'stroke-dasharray: ([0-9.,]+)', t)} - PERMITTED


def test_plotly_examples_draw_only_the_grammar():
    sys.path.insert(0, os.path.join(ROOT, 'examples'))
    import plotly_examples as px_ex
    ok_dash = {'solid'} | {','.join('%gpx' % float(v) for v in p.split()) for p in PERMITTED}
    for fn in (px_ex.ex1, px_ex.ex2, px_ex.ex3):
        fig = fn()
        for tr in fig.data:
            d = getattr(getattr(tr, 'line', None), 'dash', None)
            assert d is None or d in ok_dash, d
        for sh in fig.layout.shapes:
            assert sh.line.dash is None or sh.line.dash in ok_dash


# ---- the field-colour proposal -------------------------------------------------------------------------------------
def test_fields_report_is_what_the_maps_measure():
    r = run('tools/validate_fields.py', '--check')
    assert r.returncode == 0, r.stdout


def test_fields_proposal_keeps_the_grammar_s_colour_rules():
    rep = json.load(open(os.path.join(ROOT, 'fields-report.json'), encoding='utf-8'))
    for role, p in rep['proposed'].items():
        assert p['yellowOrange'] == 0, role                       # WARRANT v2.2 rule 6
    assert rep['proposed']['magnitude']['lightnessMonotone']      # a sequential map is ordered by lightness
    assert rep['maps']['bam']['passes']                           # the diverging map clears the CVD thresholds
    assert 'PROPOSED' in lf.STATUS


def test_red_control_a_yellow_is_seen():
    assert lf.yellow_orange((0.95, 0.85, 0.1)) and lf.yellow_orange((0.95, 0.55, 0.1)) and not lf.yellow_orange((0.2, 0.4, 0.8))


# ---- what Leadline takes from cert-machine, and the tokens ----------------------------------------------------------
def test_copies_are_their_pins():
    r = run('tools/pins.py', '--check')
    assert r.returncode == 0, r.stdout


def test_figma_tokens_are_generated():
    r = run('tools/tokens.py', '--check')
    assert r.returncode == 0, r.stdout


def test_docs_are_built_from_the_sources():
    r = run('tools/build_docs.py', '--check')
    assert r.returncode == 0, r.stdout


def test_docs_links_resolve():
    """every local href and src of docs/index.html is a file in docs/"""
    t = open(os.path.join(ROOT, 'docs', 'index.html'), encoding='utf-8').read()
    local = [u for u in re.findall(r'(?:href|src)="([^"#]+)"', t) if not re.match(r'(https?:|mailto:)', u) and u != './']
    assert local and all(os.path.isfile(os.path.join(ROOT, 'docs', u)) for u in local), [u for u in local if not os.path.isfile(os.path.join(ROOT, 'docs', u))]
