import csv
import html
from pathlib import Path

import streamlit as st
import streamlit.components.v1 as components


ROSTER_PATH = (
    Path(__file__).resolve().parents[1]
    / "data_room"
    / "people"
    / "employee_roster.csv"
)


def load_employees() -> tuple[list[dict[str, str | int]], int | None]:
    employees: list[dict[str, str | int]] = []
    reported_headcount: int | None = None

    with ROSTER_PATH.open(encoding="utf-8", newline="") as roster_file:
        rows = iter(csv.DictReader(roster_file))
        for row in rows:
            if row.get("employee_id") == "Summary Statistics:":
                for summary_row in rows:
                    if summary_row.get("employee_id") == "Total Employees":
                        try:
                            reported_headcount = int(summary_row["name"])
                        except (KeyError, TypeError, ValueError) as error:
                            raise ValueError(
                                "Invalid total employee count in roster summary."
                            ) from error
                        break
                break
            if not any(row.values()):
                continue

            try:
                compensation = int(row["comp_usd"])
                employee_id = row["employee_id"]
                name = row["name"]
                role = row["role"]
                department = row["department"]
                reports_to = row["reports_to"]
            except (KeyError, TypeError, ValueError) as error:
                raise ValueError(
                    f"Invalid employee roster row: {row}"
                ) from error

            employees.append(
                {
                    "employee_id": employee_id,
                    "name": name,
                    "role": role,
                    "department": department,
                    "compensation": compensation,
                    "reports_to": reports_to,
                }
            )

    if not employees:
        raise ValueError(f"No employees were found in {ROSTER_PATH}.")

    employees.sort(
        key=lambda employee: (
            employee["compensation"],
            str(employee["name"]).casefold(),
            employee["employee_id"],
        )
    )
    return employees, reported_headcount


def select_team(
    prioritized_employees: list[dict[str, str | int]],
    headcount: int,
    must_have_roles: list[str],
) -> list[dict[str, str | int]]:
    if len(must_have_roles) > headcount:
        raise ValueError(
            "Headcount must be at least the number of must-have positions."
        )

    required_ids: set[str] = set()
    for role in must_have_roles:
        required_employee = next(
            (
                employee
                for employee in prioritized_employees
                if employee["role"] == role
            ),
            None,
        )
        if required_employee is None:
            raise ValueError(f"No employee is available for the must-have role: {role}.")
        required_ids.add(str(required_employee["employee_id"]))

    team = [
        employee
        for employee in prioritized_employees
        if str(employee["employee_id"]) in required_ids
    ]
    team_ids = required_ids.copy()
    team.extend(
        employee
        for employee in prioritized_employees
        if str(employee["employee_id"]) not in team_ids
    )
    return team[:headcount]


def build_hierarchy_html(
    team: list[dict[str, str | int]],
    all_employees: list[dict[str, str | int]],
) -> str:
    selected_ids = {str(employee["employee_id"]) for employee in team}
    all_employee_ids = {
        str(employee["employee_id"]) for employee in all_employees
    }
    children: dict[str, list[dict[str, str | int]]] = {}
    roots: list[dict[str, str | int]] = []
    missing_manager: list[dict[str, str | int]] = []
    for employee in team:
        manager_id = str(employee["reports_to"])
        if manager_id in selected_ids:
            children.setdefault(manager_id, []).append(employee)
        elif manager_id in all_employee_ids:
            missing_manager.append(employee)
        else:
            roots.append(employee)

    def render_employee(
        employee: dict[str, str | int],
        path: frozenset[str] = frozenset(),
    ) -> str:
        employee_id = str(employee["employee_id"])
        if employee_id in path:
            raise ValueError(f"Reporting cycle detected at employee {employee_id}.")

        name = html.escape(str(employee["name"]))
        role = html.escape(str(employee["role"]))
        department = html.escape(str(employee["department"]))
        compensation = f"${int(employee['compensation']):,}"
        node = (
            '<div class="employee-card" tabindex="0">'
            f'<span class="employee-name">{name}</span>'
            '<span class="employee-tooltip" role="tooltip">'
            f"<strong>{name}</strong><br>"
            f"{role}<br>"
            f"Department: {department}<br>"
            f"Annual base compensation: {compensation}"
            "</span></div>"
        )
        descendants = children.get(employee_id, [])
        if descendants:
            next_path = path | {employee_id}
            node += "<ul>" + "".join(
                render_employee(child, next_path) for child in descendants
            ) + "</ul>"
        return f"<li>{node}</li>"

    roots_markup = "".join(render_employee(employee) for employee in roots)
    missing_manager_markup = ""
    if missing_manager:
        missing_manager_markup = (
            '<li class="missing-manager">'
            '<div class="group-label">Manager not in selected team</div>'
            "<ul>"
            + "".join(render_employee(employee) for employee in missing_manager)
            + "</ul></li>"
        )

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<style>
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    color: #243746;
    background: transparent;
    font-family: sans-serif;
}}
.chart {{
    width: 100%;
    min-width: 0;
    overflow-x: auto;
    padding: 100px 16px 32px;
}}
.org-tree ul {{
    display: flex;
    justify-content: center;
    position: relative;
    gap: 0;
    margin: 0;
    padding: 18px 0 0;
    list-style: none;
}}
.org-tree > ul {{
    width: max-content;
    min-width: 100%;
    padding-top: 0;
}}
.org-tree > ul > li::before,
.org-tree > ul > li::after {{ display: none; }}
.org-tree li {{
    position: relative;
    padding: 20px 4px 0;
    text-align: center;
}}
.org-tree > ul > li {{ padding-top: 0; }}
.org-tree li::before,
.org-tree li::after {{
    position: absolute;
    top: 0;
    right: 50%;
    width: 50%;
    height: 18px;
    border-top: 1px solid #9aabb7;
    content: "";
}}
.org-tree li::after {{
    right: auto;
    left: 50%;
    border-left: 1px solid #9aabb7;
}}
.org-tree li:only-child::before,
.org-tree li:only-child::after {{ display: none; }}
.org-tree li:first-child::before,
.org-tree li:last-child::after {{ border: 0; }}
.org-tree li:last-child::before {{ border-right: 1px solid #9aabb7; }}
.org-tree ul ul::before {{
    position: absolute;
    top: 0;
    left: 50%;
    height: 18px;
    border-left: 1px solid #9aabb7;
    content: "";
}}
.employee-card {{
    position: relative;
    display: inline-block;
    min-width: 112px;
    max-width: 152px;
    padding: 8px 10px;
    border: 1px solid #4a6f8a;
    border-radius: 8px;
    background: #eaf2f8;
    color: #243746;
    font-size: 13px;
    line-height: 1.35;
    cursor: default;
}}
.employee-name {{ overflow-wrap: anywhere; }}
.employee-card:hover,
.employee-card:focus {{
    border-color: #274b63;
    outline: 2px solid #9bb8cc;
    outline-offset: 2px;
}}
.employee-tooltip {{
    position: absolute;
    z-index: 10;
    bottom: calc(100% + 8px);
    left: 50%;
    display: none;
    width: min(240px, calc(100vw - 32px));
    padding: 10px 12px;
    transform: translateX(-50%);
    border: 1px solid #4a6f8a;
    border-radius: 8px;
    background: #fff;
    box-shadow: 0 3px 10px #24374629;
    color: #243746;
    font-size: 13px;
    line-height: 1.55;
    text-align: left;
    white-space: normal;
}}
.employee-card:hover .employee-tooltip,
.employee-card:focus .employee-tooltip {{ display: block; }}
.group-label {{
    display: inline-block;
    padding: 7px 10px;
    border: 1px dashed #8a9ba8;
    border-radius: 8px;
    background: #f4f6f7;
    color: #526575;
    font-size: 13px;
}}
</style>
</head>
<body>
<div class="chart org-tree"><ul>{roots_markup}{missing_manager_markup}</ul></div>
</body>
</html>"""


st.set_page_config(page_title="Headcount Cost Planner", page_icon="💼")
st.title("Headcount Cost Planner")
st.write(
    "Choose a team size to estimate annual base compensation. "
    "Choose whether to prioritize higher- or lower-compensated employees."
)

employees, reported_headcount = load_employees()
if reported_headcount is not None and reported_headcount != len(employees):
    st.warning(
        f"The roster lists {len(employees)} employees, but its summary reports "
        f"{reported_headcount}. Scenarios use the listed employee records."
    )

headcount = st.slider(
    "Total headcount",
    min_value=1,
    max_value=len(employees),
    value=min(25, len(employees)),
    step=1,
)

_, priority_column = st.columns([2, 1])
with priority_column:
    highest_first = st.toggle(
        "Highest compensation first",
        value=True,
        help="Turn off to prioritize lowest-compensated employees instead.",
    )

must_have_roles = st.multiselect(
    "Must-have positions",
    options=sorted({str(employee["role"]) for employee in employees}),
    help="Include one employee from each selected role. Compensation priority chooses which employee when a role has several.",
)

if highest_first:
    prioritized_employees = sorted(
        employees,
        key=lambda employee: (
            -int(employee["compensation"]),
            str(employee["name"]).casefold(),
            employee["employee_id"],
        ),
    )
else:
    prioritized_employees = employees

if len(must_have_roles) > headcount:
    st.error(
        f"You selected {len(must_have_roles)} must-have positions, but the "
        f"headcount is {headcount}. Increase headcount or select fewer positions."
    )
    st.stop()

team = select_team(prioritized_employees, headcount, must_have_roles)
total_cost = sum(int(employee["compensation"]) for employee in team)

st.metric(
    "Annual base compensation",
    f"${total_cost:,.0f}",
    help="Sum of the selected employees' base compensation; excludes equity and commission.",
)
st.caption(
    f"Showing the {headcount} employees prioritized by "
    f"{'highest' if highest_first else 'lowest'} "
    f"compensation from {len(employees)} roster entries. "
    f"Equity and commission are not included."
)

view = st.radio(
    "Selected team view",
    options=("Table", "Hierarchy diagram"),
    horizontal=True,
)

if view == "Table":
    st.dataframe(
        [
            {
                "Name": employee["name"],
                "Role": employee["role"],
                "Department": employee["department"],
                "Annual base compensation": f"${int(employee['compensation']):,}",
            }
            for employee in team
        ],
        hide_index=True,
    )
else:
    components.html(
        build_hierarchy_html(team, employees),
        height=700,
        scrolling=True,
    )
