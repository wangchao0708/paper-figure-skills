"""Command-line entry point for figspec."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def _not_ready(command: str) -> int:
    print(f"figspec {command}: not implemented yet", file=sys.stderr)
    return 2


def _run_probe(args: argparse.Namespace) -> int:
    from .probe import (
        ProbeBatchError,
        ProbeError,
        format_table,
        probe_all,
        probe_paper,
        probe_template,
        save_all_venues,
        save_venue,
    )

    if args.venue and args.venue_option and args.venue != args.venue_option:
        print("figspec probe: conflicting venue arguments", file=sys.stderr)
        return 2
    venue = args.venue_option or args.venue

    if args.all and venue:
        print("figspec probe: --all cannot be combined with a venue", file=sys.stderr)
        return 2
    if args.all and args.tex:
        print("figspec probe: --all cannot be combined with --tex", file=sys.stderr)
        return 2
    if args.tex and venue is None:
        print("figspec probe: --tex requires --venue", file=sys.stderr)
        return 2
    if venue is None and not args.all:
        print("figspec probe: provide a venue or --all", file=sys.stderr)
        return 2

    if args.all:
        try:
            results = probe_all()
        except ProbeBatchError as exc:
            if exc.results:
                print(format_table(exc.results))
            for error in exc.errors.values():
                print(str(error), file=sys.stderr)
            return 1
        path = save_all_venues(results)
        print(format_table(results))
        print(f"\nwrote {path}")
        return 0

    try:
        if args.tex:
            record = probe_paper(args.tex, venue)
            print(format_table({record["venue"]: record}))
            print(f"\nwrote {Path(args.tex).expanduser().resolve().parent / '.figspec.yaml'}")
        else:
            from .spec import resolve_venue

            canonical = resolve_venue(venue)
            record = probe_template(canonical)
            path = save_venue(canonical, record)
            print(format_table({canonical: record}))
            print(f"\nwrote {path}")
    except (ProbeError, ValueError) as exc:
        print(f"figspec probe: {exc}", file=sys.stderr)
        return 1
    return 0


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
    probe_parser.add_argument("--venue", dest="venue_option", help="venue (also accepted positionally)")
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
    if args.command == "probe":
        return _run_probe(args)
    return _not_ready(args.command)


if __name__ == "__main__":
    raise SystemExit(main())
