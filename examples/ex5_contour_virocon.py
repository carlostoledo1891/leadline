"""Example 5: a 20-year environmental contour from virocon, over the hours it was fitted to.

Dataset A of the environmental-contour benchmark (82,805 hourly sea states from an NDBC buoy) counted exactly into chosen
cells, drawn as the neutral order ramp: DECIDED, given the cells. The joint model is virocon's published OMAE2020 Hs–Tz
model, fitted by virocon; the IFORM contour for a 20-year return period with 1-hour states is a fit and a numerical
construction, so COMPUTED (dashed), on a paper casing because it crosses the field. Beside it, the premise ladder: what
the contour rests on, every rung ASSUMED, so the contour is too.

    python examples/ex5_contour_virocon.py   writes examples/out/ex5_contour_virocon.svg (-grey.svg) and plotly_ex5_contour_virocon.html
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, 'data'))
import leadline.mpl as lm  # noqa: E402
import fetch  # noqa: E402

CLASSES = [(1, 9), (10, 99), (100, 499), (500, 1999), (2000, None)]
TZ, HS = (0, 20, 80), (0, 12, 60)          # the cells: 0.25 s × 0.2 m, chosen
RETURN_PERIOD, STATE_HOURS = 20, 1


def contour():
    """The fitted model's IFORM contour (Hs, Tz vertices, closed) and the record it was fitted to."""
    from virocon import GlobalHierarchicalModel, IFORMContour, calculate_alpha, get_OMAE2020_Hs_Tz
    _, hs, tz = fetch.dataset_a()
    data = np.column_stack([hs, tz])
    dists, fits, _ = get_OMAE2020_Hs_Tz()
    model = GlobalHierarchicalModel(dists)
    model.fit(data, fit_descriptions=fits)
    c = IFORMContour(model, calculate_alpha(STATE_HOURS, RETURN_PERIOD)).coordinates
    c = np.vstack([c, c[:1]])
    return c[:, 0], c[:, 1], np.asarray(hs), np.asarray(tz)


def counts(hs, tz):
    nx, ny = TZ[2], HS[2]
    ix = np.floor((tz - TZ[0]) / (TZ[1] - TZ[0]) * nx).astype(int)
    iy = np.floor((hs - HS[0]) / (HS[1] - HS[0]) * ny).astype(int)
    ok = (ix >= 0) & (ix < nx) & (iy >= 0) & (iy < ny)
    grid = np.zeros((ny, nx), dtype=int)
    np.add.at(grid, (iy[ok], ix[ok]), 1)
    return grid.tolist(), int((~ok).sum())


def build(mode='colour', data=None):
    lm.use(mode)
    chs, ctz, hs, tz = data or contour()
    grid, off = counts(hs, tz)
    fig = plt.figure(figsize=(7.0, 3.3))
    ax = fig.add_axes([0.08, 0.14, 0.50, 0.80])
    shades = lm.field(ax, TZ, HS, grid, CLASSES)
    lm.line(ax, ctz, chs, lm.COMPUTED, on_field=True)
    k = int(np.argmax(chs))
    ax.annotate('max Hs on the contour %.2f m (computed)' % chs[k], (ctz[k], chs[k]), xytext=(6, 4), textcoords='offset points', fontsize=6.5,
                color=lm.colour('ink-2'), bbox=dict(facecolor=lm.colour('paper'), edgecolor='none', pad=1))
    ax.set_xlim(TZ[0], TZ[1])
    ax.set_ylim(HS[0], HS[1])
    ax.set_xlabel('zero-up-crossing period Tz, s')
    ax.set_ylabel('significant wave height Hs, m')
    ax.set_title('dataset A: %s hours, counted per cell' % format(len(hs), ','), fontsize=7.5, loc='left')
    lm.legend(ax, standings=(lm.COMPUTED,), glosses=False, extra=shades, loc='upper left', fontsize=6,
              title='hours per cell (0.25 s × 0.2 m, chosen)', title_fontsize=6)
    side = fig.add_axes([0.62, 0.10, 0.37, 0.84])
    lm.premises(side, [
        (lm.ASSUMED, 'The record', 'NDBC hourly sea states, dataset A, pinned by sha256'),
        (lm.ASSUMED, 'The model', 'OMAE2020 Hs–Tz (virocon), fitted by virocon'),
        (lm.ASSUMED, 'The states', '1-hour sea states, independent draws'),
        (lm.ASSUMED, 'The method', 'IFORM, a 20-year return period: choices'),
    ])
    return fig


def build_plotly(data=None):
    import leadline.plotly as lp
    import plotly.graph_objects as go
    lp.use('colour')
    chs, ctz, hs, tz = data or contour()
    grid, _ = counts(hs, tz)
    bounds = [1, 10, 100, 500, 2000]
    z = [[None if not n else sum(1 for b in bounds if n >= b) - 1 for n in row] for row in grid]
    (x0, x1, nx), (y0, y1, ny) = TZ, HS
    fig = lp.figure(title='A 20-year IFORM contour (virocon, OMAE2020 Hs–Tz) over dataset A')
    fig.add_trace(go.Heatmap(x0=x0 + (x1 - x0) / nx / 2, dx=(x1 - x0) / nx, y0=y0 + (y1 - y0) / ny / 2, dy=(y1 - y0) / ny, z=z, zmin=-0.5, zmax=4.5,
                             colorscale=lp.ramp_scale(5), hoverinfo='skip',
                             colorbar=dict(lp.colorbar_below('hours per cell (0.25 s × 0.2 m cells)', y=-0.30), tickvals=[0, 1, 2, 3, 4], ticktext=['1–9', '10–99', '100–499', '500–1,999', '2,000+'])))
    lp.line(fig, list(ctz), list(chs), lp.COMPUTED, on_field=True, name='20-year contour (computed)', hovertemplate='Tz %{x:.2f} s · Hs %{y:.2f} m<extra></extra>')
    lp.legend_standings(fig, (lp.COMPUTED,), glosses=True)
    fig.update_xaxes(title_text='zero-up-crossing period Tz, s', range=[x0, x1], showgrid=False)
    fig.update_yaxes(title_text='significant wave height Hs, m', range=[y0, y1], showgrid=False)
    fig.update_layout(margin=dict(b=130))
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    d = contour()
    for mode, suffix in (('colour', ''), ('grey', '-grey')):
        build(mode, d).savefig(os.path.join(out, 'ex5_contour_virocon%s.svg' % suffix))
        plt.close('all')
    build_plotly(d).write_html(os.path.join(out, 'plotly_ex5_contour_virocon.html'), include_plotlyjs='cdn', config={'responsive': True, 'displaylogo': False},
                               default_width='100%', default_height='560px')
    print('wrote ex5_contour_virocon (svg, grey, plotly); max Hs on the contour %.2f m' % float(np.max(d[0])))
