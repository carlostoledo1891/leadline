"""Leadline: WARRANT's grammar for the sea and for fields, in Python.

A leadsman's calls kept apart a depth read at a marked fathom ("by the mark five") and one judged between the marks
("by the deep six"). Leadline keeps the same distinction in a figure: every mark says what it rests on.

    import leadline.mpl as lm        # matplotlib: the print register (WARRANT v2.3), approved
    import leadline.plotly as lp     # plotly: the same register, the same marks and refusals
    import leadline.fields as lf     # colour for fields (magnitude, difference, direction): a PROPOSAL

Leadline is a dialect of WARRANT, the grammar of cert-machine (github.com/carlostoledo1891/cert-machine): the strokes,
inks, identities, ramp and legend words are read from leadline/mpl/register.json, which cert-machine generates; PINS.json
names every file taken from there and its sha256. MIT licensed.
"""
__version__ = '0.1.0'
GRAMMAR = 'WARRANT v2.3 (print register), cert-machine design/WARRANT.md; field colours proposed, not yet approved'
