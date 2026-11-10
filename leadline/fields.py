"""leadline.fields: colour for FIELDS (a quantity over a map or a plane) — a PROPOSAL, not yet part of WARRANT.

WARRANT draws standing with the stroke and verdicts with words; its only colours are the witness red, at most three
identity colours and one neutral order ramp. Metocean figures also need colour for a physical quantity spread over a
plane (Hs over a basin, a density of sea states, a difference between two hindcasts, a mean direction). This module
proposes three roles for that, each one of Fabio Crameri's scientific colour maps (cmcrameri, already common in
metocean code), chosen by the grammar's own rules and measured by tools/validate_fields.py (fields-report.json):

    magnitude    oslo     sequential, lightness monotone, no yellow or orange (v2.2 rule 6); on paper reversed, so that
                          more is darker (v2.3 rule 4)
    difference   bam      diverging around a light middle, both sides apart for normal vision and the three colour-
                          vision deficiencies (the validator's thresholds: ΔE ≥ 15 normal, ≥ 8 CVD)
    direction    bamO     cyclic, the same hues as bam

The rules that come with them (the proposal's, to be approved with the colours):
  1. A field never carries standing or a verdict: it is the data. Lines over it keep their strokes (leadline.mpl.line /
     leadline.plotly.line with on_field=True: a paper casing under the line).
  2. On a coloured field, series are told apart by MARKER and word, not by the print blue: the blue sits ΔE ~4 from the
     magnitude map (fields-report.json), so over a field every series is ink, ink-2 or ink-3.
  3. The witness × over a field is always drawn on a paper casing.
  4. A colour bar with the quantity, its unit and its source is always drawn beside the field.

STATUS = 'PROPOSED'. Nothing here is approved until WARRANT records it (v2.2 rule 7); until then a figure that needs a
field and wants only approved colours uses leadline.mpl.field (the neutral order ramp).

MIT licensed.
"""
import numpy as np

STATUS = 'PROPOSED (2026-11-10): not part of WARRANT until approved and recorded in its design/WARRANT.md (v2.2 rule 7)'
ROLES = {
    'magnitude': {'map': 'oslo', 'kind': 'sequential', 'paper_reversed': True},
    'difference': {'map': 'bam', 'kind': 'diverging', 'paper_reversed': False},
    'direction': {'map': 'bamO', 'kind': 'cyclic', 'paper_reversed': False},
}


def _cm(name):
    try:
        import cmcrameri.cm as cmc
    except ImportError:
        raise ImportError('leadline.fields needs cmcrameri (pip install cmcrameri), the colour maps it proposes')
    return getattr(cmc, name)


def cmap(role, medium='paper'):
    """The matplotlib colormap for a field's role ('magnitude', 'difference', 'direction') on paper or screen."""
    if role not in ROLES:
        raise ValueError('a field is a magnitude, a difference or a direction (%s)' % ', '.join(ROLES))
    if medium not in ('paper', 'screen'):
        raise ValueError("medium is 'paper' or 'screen'")
    r = ROLES[role]
    return _cm(r['map'] + ('_r' if (r['paper_reversed'] and medium == 'paper') else ''))


def plotly_scale(role, medium='paper', n=11):
    """The same map as a plotly colorscale of n stops."""
    cm = cmap(role, medium)
    out = []
    for k in range(n):
        t = k / (n - 1)
        r, g, b, _ = cm(t)
        out.append([t, '#%02x%02x%02x' % (int(round(r * 255)), int(round(g * 255)), int(round(b * 255)))])
    return out


# ---- the measurements the proposal rests on (tools/validate_fields.py writes them to fields-report.json) -------------
def _lin(c):
    c = np.asarray(c, float)
    return np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4)


def oklab(rgb):
    """OKLab of sRGB values in [0, 1] (Ottosson 2020)."""
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    return np.cbrt(_lin(rgb) @ m1.T) @ m2.T


MACHADO = {  # Machado, Oliveira & Fernandes 2009, severity 1.0, on linear RGB
    'protan': np.array([[0.152286, 1.052583, -0.204868], [0.114503, 0.786281, 0.099216], [-0.003882, -0.048116, 1.051998]]),
    'deutan': np.array([[0.367322, 0.860646, -0.227968], [0.280085, 0.672501, 0.047413], [-0.011820, 0.042940, 0.968881]]),
    'tritan': np.array([[1.255528, -0.076749, -0.178779], [-0.078411, 0.930809, 0.147602], [0.004733, 0.691367, 0.303900]]),
}


def delta_e(c1, c2, vision=None):
    """ΔE × 100 in OKLab between two sRGB colours, under normal vision or a simulated deficiency."""
    a, b = _lin(np.asarray(c1, float)[:3]), _lin(np.asarray(c2, float)[:3])
    if vision is not None:
        a, b = np.clip(MACHADO[vision] @ a, 0, 1), np.clip(MACHADO[vision] @ b, 0, 1)
    m1 = np.array([[0.4122214708, 0.5363325363, 0.0514459929], [0.2119034982, 0.6806995451, 0.1073969566], [0.0883024619, 0.2817188376, 0.6299787005]])
    m2 = np.array([[0.2104542553, 0.7936177850, -0.0040720468], [1.9779984951, -2.4285922050, 0.4505937099], [0.0259040371, 0.7827717662, -0.8086757660]])
    la, lb = np.cbrt(a @ m1.T) @ m2.T, np.cbrt(b @ m1.T) @ m2.T
    return float(100 * np.linalg.norm(la - lb))


def yellow_orange(rgb, chroma=0.05):
    """Whether an sRGB colour reads as yellow or orange: OKLCH hue in [35°, 115°] at a visible chroma."""
    L, a, b = oklab(np.asarray(rgb, float)[:3])
    h = (np.degrees(np.arctan2(b, a)) + 360) % 360
    return bool(35 <= h <= 115 and np.hypot(a, b) > chroma)
