---
name: paper-figure-spec
description: 为学术论文绘图确定画布宽度、字号与字体。用户给出会议或期刊名（如 CVPR、NeurIPS、ACL、CCS、TPAMI）及单栏/双栏，或要求按某 venue 规范出图、检查图中字号、本地预览图在论文中的效果时使用。
---

# paper-figure-spec

为论文绘图确定与官方模板一致的画布宽度、字号和字体，并检查成品图。

## 工作流

1. 解析 venue（不区分大小写，查 aliases）和 layout（单栏/single、双栏/double）。未知 venue 先问用户。
2. 运行 `figspec spec <venue> <layout>`，先向用户回显规格行。若 `figspec` 不存在，提示用户在目标 Python 环境执行 `pip install -e <仓库根>`；仓库根为本目录 realpath 的上两级（`../..`）。
3. 画图代码使用：
   ```python
   import figspec

   spec = figspec.setup(venue, layout)
   fig, ax = plt.subplots(figsize=(spec.width_in, h), layout="constrained")
   ```
   图高由内容决定。投稿导出 PDF；需要在 draw.io 修改时另外导出 SVG。
4. 每张图必须运行 `figspec check <fig.pdf> <venue> <layout>`；FAIL 时修正后重新导出。
5. 用户要求预览时运行 `figspec preview <venue> <layout> <fig.pdf> [fig2.pdf]`。
6. 用户提供论文工程路径时，先运行 `figspec probe --tex <paper>/main.tex --venue <venue>`，以工程实际模板为准。
7. LaTeX 中写 `\includegraphics{fig.pdf}`，不带 width。
8. 遵守强约束，详见 `references/rules.md`；draw.io 工作流见 `references/drawio.md`。

## 强约束

- 禁止使用 `bbox_inches="tight"`；布局一律用 `layout="constrained"`。
- seaborn 的 `set_theme` / `set_context` 必须在 `figspec.setup()` 之前调用。
- `venues.yaml` 中的数值只能由 `figspec probe` / `figspec calib` 生成，禁止手改。
- 图的高度不做规定，由内容决定。
- 成品图按最终尺寸导出，LaTeX 中不缩放、不指定 width。
