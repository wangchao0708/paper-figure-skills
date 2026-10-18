# Paper figure rules

## Width

- Two-column templates: `single` = `\columnwidth`; `double` = `\textwidth`.
- Single-column templates (NeurIPS, ICLR, etc.): `single` = `0.48 × \textwidth`; `double` = `\textwidth`.
- All stored values are TeX pt. Convert to inches with `in = pt / 72.27`.
- Do not use `bbox_inches="tight"`; it changes the final width. Use `layout="constrained"`.

## Font sizes

- Take the template's own levels, with a lower bound of 6 pt.
- Labels, legends and annotations: `\footnotesize`.
- Ticks: `\scriptsize`.
- Panel titles: `\small`.
- Use the family exposed by `figspec spec`:
  - times → Times New Roman
  - libertine → Linux Libertine O
  - cm → Latin Modern Roman
- Call seaborn's `set_theme` / `set_context` before `figspec.setup()`; they overwrite font sizes.

## Export and embedding

- Export at the final physical size. Insert in LaTeX with `\includegraphics{fig.pdf}`, without `width`.
- Use PDF for submission. Use SVG only for further editing in draw.io.
- Run `figspec check` on every exported PDF. Fix all FAILs before submission.

## Draw.io

- Open `references/drawio.md` for the calibrated import scale and font-unit conversion.
- The `figspec spec` output includes a draw.io line for canvas width and font sizes.
- If importing a matplotlib SVG, apply the documented import compensation before relying on 1:1 dimensions.

## Data integrity

- Do not hand-edit `figspec/data/venues.yaml`.
- Re-probe after replacing a template: `figspec probe <venue>`.
- Recalibrate draw.io only after changing the calibration protocol: `figspec calib --measure`.

## Height

- The figure height is determined by its content; no fixed height is imposed.
