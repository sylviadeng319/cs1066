from __future__ import annotations

import csv
import math
from datetime import date, timedelta
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "docs"

NON_IVY_OPPONENTS = {
    2026: [
        "California", "Providence", "Stony Brook", "Bryant", "Delaware", "UMass Lowell",
        "Penn State", "Sacred Heart", "Siena", "UMass", "Boston College", "Rhode Island",
        "Vermont", "Fordham",
    ],
    2027: [
        "Seton Hall", "UMass Lowell", "Hofstra", "Villanova", "Fairfield", "Delaware",
        "Fordham", "Merrimack", "Maine", "UMass", "Stanford", "New Hampshire",
        "Providence", "Northeastern",
    ],
    2028: [
        "Marist", "Dayton", "George Washington", "Buffalo", "Lehigh", "New Mexico",
        "Saint Joseph's", "Towson", "Duquesne", "VCU", "Temple", "Loyola Chicago",
        "South Florida", "La Salle",
    ],
    2029: [
        "Butler", "San Diego", "Tulane", "Old Dominion", "St. John's", "Toledo",
        "Wake Forest", "Missouri State", "Clemson", "Charlotte", "Quinnipiac", "Rhode Island",
        "North Carolina A&T", "Western Kentucky",
    ],
    2030: [
        "Miami (OH)", "South Dakota", "Campbell", "Texas A&M Commerce", "Northeastern", "Saint Louis",
        "UC Davis", "Green Bay", "Monmouth", "Niagara", "La Salle", "Manhattan",
        "Cal State Fullerton", "Wichita State",
    ],
    2031: [
        "Washington State", "Kansas State", "East Carolina", "Milwaukee", "Iona", "UNLV",
        "Liberty", "Appalachian State", "Eastern Michigan", "Montana", "James Madison", "Saint Mary's",
        "DePaul", "Murray State",
    ],
    2032: [
        "Georgia Tech", "Pacific", "Pepperdine", "Nevada", "Fresno State", "Denver",
        "Middle Tennessee", "Oakland", "UAB", "Abilene Christian", "Harvard's own alumni team", "Belmont",
        "Northern Iowa", "Santa Clara",
    ],
    2033: [
        "VCU", "Northwestern", "Tulsa", "Howard", "UNC Wilmington", "San Francisco",
        "Wofford", "Arkansas State", "Coastal Carolina", "Cleveland State", "Evansville", "Georgia Southern",
        "IUPUI", "Louisiana Tech",
    ],
    2034: [
        "Boston University", "Syracuse", "Bucknell", "Northern Illinois", "Maine", "Holy Cross",
        "Rutgers", "Long Beach State", "Iona", "Mercer", "Texas State", "Oregon State",
        "Vanderbilt", "Air Force",
    ],
    2035: [
        "Michigan State", "North Carolina State", "Pittsburgh", "Vermont", "Army", "Campbell",
        "Penn", "UNC Asheville", "South Carolina", "William & Mary", "Massachusetts", "Mississippi State",
        "Marquette", "UConn",
    ],
}

IVY_OPPONENTS = ["Dartmouth", "Yale", "Cornell", "Columbia", "Brown", "Princeton", "Penn"]
OPPONENT_SUFFIXES = ["University", "State", "College", "A&M"]

PLAYER_NAMES = [
    "Mila Tran", "Naomi Ross", "Harper Levin", "Avery Shah", "Kendall Moss", "Elena Price",
    "Sydney Baird", "Lena Brooks", "Riley Stone", "Maya Dubois", "Tess Moreno", "Nora Patel",
    "Iris Coleman", "Olivia Kim", "Sophie Weller", "Ariana Holt", "Chloe McNair", "Paisley Jones",
    "Jade Mercer", "Daria Flynn", "Evelyn Nash", "Addison Nunez", "Hannah Bell", "Sasha Rios",
    "Renee Holt", "Mia Foster", "Claire Wren", "Nina Soto", "Taylor Pierce", "Keira Bell",
]

SEASON_ORDER = [
    "2026-27", "2027-28", "2028-29", "2029-30", "2030-31",
    "2031-32", "2032-33", "2033-34", "2034-35", "2035-36",
]


def month_name(month_num: int) -> str:
    return [
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ][month_num - 1]


def season_years(season: str) -> tuple[int, int]:
    start, end = season.split("-")
    return int(start), int(end)


def weekday_name(date_obj: date) -> str:
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[date_obj.weekday()]


def team_record_string(wins: int, losses: int) -> str:
    return f"{wins}-{losses}"


def score_to_quarters(final_score: int) -> list[int]:
    q1 = max(10, (final_score * 3) // 8)
    q2 = max(9, (final_score * 2) // 8)
    q3 = max(10, (final_score * 3) // 8)
    q4 = max(final_score - q1 - q2 - q3, 0)
    if q4 < 0:
        q4 = 0
    total = q1 + q2 + q3 + q4
    while total < final_score:
        q4 += 1
        total += 1
    while total > final_score:
        if q4 > 0:
            q4 -= 1
            total -= 1
        else:
            q3 -= 1
            total -= 1
    return [q1, q2, q3, q4]


def todays_date_for(season: str, month: int, day: int) -> date:
    year_start, _ = season_years(season)
    return date(year_start, month, day)


def friendly_site(site_type: str, opponent: str) -> str:
    if site_type == "vs":
        return f"Cambridge, Mass."
    if site_type == "at":
        return f"{opponent}, {opponent[:1].lower()}"
    return "Princeton, N.J."


def game_slugs(season: str, index: int, opponent: str, site_tag: str) -> str:
    season_start, _ = season_years(season)
    if index < 10:
        num = f"0{index}"
    else:
        num = str(index)
    slug = f"{num}-{season_start}-{site_tag}-{opponent.lower().replace(' ', '-')}.md"
    return slug


def build_roster_for_season(season_index: int) -> list[dict]:
    roster = []
    for i, name in enumerate(PLAYER_NAMES[:14]):
        year = "Fy"
        season_start, _ = season_years(SEASON_ORDER[season_index])
        if i % 4 == 0:
            year = "Sr"
        elif i % 4 == 1:
            year = "Jr"
        elif i % 4 == 2:
            year = "So"
        roster.append({
            "name": name,
            "no": 10 + i,
            "year": year,
            "pos": ["G", "F", "C", "G/F"][i % 4],
            "ht": ["5-8", "5-10", "6-1", "6-2", "6-4", "5-6", "6-3"][i % 7],
            "hometown": [
                "Seattle, Wash.", "Austin, Texas", "Cleveland, Ohio", "Denver, Colo.",
                "Portland, Ore.", "Nashville, Tenn.", "Charlotte, N.C.", "Phoenix, Ariz.",
                "Madison, Wis.", "Ann Arbor, Mich.", "Atlanta, Ga.", "Boston, Mass.",
                "Los Angeles, Calif.", "Houston, Texas",
            ][i],
        })
    return roster


def season_game_schedule(season: str) -> list[dict]:
    season_start, season_end = season_years(season)
    schedule = []
    non_ivy = NON_IVY_OPPONENTS[season_start]
    for idx, opp in enumerate(non_ivy, start=1):
        if idx <= 7:
            site = "at"
            home = False
        elif idx <= 11:
            site = "vs"
            home = True
        else:
            site = "at" if idx % 2 == 0 else "vs"
            home = idx % 2 == 1
        month = 11 if idx <= 13 else 12
        day = [3, 6, 8, 11, 15, 18, 23, 25, 28, 30, 2, 6, 9, 20][idx - 1]
        sched_date = date(season_start, month, day)
        if idx > 13:
            month = 12
            day = 20
        schedule.append({
            "game": idx,
            "date": sched_date,
            "opponent": opp,
            "site_tag": site,
            "site": f"{opp} / Cambridge, Mass." if site == "vs" else f"{opp} / {opp} Arena",
            "is_ivy": False,
            "home": home,
        })

    # re-order to create a nicer 14-game Ivy block, matching standard schedule pattern.
    ivy_block = [
        ("Dartmouth", "at", False), ("Yale", "vs", True), ("Cornell", "vs", True),
        ("Columbia", "vs", True), ("Brown", "vs", True), ("Princeton", "at", False),
        ("Penn", "at", False), ("Brown", "at", False), ("Penn", "vs", True),
        ("Princeton", "vs", True), ("Dartmouth", "vs", True), ("Cornell", "at", False),
        ("Columbia", "at", False), ("Yale", "at", False),
    ]
    dates = [
        (1, 2), (1, 9), (1, 16), (1, 18), (1, 23), (1, 29), (1, 31),
        (2, 5), (2, 10), (2, 12), (2, 18), (2, 23), (2, 26), (2, 28),
    ]
    for idx, ((opp, site_tag, home), (month, day)) in enumerate(zip(ivy_block, dates), start=1):
        date_obj = date(season_start + 1, month, day)
        schedule.append({
            "game": len(schedule) + 1,
            "date": date_obj,
            "opponent": opp,
            "site_tag": site_tag,
            "site": f"Cambridge, Mass." if home else f"{opp} / {opp} Arena",
            "is_ivy": True,
            "home": home,
        })
    return schedule


def loc_label(site_tag: str, opponent: str) -> str:
    if site_tag == "vs":
        return f"Cambridge, Mass."
    return f"{opponent}, {opponent.split()[-1][:2].upper()}"


def season_result_pattern(season_index: int, is_ivy_block: bool = False) -> list[bool]:
    # Using a deterministic pattern with a strong season and varying results.
    patterns = [
        [1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1, 1, 0, 0, 1, 1, 1, 1],
        [0, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1, 1, 1, 1, 0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1],
        [1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1],
        [0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 0, 1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 1, 0, 1, 1],
        [1, 0, 1, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1],
        [0, 1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1],
        [1, 1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0],
        [1, 0, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1],
    ]
    return patterns[season_index][:28]


def build_box_score(players: list[dict], total_points: int, opp_total: int) -> list[dict]:
    remaining = total_points
    rows = []
    # produce 8-9 players with a plausible spread.
    for idx, player in enumerate(players[:8]):
        if idx == 7:
            pts = remaining
        else:
            pts = max(0, int(round((total_points * (0.38 - idx * 0.02)) if idx < 4 else (total_points * (0.13 - idx * 0.01)))))
            pts = max(2, pts)
            if pts > remaining:
                pts = remaining
            remaining -= pts
        fg_makes = max(0, min(12, (pts // 2) + (idx % 3)))
        fg_attempts = fg_makes + (4 if idx % 2 == 0 else 3)
        three_makes = max(0, min(6, (fg_makes // 3) + (1 if idx == 2 else 0)))
        three_attempts = three_makes + (2 if idx % 2 == 0 else 1)
        ft_makes = max(1, min(6, (pts // 4) + (1 if idx in {0, 3} else 0)))
        ft_attempts = ft_makes + (1 if idx % 2 == 0 else 2)
        minutes = 18 + (idx * 4) + (8 if idx in {0, 1, 2, 3} else 0)
        rows.append({
            "player": player["name"],
            "no": player["no"],
            "min": minutes,
            "fg": f"{fg_makes}-{fg_attempts}",
            "three": f"{three_makes}-{three_attempts}",
            "ft": f"{ft_makes}-{ft_attempts}",
            "oreb": 1 + (idx % 3),
            "dreb": 2 + (idx % 4),
            "reb": 3 + (idx % 5),
            "ast": 1 + (idx % 3),
            "stl": 1 if idx % 3 == 0 else 0,
            "blk": 1 if idx in {0, 2, 6} else 0,
            "to": 1 + (idx % 3),
            "pf": 1 if idx % 5 == 0 else 0,
            "pts": pts,
            "starter": idx < 5,
        })
    rows[0]["starter"] = True
    rows[0]["pts"] = max(rows[0]["pts"], total_points // 3)
    total_score = sum(r["pts"] for r in rows)
    if total_score != total_points:
        diff = total_points - total_score
        rows[-1]["pts"] += diff
    return rows


def team_stat_table(harvard_total: int, opp_total: int) -> tuple[dict, dict]:
    harvard_fg = 0.44 + (harvard_total % 7) / 100
    harvard_3 = 0.28 + (harvard_total % 5) / 100
    harvard_ft = 0.70 + (harvard_total % 9) / 100
    opp_fg = max(0.30, 0.39 + (opp_total % 6) / 100)
    opp_3 = max(0.25, 0.31 + (opp_total % 4) / 100)
    opp_ft = max(0.60, 0.68 + (opp_total % 8) / 100)
    harvard = {
        "FG%": f".{int(round(harvard_fg * 1000)):03}",
        "3P%": f".{int(round(harvard_3 * 1000)):03}",
        "FT%": f".{int(round(harvard_ft * 1000)):03}",
        "Rebounds": 36 + (harvard_total % 11),
        "Turnovers": 11 + (harvard_total % 6),
        "Steals": 5 + (harvard_total % 5),
    }
    opp = {
        "FG%": f".{int(round(opp_fg * 1000)):03}",
        "3P%": f".{int(round(opp_3 * 1000)):03}",
        "FT%": f".{int(round(opp_ft * 1000)):03}",
        "Rebounds": max(24, 30 + (opp_total % 12)),
        "Turnovers": 9 + (opp_total % 7),
        "Steals": 4 + (opp_total % 6),
    }
    return harvard, opp


def score_by_quarters(harvard_total: int, opp_total: int) -> tuple[list[int], list[int]]:
    h = score_to_quarters(harvard_total)
    o = score_to_quarters(opp_total)
    return h, o


def format_game_final(result: bool, home: bool) -> str:
    if result:
        return "W, "
    return "L, "


def create_game_article(
    season: str,
    game_num: int,
    schedule_entry: dict,
    harvard_points: int,
    opp_points: int,
    roster: list[dict],
    game_type: str,
    overall_wins: int,
    overall_losses: int,
    ivy_wins: int,
    ivy_losses: int,
) -> str:
    season_start, _ = season_years(season)
    opp = schedule_entry["opponent"]
    site_tag = schedule_entry["site_tag"]
    location = schedule_entry["site"]
    date_obj = schedule_entry["date"]
    win = harvard_points > opp_points
    title = f"# Crimson {('Beat' if win else 'Fall to')} {opp} in {'Road' if site_tag == 'at' else 'Home'} Thriller, {harvard_points}-{opp_points}"
    qh, qo = score_by_quarters(harvard_points, opp_points)
    harvard_stats, opp_stats = team_stat_table(harvard_points, opp_points)
    rows = build_box_score(roster, harvard_points, opp_points)
    opponent_rows = [
        {"name": opp, "min": 200, "fg": f"{max(12, opp_points // 2)}-{max(24, opp_points // 2 + 18)}", "three": f"{max(4, opp_points // 8)}-{max(9, opp_points // 5)}", "ft": f"{max(6, opp_points // 5)}-{max(9, opp_points // 4)}", "oreb": 7, "dreb": 14, "reb": 21, "ast": 7, "stl": 6, "blk": 1, "to": 11, "pf": 16, "pts": opp_points}
    ]
    row_lines = []
    for row in rows:
        row_lines.append(
            f"| {row['no']} | {row['player']} {'*' if row['starter'] else ''} | {row['min']} | {row['fg']} | {row['three']} | {row['ft']} | {row['oreb']} | {row['dreb']} | {row['reb']} | {row['ast']} | {row['stl']} | {row['blk']} | {row['to']} | {row['pf']} | {row['pts']} |"
        )
    opp_lines = []
    opp_line = (
        f"| **Totals** | 200 | {max(12, opp_points // 2)}-{max(22, opp_points // 2 + 17)} | {max(4, opp_points // 8)}-{max(9, opp_points // 4)} | {max(3, opp_points // 5)}-{max(7, opp_points // 4)} | 9 | 18 | 27 | 11 | 8 | 2 | 12 | 14 | {opp_points} |"
    )
    opp_lines.append(opp_line)
    article = f"""{title}

**Final:** Harvard {harvard_points}, {opp} {opp_points}
**Date:** {weekday_name(date_obj)}, {month_name(date_obj.month)} {date_obj.day}, {date_obj.year}
**Location:** {location}
**Attendance:** {4000 + (game_num * 127) % 8000}
**Game:** {game_type}
**Harvard record:** {overall_wins}-{overall_losses} overall, {ivy_wins}-{ivy_losses} Ivy

## Score by Quarter

| Team | 1 | 2 | 3 | 4 | F |
|---|---:|---:|---:|---:|---:|
| Harvard | {qh[0]} | {qh[1]} | {qh[2]} | {qh[3]} | {harvard_points} |
| {opp} | {qo[0]} | {qo[1]} | {qo[2]} | {qo[3]} | {opp_points} |

## Team Statistics

| Statistic | Harvard | {opp} |
|---|---:|---:|
| Field Goal % | {harvard_stats['FG%']} | {opp_stats['FG%']} |
| 3-Point FG % | {harvard_stats['3P%']} | {opp_stats['3P%']} |
| Free Throw % | {harvard_stats['FT%']} | {opp_stats['FT%']} |
| Rebounds | {harvard_stats['Rebounds']} | {opp_stats['Rebounds']} |
| Turnovers | {harvard_stats['Turnovers']} | {opp_stats['Turnovers']} |
| Steals | {harvard_stats['Steals']} | {opp_stats['Steals']} |

## Box Score

### Harvard

| # | Player | MIN | FG | 3PT | FT | OREB | DREB | REB | AST | STL | BLK | TO | PF | PTS |
|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(row_lines)}
| | TEAM | | | | | 3 | 5 | 8 | | | | | | |
| | **Totals** | 200 | {sum(int(x.split('-')[0]) for x in [r['fg'] for r in rows])}-{sum(int(x.split('-')[1]) for x in [r['fg'] for r in rows])} | {sum(int(x.split('-')[0]) for x in [r['three'] for r in rows])}-{sum(int(x.split('-')[1]) for x in [r['three'] for r in rows])} | {sum(int(x.split('-')[0]) for x in [r['ft'] for r in rows])}-{sum(int(x.split('-')[1]) for x in [r['ft'] for r in rows])} | 11 | 31 | 42 | 14 | 8 | 2 | 14 | 12 | {harvard_points} |

FG%: {harvard_stats['FG%']} | 3PT%: {harvard_stats['3P%']} | FT%: {harvard_stats['FT%']}

### {opp}

| Team | MIN | FG | 3PT | FT | OREB | DREB | REB | AST | STL | BLK | TO | PF | PTS |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
{chr(10).join(opp_lines)}

FG%: {opp_stats['FG%']} | 3PT%: {opp_stats['3P%']} | FT%: {opp_stats['FT%']}

---

Harvard women's basketball {('found a way to win' if win else 'saw a late push fall short')} in a game that tested the Crimson throughout. The team battled from the opening tip and {('did just enough late to finish' if win else 'never quite found enough offense down the stretch')} as {opp} pushed at key moments before Harvard steadied the game with a strong final stretch.

The result was a {('confident' if win else 'hard-fought')} performance that kept the team in control of its {('season' if not schedule_entry['is_ivy'] else 'Ivy race')} while also reminding everyone that the road ahead is demanding. Carrie's leadership remained decisive as the players executed on both ends of the floor and kept their poise during a tense closing sequence.

## How it Happened

Harvard started {('strongly' if qh[0] > qo[0] else 'evenly')} with a balanced offensive attack, taking a {qh[0]}-{qo[0]} lead after the first quarter. The Crimson kept the pressure on in the second, pushing the margin to {max(qh[0] + qh[1], qo[0] + qo[1])} while holding {opp} to a difficult rhythm on the defensive end.

A key sequence in the third quarter helped Harvard build separation before {opp} made a late push in the fourth. The Crimson responded with crisp ball movement, strong rebounding, and timely free throws to finish the game in front. In the closing moments, the offense stayed patient, and the defense forced the possessions that mattered most.

## Harvard Highlights

- Harvard improved to {overall_wins}-{overall_losses} overall with a {('hard-earned' if win else 'frustrating')} result over {opp}.
- Senior leader {rows[0]['player']} scored {rows[0]['pts']} points and provided a steady presence on both ends.
- Junior guard {rows[1]['player']} added {rows[1]['pts']} points and created timely offense in the middle of the game.
- Harvard won the rebound battle and limited {opp} to a difficult shooting night.
- The Crimson closed the game with efficient execution in the final minutes and knocked down enough free throws to seal the result.
"""
    return article


def season_readme(season: str, schedule: list[dict], roster: list[dict]) -> str:
    start_year, end_year = season_years(season)
    title = f"# {season} Harvard Women's Basketball"
    roster_lines = [
        "## Roster",
        "",
        "| No. | Name | Yr. | Pos. | Ht. | Hometown |",
        "|---:|---|---|---|---|---|",
    ]
    for player in roster:
        roster_lines.append(f"| {player['no']} | {player['name']} | {player['year']} | {player['pos']} | {player['ht']} | {player['hometown']} |")
    roster_lines.append("")
    roster_lines.append("Head coach: Carrie Moore, The Kathy Delaney-Smith Head Coach for Harvard Women's Basketball")
    roster_lines.append("")
    summary = [
        title,
        "",
        f"Harvard finished the {season} season with a projected slate that developed into a competitive and resilient campaign under Carrie Moore.",
        "",
        *roster_lines,
        "## Schedule and Results",
        "",
        "| # | Date | Opponent | Site | Result | Record | Recap |",
        "|---:|---|---|---|---|---|---|",
    ]
    # W-L are generated in the season loop, so README is a generic summary for the directory.
    for entry in schedule:
        site = "at" if entry["site_tag"] == "at" else "vs"
        summary.append(f"| {entry['game']} | {entry['date'].strftime('%b. %-d')} | {site} {entry['opponent']} | {entry['site']} | TBD | TBD | [Recap](./{entry['game']}.md) |")
    summary.append("")
    return "\n".join(summary)


def write_season_files() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for season_index, season in enumerate(SEASON_ORDER):
        season_dir = OUT / season
        season_dir.mkdir(exist_ok=True)
        roster = build_roster_for_season(season_index)
        schedule = season_game_schedule(season)
        game_wins = season_result_pattern(season_index)
        ivy_wins = 0
        ivy_losses = 0
        overall_wins = 0
        overall_losses = 0
        for game_num, (win, entry) in enumerate(zip(game_wins, schedule), start=1):
            harvard_points = 57 + ((game_num * 7 + season_index * 3) % 24)
            opp_points = 48 + ((game_num * 5 + season_index * 2) % 24)
            if win:
                harvard_points += 3
                overall_wins += 1
            else:
                opp_points += 2
                overall_losses += 1
            if entry["is_ivy"]:
                if win:
                    ivy_wins += 1
                else:
                    ivy_losses += 1
            final_h = harvard_points
            final_o = opp_points
            game_file = season_dir / game_slug(entry, game_num, season)
            article_text = create_game_article(
                season,
                game_num,
                entry,
                final_h,
                final_o,
                roster,
                "Non-conference" if not entry["is_ivy"] else "Ivy League",
                overall_wins,
                overall_losses,
                ivy_wins,
                ivy_losses,
            )
            game_file.write_text(article_text, encoding="utf-8")

        # Small season summary file
        summary = f"""# {season} Harvard Women's Basketball

Harvard closed the {season} slate with a {overall_wins}-{overall_losses} record and an Ivy League mark of {ivy_wins}-{ivy_losses}.

## Roster

| No. | Name | Yr. | Pos. | Ht. | Hometown |
|---:|---|---|---|---|---|
"""
        for player in roster:
            summary += f"| {player['no']} | {player['name']} | {player['year']} | {player['pos']} | {player['ht']} | {player['hometown']} |\n"
        summary += "\nHead coach: Carrie Moore, The Kathy Delaney-Smith Head Coach for Harvard Women's Basketball\n\n## Schedule\n\n| # | Date | Opponent | Site | Result | Record |\n|---:|---|---|---|---|---|\n"
        for idx, entry in enumerate(schedule, start=1):
            result = "W" if game_wins[idx - 1] else "L"
            summary += f"| {idx} | {entry['date'].strftime('%b. %d')} | {entry['opponent']} | {entry['site_tag']} | {result} | {overall_wins}-{overall_losses} |\n"
        summary += "\n"
        (season_dir / "README.md").write_text(summary, encoding="utf-8")


def game_slug(entry: dict, game_num: int, season: str) -> str:
    season_start, _ = season_years(season)
    site_tag = entry["site_tag"]
    opp = entry["opponent"].lower().replace(" ", "-")
    return f"{game_num:02d}-{season_start}-{site_tag}-{opp}.md"


if __name__ == "__main__":
    write_season_files()
    print(f"Generated {len(SEASON_ORDER)} seasons of future recap markdown files in {OUT}")
