# paper-figure-skills

为学术论文绘图确定画布宽度、字号与字体，并提供 matplotlib 配置、成品图检查和本地 LaTeX 预览。

## 安装

```bash
git clone <repo-url> paper-figure-skills
cd paper-figure-skills
./install.sh
pip install -e .
figspec fonts --install
```

## 使用

```bash
figspec spec CVPR single
figspec probe CVPR
figspec probe --all
figspec probe --tex /path/to/paper/main.tex --venue CVPR
figspec check fig.pdf CVPR single
figspec preview CVPR single fig.pdf
```

绘图代码：

```python
import figspec

spec = figspec.setup("CVPR", "single")
fig, ax = plt.subplots(figsize=(spec.width_in, 2.2), layout="constrained")
fig.savefig("fig.pdf")
```

LaTeX 中按最终尺寸插入，不指定宽度：

```tex
\includegraphics{fig.pdf}
```

## 每年更新模板

```bash
# 1. 用官方最新模板替换 templates/<venue>/
# 2. 重新探测
figspec probe <venue>
# 3. 检查 figspec/data/venues.yaml 的 diff 是否符合预期
git diff -- figspec/data/venues.yaml
# 4. 提交
git add -A && git commit -m "update <venue> template"
```
