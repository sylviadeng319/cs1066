# Exoplanet database and candidate lists

The old `exoplanets.db` was migrated into
`exoplanets_with_candidates.db`, verified, and removed. The migrated database
is now the default for the loader, query program, and ranked-list interface.
It preserves the old retrieval and planet data and includes the saved
`top5_candidates.json` list. Since the legacy JSON had no human notes, decision,
or follow-up status, those fields are marked as unrecorded.

The one-time migration script is still available if you have a separate copy
of the old database. It refuses to overwrite an existing destination:

```bash
python m11/migrate_exoplanets_db.py --source /path/to/exoplanets.db \
  --destination /path/to/new_exoplanets.db
```

The database-backed ranked-list program uses
`m11/exoplanets_with_candidates.db` by default:

```bash
python m11/exoplanet_candidates.py
```

Enter notes, the team's decision, and follow-up status in the browser form.
Each submission is saved to both SQLite and `m11/top5_candidates.json`. To
inspect saved provenance and the selected planets:

```bash
python m11/query_exoplanets.py --candidate-lists
python m11/query_exoplanets.py --list-id 1
```

Record a decision and its reason for a particular ranked planet, then search
the saved list history by planet name:

```bash
python m11/query_exoplanets.py --record-review 1 1 selected \
  --reason "Strong transit signal and within our preferred radius range."
python m11/query_exoplanets.py --record-review 1 2 rejected \
  --reason "Follow-up would be difficult because of the host star's activity."
python m11/query_exoplanets.py --candidate-planet "K2-18 c"
```

The review command takes a list ID, rank, decision (`selected` or `rejected`),
and a non-empty reason. Re-recording the same list/rank updates the decision
and rationale. The planet lookup displays the decision and reason alongside
the list's criteria and timestamp.

The regular planet search continues to work with the migrated database:

```bash
python m11/query_exoplanets.py --planet "55 Cnc"
```
