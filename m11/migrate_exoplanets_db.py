"""Copy the existing exoplanet database and import its saved candidate list."""

import argparse
import json
import math
import os
from pathlib import Path
import sqlite3
import sys
from typing import Any

from load_exoplanets import CANDIDATE_LIST_SCHEMA

DEFAULT_DESTINATION = Path(__file__).with_name("exoplanets_with_candidates.db")
DEFAULT_CANDIDATE_LIST = Path(__file__).with_name("top5_candidates.json")
LEGACY_NOTES = "No human notes were recorded in the legacy JSON file."
LEGACY_DECISION = "No decision was recorded in the legacy JSON file."
LEGACY_FOLLOW_UP_STATUS = "not recorded"


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Create a copy of the exoplanet database with candidate-list "
            "tables and import the existing ranked-list JSON."
        )
    )
    parser.add_argument(
        "--source",
        type=Path,
        required=True,
        help="path to the old SQLite database to migrate",
    )
    parser.add_argument(
        "--destination",
        type=Path,
        default=DEFAULT_DESTINATION,
        help=f"new SQLite database (default: {DEFAULT_DESTINATION})",
    )
    parser.add_argument(
        "--candidate-list",
        type=Path,
        default=DEFAULT_CANDIDATE_LIST,
        help=f"saved ranked-list JSON (default: {DEFAULT_CANDIDATE_LIST})",
    )
    return parser.parse_args()


def finite_number(value: Any, field_name: str) -> float | None:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Candidate list contains an invalid {field_name}.")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"Candidate list contains a non-finite {field_name}.")
    return number


def import_candidate_list(
    connection: sqlite3.Connection,
    candidate_list: dict[str, Any],
    source_file: Path,
) -> int:
    retrieval_id = candidate_list.get("retrieval_id")
    generated_at = candidate_list.get("generated_at_utc")
    criteria = candidate_list.get("criteria")
    ranking = candidate_list.get("ranking")
    results = candidate_list.get("results")
    if isinstance(retrieval_id, bool) or not isinstance(retrieval_id, int):
        raise ValueError("Candidate list is missing a valid retrieval ID.")
    if not isinstance(generated_at, str) or not generated_at:
        raise ValueError("Candidate list is missing its generation timestamp.")
    if not isinstance(criteria, dict) or not isinstance(ranking, str):
        raise ValueError("Candidate list is missing its criteria or ranking rule.")
    if not isinstance(results, list):
        raise ValueError("Candidate list results must be a JSON array.")
    retrieval_exists = connection.execute(
        "SELECT 1 FROM retrievals WHERE retrieval_id = ?", (retrieval_id,)
    ).fetchone()
    if retrieval_exists is None:
        raise ValueError(f"Retrieval {retrieval_id} is not present in the old database.")

    list_cursor = connection.execute(
        """
        INSERT INTO candidate_lists (
            retrieval_id, generated_at_utc, source, criteria_json,
            ranking_description, notes, decision, follow_up_status
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            retrieval_id,
            generated_at,
            f"Legacy JSON import: {source_file.name}",
            json.dumps(criteria, sort_keys=True),
            ranking,
            LEGACY_NOTES,
            LEGACY_DECISION,
            LEGACY_FOLLOW_UP_STATUS,
        ),
    )
    list_id = int(list_cursor.lastrowid)

    for rank, result in enumerate(results, start=1):
        if not isinstance(result, dict):
            raise ValueError("Every candidate-list result must be a JSON object.")
        planet_name = result.get("planet_name")
        host_star = result.get("host_star")
        if not isinstance(planet_name, str) or not isinstance(host_star, str):
            raise ValueError("Candidate-list results need planet and host-star names.")
        planet = connection.execute(
            "SELECT planet_id FROM planets WHERE pl_name = ?", (planet_name,)
        ).fetchone()
        if planet is None:
            raise ValueError(
                f"Candidate planet {planet_name!r} is not present in the database."
            )
        score = finite_number(result.get("ranking_score"), "ranking score")
        if score is None:
            raise ValueError("Candidate-list results need a ranking score.")
        connection.execute(
            """
            INSERT INTO candidate_list_items (
                list_id, rank, planet_id, planet_name, host_star,
                pl_rade, pl_orbper, pl_eqt, ranking_score
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                list_id,
                rank,
                planet["planet_id"],
                planet_name,
                host_star,
                finite_number(result.get("pl_rade"), "planet radius"),
                finite_number(result.get("pl_orbper"), "orbital period"),
                finite_number(result.get("pl_eqt"), "equilibrium temperature"),
                score,
            ),
        )
    return list_id


def migrate(source_path: Path, destination_path: Path, candidate_path: Path) -> int:
    source_path = source_path.resolve()
    destination_path = destination_path.resolve()
    candidate_path = candidate_path.resolve()
    if source_path == destination_path:
        raise ValueError("Source and destination databases must be different files.")
    if not source_path.is_file():
        raise FileNotFoundError(f"Source database not found: {source_path}")
    if not candidate_path.is_file():
        raise FileNotFoundError(f"Candidate-list JSON not found: {candidate_path}")
    if destination_path.exists():
        raise FileExistsError(
            f"Destination already exists: {destination_path}; choose a new path "
            "rather than overwriting database data."
        )

    with candidate_path.open(encoding="utf-8") as candidate_file:
        candidate_list = json.load(candidate_file)
    if not isinstance(candidate_list, dict):
        raise ValueError("Candidate-list JSON must contain an object.")

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    source_uri = f"{source_path.as_uri()}?mode=ro"
    descriptor = os.open(
        destination_path,
        os.O_CREAT | os.O_EXCL | os.O_RDWR,
        0o666,
    )
    os.close(descriptor)
    try:
        with sqlite3.connect(source_uri, uri=True) as source:
            with sqlite3.connect(destination_path) as destination:
                destination.row_factory = sqlite3.Row
                source.backup(destination)
                destination.execute("PRAGMA foreign_keys = ON")
                destination.executescript(CANDIDATE_LIST_SCHEMA)
                with destination:
                    list_id = import_candidate_list(
                        destination, candidate_list, candidate_path
                    )
                integrity = destination.execute(
                    "PRAGMA integrity_check"
                ).fetchone()[0]
                if integrity != "ok":
                    raise sqlite3.DatabaseError(
                        f"Integrity check failed: {integrity}"
                    )
                violations = destination.execute(
                    "PRAGMA foreign_key_check"
                ).fetchall()
                if violations:
                    raise sqlite3.DatabaseError(
                        f"Foreign-key check failed with {len(violations)} violation(s)."
                    )
    except Exception:
        destination_path.unlink(missing_ok=True)
        raise
    return list_id


def main() -> int:
    args = parse_arguments()
    try:
        list_id = migrate(args.source, args.destination, args.candidate_list)
    except (FileExistsError, FileNotFoundError, OSError, ValueError, sqlite3.Error) as error:
        print(f"Could not migrate exoplanet database: {error}", file=sys.stderr)
        return 1

    print(
        f"Created {args.destination} from {args.source}; "
        f"imported candidate list {list_id} from {args.candidate_list}."
    )
    print(f"The source database was left unchanged.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
