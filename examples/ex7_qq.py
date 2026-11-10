"""Example 7: a QQ plot — the monthly maxima against a fitted GEV.

Dataset A's monthly maxima of Hs are exact (the largest hour of each month: DECIDED). The GEV is fitted to them by maximum
likelihood (scipy), so its quantiles are COMPUTED; the plotting positions i/(n + 1) are a convention, CHOSEN, and the
figure says so in italic. Each point pairs a decided value with a computed one, so the curve through them is as strong as
its weakest coordinate: computed, dashed (WARRANT's meet). The 1:1 line is a guide. Months with no hour on record are not
maxima of anything: they are counted and named.

    python examples/ex7_qq.py        writes examples/out/ex7_qq.svg and ex7_qq-grey.svg
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


def maxima():
    t, hs, _ = fetch.dataset_a()
    by = {}
    for a, h in zip(t, hs):
        k = a[:7]
        by[k] = max(by.get(k, -1.0), h)
    months = sorted(by)
    first, last = months[0], months[-1]
    span = (int(last[:4]) - int(first[:4])) * 12 + int(last[5:7]) - int(first[5:7]) + 1
    return np.array([by[k] for k in months]), span - len(months)


def fit(m):
    from scipy.stats import genextreme
    c, loc, scale = genextreme.fit(m)
    return genextreme(c, loc=loc, scale=scale), (c, loc, scale)


def build(mode='colour'):
    lm.use(mode)
    m, empty = maxima()
    dist, (c, loc, scale) = fit(m)
    y = np.sort(m)
    n = len(y)
    p = np.arange(1, n + 1) / (n + 1)
    x = dist.ppf(p)
    fig, ax = plt.subplots(figsize=(4.6, 4.0))
    lo, hi = float(min(x.min(), y.min())) - 0.3, float(max(x.max(), y.max())) + 0.3
    ax.plot([lo, hi], [lo, hi], color=lm.colour('guide'), linewidth=0.8, linestyle=(0, tuple(float(v) for v in lm.REGISTER['patterns']['GUIDE'].split())), zorder=1)   # the guide pattern
    lm.line(ax, x, y, lm.COMPUTED)
    ax.set_xlim(lo, hi)
    ax.set_ylim(lo, hi)
    ax.set_aspect('equal')
    ax.set_xlabel('GEV quantile, m (fitted by maximum likelihood)')
    ax.set_ylabel('monthly maximum of Hs, m (the record)')
    ax.set_title('dataset A: %d monthly maxima' % n, fontsize=7.5, loc='left')
    ax.text(0.02, 0.97, 'given plotting positions i/(n + 1)', transform=ax.transAxes, fontsize=6.5, style='italic', color=lm.colour('ink-3'), va='top')
    ax.text(0.02, 0.91, 'GEV ξ = %.3f, μ = %.2f m, σ = %.2f m (computed)' % (-c, loc, scale), transform=ax.transAxes, fontsize=6.5, color=lm.colour('ink-2'), va='top')
    if empty:
        ax.text(0.98, 0.03, '∅ %d months with no hour on record: no maximum' % empty, transform=ax.transAxes, fontsize=6.5, color=lm.colour('ink'), ha='right', va='bottom')
    lm.legend(ax, standings=(lm.COMPUTED,), glosses=False, extra=[(plt.Line2D([], [], color=lm.colour('guide'), linewidth=0.8, linestyle=(0, (2.0, 3.0))), 'guide: 1:1')],
              loc='lower right', bbox_to_anchor=(1.0, 0.08), fontsize=6.5)
    fig.tight_layout()
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    for mode, suffix in (('colour', ''), ('grey', '-grey')):
        build(mode).savefig(os.path.join(out, 'ex7_qq%s.svg' % suffix))
        plt.close('all')
    m, e = maxima()
    print('wrote ex7_qq: %d monthly maxima, %d empty months' % (len(m), e))
