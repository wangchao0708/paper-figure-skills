# paper-figure-skills 构建计划

> 本文件供 coding agent（opencode + DeepSeek，或 Codex）执行，放在仓库根目录。安装与使用说明见 README.md。

## 执行规则（必须遵守）

1. 每次只执行一个 Phase。完成后按顺序做三件事：
   - 运行该 Phase 的「验收」；
   - 执行 `git add -A && git commit -m "phase N: <摘要>"`；
   - 停下来向我汇报（做了什么、验收输出、遗留问题），等我回复后再进入下一个 Phase。
2. 本文件没有覆盖到的决策，先问我，不要猜。
3. 所有检查都以脚本输出的数值为准，不依赖查看图片。
4. 代码中不得写死 `~/.codex`、`~/.config/opencode` 等路径。仓库根目录用 `Path(__file__).resolve().parents[1]` 推出，并允许用环境变量 `FIGSPEC_HOME` 覆盖。
5. 运行环境为 macOS + MacTeX。Python 环境在 Phase 0 问我，之后所有 python/pip 命令都在该环境中执行。
6. 需要 sudo 的命令不要自己执行，把命令交给我。

## 目标

输入 (venue, layout)，其中 layout ∈ {single（单栏）, double（双栏）}。输出该 venue 下的画布宽度、各级字号和字体，并提供以下功能：一行设置 matplotlib、检查成品图、用官方模板在本地编译预览。

支持的 venue：CVPR ICCV NeurIPS ICLR ICML ACL AAAI MM CCS S&P USENIX-Security NDSS TIFS TPAMI IJCV TMM

### 规则

- 宽度
  - 双栏模板：single = `\columnwidth`，double = `\textwidth`。
  - 单栏模板（NeurIPS、ICLR 等）：single = 0.48 × `\textwidth`，double = `\textwidth`。
- 单位：所有数值以 TeX pt 存储，换算英寸时用 in = pt / 72.27。
- 字号：直接取模板自身的字号层级，下限 6 pt。
  - label、legend、annotation 用 `\footnotesize`；
  - tick 用 `\scriptsize`；
  - panel title 用 `\small`。
- 字体与正文一致：times 用 Times New Roman；libertine 用 Linux Libertine O；cm 用 Latin Modern Roman。
- 成品图按最终尺寸导出，LaTeX 中用 `\includegraphics{fig.pdf}` 插入，不带 width。

### 强约束（写入 AGENTS.md 和 SKILL.md）

- 禁止使用 `bbox_inches="tight"`，它会改变成品宽度；布局一律用 `layout="constrained"`。
- seaborn 的 `set_theme` / `set_context` 会覆盖字号，必须在 `figspec.setup()` 之前调用。
- `venues.yaml` 中的数值只能由探针生成，禁止手改。
- 图的高度不做规定，由内容决定。

## 仓库结构

```
paper-figure-skills/
├── AGENTS.md                    # 仓库约定（≤ 30 行）
├── BUILD.md                     # 本文件
├── README.md                    # 安装、使用、每年更新模板
├── install.sh                   # 把 skill 链接到 opencode 与 Codex 的目录
├── pyproject.toml               # pip install -e . 后得到 figspec 包与 CLI
├── .gitignore
├── skills/
│   └── paper-figure-spec/       # 目录名 = skill ID = frontmatter name
│       ├── SKILL.md
│       └── references/
│           ├── rules.md         # 上面的规则与强约束
│           ├── venue_sources.md # 每个 venue 的模板来源、版本、documentclass 选项
│           └── drawio.md        # draw.io 校准结果与流程
├── figspec/
│   ├── __init__.py              # 导出 setup()
│   ├── cli.py                   # figspec {spec,probe,check,preview,fonts,calib,fetch}
│   ├── spec.py                  # 宽度、字号、字体规则；读取 venues.yaml 与 .figspec.yaml
│   ├── probe.py
│   ├── check.py
│   ├── preview.py
│   ├── fonts.py                 # 查找 OTF、安装到 ~/Library/Fonts、刷新 matplotlib 缓存
│   └── data/venues.yaml
├── templates/<venue>/           # 官方模板 + min.tex
└── tests/
```

---

## Phase 0 仓库与环境

1. 先问我三件事：
   - Python 环境（conda 环境名或 venv 路径）；
   - GitHub 仓库名，默认 `paper-figure-skills`；
   - 仓库可见性，默认 private。
2. 检查 TeX 环境：`which latexmk pdflatex kpsewhich`，以及 `kpsewhich acmart.cls IEEEtran.cls`。缺少的包给出对应的 `sudo tlmgr install <pkg>` 命令，由我执行。
3. 安装命令行工具：
   - `brew install poppler`，提供 pdffonts；
   - 检查 `gh --version`，未安装则 `brew install gh`；未登录则让我执行 `gh auth login`。
4. 写 `.gitignore`，内容包括：`*.aux *.log *.out *.fls *.fdb_latexmk *.synctex.gz __pycache__/ *.egg-info/ .DS_Store build/ calib/out*`。
5. 写 `pyproject.toml`：依赖 matplotlib、seaborn、pymupdf、pyyaml；console script 为 `figspec = figspec.cli:main`。然后执行 `pip install -e .`。
6. 写 `AGENTS.md`，不超过 30 行，摘录「执行规则」和「强约束」。
7. 写 `README.md` 骨架，含「安装」「使用」「每年更新模板」三节，后续 Phase 逐步补全。

**验收：**
- `figspec --help` 能正常输出；
- `gh repo create <name> --<visibility> --source=. --remote=origin --push` 执行成功。

## Phase 1 获取模板

从官方来源下载最新版模板，把版本号、URL 和 documentclass 选项记入 `references/venue_sources.md`。documentclass 选项以最新 CFP 或作者指南为准，例如 S&P 是否使用 compsoc。

| venue | 模板来源 |
| --- | --- |
| CVPR / ICCV | CVPR author kit（GitHub cvpr-org/author-kit）；ICCV 用其最新的 author kit |
| NeurIPS | neurips.cc 当年的 style files |
| ICLR | GitHub ICLR/Master-Template |
| ICML | icml.cc 作者指南中的 style files |
| ACL | GitHub acl-org/acl-style-files |
| AAAI | AAAI 官网 Author Kit |
| MM、CCS | MacTeX 自带的 acmart，`\documentclass[sigconf]{acmart}` |
| S&P | IEEEtran conference，选项按 CFP 确认 |
| NDSS | NDSS 官网模板 |
| USENIX Security | usenix.org 的 LaTeX 模板 |
| TIFS、TMM | IEEEtran `journal` |
| TPAMI | IEEEtran `journal,compsoc` |
| IJCV | Springer Nature 官方 LaTeX 模板（sn-jnl） |

- 为每个 venue 写 `templates/<venue>/min.tex`：只保留 documentclass、venue 宏包（camera-ready 模式），以及 `\begin{document}` 之后的 `%%BODY%%` 占位。
- 有下载不到的模板时，列出清单并问我。
- 关于是否提交模板文件：
  - 仓库为 private：模板直接提交。
  - 仓库为 public：把第三方模板文件加入 .gitignore，改为由 `figspec fetch <venue>|--all` 按 venue_sources.md 下载。

**验收：** 每个 min.tex 都能用 `latexmk -pdf` 单独编译通过，并输出一张汇总表。

## Phase 2 探针：`figspec probe`

- `figspec probe <venue>` 或 `figspec probe --all`：
  - 在 `\begin{document}` 之后插入下面的探针，再加一段正文，用 latexmk 编译，然后从 .log 中解析 FIGSPEC 行：

    ```tex
    \makeatletter
    \typeout{FIGSPEC twocolumn=\if@twocolumn 1\else 0\fi}
    \typeout{FIGSPEC textwidth=\the\textwidth}
    \typeout{FIGSPEC columnwidth=\the\columnwidth}
    \typeout{FIGSPEC body=\f@size}
    {\small\typeout{FIGSPEC small=\f@size}}
    {\footnotesize\typeout{FIGSPEC footnotesize=\f@size}}
    {\scriptsize\typeout{FIGSPEC scriptsize=\f@size}}
    \makeatother
    ```

  - 用 pdffonts 读出正文字体名，归入 family ∈ {times, libertine, cm, other}。遇到 other 时问我。
  - 结果写入 `figspec/data/venues.yaml`，字段为：source, class_opts, twocolumn, textwidth_pt, columnwidth_pt, body_pt, small_pt, footnotesize_pt, scriptsize_pt, body_font, family, probed_at, aliases。
  - aliases 示例：
    - sp ← ["S&P", "IEEE S&P", "Oakland"]
    - usenixsec ← ["USENIX Security", "USENIX Sec"]
    - acmmm ← ["MM", "ACM MM"]
- `figspec probe --tex <paper>/main.tex --venue <venue>`：把论文工程复制到临时目录，插入探针后编译。结果写入 `<paper>/.figspec.yaml`，**不写入本仓库**。
- 查找顺序：从当前目录逐级向上查找 `.figspec.yaml`；找不到时才使用仓库的 `venues.yaml`。

**验收：**
1. 16 个 venue 全部探测成功，打印汇总表：venue | twocolumn | columnwidth | textwidth | body | small/footnotesize/scriptsize | family。
2. 与下列参考值比较。参考值凭记忆给出，只用于 sanity check。偏差超过 2% 时标出来、对照模板复核，但不要把探测值改成参考值。
   - IEEEtran（TIFS、TMM、S&P）：textwidth ≈ 516 pt，columnwidth ≈ 252 pt，正文 10 pt；compsoc 可能不同
   - acmart sigconf（MM、CCS）：textwidth ≈ 506 pt，columnwidth ≈ 241 pt，正文 9 pt
   - NeurIPS、ICLR：单栏，textwidth ≈ 397.5 pt，正文 10 pt
   - ACL：columnwidth ≈ 219 pt，正文 11 pt
   - CVPR：textwidth ≈ 497 pt，columnwidth ≈ 237 pt
   - ICML：textwidth ≈ 488 pt，columnwidth ≈ 235 pt

## Phase 3 规格与字体：`figspec spec` / `setup()`

- `figspec fonts --install`：
  - 用 kpsewhich 在 MacTeX 中找到 Linux Libertine 和 Latin Modern 的 OTF，复制到 `~/Library/Fonts`（draw.io 也要用这些字体）；
  - Times New Roman 使用 macOS 系统自带字体；
  - 最后重建 matplotlib 字体缓存。
- `figspec.setup(venue, layout)` 需要设置以下 rcParams：
  - 字体与字号：font.family/serif、font.size、axes.labelsize、axes.titlesize、xtick/ytick.labelsize、legend.fontsize、legend.title_fontsize、figure.titlesize；
  - mathtext：times 用 stix，cm 用 cm，libertine 用 custom；
  - `pdf.fonttype=42`、`ps.fonttype=42`，避免 Type 3 字体；
  - `svg.fonttype='none'`，让 SVG 文字保留为文本；
  - `savefig.bbox=None`。
  
  函数返回 spec 对象，包含 width_in、width_pt、各级字号和 family。
- `figspec spec CVPR single` 输出一行：
  `CVPR · 单栏 → 3.28 in / 237.1 pt / 8.33 cm · Times New Roman · 标签/图例 8 · 刻度 7 · 子图标题 9 (pt)`

**验收：** 给出 4 个 venue 的 spec 输出，并确认 `figspec fonts --check` 显示三种字体都能被 matplotlib 找到。

## Phase 4 检查：`figspec check fig.pdf <venue> <layout>`

- 宽度：页面宽度与目标宽度的偏差 ≤ 1%。
- 字号：用 PyMuPDF 提取所有文字 span 的字号，输出分布及最小、最大值。小于 6 pt 或大于 small_pt 时判 FAIL。
- 字体：用 pdffonts 检查所有字体都已嵌入且没有 Type 3。字体族与 venue 不符时给 WARN。

**验收：** 用 matplotlib 生成一张含 8 pt 文字的图，check 报告 8.0±0.1。如果不符，改用 pdfplumber 实现。

## Phase 5 预览：`figspec preview <venue> <layout> fig.pdf [fig2.pdf]`

- 基于 min.tex 生成 preview.tex，内容依次为：一段 lipsum 正文、图、再一段正文。
- 图环境：
  - 双栏模板：single 用 figure，double 用 figure*；
  - 单栏模板：single 用两个 0.48\textwidth 的 minipage 并排（只给一张图时复制一份），double 用 figure。
- `\includegraphics` 不带 width。
- TEXINPUTS 指向 `templates/<venue>`，输出到 `build/preview/<venue>-<layout>/`。log 中出现 Overfull \hbox 时给出警告。
- 编译成功后用 `open` 打开 PDF。

**验收：** 对 CVPR 和 NeurIPS 的 single/double 各生成一份预览，共 4 份。

## Phase 6 draw.io 校准：`figspec calib`（需要我手动配合一次）

1. 生成 `calib/calib.svg` 和 `calib/calib.pdf`：宽 237 pt，包含 8 pt 文字 "Calib-8pt" 和一条 1 in 长的参考线。
2. 告诉我操作步骤：在 draw.io 中导入 calib.svg，不做缩放；新增一个字号设为 10 的文字框；勾选 Crop 后导出 PDF，存为 `calib/out.pdf`。然后等我完成。
3. 用 check 测量 out.pdf，得出两件事：导入的 SVG 是否保持 1:1；draw.io 字号单位与 pt 的换算系数。结果写入 `references/drawio.md` 和 venues.yaml 的全局字段。
4. 在 `figspec spec` 的输出中追加一行 draw.io 等效值：页面宽度，以及各级字号在 draw.io 中应填的数值。

## Phase 7 SKILL.md 与安装

1. 写 `skills/paper-figure-spec/SKILL.md`。

   frontmatter（name 必须与目录名一致）：

   ```yaml
   ---
   name: paper-figure-spec
   description: 为学术论文绘图确定画布宽度、字号与字体。用户给出会议或期刊名（如 CVPR、NeurIPS、ACL、CCS、TPAMI）及单栏/双栏，或要求按某 venue 规范出图、检查图中字号、本地预览图在论文中的效果时使用。
   ---
   ```

   正文不超过 80 行。文中路径一律相对于本 SKILL.md 所在目录，内容包括：
   1. 解析 venue（不区分大小写，查 aliases）和 layout（单栏/single、双栏/double）。遇到未知 venue 先问用户。
   2. 运行 `figspec spec <venue> <layout>`，先向用户回显一行规格。如果 `figspec` 命令不存在，提示用户在其 Python 环境中执行 `pip install -e <仓库根>`。仓库根为本目录 realpath 的上两级。
   3. 画图代码中 `import figspec; spec = figspec.setup(venue, layout)`，并设 `figsize=(spec.width_in, h)`。导出 PDF 用于投稿；需要在 draw.io 里修改时另外导出 SVG。
   4. 每张图都必须运行 `figspec check`，FAIL 时修正后重新导出。
   5. 用户要求预览时运行 `figspec preview`。
   6. 用户提供论文工程路径时，先运行 `figspec probe --tex`，以工程实际使用的模板为准。
   7. LaTeX 中插图写成 `\includegraphics{fig.pdf}`，不带 width。
   8. 遵守「强约束」，详见 `references/rules.md`。
2. 写 `install.sh`，用法为 `./install.sh [--copy] [--only opencode|codex]`：
   - 安装目标：
     - `~/.config/opencode/skills/paper-figure-spec`
     - `~/.codex/skills/paper-figure-spec`
   - 默认用 `ln -sfn` 链接到 `<repo>/skills/paper-figure-spec`，之后 `git pull` 即可更新。加 `--copy` 时改用 `rsync -a --delete` 复制。
   - 目标位置已存在、且不是指向本仓库的链接时，先备份为 `.bak-<时间戳>` 再替换。
   - 脚本必须幂等。结束时提示执行 `pip install -e <repo>`，并重启 opencode/Codex。
3. 补全 README.md：
   - 安装：`git clone` → `./install.sh` → `pip install -e .` → `figspec fonts --install`
   - 使用示例
   - 每年更新模板：替换 `templates/<venue>` → `figspec probe <venue>` → 检查 venues.yaml 的 diff → commit

**验收：**
1. install.sh 连续运行两次，结果一致。
2. 新开一个 opencode 会话，让它列出可用的 skills，结果中应包含 paper-figure-spec。如果没有，用 `./install.sh --copy` 重装再试，并在 README 中写明是否需要 `--copy`。

## Phase 8 总验收与发布

1. 为 CVPR、NeurIPS、CCS、ACL 各画一张示例折线图，single 和 double 各一张，共 8 张，放在 `examples/`。
2. 8 张图的 `figspec check` 全部 PASS，`figspec preview` 编译出 8 个 PDF，汇报它们的路径。
3. 运行 `tests/` 中的测试：覆盖 spec 规则、aliases 解析、check 自测。
4. 最后执行 `git tag v0.1 && git push --follow-tags`。
