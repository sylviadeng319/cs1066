import csv
from pathlib import Path

import streamlit as st


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


st.set_page_config(page_title="Headcount Cost Planner", page_icon="💼")
st.title("Headcount Cost Planner")
st.write(
    "Choose a team size to estimate annual base compensation. "
    "Employees are prioritized from lowest to highest compensation."
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

team = employees[:headcount]
total_cost = sum(int(employee["compensation"]) for employee in team)

st.metric(
    "Annual base compensation",
    f"${total_cost:,.0f}",
    help="Sum of the selected employees' base compensation; excludes equity and commission.",
)
st.caption(
    f"Showing the {headcount} lowest-compensated employees from "
    f"{len(employees)} roster entries. Equity and commission are not included."
)

st.subheader("Selected team")
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
