"""Command-line interface for AfroJobsPy."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from afrojobspy import __version__, list_sites, scrape_jobs


def _configure_logging(verbose: bool) -> None:
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%H:%M:%S",
    )


def cmd_list_sites(_args: argparse.Namespace) -> int:
    catalogue = list_sites()
    print(json.dumps(catalogue, indent=2))
    return 0


def cmd_search(args: argparse.Namespace) -> int:
    sites = None
    if args.sites:
        sites = [s.strip() for s in args.sites.split(",") if s.strip()]

    df = scrape_jobs(
        search_term=args.query or "",
        location=args.location or "",
        results_wanted=args.num,
        sites=sites,
        country=args.country,
        region=args.region,
        max_workers=args.workers,
    )

    if df.empty:
        print("No jobs found.", file=sys.stderr)
        return 1

    out = args.output
    if out:
        lower = out.lower()
        if lower.endswith(".csv"):
            df.to_csv(out, index=False)
        elif lower.endswith(".json"):
            df.to_json(out, orient="records", indent=2, force_ascii=False)
        elif lower.endswith((".xlsx", ".xls")):
            df.to_excel(out, index=False)
        else:
            df.to_csv(out, index=False)
        print(f"Wrote {len(df)} jobs → {out}")
    else:
        cols = [c for c in ("title", "company", "country", "site_name", "job_url") if c in df.columns]
        print(df[cols].to_string(index=False))
        print(f"\nTotal: {len(df)} jobs")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="afrojobspy",
        description="Scrape job listings from African employment platforms.",
    )
    parser.add_argument("--version", action="version", version=f"afrojobspy {__version__}")
    parser.add_argument("-v", "--verbose", action="store_true", help="Debug logging")

    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list-sites", help="Show supported sites, countries and regions")
    p_list.set_defaults(func=cmd_list_sites)

    p_search = sub.add_parser("search", help="Search for jobs")
    p_search.add_argument("-q", "--query", default="", help="Search keyword")
    p_search.add_argument("-c", "--country", default=None, help="Country filter (e.g. ethiopia)")
    p_search.add_argument("-r", "--region", default=None, help="Region filter (e.g. east_africa)")
    p_search.add_argument("-s", "--sites", default=None, help="Comma-separated site keys")
    p_search.add_argument("-l", "--location", default="", help="Location hint")
    p_search.add_argument("-n", "--num", type=int, default=15, help="Results wanted per site")
    p_search.add_argument("-w", "--workers", type=int, default=6, help="Max concurrent workers")
    p_search.add_argument("-o", "--output", default=None, help="Output file (.csv / .json / .xlsx)")
    p_search.set_defaults(func=cmd_search)

    args = parser.parse_args(argv)
    _configure_logging(args.verbose)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
