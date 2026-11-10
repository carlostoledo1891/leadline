"""The kit's three examples drawn with plotly: the same data, the same marks, the same refusals, as interactive HTML.

    python examples/plotly_examples.py      writes examples/out/plotly_ex1_design_wave.html, _ex2_return_curve, _ex3_contours

Each HTML file loads plotly.js from its CDN, scales to its container (config responsive) and has a greyscale twin
(-grey.html) for a mono printer's eye.
"""
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import leadline.plotly as wp  # noqa: E402
from plotly.subplots import make_subplots  # noqa: E402
import plotly.graph_objects as go  # noqa: E402

NAMES = {'native': 'hourly', 'daily': 'daily', 'weekly': 'weekly', 'monthly': 'monthly', 'annual': 'annual'}
CONFIG = {'responsive': True, 'displaylogo': False}


def data(name):
    with open(os.path.join(HERE, 'data', name), encoding='utf-8') as fh:
        return json.load(fh)


def ex1():
    """Buoy A's certified 100-year Hs by block: the picked family a decided knot, the other hollow; the delta method's
    interval a computed whisker; the annual choice refused, so a void and words."""
    D = data('buoy-a.json')
    series, offset = {'expweibull': 0, 'lognormal': 1}, {'expweibull': -0.12, 'lognormal': 0.12}
    fig = wp.figure(title='100-year Hs by the block the maxima are taken over (buoy A, %d years)' % D['years'])
    for i, b in enumerate(D['blocks']):
        if b['verdict'] == 'REFUSED':
            wp.void(fig, i - 0.42, i + 0.42, 8, 22, words='choice refused:\nno certified exp. Weibull')
        for f, F in b['families'].items():
            if not F['certified']:
                continue
            hi = float(F['levels']['100'][1])
            picked = b['pick'] == f
            x = i + offset[f]
            if picked and F['delta']:
                d0, d1 = (float(v) for v in F['delta']['100'])
                wp.whisker(fig, x, d0, d1, wp.COMPUTED, series=series[f], hovertemplate='delta 95%%: %.2f–%.2f m<extra></extra>' % (d0, d1))
            wp.knot(fig, x, hi, series=series[f], hollow=not picked, size=9 if picked else 7,
                    hovertemplate='%s · %s: %.4f m%s<extra></extra>' % (NAMES[b['block']], f, hi, ' (A² pick)' if picked else ''))
    big = float(D['largestHour'])
    wp.line(fig, [-0.6, 3.5], [big, big], wp.DECIDED, width=0.8, hovertemplate='largest hour on record %.2f m<extra></extra>' % big)
    fig.add_annotation(x=-0.55, y=big, yshift=-10, xanchor='left', text='largest hour on record %.2f m' % big, showarrow=False, font=dict(size=10, color=wp.colour('ink-3')))
    for name, s, hollow in (('exp. Weibull, A² pick (decided)', 0, False), ('lognormal, A² pick (decided)', 1, False), ('hollow: where A² picks the other', 0, True)):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name=name, marker=dict(symbol=wp.SYMBOL[wp.REGISTER['identity'][s]['marker']] + ('-open' if hollow else ''),
                                 size=8, color=wp.series_colour(s))))
    wp.legend_standings(fig, (wp.COMPUTED, wp.REFUSED), glosses=False)
    fig.update_xaxes(tickvals=list(range(len(D['blocks']))), ticktext=[NAMES[b['block']] for b in D['blocks']], range=[-0.6, len(D['blocks']) - 0.4], showgrid=False)
    fig.update_yaxes(title_text='100-year Hs, m', range=[8, 22])
    return fig


def ex2():
    """The monthly return-level curve: certified knots decided, the joins chosen (one curve of many the knots admit),
    the 100-year design period a guide, the delta intervals computed."""
    D = data('buoy-a.json')
    M = next(b for b in D['blocks'] if b['block'] == 'monthly')
    T = [int(t) for t in D['returnPeriods']]
    fig = wp.figure(title='Return levels, buoy A, monthly maxima — given A²')
    wp.guide(fig, x=math.log10(100))
    for idx, f in enumerate(('lognormal', 'expweibull')):
        F = M['families'][f]
        ys = [float(F['levels'][str(t)][1]) for t in T]
        wp.line(fig, T, ys, wp.CHOSEN, series=idx, hoverinfo='skip')
        for t, y in zip(T, ys):
            wp.knot(fig, t, y, series=idx, hollow=M['pick'] != f, hovertemplate='%s · %d years: %.4f m<extra></extra>' % (f, t, y))
        if F['delta']:
            for t in (100, 1000):
                lo, hi = (float(v) for v in F['delta'][str(t)])
                wp.whisker(fig, t * (1.08 if idx else 0.93), lo, hi, wp.COMPUTED, series=idx, hovertemplate='delta 95%%: %.2f–%.2f m<extra></extra>' % (lo, hi))
    for name, s, hollow in (('lognormal (A² pick)', 0, False), ('exp. Weibull', 1, True)):
        fig.add_trace(go.Scatter(x=[None], y=[None], mode='markers', name=name, marker=dict(symbol=wp.SYMBOL[wp.REGISTER['identity'][s]['marker']] + ('-open' if hollow else ''),
                                 size=8, color=wp.series_colour(s))))
    wp.legend_standings(fig, (wp.COMPUTED, wp.CHOSEN), glosses=False)
    fig.update_xaxes(type='log', title_text='return period, years', tickvals=T, ticktext=[str(t) for t in T], range=[math.log10(7), math.log10(1500)], showgrid=False)
    fig.update_yaxes(title_text='return level Hs, m', range=[6, 26])
    return fig


def ex3():
    """Environmental contours over the hours they were scored on: the hours counted exactly into chosen cells as the
    neutral order ramp; three submitted 20-year contours decided, on a paper casing; the edge the test adds chosen."""
    D = data('contours-a20.json')
    F = D['field']
    (x0, x1, nx), (y0, y1, ny) = F['tz'], F['hs']
    flat = [v for row in F['counts'] for v in row] if isinstance(F['counts'][0], list) else F['counts']
    bounds = [1, 10, 100, 500, 2000]
    z = []
    for iy in range(ny):
        row = []
        for ix in range(nx):
            n = flat[iy * nx + ix]
            row.append(None if not n else sum(1 for b in bounds if n >= b) - 1)
        z.append(row)
    fig = wp.figure(title='Dataset A: %s hours counted exactly per chosen cell, and three 20-year contours' % format(D['hours'], ','))
    fig.add_trace(go.Heatmap(x0=x0 + (x1 - x0) / nx / 2, dx=(x1 - x0) / nx, y0=y0 + (y1 - y0) / ny / 2, dy=(y1 - y0) / ny, z=z, zmin=-0.5, zmax=4.5,
                             colorscale=wp.ramp_scale(5), showscale=True, hoverinfo='skip',
                             colorbar=dict(wp.colorbar_below('hours per cell', y=-0.30), tickvals=[0, 1, 2, 3, 4], ticktext=['1–9', '10–99', '100–499', '500–1,999', '2,000+'])))
    for i, c in enumerate(D['contours']):
        tz, hs = [float(v) for v in c['tz']], [float(v) for v in c['hs']]
        wp.line(fig, tz, hs, wp.DECIDED, series=i, on_field=True, name='%s · %s: %s outside (exact)' % (c['contribution'], c['method'], format(c['outside'], ',')),
                hovertemplate='Tz %{x:.2f} s · Hs %{y:.2f} m<extra></extra>')
        if not c['closed']:
            wp.line(fig, [tz[-1], tz[0]], [hs[-1], hs[0]], wp.CHOSEN, series=i, hoverinfo='skip')
        wp.knot(fig, float(c['tzAtMaxHs']), float(c['maxHs']), series=i, hovertemplate='max Hs %.2f m<extra></extra>' % float(c['maxHs']))
    wp.legend_standings(fig, (wp.DECIDED, wp.CHOSEN), glosses=False)
    fig.update_xaxes(title_text='zero-up-crossing period Tz, s', range=[0, 20], showgrid=False)
    fig.update_yaxes(title_text='significant wave height Hs, m', range=[0, 12], showgrid=False)
    fig.update_layout(margin=dict(b=130))
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    for mode, suffix in (('colour', ''), ('grey', '-grey')):
        wp.use(mode)
        for name, fn in (('plotly_ex1_design_wave', ex1), ('plotly_ex2_return_curve', ex2), ('plotly_ex3_contours', ex3)):
            fn().write_html(os.path.join(out, name + suffix + '.html'), include_plotlyjs='cdn', config=CONFIG, default_width='100%', default_height='560px')
    wp.use('colour')
    print('wrote the plotly examples to examples/out/')
