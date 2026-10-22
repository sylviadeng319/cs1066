"""Download a sample of NASA Exoplanet Archive planet data as JSON."""

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import requests


TAP_URL = "https://exoplanetarchive.ipac.caltech.edu/TAP/sync"
TABLE = "pscomppars"
FIELDS = (
    "pl_name",
    "hostname",
    "pl_rade",
    "pl_rade_reflink",
    "pl_bmasse",
    "pl_bmasse_reflink",
    "pl_orbper",
    "pl_orbper_reflink",
    "pl_eqt",
    "pl_eqt_reflink",
    "sy_vmag",
    "sy_vmag_reflink",
    "st_teff",
    "st_teff_reflink",
    "sy_dist",
    "sy_dist_reflink",
    "ra",
    "ra_reflink",
    "dec",
    "discoverymethod",
    "disc_facility",
    "disc_refname",
    "tran_flag",
)


def positive_integer(value: str) -> int:
    """Parse a positive integer for the maximum number of rows to download."""
    try:
        number = int(value)
    except ValueError as error:
        raise argparse.ArgumentTypeError("must be a positive integer") from error
    if number < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return number


def build_query(limit: int) -> str:
    """Build the TAP query, selecting only known columns from the composite table."""
    return (
        f"SELECT TOP {limit} {', '.join(FIELDS)} "
        f"FROM {TABLE} ORDER BY pl_name"
    )


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Download exoplanet data from the NASA Exoplanet Archive."
    )
    parser.add_argument(
        "--limit",
        type=positive_integer,
        default=100,
        help="maximum number of planet rows to download (default: 100)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path(__file__).with_name("exoplanets.json"),
        help="JSON output path (default: m11/exoplanets.json)",
    )
    parser.add_argument(
        "--metadata-output",
        type=Path,
        help=(
            "metadata JSON path (default: next to the data file, "
            "named <data-stem>_metadata.json)"
        ),
    )
    return parser.parse_args()


def main() -> int:
    args = parse_arguments()
    query = build_query(args.limit)

    try:
        response = requests.get(
            TAP_URL,
            params={"query": query, "format": "json"},
            timeout=60,
        )
        response.raise_for_status()
        retrieved_at = datetime.now(timezone.utc).isoformat()
        response_hash = hashlib.sha256(response.content).hexdigest()
        rows = response.json()
    except requests.RequestException as error:
        print(f"NASA Exoplanet Archive request failed: {error}", file=sys.stderr)
        return 1
    except ValueError as error:
        print(f"The Archive did not return valid JSON: {error}", file=sys.stderr)
        return 1

    if not isinstance(rows, list) or any(not isinstance(row, dict) for row in rows):
        print("The Archive returned JSON in an unexpected format.", file=sys.stderr)
        return 1

    metadata_path = args.metadata_output or args.output.with_name(
        f"{args.output.stem}_metadata.json"
    )
    metadata = {
        "retrieved_at_utc": retrieved_at,
        "source_table": TABLE,
        "query": query,
        "selected_fields": list(FIELDS),
        "response_hash": {
            "algorithm": "SHA-256",
            "value": response_hash,
            "input": "raw HTTP response body bytes",
        },
        "transformations": [
            "Parsed the Archive's JSON response into JSON records.",
            "Re-serialized the records as UTF-8 JSON with two-space indentation "
            "and a trailing newline; field values were not otherwise changed.",
        ],
    }

    try:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        with args.output.open("w", encoding="utf-8") as output_file:
            json.dump(rows, output_file, indent=2, ensure_ascii=False)
            output_file.write("\n")
        metadata_path.parent.mkdir(parents=True, exist_ok=True)
        with metadata_path.open("w", encoding="utf-8") as metadata_file:
            json.dump(metadata, metadata_file, indent=2, ensure_ascii=False)
            metadata_file.write("\n")
    except OSError as error:
        print(
            f"Could not write the data or metadata output: {error}",
            file=sys.stderr,
        )
        return 1

    print(f"Saved {len(rows)} planet records to {args.output}")
    print(f"Saved retrieval metadata to {metadata_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
