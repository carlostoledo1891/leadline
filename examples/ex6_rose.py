"""Example 6: a wave rose — where the waves come from, and how high.

NDBC buoy 44007, 2015: every record with a mean wave direction and an Hs, counted into 16 direction sectors and 1-metre
Hs classes. The counts are exact, so DECIDED — given the sectors and the classes, which are chosen, and the figure says so
in italic (WARRANT's mood rule). The classes take the neutral order ramp, darker for higher waves. The records without a
direction or an Hs are not drawn as anything: they are counted and named in words, after ∅.

    python examples/ex6_rose.py      writes examples/out/ex6_rose.svg and ex6_rose-grey.svg
"""
import math
import os
import sys

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Patch

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, 'data'))
import leadline.mpl as lm  # noqa: E402
import fetch  # noqa: E402

SECTORS = 16
CLASSES = [(0, 1), (1, 2), (2, 3), (3, 4), (4, None)]      # Hs, m: chosen


def counts():
    rows = fetch.ndbc_44007_2015()
    width = 360 / SECTORS
    table = [[0] * len(CLASSES) for _ in range(SECTORS)]
    missing = 0
    for r in rows:
        mwd, hs = r[9], r[7]
        if mwd >= 999 or hs >= 99:
            missing += 1
            continue
        s = int(((mwd + width / 2) % 360) // width)
        k = next(i for i, (lo, hi) in enumerate(CLASSES) if hs >= lo and (hi is None or hs < hi))
        table[s][k] += 1
    return table, missing, len(rows)


def build(mode='colour'):
    lm.use(mode)
    table, missing, total = counts()
    ramp = lm.REGISTER['ramp']
    fig = plt.figure(figsize=(6.4, 3.6))
    ax = fig.add_axes([0.04, 0.08, 0.56, 0.84], projection='polar')
    ax.set_theta_zero_location('N')
    ax.set_theta_direction(-1)
    width = 2 * math.pi / SECTORS
    base = [0] * SECTORS
    for k in range(len(CLASSES)):
        vals = [table[s][k] for s in range(SECTORS)]
        ax.bar([s * width for s in range(SECTORS)], vals, width=width * 0.94, bottom=base, color=lm.colour(ramp[k]),
               edgecolor=lm.colour('paper'), linewidth=0.6, zorder=2)
        base = [b + v for b, v in zip(base, vals)]
    ax.set_xticks([i * math.pi / 4 for i in range(8)])
    ax.set_xticklabels(['N', 'NE', 'E', 'SE', 'S', 'SW', 'W', 'NW'], fontsize=7)
    ax.tick_params(axis='y', labelsize=6, colors=lm.colour('ink-3'))
    ax.set_rlabel_position(292.5)                      # the radial labels where the bars are not
    ax.grid(color=lm.colour('grid'), linewidth=0.5)
    ax.spines['polar'].set_color(lm.colour('guide'))
    side = fig.add_axes([0.62, 0.08, 0.37, 0.84])
    side.set_axis_off()
    side.text(0, 0.98, 'NDBC 44007, 2015', fontsize=8, fontweight='bold', color=lm.colour('ink'), va='top')
    side.text(0, 0.90, 'records by the direction waves come from\nand by Hs: exact counts', fontsize=7, color=lm.colour('ink-2'), va='top')
    side.text(0, 0.76, 'given %d sectors and 1 m classes' % SECTORS, fontsize=7, style='italic', color=lm.colour('ink-3'), va='top')
    handles = [Patch(facecolor=lm.colour(ramp[k]), edgecolor='none') for k in range(len(CLASSES))]
    labels = ['Hs %g–%g m' % (lo, hi) if hi is not None else 'Hs %g m and more' % lo for lo, hi in CLASSES]
    side.legend(handles, labels, loc='center left', bbox_to_anchor=(0, 0.42), frameon=False, fontsize=7)
    side.text(0, 0.06, '∅ %s of %s records have no direction or no Hs:\nnot drawn, counted here' % (format(missing, ','), format(total, ',')),
              fontsize=6.5, color=lm.colour('ink'), va='bottom')
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    for mode, suffix in (('colour', ''), ('grey', '-grey')):
        build(mode).savefig(os.path.join(out, 'ex6_rose%s.svg' % suffix))
        plt.close('all')
    t, m, n = counts()
    print('wrote ex6_rose: %d records, %d drawn, %d without a direction or Hs' % (n, n - m, m))
