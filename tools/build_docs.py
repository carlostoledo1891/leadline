"""tools/build_docs.py — Leadline's documentation, docs/index.html, built from the package: the strokes, inks, legend words
and identities from leadline/mpl/register.json, the proposal's numbers from fields-report.json, the figures from
examples/out/. Nothing on the page that a record holds is typed here.

    python tools/build_docs.py            write docs/ (index.html, figures/, examples/, downloads)
    python tools/build_docs.py --check    refuse when docs/ differs from what the sources give now
"""
import html
import json
import os
import shutil
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
import leadline  # noqa: E402
import leadline.mpl as lm  # noqa: E402
import leadline.fields as lf  # noqa: E402

R = lm.REGISTER
REPO = 'https://github.com/carlostoledo1891/leadline'
WARRANT = 'https://carlostoledo.co/grammar/'
E = html.escape


def tok(name):
    return '#' + R['tokens'][name]['hex'].lstrip('#')


def stroke_svg(standing, w=180, h=18):
    st = next(s for s in R['standings'] if s['standing'] == standing)
    if standing == 'REFUSED':
        return ('<svg class="spec" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="refused: a hatched void">'
                '<defs><pattern id="hatch" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
                '<line x1="0" y1="0" x2="0" y2="6" stroke="%s" stroke-width="1"/></pattern></defs>'
                '<rect x="1" y="1" width="%d" height="%d" fill="url(#hatch)" stroke="%s" stroke-width="0.8"/></svg>') % (w, h, w, h, tok('guide'), w - 2, h - 2, tok('guide'))
    pat = {'DECIDED': None, 'COMPUTED': R['patterns']['CLAIM'], 'CHOSEN': R['patterns']['PICK']}[standing]
    dash = '' if pat is None else ' stroke-dasharray="%s"' % pat.replace(' ', ',')
    cap = ' stroke-linecap="round"' if st['cap'] == 'round' else ''
    return ('<svg class="spec" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="%s stroke">'
            '<line x1="2" y1="%g" x2="%d" y2="%g" stroke="%s" stroke-width="%g"%s%s/></svg>') % (
        w, h, w, h, standing.lower(), h / 2, w - 2, h / 2, tok(st['token']), R['line_pt'] * 1.4, dash, cap)


def gradient(role):
    stops = lf.plotly_scale(role, 'paper', n=9)
    return 'linear-gradient(90deg, %s)' % ', '.join('%s %d%%' % (c, round(t * 100)) for t, c in stops)


CSS = """
:root{--paper:%(paper)s;--ink:%(ink)s;--ink-2:%(ink2)s;--ink-3:%(ink3)s;--guide:%(guide)s;--grid:%(grid)s;--witness:%(witness)s;--id-2:%(id2)s;
--sans:Inter,"DejaVu Sans",system-ui,sans-serif;--mono:"JetBrains Mono","DejaVu Sans Mono",ui-monospace,monospace;color-scheme:light}
*{box-sizing:border-box}html{-webkit-text-size-adjust:100%%}
body{margin:0;background:var(--paper);color:var(--ink-2);font:16px/1.6 var(--sans)}
.wrap{max-width:880px;margin:0 auto;padding:0 16px}
header.top{border-bottom:1px solid var(--grid)}header.top .wrap{display:flex;justify-content:space-between;align-items:center;height:52px;gap:12px}
.brand{font-weight:600;color:var(--ink);text-decoration:none;letter-spacing:-.01em}.brand small{font:500 11px var(--mono);color:var(--ink-3);margin-left:8px;letter-spacing:.04em}
nav a{font:500 13px var(--sans);color:var(--ink-3);text-decoration:none;margin-left:16px}nav a:hover{color:var(--ink)}
.eyebrow{font:500 12px var(--mono);letter-spacing:.08em;text-transform:uppercase;color:var(--ink-3);margin:56px 0 12px}
h1{font-size:clamp(32px,6vw,48px);line-height:1.08;letter-spacing:-.02em;color:var(--ink);margin:0 0 20px;font-weight:600}
h2{font-size:24px;line-height:1.2;color:var(--ink);margin:64px 0 12px;font-weight:600;letter-spacing:-.01em}
h3{font-size:16px;color:var(--ink);margin:28px 0 6px;font-weight:600}
p{margin:0 0 14px;max-width:72ch}.lede{font-size:19px;line-height:1.55;color:var(--ink-2)}
blockquote{margin:24px 0;padding:0 0 0 16px;border-left:2px solid var(--ink);font-size:17px;color:var(--ink-2);max-width:70ch}
a{color:var(--ink);text-underline-offset:3px}code,pre{font-family:var(--mono);font-size:13px}
code{background:#f3f3f3;padding:1px 5px}pre{background:#f6f6f6;border:1px solid var(--grid);padding:14px 16px;overflow-x:auto;line-height:1.5}
pre code{background:none;padding:0}
.badges{display:flex;flex-wrap:wrap;gap:8px;margin:20px 0 8px}.badge{font:500 12px var(--mono);border:1px solid var(--ink);padding:3px 8px;color:var(--ink);text-decoration:none}
.badge.dim{border-color:var(--guide);color:var(--ink-3)}
.tag{display:inline-block;font:600 11px var(--mono);letter-spacing:.06em;padding:2px 7px;vertical-align:middle;margin-left:8px}
.tag.prop{border:1px dashed var(--ink-3);color:var(--ink-3)}.tag.ok{background:var(--ink);color:var(--paper)}
figure{margin:24px 0}figure img{display:block;width:100%%;height:auto;border:1px solid var(--grid)}
figcaption{font-size:14px;color:var(--ink-3);margin-top:8px;max-width:72ch}figcaption a{margin-right:14px;font-family:var(--mono);font-size:12px}
table{border-collapse:collapse;width:100%%;font-size:14px;margin:12px 0 20px}th,td{text-align:left;vertical-align:top;padding:9px 10px;border-bottom:1px solid var(--grid)}
th{font:600 11px var(--mono);letter-spacing:.06em;text-transform:uppercase;color:var(--ink-3)}td.w{white-space:nowrap}
.tablewrap{overflow-x:auto}
.spec{display:block;max-width:100%%}
.rules{padding-left:20px}.rules li{margin:0 0 8px;max-width:72ch}
.swatch{height:14px;border:1px solid var(--grid);min-width:120px}
.x{color:var(--witness);font-weight:700}
.gallery{display:grid;grid-template-columns:1fr;gap:8px}
footer{margin:80px 0 0;border-top:1px solid var(--grid);padding:24px 0 48px;font-size:13px;color:var(--ink-3)}
@media (max-width:560px){nav a{margin-left:9px;font-size:12px}.brand small{display:none}h2{margin-top:48px}.lede{font-size:17px}td,th{padding:8px 6px}}
"""


def page():
    rep = json.load(open(os.path.join(ROOT, 'fields-report.json'), encoding='utf-8'))
    legend = {g['standing']: g for g in R['legend']}
    ids = R['identity']
    css = CSS % {'paper': tok('paper'), 'ink': tok('ink'), 'ink2': tok('ink-2'), 'ink3': tok('ink-3'), 'guide': tok('guide'), 'grid': tok('grid'),
                 'witness': tok('witness'), 'id2': tok('id-2')}
    rows = []
    for s in ('DECIDED', 'COMPUTED', 'CHOSEN', 'REFUSED'):
        g = legend[s]
        pat = {'DECIDED': 'solid', 'COMPUTED': 'dashed ' + R['patterns']['CLAIM'], 'CHOSEN': 'dotted ' + R['patterns']['PICK'] + ', round caps',
               'REFUSED': 'no mark: a hatched void and ∅ in words'}[s]
        rows.append('<tr><td class="w"><b>%s</b></td><td>%s</td><td>%s<div style="font:12px var(--mono);color:var(--ink-3);margin-top:4px">%s</div></td></tr>' % (
            E(g['label']), E(g['gloss']), stroke_svg(s), E(pat)))
    idrow = ' &nbsp; '.join('<span style="color:%s">%s</span> series %d' % (tok(i['token']), i['glyph'], k + 1) for k, i in enumerate(ids))
    prop = rep['proposed']
    bam = rep['maps']['bam']
    side = bam['sides'][1]
    frows = []
    why = {'magnitude': 'sequential; lightness monotone; %d samples of 256 read as yellow or orange; more is darker on paper' % prop['magnitude']['yellowOrange'],
           'difference': 'diverging; the two sides at 15%%/85%%: ΔE %.1f normal, %.1f protan, %.1f deutan, %.1f tritan (thresholds %d and %d); %d yellow or orange' % (
               side['normal'], side['protan'], side['deutan'], side['tritan'], rep['thresholds']['normal'], rep['thresholds']['cvd'], prop['difference']['yellowOrange']),
           'direction': 'cyclic, the hues of the difference map; %d yellow or orange' % prop['direction']['yellowOrange']}
    for role in ('magnitude', 'difference', 'direction'):
        frows.append('<tr><td class="w"><b>%s</b></td><td class="w"><code>%s</code></td><td><div class="swatch" style="background:%s"></div></td><td>%s</td></tr>' % (
            role, E(prop[role]['map']), gradient(role), E(why[role])))
    passing = [n for n, m in rep['maps'].items() if m['kind'] == 'diverging' and m['yellowOrange'] == 0 and m.get('passes')]
    ex = [('ex2_return_curve', 'A return-level curve, buoy A, monthly maxima', 'Certified knots are decided; the joins between them are one curve of the many the knots allow, so they are chosen (dotted); the delta-method intervals are computed (dashed); 100 years is a guide. Beside it, the premise ladder names what the number rests on.'),
          ('ex1_design_wave', 'A design wave by block', 'The 100-year Hs by the block the maxima are taken over: the picked family decided, the other hollow, the statistical interval computed; where the choice is refused, a void and words instead of a point.'),
          ('ex3_contours', 'Environmental contours over the hours', 'Three submitted 20-year contours over the hours counted exactly into cells (the neutral order ramp); the edge a test adds to close an open file is chosen. The small side panel shows the witness on an unrelated record: a printed arithmetic step that does not hold.')]
    gal = []
    for name, title, cap in ex:
        gal.append('<figure><a href="figures/%s.svg"><img src="figures/%s.svg" alt="%s" loading="lazy"></a><figcaption><b>%s.</b> %s<br><a href="examples/plotly_%s.html">interactive (plotly)</a><a href="figures/%s-grey.svg">greyscale</a><a href="%s/blob/main/examples/%s.py">source</a></figcaption></figure>' % (
            name, name, E(title), E(title), E(cap), name, name, REPO, name))
    body = """
<header class="top"><div class="wrap"><a class="brand" href="./">Leadline<small>v%(ver)s</small></a><nav><a href="#strokes">Strokes</a><a href="#start">Start</a><a href="#examples">Examples</a><a href="#fields">Fields</a><a href="%(repo)s">GitHub</a></nav></div></header>
<main class="wrap">
<div class="eyebrow">a dialect of WARRANT · for metocean and offshore figures</div>
<h1>Every mark says what it rests on.</h1>
<p class="lede">Leadline is a visual grammar for matplotlib and plotly figures. A value an exact decision backs is drawn one way; a fitted or printed number another; a value picked from several the data allow a third. Where nothing could be decided, the figure says so in words instead of drawing a zero.</p>
<blockquote>A leadsman's calls kept two kinds of depth apart: one read at a marked fathom, <i>"by the mark five"</i>, and one judged between the marks, <i>"by the deep six"</i>. Leadline keeps the same distinction in a figure.</blockquote>
<div class="badges"><a class="badge" href="%(repo)s">GitHub</a><span class="badge">MIT</span><span class="badge">Python ≥ 3.7</span><span class="badge dim">v%(ver)s · a starter to iterate on</span></div>
<figure><a href="figures/ex2_return_curve.svg"><img src="figures/ex2_return_curve.svg" alt="A return-level curve drawn in Leadline"></a><figcaption>Return levels at a buoy: decided knots, chosen joins, computed intervals, a guide at 100 years, and the premises the numbers rest on. <a href="examples/plotly_ex2_return_curve.html">interactive</a></figcaption></figure>

<h2 id="strokes">Four strokes</h2>
<p>A mark's standing is carried by its stroke and nothing else. Verdicts are words; colour carries neither.</p>
<div class="tablewrap"><table><thead><tr><th>standing</th><th>what it rests on</th><th>stroke</th></tr></thead><tbody>%(rows)s</tbody></table></div>
<p>At most three series are compared in one figure, each with its own colour <i>and</i> marker, so a greyscale copy loses nothing: %(ids)s. The pattern <code>%(guide)s</code> is a guide (a ruler, a leader) and says nothing; no other dash pattern is ever drawn.</p>

<h2>The rules</h2>
<ol class="rules">
<li><b>Standing is not a verdict.</b> Words carry verdicts; the stroke carries standing; colour carries neither.</li>
<li><b>A pick is chosen.</b> When the data allow several values and one is shown, it is drawn dotted and the figure says "one of several".</li>
<li><b>An empty result is ∅ and words</b>, never a zero-height bar, a zero, or a gap.</li>
<li><b>One red</b>, <span class="x">×</span> only, beside words, for a counterexample that is shown.</li>
<li><b>Ink first.</b> Every figure reads completely in greyscale; a colour always comes with a shape and a word.</li>
<li><b>A legend wherever a standing is drawn</b>, in the grammar's own words.</li>
</ol>
<p>The helpers refuse what the grammar forbids: a stroke for <i>refused</i>, a void or a witness without words, a fourth series, a caller's own colour or dash on a standing line.</p>

<h2 id="start">Start</h2>
<pre><code>git clone %(repo)s && cd leadline
pip install -e ".[all]"          # matplotlib, numpy, plotly, cmcrameri</code></pre>
<h3>matplotlib</h3>
<pre><code>import leadline.mpl as lm
lm.use()                                       # or lm.use('grey'): as a mono laser printer prints it
lm.line(ax, T, levels, lm.CHOSEN, series=0)    # joins between certified knots: one curve of many
lm.knot(ax, 100, level_100, series=0)          # a decided value
lm.whisker(ax, 100, lo, hi, lm.COMPUTED)       # a statistical interval
lm.void(ax, x0, x1, y0, y1, words='choice refused: no certified fit')
lm.legend(ax, standings=(lm.COMPUTED, lm.CHOSEN, lm.REFUSED))</code></pre>
<h3>plotly</h3>
<pre><code>import leadline.plotly as lp
lp.use()                                       # the 'warrant' template; legends and colour bars under the plot
fig = lp.figure(title='Return levels')
lp.line(fig, T, levels, lp.CHOSEN, series=0)
lp.knot(fig, 100, level_100, series=0)
lp.legend_standings(fig, (lp.COMPUTED, lp.CHOSEN))</code></pre>

<h2 id="examples">Examples</h2>
<p>Drawn from public records (an NDBC buoy; dataset A of the environmental-contour benchmark), each in matplotlib for print and in plotly for the screen, each with a greyscale twin.</p>
<div class="gallery">%(gallery)s</div>

<h2 id="fields">Colour for fields <span class="tag prop">PROPOSAL</span></h2>
<p>WARRANT's colours are ink, three series identities and one neutral ramp. Metocean figures also colour a quantity spread over a plane: Hs over a basin, a density of sea states, the difference between two hindcasts, a mean direction. <code>leadline.fields</code> proposes three roles, each one of Fabio Crameri's scientific colour maps, chosen by WARRANT's own colour rules (no yellow or orange; legible under colour-vision deficiencies) and measured by <code>tools/validate_fields.py</code>.</p>
<div class="tablewrap"><table><thead><tr><th>role</th><th>map</th><th>on paper</th><th>measured</th></tr></thead><tbody>%(frows)s</tbody></table></div>
<p>Of the diverging maps measured, the ones with no yellow or orange that keep both sides apart for every vision: <code>%(passing)s</code>. Four rules come with the proposal: a field never carries standing or a verdict; on a coloured field, series are told apart by marker and word (the second-series blue sits ΔE %(blue).1f from the magnitude map); the witness <span class="x">×</span> over a field sits on a paper casing (the red sits ΔE %(wit).1f from the difference map); a colour bar names the quantity, its unit and its source. Until the proposal is approved, the neutral ramp is the approved way to draw a field.</p>
<figure><a href="figures/ex4_fields.svg"><img src="figures/ex4_fields.svg" alt="A synthetic magnitude field and a synthetic difference field in the proposed colours" loading="lazy"></a><figcaption><b>Synthetic data, for the proposal only.</b> Left: a magnitude with one interpolated level line (computed, on a paper casing). Right: a difference between two made-up hindcasts. <a href="examples/plotly_ex4_fields.html">interactive</a><a href="fields-report.json">the measurements</a></figcaption></figure>

<h2>Figma</h2>
<p>The same inks, strokes, identities, type and (marked proposed) field colours as design tokens: <a href="leadline.tokens.json">leadline.tokens.json</a>, in the W3C Design Tokens format that Tokens Studio imports. They are generated from the package, never typed.</p>

<h2>How Leadline stays WARRANT</h2>
<p>The matplotlib register is copied byte for byte from <a href="https://github.com/carlostoledo1891/cert-machine">cert-machine</a>'s print kit, and <code>PINS.json</code> names every file taken from there with its sha256 and commit. <code>python tools/pins.py --check</code> refuses an edited copy. A change to the grammar starts in cert-machine and its <a href="%(warrant)s">WARRANT page</a>; a change to the field proposal starts here.</p>
</main>
<footer><div class="wrap">Leadline v%(ver)s · MIT · the examples' data carry their own licences (<a href="%(repo)s/blob/main/examples/data/README.md">examples/data</a>) · colour maps: Crameri, Shephard &amp; Heron, <i>Nature Communications</i> 11, 5444 (2020) · <a href="%(repo)s">source</a></div></footer>
""" % {'ver': leadline.__version__, 'repo': REPO, 'warrant': WARRANT, 'rows': ''.join(rows), 'ids': idrow, 'guide': R['patterns']['GUIDE'], 'gallery': ''.join(gal),
       'frows': ''.join(frows), 'passing': ', '.join(passing), 'blue': prop['magnitude']['printBlueWorst'], 'wit': prop['difference']['witnessWorst']}
    head = ('<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>Leadline</title><meta name="description" content="Leadline: a visual grammar for matplotlib and plotly figures in which every mark says what it rests on.">'
            '<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
            '<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@500;600&display=swap" rel="stylesheet">'
            '<style>%s</style></head><body>') % css
    return head + body + '</body></html>\n'


FILES = {'figures': ['ex1_design_wave.svg', 'ex1_design_wave-grey.svg', 'ex2_return_curve.svg', 'ex2_return_curve-grey.svg', 'ex3_contours.svg', 'ex3_contours-grey.svg', 'ex4_fields.svg'],
         'examples': ['plotly_ex1_design_wave.html', 'plotly_ex2_return_curve.html', 'plotly_ex3_contours.html', 'plotly_ex4_fields.html']}


def build(out):
    os.makedirs(os.path.join(out, 'figures'), exist_ok=True)
    os.makedirs(os.path.join(out, 'examples'), exist_ok=True)
    for d, names in FILES.items():
        for n in names:
            shutil.copyfile(os.path.join(ROOT, 'examples', 'out', n), os.path.join(out, d, n))
    shutil.copyfile(os.path.join(ROOT, 'tokens', 'leadline.tokens.json'), os.path.join(out, 'leadline.tokens.json'))
    shutil.copyfile(os.path.join(ROOT, 'fields-report.json'), os.path.join(out, 'fields-report.json'))
    with open(os.path.join(out, 'index.html'), 'w', encoding='utf-8') as f:
        f.write(page())


def tree(d):
    out = {}
    for base, dirs, files in os.walk(d):
        dirs[:] = [x for x in dirs if x != '.vercel']        # the Vercel CLI's link to the project, not documentation
        for n in files:
            p = os.path.join(base, n)
            out[os.path.relpath(p, d)] = open(p, 'rb').read()
    return out


if __name__ == '__main__':
    docs = os.path.join(ROOT, 'docs')
    if '--check' in sys.argv:
        tmp = tempfile.mkdtemp()
        build(tmp)
        same = tree(tmp) == tree(docs)
        shutil.rmtree(tmp)
        if not same:
            print('REFUSED  docs/ differs from what the sources give now (python tools/build_docs.py)')
            sys.exit(1)
        print('docs/: as built')
    else:
        build(docs)
        print('wrote docs/index.html and its figures')
