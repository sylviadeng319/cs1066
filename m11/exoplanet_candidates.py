"""Browser-based exoplanet range search backed by the local SQLite database."""

import argparse
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import html
import json
import math
from pathlib import Path
import sqlite3
import sys
from typing import Any
from urllib.parse import parse_qs


DEFAULT_DATABASE = Path(__file__).with_name("exoplanets_with_candidates.db")
DEFAULT_OUTPUT = Path(__file__).with_name("top5_candidates.json")
FOLLOW_UP_STATUSES = ("not recorded", "not started", "in progress", "complete")
FIELDS = {
    "pl_rade": ("Planet radius (Earth radii)", "Earth radii"),
    "pl_orbper": ("Orbital period (days)", "days"),
    "pl_eqt": ("Equilibrium temperature (K)", "K"),
}
RANKING_DESCRIPTION = (
    "Sum of squared distances from each range midpoint, normalized by "
    "half that range's width; lower scores rank higher."
)


def parse_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Start a local browser interface for exoplanet candidates."
    )
    parser.add_argument(
        "--database",
        type=Path,
        default=DEFAULT_DATABASE,
        help=f"SQLite database path (default: {DEFAULT_DATABASE})",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help=f"JSON output path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="interface address (default: 127.0.0.1)",
    )
    parser.add_argument("--port", type=int, default=8000, help="port (default: 8000)")
    return parser.parse_args()


def parse_ranges(form: dict[str, list[str]]) -> dict[str, tuple[float, float]]:
    ranges: dict[str, tuple[float, float]] = {}
    for field_name in FIELDS:
        try:
            minimum = float(form[f"{field_name}_min"][0])
            maximum = float(form[f"{field_name}_max"][0])
        except (KeyError, IndexError, ValueError) as error:
            raise ValueError(
                f"Enter a valid minimum and maximum for {FIELDS[field_name][0]}."
            ) from error
        if not math.isfinite(minimum) or not math.isfinite(maximum):
            raise ValueError("Range values must be finite numbers.")
        if minimum < 0 or maximum < 0:
            raise ValueError("Range values cannot be negative.")
        if minimum > maximum:
            raise ValueError(
                f"The minimum cannot exceed the maximum for {FIELDS[field_name][0]}."
            )
        ranges[field_name] = (minimum, maximum)
    return ranges


def search_candidates(
    database_path: Path,
    ranges: dict[str, tuple[float, float]],
    limit: int = 5,
) -> tuple[int, list[dict[str, Any]]]:
    conditions: list[str] = []
    parameters: list[float | int] = []
    for field_name, (minimum, maximum) in ranges.items():
        conditions.extend((f"po.{field_name} >= ?", f"po.{field_name} <= ?"))
        parameters.extend((minimum, maximum))

    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        retrieval = connection.execute(
            """
            SELECT retrieval_id
            FROM retrievals
            ORDER BY retrieved_at_utc DESC, retrieval_id DESC
            LIMIT 1
            """
        ).fetchone()
        if retrieval is None:
            raise ValueError("The database does not contain any retrievals.")
        retrieval_id = int(retrieval["retrieval_id"])
        rows = connection.execute(
            f"""
            SELECT p.pl_name, h.hostname, po.pl_rade, po.pl_orbper, po.pl_eqt
            FROM planet_observations AS po
            JOIN planets AS p ON p.planet_id = po.planet_id
            JOIN host_stars AS h ON h.star_id = p.star_id
            WHERE po.retrieval_id = ? AND {' AND '.join(conditions)}
            """,
            (retrieval_id, *parameters),
        ).fetchall()

    candidates: list[dict[str, Any]] = []
    for row in rows:
        score = 0.0
        for field_name, (minimum, maximum) in ranges.items():
            midpoint = (minimum + maximum) / 2
            half_width = (maximum - minimum) / 2
            deviation = float(row[field_name]) - midpoint
            if half_width > 0:
                score += (deviation / half_width) ** 2
            elif deviation != 0:
                score = math.inf
                break
        candidates.append(
            {
                "planet_name": row["pl_name"],
                "host_star": row["hostname"],
                "pl_rade": row["pl_rade"],
                "pl_orbper": row["pl_orbper"],
                "pl_eqt": row["pl_eqt"],
                "ranking_score": score,
            }
        )
    candidates.sort(key=lambda candidate: (candidate["ranking_score"], candidate["planet_name"]))
    return retrieval_id, candidates[:limit]


def save_candidate_list(
    database_path: Path,
    retrieval_id: int,
    ranges: dict[str, tuple[float, float]],
    candidates: list[dict[str, Any]],
    generated_at: str,
    notes: str,
    decision: str,
    follow_up_status: str,
) -> int:
    with sqlite3.connect(database_path) as connection:
        connection.row_factory = sqlite3.Row
        cursor = connection.execute(
            """
            INSERT INTO candidate_lists (
                retrieval_id, generated_at_utc, source, criteria_json,
                ranking_description, notes, decision, follow_up_status
            )
            VALUES (?, ?, 'browser search', ?, ?, ?, ?, ?)
            """,
            (
                retrieval_id,
                generated_at,
                json.dumps(
                    {
                        field_name: {"minimum": bounds[0], "maximum": bounds[1]}
                        for field_name, bounds in ranges.items()
                    },
                    sort_keys=True,
                ),
                RANKING_DESCRIPTION,
                notes,
                decision,
                follow_up_status,
            ),
        )
        list_id = int(cursor.lastrowid)
        for rank, candidate in enumerate(candidates, start=1):
            planet = connection.execute(
                "SELECT planet_id FROM planets WHERE pl_name = ?",
                (candidate["planet_name"],),
            ).fetchone()
            if planet is None:
                raise sqlite3.IntegrityError(
                    f"Candidate planet {candidate['planet_name']!r} "
                    "is not present in the database."
                )
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
                    candidate["planet_name"],
                    candidate["host_star"],
                    candidate["pl_rade"],
                    candidate["pl_orbper"],
                    candidate["pl_eqt"],
                    candidate["ranking_score"],
                ),
            )
    return list_id


def render_page(
    ranges: dict[str, tuple[float, float]] | None = None,
    candidates: list[dict[str, Any]] | None = None,
    message: str | None = None,
    notes: str = "",
    decision: str = "",
    follow_up_status: str = "not started",
    list_id: int | None = None,
) -> str:
    ranges = ranges or {
        "pl_rade": (0.5, 2.5),
        "pl_orbper": (0.1, 20.0),
        "pl_eqt": (150.0, 600.0),
    }
    form_fields = []
    for field_name, (label, units) in FIELDS.items():
        minimum, maximum = ranges[field_name]
        form_fields.append(
            f"""
            <fieldset>
              <legend>{html.escape(label)}</legend>
              <label>Minimum ({html.escape(units)})
                <input name="{field_name}_min" type="number" step="any"
                       min="0" value="{minimum}" required>
              </label>
              <label>Maximum ({html.escape(units)})
                <input name="{field_name}_max" type="number" step="any"
                       min="0" value="{maximum}" required>
              </label>
            </fieldset>
            """
        )

    results_html = ""
    if candidates is not None:
        range_summary = "".join(
            "<li>"
            + html.escape(label)
            + f": {minimum:g}–{maximum:g} {html.escape(units)}</li>"
            for field_name, (label, units) in FIELDS.items()
            for minimum, maximum in (ranges[field_name],)
        )
        if candidates:
            rows_html = "".join(
                f"<tr><td>{rank}</td>"
                + "".join(
                    f"<td>{html.escape(str(value))}</td>"
                    for value in (
                        candidate["planet_name"],
                        candidate["host_star"],
                        candidate["pl_rade"],
                        candidate["pl_orbper"],
                        candidate["pl_eqt"],
                        f'{candidate["ranking_score"]:.4f}',
                    )
                )
                + "</tr>"
                for rank, candidate in enumerate(candidates, start=1)
            )
            results_html = f"""
            <h2>Top {len(candidates)} candidate(s)</h2>
            <p>Saved as candidate list {list_id} with follow-up status
            <strong>{html.escape(follow_up_status)}</strong>.</p>
            <h3>Search ranges</h3>
            <ul>{range_summary}</ul>
            <h3>Team notes and decision</h3>
            <p><strong>Notes:</strong> {html.escape(notes) or "None recorded."}</p>
            <p><strong>Decision:</strong>
            {html.escape(decision) or "None recorded."}</p>
            <p>A lower score means the planet's measurements are closer to the
            midpoint of the selected ranges.</p>
            <div class="table-wrap"><table>
              <thead><tr><th>Rank</th><th>Planet</th><th>Host star</th>
              <th>Radius (Earth)</th><th>Period (days)</th>
              <th>Temperature (K)</th><th>Score</th></tr></thead>
              <tbody>{rows_html}</tbody>
            </table></div>
            <p>The results were saved to <code>top5_candidates.json</code>
            (or the path supplied with <code>--output</code>).</p>
            """
        else:
            results_html = f"""
            <h2>Search ranges</h2>
            <ul>{range_summary}</ul>
            <p>Saved as candidate list {list_id} with follow-up status
            <strong>{html.escape(follow_up_status)}</strong>.</p>
            <p><strong>Notes:</strong> {html.escape(notes) or "None recorded."}</p>
            <p><strong>Decision:</strong>
            {html.escape(decision) or "None recorded."}</p>
            <p>No planets matched all three ranges.</p>
            """

    notice = f'<p class="notice">{html.escape(message)}</p>' if message else ""
    return f"""<!doctype html>
    <html lang="en">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>Exoplanet candidate search</title>
      <style>
        body {{ font: 16px system-ui, sans-serif; max-width: 900px;
               margin: 2rem auto; padding: 0 1rem; color: #17212b; }}
        fieldset {{ display: flex; flex-wrap: wrap; gap: 1rem;
                    margin: 1rem 0; border: 1px solid #9aa8b5; }}
        label {{ display: grid; gap: .35rem; }}
        input {{ width: 12rem; padding: .45rem; }}
        button {{ padding: .6rem 1rem; cursor: pointer; }}
        .table-wrap {{ overflow-x: auto; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ text-align: left; padding: .55rem; border-bottom: 1px solid #ccd3d9; }}
        th {{ background: #eef3f7; }}
        .notice {{ color: #9b1c1c; }}
      </style>
    </head>
    <body>
      <h1>Exoplanet candidate search</h1>
      <p>Set inclusive ranges for all three fields. The search uses the latest
      retrieval in the local SQLite database.</p>
      {notice}
      <form method="post">
        {''.join(form_fields)}
        <fieldset>
          <legend>List provenance and follow-up</legend>
          <label>Notes
            <textarea name="list_notes" rows="3" maxlength="5000">{html.escape(notes)}</textarea>
          </label>
          <label>Decision
            <textarea name="list_decision" rows="3" maxlength="5000">{html.escape(decision)}</textarea>
          </label>
          <label>Follow-up status
            <select name="follow_up_status">
              {''.join(
                  f'<option value="{status}"'
                  f'{" selected" if follow_up_status == status else ""}>'
                  f'{status.title()}</option>'
                  for status in FOLLOW_UP_STATUSES
              )}
            </select>
          </label>
        </fieldset>
        <button type="submit">Find top five candidates</button>
      </form>
      {results_html}
    </body>
    </html>"""


class CandidateRequestHandler(BaseHTTPRequestHandler):
    database_path = DEFAULT_DATABASE
    output_path = DEFAULT_OUTPUT

    def send_html(self, status: int, body: str) -> None:
        content = body.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_GET(self) -> None:
        if self.path != "/":
            self.send_error(404, "Page not found")
            return
        self.send_html(200, render_page())

    def do_POST(self) -> None:
        if self.path != "/":
            self.send_error(404, "Page not found")
            return
        ranges = None
        notes = ""
        decision = ""
        follow_up_status = "not started"
        try:
            content_length = int(self.headers.get("Content-Length", "0"))
            if content_length > 16_384:
                raise ValueError("The submitted form is too large.")
            form = parse_qs(
                self.rfile.read(content_length).decode("utf-8"),
                strict_parsing=True,
                keep_blank_values=True,
            )
            ranges = parse_ranges(form)
            notes = form.get("list_notes", [""])[0].strip()
            decision = form.get("list_decision", [""])[0].strip()
            follow_up_status = form.get("follow_up_status", ["not started"])[0]
            if len(notes) > 5000 or len(decision) > 5000:
                raise ValueError("Notes and decisions must be 5,000 characters or fewer.")
            if follow_up_status not in FOLLOW_UP_STATUSES:
                raise ValueError("Choose a valid follow-up status.")
            retrieval_id, candidates = search_candidates(self.database_path, ranges)
            saved_at = datetime.now(timezone.utc).isoformat()
            list_id = save_candidate_list(
                self.database_path,
                retrieval_id,
                ranges,
                candidates,
                saved_at,
                notes,
                decision,
                follow_up_status,
            )
            output = {
                "list_id": list_id,
                "retrieval_id": retrieval_id,
                "generated_at_utc": saved_at,
                "criteria": {
                    field_name: {"minimum": bounds[0], "maximum": bounds[1]}
                    for field_name, bounds in ranges.items()
                },
                "ranking": RANKING_DESCRIPTION,
                "notes": notes,
                "decision": decision,
                "follow_up_status": follow_up_status,
                "results": candidates,
            }
            try:
                self.output_path.parent.mkdir(parents=True, exist_ok=True)
                with self.output_path.open("w", encoding="utf-8") as output_file:
                    json.dump(output, output_file, indent=2, ensure_ascii=False)
                    output_file.write("\n")
            except OSError as error:
                raise OSError(
                    f"Candidate list {list_id} was saved to SQLite, but its JSON "
                    f"file could not be written: {error}"
                ) from error
        except (UnicodeDecodeError, ValueError) as error:
            self.send_html(
                400,
                render_page(
                    ranges,
                    message=str(error),
                    notes=notes,
                    decision=decision,
                    follow_up_status=follow_up_status,
                ),
            )
            return
        except (OSError, sqlite3.Error) as error:
            self.send_html(
                500,
                render_page(
                    ranges,
                    message=f"Could not create results: {error}",
                    notes=notes,
                    decision=decision,
                    follow_up_status=follow_up_status,
                ),
            )
            return

        self.send_html(
            200,
            render_page(
                ranges,
                candidates,
                notes=notes,
                decision=decision,
                follow_up_status=follow_up_status,
                list_id=list_id,
            ),
        )

    def log_message(self, format_string: str, *args: Any) -> None:
        print(f"{self.address_string()} - {format_string % args}", file=sys.stderr)


def main() -> int:
    args = parse_arguments()
    if not args.database.is_file():
        print(f"Database not found: {args.database}", file=sys.stderr)
        return 1
    if not 1 <= args.port <= 65535:
        print("Port must be between 1 and 65535.", file=sys.stderr)
        return 2

    handler = type(
        "ConfiguredCandidateRequestHandler",
        (CandidateRequestHandler,),
        {"database_path": args.database, "output_path": args.output},
    )
    try:
        server = ThreadingHTTPServer((args.host, args.port), handler)
    except OSError as error:
        print(f"Could not start the local web server: {error}", file=sys.stderr)
        return 1

    print(f"Open http://{args.host}:{args.port}/ in your browser. Press Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping exoplanet candidate search.")
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
