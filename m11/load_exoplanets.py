"""Load an Archive JSON download and its metadata into SQLite."""

import argparse
import json
import sqlite3
import sys
from pathlib import Path
from typing import Any


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

DEFAULT_DATABASE = Path(__file__).with_name("exoplanets_with_candidates.db")

SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS retrievals (
    retrieval_id INTEGER PRIMARY KEY,
    retrieved_at_utc TEXT NOT NULL,
    source_table TEXT NOT NULL,
    query TEXT NOT NULL,
    response_sha256 TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS host_stars (
    star_id INTEGER PRIMARY KEY,
    hostname TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS planets (
    planet_id INTEGER PRIMARY KEY,
    pl_name TEXT NOT NULL UNIQUE,
    star_id INTEGER NOT NULL REFERENCES host_stars(star_id)
);

CREATE TABLE IF NOT EXISTS star_observations (
    retrieval_id INTEGER NOT NULL REFERENCES retrievals(retrieval_id)
        ON DELETE CASCADE,
    star_id INTEGER NOT NULL REFERENCES host_stars(star_id),
    ra REAL,
    ra_ref TEXT,
    dec REAL,
    sy_vmag REAL,
    sy_vmag_ref TEXT,
    st_teff REAL,
    st_teff_ref TEXT,
    sy_dist REAL,
    sy_dist_ref TEXT,
    PRIMARY KEY (retrieval_id, star_id)
);

CREATE TABLE IF NOT EXISTS planet_observations (
    retrieval_id INTEGER NOT NULL REFERENCES retrievals(retrieval_id)
        ON DELETE CASCADE,
    planet_id INTEGER NOT NULL REFERENCES planets(planet_id),
    pl_rade REAL,
    pl_rade_ref TEXT,
    pl_bmasse REAL,
    pl_bmasse_ref TEXT,
    pl_orbper REAL,
    pl_orbper_ref TEXT,
    pl_eqt REAL,
    pl_eqt_ref TEXT,
    discoverymethod TEXT,
    disc_facility TEXT,
    disc_refname TEXT,
    tran_flag INTEGER CHECK (tran_flag IN (0, 1) OR tran_flag IS NULL),
    PRIMARY KEY (retrieval_id, planet_id)
);

CREATE TABLE IF NOT EXISTS field_catalog (
    field_name TEXT PRIMARY KEY
);

CREATE TABLE IF NOT EXISTS retrieval_fields (
    retrieval_id INTEGER NOT NULL REFERENCES retrievals(retrieval_id)
        ON DELETE CASCADE,
    field_name TEXT NOT NULL REFERENCES field_catalog(field_name),
    position INTEGER NOT NULL,
    PRIMARY KEY (retrieval_id, field_name),
    UNIQUE (retrieval_id, position)
);

CREATE TABLE IF NOT EXISTS transformation_catalog (
    transformation_id INTEGER PRIMARY KEY,
    description TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS retrieval_transformations (
    retrieval_id INTEGER NOT NULL REFERENCES retrievals(retrieval_id)
        ON DELETE CASCADE,
    transformation_id INTEGER NOT NULL
        REFERENCES transformation_catalog(transformation_id),
    position INTEGER NOT NULL,
    PRIMARY KEY (retrieval_id, transformation_id),
    UNIQUE (retrieval_id, position)
);

CREATE INDEX IF NOT EXISTS idx_planets_star_id
    ON planets(star_id);
CREATE INDEX IF NOT EXISTS idx_planet_observations_planet_id
    ON planet_observations(planet_id);
CREATE INDEX IF NOT EXISTS idx_star_observations_star_id
    ON star_observations(star_id);
"""

CANDIDATE_LIST_SCHEMA = """
CREATE TABLE IF NOT EXISTS candidate_lists (
    list_id INTEGER PRIMARY KEY,
    retrieval_id INTEGER NOT NULL REFERENCES retrievals(retrieval_id),
    generated_at_utc TEXT NOT NULL,
    source TEXT NOT NULL,
    criteria_json TEXT NOT NULL,
    ranking_description TEXT NOT NULL,
    notes TEXT NOT NULL,
    decision TEXT NOT NULL,
    follow_up_status TEXT NOT NULL
        CHECK (follow_up_status IN (
            'not recorded', 'not started', 'in progress', 'complete'
        ))
);

CREATE TABLE IF NOT EXISTS candidate_list_items (
    list_id INTEGER NOT NULL REFERENCES candidate_lists(list_id)
        ON DELETE CASCADE,
    rank INTEGER NOT NULL CHECK (rank > 0),
    planet_id INTEGER NOT NULL REFERENCES planets(planet_id),
    planet_name TEXT NOT NULL,
    host_star TEXT NOT NULL,
    pl_rade REAL,
    pl_orbper REAL,
    pl_eqt REAL,
    ranking_score REAL NOT NULL,
    PRIMARY KEY (list_id, rank),
    UNIQUE (list_id, planet_id)
);

CREATE INDEX IF NOT EXISTS idx_candidate_lists_retrieval_id
    ON candidate_lists(retrieval_id);

CREATE TABLE IF NOT EXISTS candidate_item_reviews (
    list_id INTEGER NOT NULL,
    rank INTEGER NOT NULL,
    decision TEXT NOT NULL CHECK (decision IN ('selected', 'rejected')),
    rationale TEXT NOT NULL,
    reviewed_at_utc TEXT NOT NULL,
    PRIMARY KEY (list_id, rank),
    FOREIGN KEY (list_id, rank)
        REFERENCES candidate_list_items(list_id, rank) ON DELETE CASCADE
);
"""


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Load exoplanet JSON data and metadata into SQLite."
    )
    parser.add_argument(
        "--data",
        type=Path,
        default=Path(__file__).with_name("exoplanets.json"),
        help="data JSON path (default: m11/exoplanets.json)",
    )
    parser.add_argument(
        "--metadata",
        type=Path,
        help="metadata JSON path (default: next to data as <data-stem>_metadata.json)",
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    return parser.parse_args()


def read_json(path: Path) -> Any:
    with path.open(encoding="utf-8") as input_file:
        return json.load(input_file)


def insert_observation(
    connection: sqlite3.Connection,
    retrieval_id: int,
    row: dict[str, Any],
) -> None:
    connection.execute(
        "INSERT OR IGNORE INTO host_stars (hostname) VALUES (?)",
        (row["hostname"],),
    )
    star_id = connection.execute(
        "SELECT star_id FROM host_stars WHERE hostname = ?",
        (row["hostname"],),
    ).fetchone()[0]

    connection.execute(
        "INSERT OR IGNORE INTO planets (pl_name, star_id) VALUES (?, ?)",
        (row["pl_name"], star_id),
    )
    planet_id = connection.execute(
        "SELECT planet_id FROM planets WHERE pl_name = ?",
        (row["pl_name"],),
    ).fetchone()[0]

    star_columns = (
        "ra",
        "ra_ref",
        "dec",
        "sy_vmag",
        "sy_vmag_ref",
        "st_teff",
        "st_teff_ref",
        "sy_dist",
        "sy_dist_ref",
    )
    star_values = (
        row.get("ra"),
        row.get("ra_reflink"),
        row.get("dec"),
        row.get("sy_vmag"),
        row.get("sy_vmag_reflink"),
        row.get("st_teff"),
        row.get("st_teff_reflink"),
        row.get("sy_dist"),
        row.get("sy_dist_reflink"),
    )
    connection.execute(
        f"INSERT OR IGNORE INTO star_observations "
        f"(retrieval_id, star_id, {', '.join(star_columns)}) "
        f"VALUES ({', '.join('?' for _ in range(len(star_columns) + 2))})",
        (retrieval_id, star_id, *star_values),
    )

    planet_columns = (
        "pl_rade",
        "pl_rade_ref",
        "pl_bmasse",
        "pl_bmasse_ref",
        "pl_orbper",
        "pl_orbper_ref",
        "pl_eqt",
        "pl_eqt_ref",
        "discoverymethod",
        "disc_facility",
        "disc_refname",
        "tran_flag",
    )
    planet_values = (
        row.get("pl_rade"),
        row.get("pl_rade_reflink"),
        row.get("pl_bmasse"),
        row.get("pl_bmasse_reflink"),
        row.get("pl_orbper"),
        row.get("pl_orbper_reflink"),
        row.get("pl_eqt"),
        row.get("pl_eqt_reflink"),
        row.get("discoverymethod"),
        row.get("disc_facility"),
        row.get("disc_refname"),
        row.get("tran_flag"),
    )
    connection.execute(
        f"INSERT INTO planet_observations "
        f"(retrieval_id, planet_id, {', '.join(planet_columns)}) "
        f"VALUES ({', '.join('?' for _ in range(len(planet_columns) + 2))})",
        (retrieval_id, planet_id, *planet_values),
    )


def load_retrieval(
    connection: sqlite3.Connection,
    rows: list[dict[str, Any]],
    metadata: dict[str, Any],
) -> bool:
    required_metadata = {
        "retrieved_at_utc",
        "source_table",
        "query",
        "selected_fields",
        "response_hash",
        "transformations",
    }
    if not required_metadata <= metadata.keys():
        missing = sorted(required_metadata - metadata.keys())
        raise ValueError(f"Metadata is missing fields: {', '.join(missing)}")
    if metadata["response_hash"].get("algorithm") != "SHA-256":
        raise ValueError("Metadata response hash must use SHA-256")
    response_sha256 = metadata["response_hash"].get("value")
    if not isinstance(response_sha256, str) or len(response_sha256) != 64:
        raise ValueError("Metadata contains an invalid SHA-256 value")
    if metadata["selected_fields"] != list(FIELDS):
        raise ValueError("Metadata selected fields do not match the loader schema")
    if not isinstance(metadata["transformations"], list):
        raise ValueError("Metadata transformations must be a list")

    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO retrievals
            (retrieved_at_utc, source_table, query, response_sha256)
        VALUES (?, ?, ?, ?)
        """,
        (
            metadata["retrieved_at_utc"],
            metadata["source_table"],
            metadata["query"],
            response_sha256,
        ),
    )
    if cursor.rowcount == 0:
        return False
    retrieval_id = cursor.lastrowid

    for position, field_name in enumerate(metadata["selected_fields"]):
        connection.execute(
            "INSERT OR IGNORE INTO field_catalog (field_name) VALUES (?)",
            (field_name,),
        )
        connection.execute(
            """
            INSERT INTO retrieval_fields (retrieval_id, field_name, position)
            VALUES (?, ?, ?)
            """,
            (retrieval_id, field_name, position),
        )

    for position, description in enumerate(metadata["transformations"]):
        connection.execute(
            """
            INSERT OR IGNORE INTO transformation_catalog (description)
            VALUES (?)
            """,
            (description,),
        )
        transformation_id = connection.execute(
            "SELECT transformation_id FROM transformation_catalog "
            "WHERE description = ?",
            (description,),
        ).fetchone()[0]
        connection.execute(
            """
            INSERT INTO retrieval_transformations
                (retrieval_id, transformation_id, position)
            VALUES (?, ?, ?)
            """,
            (retrieval_id, transformation_id, position),
        )

    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("Every data record must be a JSON object")
        if not isinstance(row.get("pl_name"), str) or not isinstance(
            row.get("hostname"), str
        ):
            raise ValueError("Every record must include planet and host-star names")
        insert_observation(connection, retrieval_id, row)
    return True


def main() -> int:
    args = parse_arguments()
    metadata_path = args.metadata or args.data.with_name(
        f"{args.data.stem}_metadata.json"
    )
    try:
        rows = read_json(args.data)
        metadata = read_json(metadata_path)
        if not isinstance(rows, list) or not isinstance(metadata, dict):
            raise ValueError("Data must be a JSON array and metadata a JSON object")

        args.database.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(args.database) as connection:
            connection.executescript(SCHEMA + CANDIDATE_LIST_SCHEMA)
            added = load_retrieval(connection, rows, metadata)
    except (OSError, json.JSONDecodeError, sqlite3.Error, ValueError) as error:
        print(f"Could not load retrieval into SQLite: {error}", file=sys.stderr)
        return 1

    if added:
        print(
            f"Loaded {len(rows)} planet records from {args.data} "
            f"into {args.database}"
        )
    else:
        print("This response hash is already in the database; no rows added.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
