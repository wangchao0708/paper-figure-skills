#!/usr/bin/env python3
"""Generate the three differently colored panels for the NeurIPS showcase."""

from pathlib import Path

import matplotlib.pyplot as plt

import figspec

OUTPUT_DIR = Path(__file__).resolve().parent


def _style(ax, title, xlabel, ylabel, xticks):
    ax.set_title(title)
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)
    ax.set_xticks(xticks)
    ax.grid(True, linewidth=0.5, alpha=0.3)


def make_showcase() -> list[Path]:
    paths: list[Path] = []

    # Two side-by-side panels, each at the single-column width.
    spec = figspec.setup("NeurIPS", "single")
    panels = [
        (
            "showcase-neurips-single-a",
            "Validation accuracy",
            "Epoch",
            "Accuracy (%)",
            [1, 2, 3, 4, 5, 6],
            [
                ([61.2, 68.4, 73.1, 76.0, 78.2, 79.1], "Method A", "#1f4e79", "o"),
                ([58.8, 64.9, 70.3, 73.8, 76.4, 77.5], "Method B", "#d97925", "s"),
            ],
        ),
        (
            "showcase-neurips-single-b",
            "Training loss",
            "Epoch",
            "Loss",
            [1, 2, 3, 4, 5, 6],
            [
                ([0.92, 0.62, 0.45, 0.34, 0.27, 0.23], "Method A", "#2e7d32", "o"),
                ([1.05, 0.78, 0.57, 0.44, 0.36, 0.31], "Method B", "#8e24aa", "s"),
            ],
        ),
    ]
    for slug, title, xlabel, ylabel, xticks, series in panels:
        fig, ax = plt.subplots(figsize=(spec.width_in, 2.2), layout="constrained")
        for values, label, color, marker in series:
            ax.plot(
                xticks,
                values,
                marker=marker,
                markersize=3.5,
                linewidth=1.2,
                color=color,
                label=label,
            )
        _style(ax, title, xlabel, ylabel, xticks)
        ax.legend(loc="best", frameon=False)
        path = OUTPUT_DIR / f"{slug}.pdf"
        fig.savefig(path)
        plt.close(fig)
        paths.append(path)

    # One full-width panel at the double-column width, with a third palette.
    double_spec = figspec.setup("NeurIPS", "double")
    fig, ax = plt.subplots(figsize=(double_spec.width_in, 2.2), layout="constrained")
    batches = [16, 32, 64, 128]
    ax.plot(
        batches,
        [820, 1240, 1510, 1580],
        marker="o",
        markersize=3.5,
        linewidth=1.2,
        color="#b3261e",
        label="Method A",
    )
    ax.plot(
        batches,
        [760, 1110, 1390, 1460],
        marker="s",
        markersize=3.2,
        linewidth=1.2,
        color="#00838f",
        label="Method B",
    )
    _style(ax, "Inference throughput", "Batch size", "Samples / s", batches)
    ax.legend(loc="lower right", frameon=False)
    path = OUTPUT_DIR / "showcase-neurips-double.pdf"
    fig.savefig(path)
    plt.close(fig)
    paths.append(path)
    return paths


if __name__ == "__main__":
    for path in make_showcase():
        print(path)
