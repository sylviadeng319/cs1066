"""Search exoplanet observations in the local SQLite database."""

import argparse
from datetime import datetime, timezone
import math
import sqlite3
import sys
from pathlib import Path
from typing import Any

from load_exoplanets import CANDIDATE_LIST_SCHEMA


DEFAULT_DATABASE = Path(__file__).with_name("exoplanets_with_candidates.db")
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
    list_group = parser.add_mutually_exclusive_group()
    list_group.add_argument(
        "--list-id",
        type=positive_integer,
        help="show provenance and selected planets for one saved candidate list",
    )
    list_group.add_argument(
        "--candidate-lists",
        action="store_true",
        help="show provenance for all saved candidate lists",
    )
    list_group.add_argument(
        "--candidate-planet",
        help="show saved candidate-list decisions for a planet-name substring",
    )
    parser.add_argument(
        "--record-review",
        nargs=3,
        metavar=("LIST_ID", "RANK", "DECISION"),
        help="record selected/rejected decision for a ranked candidate",
    )
    parser.add_argument(
        "--reason",
        help="human rationale required with --record-review",
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
    if args.record_review:
        try:
            list_id, rank = (int(value) for value in args.record_review[:2])
        except ValueError:
            parser.error("LIST_ID and RANK for --record-review must be positive integers")
        if list_id < 1 or rank < 1:
            parser.error("LIST_ID and RANK for --record-review must be positive integers")
        if args.record_review[2] not in ("selected", "rejected"):
            parser.error("DECISION for --record-review must be 'selected' or 'rejected'")
        if not args.reason or not args.reason.strip():
            parser.error("--record-review requires a non-empty --reason")
        if args.list_id is not None or args.candidate_lists or args.candidate_planet:
            parser.error("--record-review cannot be combined with candidate-list queries")
        if any(
            getattr(args, name) is not None
            for name in (
                "planet",
                "host",
                "min_radius",
                "max_radius",
                "min_period",
                "max_period",
                "discovery_method",
                "transit",
            )
        ):
            parser.error("--record-review cannot be combined with planet search filters")
    elif args.reason:
        parser.error("--reason can only be used with --record-review")
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


def print_candidate_lists(
    connection: sqlite3.Connection,
    list_id: int | None = None,
) -> bool:
    query = """
        SELECT list_id, retrieval_id, generated_at_utc, source, criteria_json,
               ranking_description, notes, decision, follow_up_status
        FROM candidate_lists
    """
    parameters: tuple[int, ...] = ()
    if list_id is not None:
        query += " WHERE list_id = ?"
        parameters = (list_id,)
    query += " ORDER BY generated_at_utc DESC, list_id DESC"
    lists = connection.execute(query, parameters).fetchall()
    if not lists:
        if list_id is None:
            print("No candidate lists have been saved.")
        else:
            print(f"Candidate list {list_id} was not found.")
        return list_id is None

    for saved_list in lists:
        print(f"Candidate list {saved_list['list_id']}")
        print(f"Generated: {saved_list['generated_at_utc']} (UTC)")
        print(f"Source: {saved_list['source']}")
        print(f"Retrieval: {saved_list['retrieval_id']}")
        print(f"Criteria: {saved_list['criteria_json']}")
        print(f"Ranking: {saved_list['ranking_description']}")
        print(f"Notes: {saved_list['notes'] or 'None recorded.'}")
        print(f"Decision: {saved_list['decision'] or 'None recorded.'}")
        print(f"Follow-up: {saved_list['follow_up_status']}")
        candidates = connection.execute(
            """
            SELECT rank, planet_name, host_star, ranking_score
            FROM candidate_list_items
            WHERE list_id = ?
            ORDER BY rank
            """,
            (saved_list["list_id"],),
        ).fetchall()
        print("Selected planets:")
        for candidate in candidates:
            print(
                f"  {candidate['rank']}. {candidate['planet_name']} "
                f"(host: {candidate['host_star']}, "
                f"score: {candidate['ranking_score']:g})"
            )
        print()
    return True


def print_candidate_reviews(
    connection: sqlite3.Connection,
    planet_name: str,
) -> bool:
    escaped = planet_name.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    rows = connection.execute(
        """
        SELECT
            cli.planet_name,
            cli.host_star,
            cl.list_id,
            cl.generated_at_utc,
            cl.criteria_json,
            cir.decision,
            cir.rationale,
            cir.reviewed_at_utc
        FROM candidate_list_items AS cli
        JOIN candidate_lists AS cl ON cl.list_id = cli.list_id
        LEFT JOIN candidate_item_reviews AS cir
            ON cir.list_id = cli.list_id AND cir.rank = cli.rank
        WHERE cli.planet_name LIKE ? ESCAPE '\\'
        ORDER BY cl.generated_at_utc DESC, cl.list_id DESC, cli.rank
        """,
        (f"%{escaped}%",),
    ).fetchall()
    if not rows:
        print(f"No saved candidate lists include a planet matching {planet_name!r}.")
        return False

    for row in rows:
        print(f"{row['planet_name']} (host: {row['host_star']})")
        print(f"Candidate list: {row['list_id']} ({row['generated_at_utc']} UTC)")
        print(f"Criteria: {row['criteria_json']}")
        if row["decision"] is None:
            print("Decision: not reviewed")
        else:
            print(f"Decision: {row['decision']}")
            print(f"Reason: {row['rationale']}")
            print(f"Reviewed: {row['reviewed_at_utc']} (UTC)")
        print()
    return True


def record_candidate_review(
    connection: sqlite3.Connection,
    list_id: int,
    rank: int,
    decision: str,
    rationale: str,
) -> None:
    candidate = connection.execute(
        """
        SELECT planet_name
        FROM candidate_list_items
        WHERE list_id = ? AND rank = ?
        """,
        (list_id, rank),
    ).fetchone()
    if candidate is None:
        raise ValueError(
            f"Candidate list {list_id} has no entry at rank {rank}."
        )
    reviewed_at = datetime.now(timezone.utc).isoformat()
    connection.execute(
        """
        INSERT INTO candidate_item_reviews (
            list_id, rank, decision, rationale, reviewed_at_utc
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT (list_id, rank) DO UPDATE SET
            decision = excluded.decision,
            rationale = excluded.rationale,
            reviewed_at_utc = excluded.reviewed_at_utc
        """,
        (list_id, rank, decision, rationale.strip(), reviewed_at),
    )
    print(
        f"Recorded {decision} decision for {candidate['planet_name']} "
        f"(list {list_id}, rank {rank})."
    )


def main() -> int:
    args = parse_arguments()
    if not args.database.is_file():
        print(f"Database not found: {args.database}", file=sys.stderr)
        return 1

    if (
        args.list_id is not None
        or args.candidate_lists
        or args.candidate_planet
        or args.record_review
    ):
        try:
            with sqlite3.connect(args.database) as connection:
                connection.row_factory = sqlite3.Row
                connection.execute("PRAGMA foreign_keys = ON")
                connection.executescript(CANDIDATE_LIST_SCHEMA)
                if args.record_review:
                    list_id, rank = map(int, args.record_review[:2])
                    with connection:
                        record_candidate_review(
                            connection,
                            list_id,
                            rank,
                            args.record_review[2],
                            args.reason,
                        )
                    return 0
                if args.candidate_planet:
                    found = print_candidate_reviews(
                        connection, args.candidate_planet
                    )
                    return 0 if found else 1
                found = print_candidate_lists(connection, args.list_id)
        except sqlite3.Error as error:
            print(f"Could not read candidate lists from {args.database}: {error}", file=sys.stderr)
            return 1
        except ValueError as error:
            print(f"Could not record candidate review: {error}", file=sys.stderr)
            return 1
        return 0 if found else 1

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
