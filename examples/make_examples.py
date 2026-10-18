#!/usr/bin/env python3
"""Generate the eight example line figures used for final acceptance."""

from pathlib import Path

import matplotlib.pyplot as plt

import figspec

OUTPUT_DIR = Path(__file__).resolve().parent


def make_figure(venue: str, layout: str, slug: str) -> Path:
    spec = figspec.setup(venue, layout)
    fig, ax = plt.subplots(figsize=(spec.width_in, 2.2), layout="constrained")

    epochs = [1, 2, 3, 4, 5, 6]
    method_a = [61.2, 68.4, 73.1, 76.0, 78.2, 79.1]
    method_b = [58.8, 64.9, 70.3, 73.8, 76.4, 77.5]

    ax.plot(epochs, method_a, marker="o", markersize=3.5, linewidth=1.2, label="Method A")
    ax.plot(epochs, method_b, marker="s", markersize=3.2, linewidth=1.2, label="Method B")
    ax.set_xlabel("Epoch")
    ax.set_ylabel("Accuracy (%)")
    ax.set_title("Validation accuracy")
    ax.set_xticks(epochs)
    ax.grid(True, linewidth=0.5, alpha=0.3)
    ax.legend(loc="lower right", frameon=False)

    path = OUTPUT_DIR / f"{slug}-{layout}.pdf"
    fig.savefig(path)
    plt.close(fig)
    return path


def main() -> None:
    for venue, slug in (("CVPR", "cvpr"), ("NeurIPS", "neurips"), ("CCS", "ccs"), ("ACL", "acl")):
        for layout in ("single", "double"):
            print(make_figure(venue, layout, slug))


if __name__ == "__main__":
    main()
