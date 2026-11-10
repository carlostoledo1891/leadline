"""leadline.plotly: WARRANT's print register for plotly, the same grammar as leadline.mpl and the same refusals.

A mark's STANDING is carried by its stroke and nothing else:

    DECIDED    solid            an exact decision backs it (an enclosure, an exact comparison, a proof)
    COMPUTED   dashed 5 4       float, a solver's tolerance, a fit, a number someone printed
    CHOSEN     dotted 1 5       one member of a set the data admit, picked by something that is not the data
    REFUSED    no mark          the instrument declined or the input is missing: a hatched void and the sign for the
                                empty set in words, never a zero, never a gap

Every value is read from leadline/mpl/register.json (cert-machine's design/print/ generates it): the same inks, dashes,
identities, ramp and legend words as the matplotlib kit, so a figure drawn with either reads the same.

What plotly cannot do, said rather than hidden:
  - line caps are not settable on scatter lines, so CHOSEN's dotted 1 5 is drawn with butt caps (short dashes, not
    round dots); the pattern, which carries the standing, is the grammar's;
  - shapes take no hatch, so a void is a scatter polygon with plotly's fill pattern '/', its edge in the guide grey.

    import leadline.plotly as wp
    fig = wp.figure()                       # the template applied
    wp.line(fig, x, y, wp.COMPUTED)         # a fit: dashed 5 4
    wp.knot(fig, 100, 9.4, series=0)        # a decided value
    wp.legend_standings(fig, (wp.DECIDED, wp.COMPUTED))

MIT licensed.
"""
import copy
import json
import os

import plotly.graph_objects as go
import plotly.io as pio

__all__ = ['DECIDED', 'COMPUTED', 'CHOSEN', 'REFUSED', 'REGISTER', 'TEMPLATE', 'use', 'figure', 'colour', 'dash', 'line',
           'knot', 'whisker', 'guide', 'void', 'witness', 'ramp_scale', 'legend_standings', 'series_colour', 'colorbar_below']


def colorbar_below(title, y=-0.30, x=0.0, length=1.0):
    """A horizontal colour bar under the plot (a field's bar belongs with its quantity and unit; at the side it takes a
    phone's width): pass as a trace's colorbar=."""
    return dict(orientation='h', title=dict(text=title, side='top'), x=x, xanchor='left', y=y, yanchor='top', len=length, thickness=10, outlinewidth=0)

_REG = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'mpl', 'register.json')
with open(_REG, encoding='utf-8') as _fh:
    REGISTER = json.load(_fh)

DECIDED, COMPUTED, CHOSEN, REFUSED = 'DECIDED', 'COMPUTED', 'CHOSEN', 'REFUSED'
_P = REGISTER['patterns']
_ST = {s['standing']: s for s in REGISTER['standings']}
_LG = {g['standing']: g for g in REGISTER['legend']}
LINE_PX = REGISTER['line_pt']
_state = {'mode': 'colour', 'identity_hue': True}
_STROKE_KW = ('line', 'line_color', 'line_dash', 'opacity', 'marker_color')
FONT = 'Inter, "DejaVu Sans", Arial, sans-serif'
MONO = '"JetBrains Mono", "DejaVu Sans Mono", monospace'
SYMBOL = {'o': 'circle', 's': 'square', '^': 'triangle-up'}


def colour(token, mode=None):
    """A register colour by name ('ink', 'ink-3', 'witness', 'o-3', ...), in the current mode (or the one given)."""
    t = REGISTER['tokens'][token.lstrip('-')]
    m = mode or _state['mode']
    return '#' + (t['grey'] if m == 'grey' else t['hex']).lstrip('#')


def _template(mode):
    c = lambda k: colour(k, mode)  # noqa: E731
    ids = REGISTER['identity']
    colorway = [c(i['token']) for i in ids]
    axis = dict(showline=True, linecolor=c('ink-3'), linewidth=0.8, ticks='outside', tickcolor=c('ink-3'), ticklen=3, tickwidth=0.8,
                tickfont=dict(family=FONT, size=10, color=c('ink-3')), title=dict(font=dict(family=FONT, size=11, color=c('ink-2'))),
                showgrid=True, gridcolor=c('grid'), gridwidth=0.5, zeroline=False, mirror=False)
    return go.layout.Template(layout=go.Layout(
        paper_bgcolor=c('paper'), plot_bgcolor=c('paper'), colorway=colorway,
        font=dict(family=FONT, size=11, color=c('ink')),
        title=dict(font=dict(family=FONT, size=13, color=c('ink')), x=0, xanchor='left'),
        xaxis=axis, yaxis=copy.deepcopy(axis),
        # the legend under the plot, horizontal: at a phone's 390 px a legend at the side takes half the figure
        legend=dict(bgcolor='rgba(0,0,0,0)', borderwidth=0, font=dict(family=FONT, size=10, color=c('ink')), orientation='h',
                    yanchor='top', y=-0.16, xanchor='left', x=0, itemwidth=30),
        hoverlabel=dict(bgcolor=c('paper'), bordercolor=c('ink-3'), font=dict(family=MONO, size=10, color=c('ink'))),
        margin=dict(l=52, r=12, t=40, b=40),
        coloraxis=dict(colorbar=dict(outlinewidth=0, tickfont=dict(family=FONT, size=10, color=c('ink-3')))),
    ))


TEMPLATE = {'colour': _template('colour'), 'grey': _template('grey')}
pio.templates['warrant'] = TEMPLATE['colour']
pio.templates['warrant-grey'] = TEMPLATE['grey']


def use(mode='colour', identity_hue=True):
    """Make 'warrant' (or 'warrant-grey': every colour its greyscale value, as a mono laser prints it) plotly's default
    template. identity_hue=False draws the second series in ink-2 instead of the print blue."""
    if mode not in ('colour', 'grey'):
        raise ValueError("mode is 'colour' or 'grey'")
    _state['mode'] = mode
    _state['identity_hue'] = bool(identity_hue)
    pio.templates.default = 'warrant' if mode == 'colour' else 'warrant-grey'


def figure(**layout):
    """A go.Figure with the current mode's template."""
    fig = go.Figure()
    fig.update_layout(template=TEMPLATE[_state['mode']], **layout)
    return fig


def _px(pattern):
    return ','.join('%gpx' % float(v) for v in pattern.split())


def dash(standing, width=None):
    """The plotly dash a standing takes at a stroke width: design/grammar.js's patterns in px and its rule (below 1.5
    the short variant), never scaled by width. 'solid' for DECIDED."""
    w = LINE_PX if width is None else width
    small = w < _P['SMALL_BELOW']
    if standing == DECIDED:
        return 'solid'
    if standing == COMPUTED:
        return _px(_P['CLAIM_SM'] if small else _P['CLAIM'])
    if standing == CHOSEN:
        return _px(_P['PICK_SM'] if small else _P['PICK'])
    if standing == REFUSED:
        raise ValueError('a REFUSED mark has no stroke: draw void() and say what was refused in words')
    raise ValueError('unknown standing %r' % (standing,))


def _identity(series):
    ids = REGISTER['identity']
    if not 0 <= series < len(ids):
        raise ValueError('at most %d series are compared in one figure (WARRANT v2.2 rule 4)' % len(ids))
    return ids[series]


def series_colour(series):
    """The colour of the n-th series compared in a figure (0, 1, 2)."""
    i = _identity(series)
    tok = i['fallback'] if (i.get('fallback') and not _state['identity_hue']) else i['token']
    return colour(tok)


def _refuse_stroke_kwargs(kw):
    bad = [k for k in _STROKE_KW if k in kw]
    if bad:
        raise TypeError('the stroke is read from the standing and the series, never chosen by the caller: drop %s' % ', '.join(bad))


def _add(fig, trace, row, col):
    if row is not None:
        fig.add_trace(trace, row=row, col=col)
    else:
        fig.add_trace(trace)
    return trace


def line(fig, x, y, standing=DECIDED, series=None, width=None, on_field=False, name=None, row=None, col=None, **kw):
    """A line whose stroke says its standing. series (0, 1, 2) takes that series' colour; without one, the standing's
    own tone. on_field draws a paper casing under it, for a line over a coloured or ramp field."""
    _refuse_stroke_kwargs(kw)
    w = LINE_PX if width is None else width
    d = dash(standing, w)
    c = series_colour(series) if series is not None else colour(_ST[standing]['token'])
    if on_field:
        _add(fig, go.Scatter(x=list(x), y=list(y), mode='lines', line=dict(color=colour('paper'), width=w + 2.5), hoverinfo='skip', showlegend=False), row, col)
    kw.setdefault('showlegend', name is not None)
    return _add(fig, go.Scatter(x=list(x), y=list(y), mode='lines', name=name, line=dict(color=c, width=w, dash=d), **kw), row, col)


def whisker(fig, x, lo, hi, standing=COMPUTED, series=None, width=None, row=None, col=None, **kw):
    """An interval drawn as a vertical line from lo to hi, in its standing's stroke."""
    return line(fig, [x, x], [lo, hi], standing, series=series, width=width, row=row, col=col, **kw)


def knot(fig, x, y, series=0, hollow=False, size=7, on_field=False, name=None, row=None, col=None, **kw):
    """A decided value at a point: its series' colour and marker. hollow is the figure's own second meaning (say it in
    the legend). A value that is not decided is a line or a whisker in its standing, not a knot."""
    i = _identity(series)
    c = series_colour(series)
    sym = SYMBOL[i['marker']] + ('-open' if hollow else '')
    if on_field:
        _add(fig, go.Scatter(x=[x], y=[y], mode='markers', marker=dict(symbol=SYMBOL[i['marker']], size=size + 3, color=colour('paper')), hoverinfo='skip', showlegend=False), row, col)
    kw.setdefault('showlegend', name is not None)
    return _add(fig, go.Scatter(x=[x], y=[y], mode='markers', name=name, marker=dict(symbol=sym, size=size, color=c, line=dict(color=c, width=1)), **kw), row, col)


def guide(fig, x=None, y=None, width=0.8, row=None, col=None):
    """A ruler at x (vertical) or y (horizontal) in the guide pattern 2 3: it says nothing."""
    if (x is None) == (y is None):
        raise ValueError('a guide is at an x or at a y')
    kw = dict(line=dict(color=colour('guide'), width=width, dash=_px(_P['GUIDE'])), layer='below')
    if row is not None:
        kw.update(row=row, col=col)
    return fig.add_vline(x=x, **kw) if x is not None else fig.add_hline(y=y, **kw)


def void(fig, x0, x1, y0, y1, words=None, row=None, col=None):
    """REFUSED: no mark. A hatched void over [x0, x1] x [y0, y1] and the words that say what was refused, after the
    sign for the empty set. Never a zero, never a gap."""
    if not words or not str(words).strip():
        raise ValueError('the void is drawn with words: say what was refused')
    v = _ST[REFUSED]['void']
    _add(fig, go.Scatter(x=[x0, x1, x1, x0, x0], y=[y0, y0, y1, y1, y0], mode='lines', fill='toself', hoverinfo='skip', showlegend=False,
                         line=dict(color=colour(v['edge']), width=0.6),
                         fillpattern=dict(shape='/', fgcolor=colour(v['edge']), bgcolor=colour('paper'), size=6, solidity=0.15)), row, col)
    ann = dict(x=(x0 + x1) / 2, y=y1, yanchor='top', text=v['glyph'] + ' ' + str(words).replace('\n', '<br>'), showarrow=False,
               font=dict(size=10, color=colour('ink')), bgcolor=colour('paper'))
    if row is not None:
        ann.update(row=row, col=col)
    fig.add_annotation(**ann)
    return fig


def witness(fig, x, y, words, row=None, col=None):
    """The witness: the one red, on a cross at (x, y), beside the words that say what it shows (WARRANT rule 5). Only
    for a counterexample that is SHOWN, to a claim someone made about that object's own record."""
    if not words or not str(words).strip():
        raise ValueError('the witness is a cross beside words (WARRANT rule 5): say what it shows')
    _add(fig, go.Scatter(x=[x], y=[y], mode='text', text=['×'], textfont=dict(size=16, color=colour('witness')), hoverinfo='skip', showlegend=False), row, col)
    ann = dict(x=x, y=y, xanchor='left', xshift=10, text=str(words), showarrow=False, font=dict(size=10, color=colour('ink')))
    if row is not None:
        ann.update(row=row, col=col)
    fig.add_annotation(**ann)
    return fig


def ramp_scale(classes):
    """The order ramp as a discrete plotly colorscale for `classes` steps (1 to 5), lightest to darkest: the neutral
    field of the print register, which every greyscale copy keeps."""
    ramp = REGISTER['ramp']
    if not 1 <= classes <= len(ramp):
        raise ValueError('a field has 1 to %d classes' % len(ramp))
    steps = ramp[len(ramp) - classes:]
    out = []
    for k, tok in enumerate(steps):
        out += [[k / classes, colour(tok)], [(k + 1) / classes, colour(tok)]]
    return out


def legend_standings(fig, standings=(DECIDED, COMPUTED, CHOSEN, REFUSED), glosses=True):
    """The standing legend (WARRANT rule 9: a legend wherever a standing is drawn), in the grammar's own words: one
    legend-only entry per standing, drawn in its stroke."""
    for s in standings:
        g = _LG[s]
        label = g['label'] + (' — ' + g['gloss'] if glosses else '')
        if s == REFUSED:
            v = _ST[REFUSED]['void']
            fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name=v['glyph'] + ' ' + label, showlegend=True, hoverinfo='skip',
                                     marker=dict(symbol='square-open', size=10, color=colour(v['edge']))))
        else:
            fig.add_trace(go.Scatter(x=[None], y=[None], mode='lines', name=label, showlegend=True, hoverinfo='skip',
                                     line=dict(color=colour(_ST[s]['token']), width=LINE_PX, dash=dash(s))))
    return fig
