"""Example 8: peaks over a threshold — a winter of hourly Hs, the threshold, the storm peaks, and the hours with no record.

Dataset A, one winter. The record is drawn as it is, a thin solid line (DECIDED: the record itself). The threshold u is
the 0.99 empirical quantile of the whole record: an order statistic, exact — but p = 0.99 is the analyst's pick, so the
line is CHOSEN, dotted, and named "given p = 0.99". Storms are runs above u separated by at least 48 h below it (a
declustering rule, chosen); each storm's peak is the exact maximum of its run, a decided knot, given the rule. Stretches
longer than a day with no hour on record are voids with words — never a line drawn across them.

    python examples/ex8_peaks.py     writes examples/out/ex8_peaks.svg (-grey.svg) and plotly_ex8_peaks.html
"""
import datetime as dt
import os
import sys

import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.dirname(HERE))
sys.path.insert(0, os.path.join(HERE, 'data'))
import leadline.mpl as lm  # noqa: E402
import fetch  # noqa: E402

P, SEPARATION_H, GAP_H = 0.99, 48, 24
WINDOW = (dt.datetime(2003, 10, 1), dt.datetime(2004, 4, 1))


def series():
    t, hs, _ = fetch.dataset_a()
    times = [dt.datetime.strptime(a, '%Y-%m-%d-%H') for a in t]
    hs = np.asarray(hs)
    s = np.sort(hs)
    u = float(s[int(np.ceil(P * len(s))) - 1])                    # the order statistic: exact, given p
    keep = [i for i, x in enumerate(times) if WINDOW[0] <= x < WINDOW[1]]
    tw, hw = [times[i] for i in keep], hs[keep]
    peaks, run, last_above = [], None, None
    for x, h in zip(tw, hw):
        if h > u:
            if run is not None and last_above is not None and (x - last_above).total_seconds() / 3600 >= SEPARATION_H:
                peaks.append(run)
                run = None
            run = (x, h) if run is None or h > run[1] else run
            last_above = x
    if run is not None:
        peaks.append(run)
    gaps = [(a, b) for a, b in zip(tw, tw[1:]) if (b - a).total_seconds() / 3600 > GAP_H]
    return tw, hw, u, peaks, gaps


def segments(tw, hw, gaps):
    """the record split at its gaps, so no line is ever drawn across hours that were not recorded"""
    cuts = {a for a, _ in gaps}
    seg, out = ([], []), []
    for x, h in zip(tw, hw):
        seg[0].append(x)
        seg[1].append(h)
        if x in cuts:
            out.append(seg)
            seg = ([], [])
    if seg[0]:
        out.append(seg)
    return out


def build(mode='colour'):
    lm.use(mode)
    tw, hw, u, peaks, gaps = series()
    fig, ax = plt.subplots(figsize=(7.0, 3.0))
    ax.set_ylim(0, max(float(hw.max()), u) * 1.18)
    for a, b in gaps:
        lm.void(ax, mdates.date2num(a), mdates.date2num(b), words='no record\n%d h' % round((b - a).total_seconds() / 3600), fontsize=5.5)
    for xs, ys in segments(tw, hw, gaps):
        lm.line(ax, xs, ys, lm.DECIDED, width=0.6)
    lm.line(ax, [tw[0], tw[-1]], [u, u], lm.CHOSEN)
    ax.annotate('u = %.2f m, given p = %.2f' % (u, P), (tw[0], u), xytext=(2, 4), textcoords='offset points', fontsize=6.5, style='italic', color=lm.colour('ink-2'))
    for x, h in peaks:
        lm.knot(ax, x, h, series=0, size=4)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%b %Y'))
    ax.set_ylabel('Hs, m')
    ax.set_title('dataset A, winter 2003–04: %d storms above u, given a %d h separation' % (len(peaks), SEPARATION_H), fontsize=7.5, loc='left')
    lm.legend(ax, standings=(lm.DECIDED, lm.CHOSEN, lm.REFUSED), glosses=False, series=[('storm peak (exact maximum of its run)', 0)],
              loc='upper right', fontsize=6)
    fig.tight_layout()
    return fig


def build_plotly():
    import leadline.plotly as lp
    lp.use('colour')
    tw, hw, u, peaks, gaps = series()
    top = max(float(hw.max()), u) * 1.18
    fig = lp.figure(title='Peaks over a threshold, dataset A, winter 2003–04 (given p = %.2f and a %d h separation)' % (P, SEPARATION_H))
    for a, b in gaps:
        lp.void(fig, a, b, 0, top, words='no record %d h' % round((b - a).total_seconds() / 3600))
    for i, (xs, ys) in enumerate(segments(tw, hw, gaps)):
        lp.line(fig, xs, list(ys), lp.DECIDED, width=0.8, name='the record' if i == 0 else None, hovertemplate='%{x|%d %b %Y %H:00}: %{y:.2f} m<extra></extra>')
    lp.line(fig, [tw[0], tw[-1]], [u, u], lp.CHOSEN, name='u = %.2f m, given p = %.2f' % (u, P), hoverinfo='skip')
    for k, (x, h) in enumerate(peaks):
        lp.knot(fig, x, h, series=0, name='storm peak' if k == 0 else None, hovertemplate='peak %{x|%d %b %Y %H:00}: %{y:.2f} m<extra></extra>')
    fig.update_yaxes(title_text='Hs, m', range=[0, top])
    return fig


if __name__ == '__main__':
    out = os.path.join(HERE, 'out')
    os.makedirs(out, exist_ok=True)
    for mode, suffix in (('colour', ''), ('grey', '-grey')):
        build(mode).savefig(os.path.join(out, 'ex8_peaks%s.svg' % suffix))
        plt.close('all')
    build_plotly().write_html(os.path.join(out, 'plotly_ex8_peaks.html'), include_plotlyjs='cdn', config={'responsive': True, 'displaylogo': False},
                              default_width='100%', default_height='480px')
    tw, hw, u, peaks, gaps = series()
    print('wrote ex8_peaks: u = %.2f m, %d storms, %d gaps over %d h' % (u, len(peaks), len(gaps), GAP_H))
