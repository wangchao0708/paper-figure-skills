"""Command-line entry point for figspec."""

from __future__ import annotations

import argparse
import sys


def _not_ready(command: str) -> int:
    print(f"figspec {command}: not implemented yet", file=sys.stderr)
    return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="figspec",
        description="Venue-aware figure specifications for academic papers.",
    )
    subparsers = parser.add_subparsers(dest="command", metavar="<command>")

    spec_parser = subparsers.add_parser("spec", help="print a venue/layout specification")
    spec_parser.add_argument("venue")
    spec_parser.add_argument("layout", choices=("single", "double"))

    probe_parser = subparsers.add_parser("probe", help="probe a paper template")
    probe_parser.add_argument("venue", nargs="?")
    probe_parser.add_argument("--all", action="store_true")
    probe_parser.add_argument("--tex")

    check_parser = subparsers.add_parser("check", help="check an exported PDF figure")
    check_parser.add_argument("pdf")
    check_parser.add_argument("venue")
    check_parser.add_argument("layout", choices=("single", "double"))

    preview_parser = subparsers.add_parser("preview", help="compile a LaTeX preview")
    preview_parser.add_argument("venue")
    preview_parser.add_argument("layout", choices=("single", "double"))
    preview_parser.add_argument("pdfs", nargs="+")

    fonts_parser = subparsers.add_parser("fonts", help="inspect or install fonts")
    fonts_parser.add_argument("--install", action="store_true")
    fonts_parser.add_argument("--check", action="store_true")

    subparsers.add_parser("calib", help="calibrate draw.io units")
    fetch_parser = subparsers.add_parser("fetch", help="download official templates")
    fetch_parser.add_argument("venue", nargs="?")
    fetch_parser.add_argument("--all", action="store_true")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.command:
        parser.print_help()
        return 0
    return _not_ready(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
