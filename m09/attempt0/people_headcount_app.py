### Headcount Simulator App
### m02b-instructor/people_headcount_app.py
###
### Author: Sharon + GitHub Copilot
### Date: Jan 20, 2026
###
### First prompt results, using GPT-5 mini.

import streamlit as st
import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).parent / "data_room/people/employee_roster.csv"

st.set_page_config(page_title="People Headcount Scenarios", layout="wide")

st.title("Headcount scenario simulator — prioritize by compensation")
st.markdown(
    "Use the slider to choose a target headcount. People are selected by compensation order (configurable). "
    "The app shows total compensation for the selected headcount and the selected employee list."
)


@st.cache_data
def load_roster(csv_path: Path) -> pd.DataFrame:
    # Read CSV; file contains a "Summary Statistics" section at the bottom, so coerce comp_usd and drop non-employee rows.
    df = pd.read_csv(csv_path, dtype=str, keep_default_na=False)
    # Normalize columns
    if "comp_usd" not in df.columns:
        raise RuntimeError("Expected column 'comp_usd' in roster CSV")
    df["comp_usd"] = pd.to_numeric(df["comp_usd"], errors="coerce")
    # Keep rows that have an employee_id and a numeric compensation
    df = df[df["employee_id"].str.startswith("E", na=False)]
    df = df.dropna(subset=["comp_usd"])
    # Convert comp to integer
    df["comp_usd"] = df["comp_usd"].astype(int)
    return df


try:
    roster_df = load_roster(CSV_PATH)
except Exception as exc:
    st.error(f"Could not load roster: {exc}")
    st.stop()

total_employees = int(roster_df.shape[0])

st.sidebar.header("Scenario inputs")
target_headcount = st.sidebar.slider(
    "Target headcount",
    min_value=0,
    max_value=total_employees,
    value=min(10, total_employees),
    step=1,
)

priority_option = st.sidebar.radio(
    "Prioritize by compensation",
    options=["Lowest compensation first (cost-minimizing)", "Highest compensation first"],
)

ascending = priority_option.startswith("Lowest")

# Select top N based on compensation ordering
selected = roster_df.sort_values("comp_usd", ascending=ascending).head(target_headcount)

total_cost = int(selected["comp_usd"].sum()) if not selected.empty else 0
average_cost = int(selected["comp_usd"].mean()) if not selected.empty else 0

col1, col2, col3 = st.columns(3)
col1.metric("Selected headcount", f"{selected.shape[0]}/{total_employees}")
col2.metric("Total compensation (USD)", f"${total_cost:,.0f}")
col3.metric("Average compensation (USD)", f"${average_cost:,.0f}" if selected.shape[0] else "$0")

st.markdown("### Selected employees")
if selected.empty:
    st.info("No employees selected for the current headcount.")
else:
    display_cols = ["employee_id", "name", "role", "department", "location", "comp_usd"]
    st.dataframe(selected[display_cols].reset_index(drop=True))
    st.download_button(
        "Download selected as CSV",
        selected[display_cols].to_csv(index=False).encode("utf-8"),
        file_name="selected_employees.csv",
        mime="text/csv",
    )

st.markdown("### Compensation breakdown")
if not selected.empty:
    st.bar_chart(selected.set_index("name")["comp_usd"])

st.markdown("---")
st.caption(f"Roster source: `{CSV_PATH}` — total employees in roster: {total_employees}")

