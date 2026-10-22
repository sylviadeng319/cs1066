"""Search exoplanet observations in the local SQLite database."""

import argparse
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any


DEFAULT_DATABASE = Path(__file__).with_name("exoplanets.db")
DEFAULT_LIMIT = 20


def finite_number(value: str) -> float:
    """Parse a finite numeric value for a range filter."""
    try:
        number = float(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a number") from error
    if not math.isfinite(number):
        raise argparse.ArgumentTypeError("must be a finite number")
    return number


def positive_integer(value: str) -> int:
    """Parse a positive integer for the result limit."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Search planets from the latest retrieval in the local "
            "NASA Exoplanet Archive SQLite database."
        )
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    parser.add_argument("--planet", help="case-insensitive substring of planet name")
    parser.add_argument("--host", help="case-insensitive substring of host-star name")
    parser.add_argument("--min-radius", type=finite_number, help="minimum radius in Earth radii")
    parser.add_argument("--max-radius", type=finite_number, help="maximum radius in Earth radii")
    parser.add_argument("--min-period", type=finite_number, help="minimum orbital period in days")
    parser.add_argument("--max-period", type=finite_number, help="maximum orbital period in days")
    parser.add_argument("--discovery-method", help="case-insensitive discovery method")
    parser.add_argument(
        "--transit",
        type=int,
        choices=(0, 1),
        help="filter by transit flag: 1 for detected by transits, 0 otherwise",
    )
    parser.add_argument(
        "--limit",
        type=positive_integer,
        default=DEFAULT_LIMIT,
        help=f"maximum number of results (default: {DEFAULT_LIMIT})",
    )
    args = parser.parse_args()

    for minimum_name, maximum_name in (
        ("min_radius", "max_radius"),
        ("min_period", "max_period"),
    ):
        minimum = getattr(args, minimum_name)
        maximum = getattr(args, maximum_name)
        if minimum is not None and minimum < 0:
            parser.error(f"--{minimum_name.replace('_', '-')} cannot be negative")
        if maximum is not None and maximum < 0:
            parser.error(f"--{maximum_name.replace('_', '-')} cannot be negative")
        if minimum is not None and maximum is not None and minimum > maximum:
            parser.error(
                f"--{minimum_name.replace('_', '-')} cannot exceed "
                f"--{maximum_name.replace('_', '-')}"
            )
    return args


def like_pattern(value: str) -> str:
    """Make a substring pattern while treating SQL LIKE wildcards literally."""
    escaped = value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    return f"%{escaped}%"


def build_query(args: argparse.Namespace) -> tuple[str, list[Any]]:
    conditions = ["po.retrieval_id = (SELECT retrieval_id FROM retrievals "
                  "ORDER BY retrieved_at_utc DESC, retrieval_id DESC LIMIT 1)"]
    parameters: list[Any] = []

    if args.planet:
        conditions.append("p.pl_name LIKE ? ESCAPE '\\'")
        parameters.append(like_pattern(args.planet))
    if args.host:
        conditions.append("h.hostname LIKE ? ESCAPE '\\'")
        parameters.append(like_pattern(args.host))
    if args.min_radius is not None:
        conditions.append("po.pl_rade >= ?")
        parameters.append(args.min_radius)
    if args.max_radius is not None:
        conditions.append("po.pl_rade <= ?")
        parameters.append(args.max_radius)
    if args.min_period is not None:
        conditions.append("po.pl_orbper >= ?")
        parameters.append(args.min_period)
    if args.max_period is not None:
        conditions.append("po.pl_orbper <= ?")
        parameters.append(args.max_period)
    if args.discovery_method:
        conditions.append("po.discoverymethod = ? COLLATE NOCASE")
        parameters.append(args.discovery_method)
    if args.transit is not None:
        conditions.append("po.tran_flag = ?")
        parameters.append(args.transit)

    query = f"""
        SELECT
            p.pl_name,
            h.hostname,
            po.pl_rade,
            po.pl_bmasse,
            po.pl_orbper,
            po.pl_eqt,
            po.discoverymethod,
            po.tran_flag
        FROM planet_observations AS po
        JOIN planets AS p ON p.planet_id = po.planet_id
        JOIN host_stars AS h ON h.star_id = p.star_id
        WHERE {' AND '.join(conditions)}
        ORDER BY p.pl_name
        LIMIT ?
    """
    parameters.append(args.limit)
    return query, parameters


def format_value(value: Any) -> str:
    if value is None:
        return "N/A"
    if isinstance(value, float):
        return f"{value:g}"
    return str(value)


def print_results(rows: list[sqlite3.Row]) -> None:
    headers = (
        "Planet",
        "Host star",
        "Radius (Earth)",
        "Mass (Earth)",
        "Period (days)",
        "Equil. temp (K)",
        "Discovery method",
        "Transit",
    )
    values = [[format_value(row[key]) for key in row.keys()] for row in rows]
    widths = [
        min(36, max(len(header), *(len(row[index]) for row in values)))
        for index, header in enumerate(headers)
    ]

    def shorten(value: str, width: int) -> str:
        return value if len(value) <= width else value[: width - 1] + "…"

    print(" | ".join(shorten(header, widths[index]).ljust(widths[index])
                     for index, header in enumerate(headers)))
    print("-+-".join("-" * width for width in widths))
    for row in values:
        print(" | ".join(shorten(value, widths[index]).ljust(widths[index])
                         for index, value in enumerate(row)))


def main() -> int:
    args = parse_arguments()
    if not args.database.is_file():
        print(f"Database not found: {args.database}", file=sys.stderr)
        return 1

    query, parameters = build_query(args)
    try:
        with sqlite3.connect(args.database) as connection:
            connection.row_factory = sqlite3.Row
            latest_exists = connection.execute(
                "SELECT 1 FROM retrievals LIMIT 1"
            ).fetchone()
            if latest_exists is None:
                print("The database has no retrievals yet.", file=sys.stderr)
                return 1
            rows = connection.execute(query, parameters).fetchall()
    except sqlite3.Error as error:
        print(f"Could not search database {args.database}: {error}", file=sys.stderr)
        return 1

    if not rows:
        print("No planets matched the search criteria.")
        return 0
    print_results(rows)
    print(f"\nShowing {len(rows)} result(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
