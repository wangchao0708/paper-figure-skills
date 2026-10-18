# Venue template sources

Snapshot date: **2026-10-17**. Templates are committed because the repository is private. Retrieved versions are the latest official versions available on this date; where the next edition's kit has not been released, the most recent kit is used and noted below.

`templates/<id>/min.tex` uses the camera-ready mode. `%%BODY%%` is replaced by the probe or preview generator; `\null` keeps the otherwise empty minimal document compilable as one page.

## Summary

| id | venue | template version | official source | class / package line |
| --- | --- | --- | --- | --- |
| cvpr | CVPR | CVPR2026-v1 (latex), commit `12909ae` | https://github.com/cvpr-org/author-kit/releases/tag/CVPR2026-v1%28latex%29 | `\documentclass[10pt,twocolumn,letterpaper]{article}` + `\usepackage{cvpr}` |
| iccv | ICCV | ICCV 2025 Author Kit (latest available) | https://media.eventhosts.cc/Conferences/ICCV2025/ICCV2025-Author-Kit.zip | `\documentclass[10pt,twocolumn,letterpaper]{article}` + `\usepackage{iccv}` |
| neurips | NeurIPS | NeurIPS 2026 style files (2026-06-23) | https://media.neurips.cc/Conferences/NeurIPS2026/Formatting_Instructions_For_NeurIPS_2026.zip | `\documentclass{article}` + `\usepackage[main,final]{neurips_2026}` |
| iclr | ICLR | ICLR 2027 kit, `ICLR/Master-Template` commit `46ed6f4` (2026-09-01) | https://github.com/ICLR/Master-Template/tree/46ed6f4c6cef5b175dde23639e77d44c3463b230/iclr2027 | `\documentclass{article}` + `\usepackage{iclr2027_conference,times}` + `\iclrfinalcopy` |
| icml | ICML | ICML 2026 style v2.0 (2025/10/29) | https://media.icml.cc/Conferences/ICML2026/Styles/icml2026.zip | `\documentclass{article}` + `\usepackage[accepted]{icml2026}` |
| acl | ACL | `acl-org/acl-style-files` commit `d5adc82` (2026-06-29) | https://github.com/acl-org/acl-style-files/tree/d5adc823ff0f80f98c80405ca0ab66c68e684409 | `\documentclass[11pt]{article}` + `\usepackage[final]{acl}` |
| aaai | AAAI | AAAI-27 Author Kit, `aaai2027.sty` 2027/05/04 | https://aaai.org/authorkit27/ (redirects to `AuthorKit27.zip`) | `\documentclass[letterpaper]{article}` + `\usepackage{aaai2027}` |
| acmmm | ACM MM | `acmart` v2.16 (2025/08/27), bundled with TeX Live 2026 | https://www.acm.org/publications/proceedings-template | `\documentclass[sigconf]{acmart}` |
| ccs | ACM CCS | `acmart` v2.16 (2025/08/27), bundled with TeX Live 2026 | https://www.acm.org/publications/proceedings-template | `\documentclass[sigconf]{acmart}` |
| sp | IEEE S&P | IEEEtran v1.8b (2015/08/26), S&P 2027 CFP | https://sp2027.ieee-security.org/cfpapers.html | `\documentclass[conference,compsoc]{IEEEtran}` |
| usenixsec | USENIX Security | `usenix2019_v3.2.tex` (updated 2026-09-10) + `usenix2019_v3.sty` | https://www.usenix.org/conferences/author-resources/paper-templates | `\documentclass[letterpaper,twocolumn,10pt]{article}` + `\usepackage{usenix2019_v3}` |
| ndss | NDSS | NDSS 2027 template (`bare_conf_NDSS2027.tex`, 2026-07-31) + NDSS IEEEtran V1.8b | https://www.ndss-symposium.org/ndss2027/submissions/templates/ | `\documentclass[conference]{IEEEtran}` (local NDSS class) |
| tifs | IEEE TIFS | IEEEtran v1.8b (2015/08/26) | https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/ | `\documentclass[journal]{IEEEtran}` |
| tmm | IEEE TMM | IEEEtran v1.8b (2015/08/26) | https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/ | `\documentclass[journal]{IEEEtran}` |
| tpami | IEEE TPAMI | IEEEtran v1.8b (2015/08/26) | https://journals.ieeeauthorcenter.ieee.org/create-your-ieee-journal-article/authoring-tools-and-templates/tools-for-ieee-authors/ieee-article-templates/ | `\documentclass[journal,compsoc]{IEEEtran}` |
| ijcv | IJCV | Springer Nature LaTeX template, December 2024 (`sn-jnl`) | https://www.springernature.com/gp/authors/campaigns/latex-author-support | `\documentclass[iicol,pdflatex,sn-basic]{sn-jnl}` |

## Notes and decisions

### CVPR / ICCV
- CVPR uses the latest released kit, CVPR 2026 (`cvpr.sty` provides `2026`). CVPR 2027 and ICCV 2027 kits were not published on the retrieval date.
- ICCV 2027 was not published either; the latest official kit is ICCV 2025, whose `iccv.sty` provides `2025`.
- Camera-ready mode is the default when loading `cvpr` / `iccv` without `[review]`.
- Both kits use US Letter and two columns.
- Local files: `cvpr.sty`, `iccv.sty`, `ieeenat_fullname.bst`.

### NeurIPS
- Downloaded from the official 2026 CFP link. The zip timestamp is 2026-06-23.
- `final` selects the camera-ready version; `main` selects the main track.
- Local files: `neurips_2026.sty`, plus the official example source and checklist for reference.

### ICLR
- `ICLR/Master-Template` gained the `iclr2027` directory in commit `46ed6f4` on 2026-09-01.
- The template uses `\documentclass{article}`; `\iclrfinalcopy` selects camera-ready mode.
- Local files include the official `fancyhdr.sty` and `natbib.sty`, so compilation matches the kit.

### ICML
- Official 2026 style zip; `icml2026.sty` is version 2.0, dated 2025/10/29.
- `[accepted]` selects the camera-ready version.
- The class requires a running title and the affiliations/notice command; `min.tex` supplies minimal values so the empty document compiles. `\printAffiliationsAndNotice{}` is required by the class.

### ACL
- Latest official style repository commit; `[final]` is the camera-ready mode and is the package default. `times` is loaded to match the official template.
- ACL's template uses A4 paper (595.28 × 841.89 pt), unlike the US Letter conferences.
- Local files: `acl.sty`, `acl_natbib.bst`, official sample and README.

### AAAI
- AAAI-27 author kit downloaded from `https://aaai.org/authorkit27/`, which redirects to `https://aaai.org/wp-content/uploads/2026/05/AuthorKit27.zip` (last modified 2026-05-28).
- `aaai2027.sty` is dated 2027/05/04. Camera-ready is the default; do not pass `submission`.
- The style loads `newtxtext`, which makes the body Times-compatible; do not add `times`.
- Local files: `aaai2027.sty`, `aaai2027.bst`, and the official camera-ready source.

### ACM MM / CCS
- Per BUILD.md, both use the `acmart` bundled with MacTeX rather than a downloaded copy. TeX Live 2026 ships `acmart` v2.16 (2025/08/27).
- `sigconf` is the ACM two-column conference proceedings option. Camera-ready is the default; review/anonymity options are not used.
- If TeX Live is updated, record the new `acmart` version here and re-run the probes.

### IEEE S&P
- The S&P 2027 CFP explicitly requires IEEEtran v1.8b with `conference,compsoc` and warns that other templates (including non-compsoc IEEE conference) are not acceptable.
- TeX Live 2026 provides IEEEtran V1.8b (2015/08/26), matching the CFP.

### USENIX Security
- Official USENIX template page. `usenix2019_v3.2.tex` was last modified 2026-09-10; the style file `usenix2019_v3.sty` is dated 2019-12-18.
- The template has no separate camera-ready class option; it always uses the two-column, Times 10 pt layout.
- Local files: `usenix2019_v3.sty` and `usenix2019_v3.2.tex`.

### NDSS
- Official NDSS 2027 template page provides `bare_conf_NDSS2027.tex` (last modified 2026-07-31) and the NDSS-patched `IEEEtran-4.cls` (V1.8b, last modified 2025-08-14).
- The local file is named `IEEEtran.cls` so it takes precedence over the system class, matching the official instruction not to use a different IEEEtran copy.
- Local files: `IEEEtran.cls` and `bare_conf_NDSS2027.tex`.

### IEEE TIFS / TMM / TPAMI
- These journals use the IEEEtran class from TeX Live 2026 (V1.8b), which is the official class distributed by IEEE.
- TIFS and TMM use `journal`; TPAMI uses `journal,compsoc` (Computer Society journal mode).
- The class files are not duplicated into the repository because TeX Live provides the official V1.8b unchanged.

### IJCV
- Springer Nature's official LaTeX authoring template (December 2024 zip), class `sn-jnl`.
- The IJCV submission guidelines explicitly require the `[iicol]` formatting option. `pdflatex` is used for compilation.
- `sn-basic` is selected for author-year references, matching the journal's "name and year in parentheses" citation rule. The class and all official `.bst` files are included locally.
- IJCV uses A4 paper (595.28 × 841.89 pt).
- `min.tex` loads `amsmath`, `amssymb`, and `amsfonts`; `sn-jnl.cls` calls `\allowdisplaybreaks` at `\begin{document}` but does not load `amsmath` itself.

## Local artifact checksums

SHA-256, for detecting accidental edits to downloaded style files:

```text
2602473285d1a7df2a445ac89b76e1afa0acab78e056f0369d19770245190153  cvpr/cvpr.sty
d4b522c1b3ecc0029d23f3d057383fd3bc8145c9aebf47f1b7058e91a35e3eff  iccv/iccv.sty
c3fc2894e83d2517ca18b66741d6c595986d97957dc08ec08bb2125a7ec4555a  neurips/neurips_2026.sty
797deef41724e93761426ac0cbcca46279a91cc650dd1f0ce76a4f08d2098ea6  iclr/iclr2027_conference.sty
7cdcf90f6a59c5219e7f15c88f7ed09fcaf598dad91e6cdddc4dc3cb0e397a95  icml/icml2026.sty
19dfeddc2c0e448f3926a0bef048a9db3f3611b46265b760caabd7ada4f361de  acl/acl.sty
391bce82815bf698b8e382dd3ae7e30c75d7ab46df140cb295b1266016bc8623  aaai/aaai2027.sty
4ed9aa9d0c5daec54ce3b4188a4bf6d3bef3462c79ff65551d567511d3c45ff6  usenixsec/usenix2019_v3.sty
c972aca108fda004c3514d63658e02816da2e54d9a1451e870b9bd970e003f55  ndss/IEEEtran.cls
36d0c3273a59d48dc6a9c7b080dfa1ec50dc10229d8751568d1f2e490ffa5ecc  ijcv/sn-jnl.cls
6895475b24fe526c12831f5cc1d16f37218ce5d65161f811dde4bce8dc4551b9  (system) acmart.cls v2.16
```
