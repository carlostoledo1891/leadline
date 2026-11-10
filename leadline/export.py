"""leadline.export: figure sizes for reports and one call that writes every file a report needs.

    import leadline.export as lx
    fig = build('colour')                                     # your figure, drawn with leadline.mpl
    lx.save(build, 'return-levels', out='figures')            # return-levels.svg/.pdf/.png and -grey twins

Sizes are the text widths figures are usually set at on A4 (in inches, matplotlib's unit): a full width of 160 mm and a
column of 84 mm in two-column layouts, and a 16:9 slide. A height is the width times a ratio. The greyscale twin is the
same figure drawn again with lm.use('grey'), every colour its grey value, as a mono laser prints it — so the build function
is called once per mode and nothing is post-processed.
"""
import os

import matplotlib.pyplot as plt

from . import mpl as lm

MM = 1 / 25.4
WIDTHS = {'full': 160 * MM, 'column': 84 * MM, 'slide': 10.0}


def size(width='full', ratio=0.5):
    """(width, height) in inches for a named width ('full', 'column', 'slide') or a number of millimetres."""
    w = WIDTHS[width] if isinstance(width, str) else float(width) * MM
    return (w, w * ratio)


def save(build, name, out='.', formats=('svg', 'pdf', 'png'), grey=True, dpi=300):
    """Write name.<fmt> for each format, and name-grey.<fmt> when grey is true. `build` is a function of the mode
    ('colour' or 'grey') that returns a figure drawn with leadline.mpl (it calls lm.use(mode) itself or leaves it to us).
    Returns the paths written."""
    if not callable(build):
        raise TypeError('save takes the function that builds the figure, so the greyscale twin can be drawn, not post-processed')
    os.makedirs(out, exist_ok=True)
    written = []
    for mode, suffix in (('colour', ''),) + ((('grey', '-grey'),) if grey else ()):
        lm.use(mode)
        fig = build(mode)
        for fmt in formats:
            path = os.path.join(out, '%s%s.%s' % (name, suffix, fmt))
            fig.savefig(path, dpi=dpi if fmt == 'png' else None)
            written.append(path)
        plt.close(fig)
    lm.use('colour')
    return written
