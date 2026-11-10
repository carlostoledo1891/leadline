"""Example 4 (the PROPOSAL, warrant_fields): colour for a field. SYNTHETIC data, made up for this figure only.

Left: a magnitude (an Hs-like field over a small basin) in the proposed sequential map, more is darker on paper; one
level line, interpolated from the gridded floats, so COMPUTED (dashed) on a paper casing; three sites as ink markers,
told apart by marker and word, not by hue (the proposal's rule 2). Right: a difference between two synthetic
hindcasts in the proposed diverging map, symmetric about zero, its colour bar naming the sign.

    python examples/ex4_fields.py     writes examples/out/ex4_fields.svg and examples/out/plotly_ex4_fields.html
"""
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
import leadline.mpl as wm  # noqa: E402
import leadline.fields as wf  # noqa: E402


def synthetic():
    """A smooth made-up field on a 0.25° grid and a second one shifted and scaled: nothing here is a measurement."""
    lon, lat = np.linspace(-48, -38, 41), np.linspace(-30, -20, 41)
    X, Y = np.meshgrid(lon, lat)
    a = 2.0 + 3.2 * np.exp(-((X + 41.5) ** 2 + (Y + 26.5) ** 2) / 10) + 1.1 * np.exp(-((X + 45) ** 2 + (Y + 22) ** 2) / 6)
    b = 1.06 * (2.0 + 3.2 * np.exp(-((X + 41.0) ** 2 + (Y + 26.0) ** 2) / 9.5) + 1.1 * np.exp(-((X + 45.4) ** 2 + (Y + 22.3) ** 2) / 6))
    return lon, lat, a, b - a


SITES = [(-41.8, -26.2, 0, 'site 1'), (-45.2, -22.4, 2, 'site 2')]


def build_mpl():
    wm.use('colour')
    lon, lat, hs, diff = synthetic()
    fig, (ax, bx) = plt.subplots(1, 2, figsize=(7.2, 3.1), constrained_layout=True)
    m = ax.pcolormesh(lon, lat, hs, cmap=wf.cmap('magnitude', 'paper'), shading='auto', rasterized=False)
    cs = ax.contour(lon, lat, hs, levels=[4.0], colors=[wm.colour('paper')], linewidths=wm.LINE_PT + 2.0)
    for seg in cs.allsegs[0]:
        wm.line(ax, seg[:, 0], seg[:, 1], wm.COMPUTED, width=wm.LINE_PT, zorder=4)
    for x, y, s, name in SITES:
        wm.knot(ax, x, y, series=s, size=5, on_field=True)
        ax.annotate(name, (x, y), xytext=(5, 3), textcoords='offset points', fontsize=6.5, color=wm.colour('ink'),
                    bbox=dict(facecolor=wm.colour('paper'), edgecolor='none', pad=0.8))
    fig.colorbar(m, ax=ax, shrink=0.9).set_label('Hs, m (synthetic)', fontsize=7)
    ax.set_title('magnitude — synthetic field; dashed: the 4 m level, interpolated', fontsize=7, loc='left')
    lim = float(np.max(np.abs(diff)))
    d = bx.pcolormesh(lon, lat, diff, cmap=wf.cmap('difference'), vmin=-lim, vmax=lim, shading='auto')
    fig.colorbar(d, ax=bx, shrink=0.9).set_label('B − A, m (synthetic)', fontsize=7)
    bx.set_title('difference — two synthetic hindcasts', fontsize=7, loc='left')
    for a_ in (ax, bx):
        a_.set_xlabel('longitude, °')
        a_.set_ylabel('latitude, °')
        a_.grid(False)
    return fig


def build_plotly():
    import leadline.plotly as wp
    from plotly.subplots import make_subplots
    import plotly.graph_objects as go
    wp.use('colour')
    lon, lat, hs, diff = synthetic()
    fig = make_subplots(rows=1, cols=2, horizontal_spacing=0.14, subplot_titles=('magnitude — synthetic field', 'difference — two synthetic hindcasts'))
    fig.update_layout(template=wp.TEMPLATE['colour'], title='PROPOSAL (leadline.fields): colour for fields — synthetic data')
    fig.add_trace(go.Heatmap(x=lon, y=lat, z=hs, colorscale=wf.plotly_scale('magnitude', 'paper'), colorbar=wp.colorbar_below('Hs, m (synthetic)', y=-0.22, x=0.0, length=0.43),
                             hovertemplate='%{x:.2f}°, %{y:.2f}°: %{z:.2f} m (synthetic)<extra></extra>'), row=1, col=1)
    fig.add_trace(go.Contour(x=lon, y=lat, z=hs, contours=dict(start=4, end=4, size=1, coloring='none'), line=dict(color=wp.colour('paper'), width=4), showscale=False, showlegend=False, hoverinfo='skip'), row=1, col=1)
    fig.add_trace(go.Contour(x=lon, y=lat, z=hs, contours=dict(start=4, end=4, size=1, coloring='none'), line=dict(color=wp.colour('ink-2'), width=1.5, dash=wp.dash(wp.COMPUTED)),
                             showscale=False, hoverinfo='skip', name='4 m level (computed)'), row=1, col=1)
    for x, y, s, name in SITES:
        wp.knot(fig, x, y, series=s, on_field=True, row=1, col=1, hovertemplate=name + '<extra></extra>')
    lim = float(np.max(np.abs(diff)))
    fig.add_trace(go.Heatmap(x=lon, y=lat, z=diff, zmin=-lim, zmax=lim, colorscale=wf.plotly_scale('difference'), colorbar=wp.colorbar_below('B − A, m (synthetic)', y=-0.22, x=0.57, length=0.43),
                             hovertemplate='%{x:.2f}°, %{y:.2f}°: %{z:+.3f} m (synthetic)<extra></extra>'), row=1, col=2)
    fig.update_xaxes(title_text='longitude, °', showgrid=False)
    fig.update_yaxes(title_text='latitude, °', showgrid=False)
    fig.update_layout(margin=dict(b=120, t=80))
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    build_mpl().savefig(os.path.join(out, 'ex4_fields.svg'))
    plt.close('all')
    build_plotly().write_html(os.path.join(out, 'plotly_ex4_fields.html'), include_plotlyjs='cdn', config={'responsive': True, 'displaylogo': False},
                              default_width='100%', default_height='520px')
    print('wrote examples/out/ex4_fields.svg and plotly_ex4_fields.html')
