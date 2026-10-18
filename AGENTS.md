# paper-figure-skills 仓库约定

## 执行规则

1. 每次只执行一个 Phase；完成后运行该 Phase 验收，执行 `git add -A && git commit -m "phase N: <摘要>"`，停下汇报并等待确认。
2. 本计划未覆盖的决策先询问，不要猜。
3. 所有检查以脚本输出的数值为准，不依赖查看图片。
4. 禁止写死用户配置目录；仓库根用 `Path(__file__).resolve().parents[1]` 推导，允许 `FIGSPEC_HOME` 覆盖。
5. 运行环境为 macOS + MacTeX；Python 统一使用 conda base（`/opt/anaconda3/bin/python`、`/opt/anaconda3/bin/pip`）。
6. 需要 sudo 的命令交给用户执行。

## 强约束

- 禁止使用 `bbox_inches="tight"`，它会改变成品宽度；布局一律用 `layout="constrained"`。
- seaborn 的 `set_theme` / `set_context` 会覆盖字号，必须在 `figspec.setup()` 之前调用。
- `venues.yaml` 中的数值只能由探针生成，禁止手改。
- 图的高度不做规定，由内容决定。
- 成品图按最终尺寸导出，LaTeX 中用 `\includegraphics{fig.pdf}` 插入，不带 width。

## 仓库约定

- 官方模板位于 `templates/<venue>/`，每个 venue 必须包含可编译的 `min.tex`。
- 构建产物、字体缓存和临时文件不得提交。
