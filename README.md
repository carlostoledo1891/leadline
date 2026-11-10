# Leadline

**Figures in which every mark says what it rests on — WARRANT's grammar for the sea and for fields, in Python.**

**Documentation: [leadline-grammar.vercel.app](https://leadline-grammar.vercel.app/)**

> A leadsman's calls kept two kinds of depth apart: one read at a marked fathom — *"by the mark five"* — and one judged
> between the marks — *"by the deep six"*. Leadline keeps the same distinction in a figure. A value an exact decision
> backs is drawn one way; a fitted or printed number another; a value picked from several the data allow a third; and
> where nothing could be decided, the figure says so in words instead of drawing a zero.

Leadline is a dialect of **WARRANT**, the visual grammar of [cert-machine](https://github.com/carlostoledo1891/cert-machine),
made for metocean and offshore teams: return levels, environmental contours, design waves, fields over a basin. It brings
WARRANT to the tools those figures are made with: **matplotlib**, **plotly** and **Figma**.

**Status: v0.1.0, a starter to iterate on.**

| part | what | status |
|---|---|---|
| `leadline.mpl` | the print register for matplotlib (WARRANT v2.3, "on paper"): strokes, inks, three series identities, the neutral order ramp, the witness, the void, the legend, the premise ladder | approved in WARRANT (2026-10-29); copied byte for byte from cert-machine |
| `leadline.plotly` | the same register for plotly: a template (`'warrant'`, `'warrant-grey'`) and the same helpers and refusals | new here |
| `leadline.fields` | colour for **fields** — magnitude, difference, direction — from Crameri's scientific colour maps | **a proposal**, not yet part of WARRANT |
| `tokens/leadline.tokens.json` | the same values as design tokens for Figma (Tokens Studio) | generated |

## Install

```bash
pip install -e ".[all]"            # from this folder: matplotlib, numpy, plotly, cmcrameri
```

Python ≥ 3.7. Tested on Python 3.9.6 with matplotlib 3.9.4, plotly 7.1.0 and cmcrameri 1.8.

## In thirty seconds

```python
import leadline.mpl as lm                     # matplotlib
lm.use()                                      # or lm.use('grey'): as a mono laser printer prints it
lm.line(ax, T, levels, lm.CHOSEN, series=0)   # the joins between certified knots: one curve of many — dotted
lm.knot(ax, 100, level_100, series=0)         # a decided value
lm.whisker(ax, 100, lo, hi, lm.COMPUTED)      # a statistical interval — dashed
lm.void(ax, x0, x1, y0, y1, words='choice refused: no certified exp. Weibull')
lm.legend(ax, standings=(lm.COMPUTED, lm.CHOSEN, lm.REFUSED))

import leadline.plotly as lp                  # plotly: the same calls on a figure
lp.use()
fig = lp.figure(title='Return levels')
lp.line(fig, T, levels, lp.CHOSEN, series=0)
lp.knot(fig, 100, level_100, series=0)
lp.legend_standings(fig, (lp.COMPUTED, lp.CHOSEN))
```

## The grammar

| standing | what the mark rests on | stroke |
|---|---|---|
| **decided** | an exact decision: an enclosure, an exact comparison, a proof | solid |
| **computed** | floating point, a solver's tolerance, a fit, a number someone printed | dashed `5 4` |
| **chosen** | one member of a set the data allow, picked by something that is not the data (a default, a tie-break, a seed) | dotted `1 5` |
| **refused** | the method declined, or the input is missing | **no mark**: a hatched void and ∅ in words |

- **Standing is not a verdict.** Words carry verdicts; the stroke carries standing; colour carries neither.
- **At most three series are compared in one figure**, each with its own colour *and* marker (● ■ ▲), so a greyscale
  copy loses nothing. More than three is a set of small panels.
- **One red**, only on a × beside words, for a counterexample that is shown.
- The `2 3` pattern is a guide (a ruler, a leader) and says nothing. No other dash pattern is ever drawn.
- A legend wherever a standing is drawn. The helpers refuse what the grammar forbids — a stroke for *refused*, a void
  or a witness without words, a fourth series, a caller's own colour or dash on a standing line.

## Colour for fields — a proposal

WARRANT's colours are ink, three identities and one neutral ramp. Metocean figures also colour a **quantity spread over a
plane** — Hs over a basin, a density of sea states, the difference between two hindcasts, a mean direction. `leadline.fields`
proposes three roles, each one of Fabio Crameri's maps (`cmcrameri`, already common in metocean code), chosen by WARRANT's own
colour rules and measured by `tools/validate_fields.py` (every number below is in `fields-report.json`):

| role | map | why this one |
|---|---|---|
| magnitude | `oslo` (reversed on paper: more is darker) | sequential, lightness monotone, no yellow or orange (a WARRANT rule) |
| difference | `bam` | the only diverging Crameri map with no yellow or orange whose two sides stay apart for normal vision and for the three colour-vision deficiencies (ΔE ≥ 15 / ≥ 8) |
| direction | `bamO` | cyclic, the hues of `bam` |

It comes with four rules: a field never carries standing or a verdict; on a coloured field, series are told apart by
marker and word (the second-series blue sits ΔE 3.8 from the magnitude map); the witness × over a field is drawn on a
paper casing (the red nearly vanishes against `bam`); a colour bar names the quantity, its unit and its source. Until the
proposal is approved, `leadline.mpl.field` (the neutral ramp) is the approved way to draw a field.

## The examples

`examples/out/` holds every figure already drawn (SVG for print, HTML for the screen; each with a greyscale twin):

| example | shows |
|---|---|
| `ex1_design_wave` | a certified 100-year Hs by block: the picked family decided, the other hollow, the delta interval computed, a refused choice as a void with words |
| `ex2_return_curve` | a return-level curve: certified knots decided, the joins chosen, the 100-year period a guide, the premise ladder |
| `ex3_contours` | three submitted 20-year environmental contours over the hours counted exactly into cells (the neutral ramp). Its small side panel is the kit's demonstration of the witness, on an unrelated record (a printed arithmetic step that does not hold) |
| `ex4_fields` | **the proposal**: a synthetic magnitude field with an interpolated level line (computed), and a synthetic difference field |
| `plotly_ex*` | the same figures in plotly; legends and colour bars sit under the plot, so they read at a phone's 390 px |

The data of examples 1–3 come from cert-machine's public records (buoy A of NDBC; dataset A of the environmental-contour
benchmark) and carry their own licence: see `examples/data/README.md`. Example 4 is made up and says so.

## To iterate — what would help us most

1. **Your style files and three or four figures** you put in reports (a `virocon` contour, return levels, a wind rose, an Hs
   map). We redraw them in Leadline, and the grammar meets your figures rather than ours.
2. **Where responsiveness hurts**: plotly HTML on phones, notebooks, report PDFs? The plotly template already moves legends
   and colour bars under the plot; we can measure your outputs at desktop and phone widths the way cert-machine measures
   its own pages.
3. **Which colours you need** beyond the three field roles — more series in one figure, categorical sites, a fixed colour per
   variable? Each becomes a reasoned proposal, measured the same way.
4. **Figma**: `tokens/leadline.tokens.json` imports with Tokens Studio; tell us which variables and styles you want.

## How Leadline stays WARRANT

`leadline/mpl/` and the examples' data are copied byte for byte from cert-machine's `kits/warrant-mpl`, and the three
matplotlib examples are adapted by one import line; `PINS.json` names each file with its sha256 and the cert-machine
commit. `python tools/pins.py --check` refuses an edited copy and, beside a cert-machine checkout, names what moved there.
A change to the grammar itself starts in cert-machine; a change to the proposal starts in `leadline/fields.py`.

```bash
python -m pytest tests/                     # the checks, each with its red control
python tools/build_docs.py                  # rebuild docs/ (the documentation page) from the package
cd docs && npx vercel deploy --prod         # publish it (the Vercel project "leadline")
python tools/validate_fields.py --check      # the proposal's numbers are what the maps measure
python tools/tokens.py --check               # the Figma tokens are what the sources give
python examples/plotly_examples.py           # redraw the plotly examples (the matplotlib ones: examples/ex*.py)
```

## Licence

MIT (`LICENSE`). The examples' data are not covered by it: see `examples/data/README.md`. The colour maps are Fabio
Crameri's (Crameri, Shephard & Heron 2020, *Nature Communications* 11, 5444), used through `cmcrameri`.
