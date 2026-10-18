# Template compilation

`min.tex` files use camera-ready modes. `\null` is kept after `%%BODY%%` only so the otherwise empty document produces a page for compilation checking; the probe/preview replaces `%%BODY%%` with real content.

`acmmm` and `ccs` contain `\twocolumn`: `acmart` enters the final two-column layout only inside `\maketitle`, so the minimal template switches columns explicitly. `tpami` contains the IEEEtran-sanctioned `\renewcommand{\rmdefault}{ptm}` override to use Times instead of the `compsoc` default Palatino.

Compile check:

```bash
for venue in cvpr iccv neurips iclr icml acl aaai acmmm ccs sp usenixsec ndss tifs tpami ijcv tmm; do
  mkdir -p "build/phase1/$venue"
  (cd "templates/$venue" && latexmk -pdf -interaction=nonstopmode -halt-on-error \
    -outdir="../../build/phase1/$venue" min.tex)
done
```

## Phase 1 result

| venue | documentclass / package | pages | page size (pt) | status |
| --- | --- | ---: | --- | --- |
| cvpr | `\documentclass[10pt,twocolumn,letterpaper]{article}`<br>`\usepackage{cvpr}` | 1 | 612.00 × 792.00 | OK |
| iccv | `\documentclass[10pt,twocolumn,letterpaper]{article}`<br>`\usepackage{iccv}` | 1 | 612.00 × 792.00 | OK |
| neurips | `\documentclass{article}`<br>`\usepackage[main,final]{neurips_2026}` | 1 | 612.00 × 792.00 | OK |
| iclr | `\documentclass{article}`<br>`\usepackage{iclr2027_conference,times}` + `\iclrfinalcopy` | 1 | 612.00 × 792.00 | OK |
| icml | `\documentclass{article}`<br>`\usepackage[accepted]{icml2026}` | 1 | 612.00 × 792.00 | OK |
| acl | `\documentclass[11pt]{article}`<br>`\usepackage[final]{acl}` | 1 | 595.28 × 841.89 | OK |
| aaai | `\documentclass[letterpaper]{article}`<br>`\usepackage{aaai2027}` | 1 | 612.00 × 792.00 | OK |
| acmmm | `\documentclass[sigconf]{acmart}` | 1 | 612.00 × 792.00 | OK |
| ccs | `\documentclass[sigconf]{acmart}` | 1 | 612.00 × 792.00 | OK |
| sp | `\documentclass[conference,compsoc]{IEEEtran}` | 1 | 612.00 × 792.00 | OK |
| usenixsec | `\documentclass[letterpaper,twocolumn,10pt]{article}`<br>`\usepackage{usenix2019_v3}` | 1 | 612.00 × 792.00 | OK |
| ndss | `\documentclass[conference]{IEEEtran}` (NDSS V1.8b) | 1 | 612.00 × 792.00 | OK |
| tifs | `\documentclass[journal]{IEEEtran}` | 1 | 612.00 × 792.00 | OK |
| tpami | `\documentclass[journal,compsoc]{IEEEtran}` + Times override | 1 | 612.00 × 792.00 | OK |
| ijcv | `\documentclass[iicol,pdflatex,sn-basic]{sn-jnl}` | 1 | 595.28 × 841.89 | OK |
| tmm | `\documentclass[journal]{IEEEtran}` | 1 | 612.00 × 792.00 | OK |

All 16 logs contain zero `^!` errors and zero `Overfull \hbox` warnings. Sources and versions are recorded in `skills/paper-figure-spec/references/venue_sources.md`.

## Phase 2 reference check

Reference values in BUILD.md are sanity checks only. All compared values are within 2% except:

- S&P `columnwidth_pt`: measured 243.91 vs reference 252 (−3.21%). The S&P 2027 CFP explicitly requires the `conference,compsoc` options; compsoc changes the column geometry. The measured value is retained.
- TPAMI has no BUILD.md reference value. Because `compsoc` defaults to Palatino, the template uses the IEEEtran-sanctioned `ptm` override so its family stays in the supported set; measured body size is 9.54 pt.
