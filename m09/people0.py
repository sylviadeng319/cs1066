### m09d/people0.py
#
### Headcount Simulator App
### m02g/people_headcount_app.py
###
### Author: Sharon + GitHub Copilot
### Date: Jan 20, 2026
###
### Simplified prioritization headcount app.

import streamlit as st
import pandas as pd
from pathlib import Path

CSV_PATH = Path(__file__).parent / "data_room/people/employee_roster.csv"

st.set_page_config(page_title="People Headcount Scenarios", layout="wide")

# --- Harvard-style styling (crimson, serif)
HARVARD_CRIMSON = "#A51C30"
st.markdown(
    f"""
    <style>
      .app-title {{ font-family: "Merriweather", Georgia, serif; font-size:32px; font-weight:700; color: {HARVARD_CRIMSON}; margin-bottom:6px; }}
      .app-sub {{ color: #374151; margin-top:0; margin-bottom:12px; font-size:14px; }}
      .kpi-card {{ padding: 14px; border-radius:8px; color: #111827; background: #ffffff; border: 1px solid #e6e6e6; }}
      .kpi-label {{ font-size:13px; color: #6b7280; margin-bottom:6px; }}
      .kpi-value {{ font-size:20px; font-weight:700; color: #111827; }}
      .data-table {{ border-radius:8px; overflow:hidden; box-shadow: 0 2px 6px rgba(15,23,42,0.04); }}
      .harvard-hr {{ height:4px; background:{HARVARD_CRIMSON}; border-radius:2px; margin:10px 0 18px 0; }}
      .small-note {{ color: #6b7280; font-size:12px; }}
      /* Sidebar: dark Harvard maroon with white text for high contrast */
      .stSidebar {{ background-color: #341219 !important; color: #ffffff !important; }}
      section[data-testid="stSidebar"] > div:first-child {{ background-color: transparent !important; }}
      /* Ensure common sidebar widgets and labels are readable */
      section[data-testid="stSidebar"] .stMarkdown, section[data-testid="stSidebar"] label, section[data-testid="stSidebar"] .stRadio, section[data-testid="stSidebar"] .stSlider, section[data-testid="stSidebar"] .stTextInput, section[data-testid="stSidebar"] .stSelectbox, section[data-testid="stSidebar"] .stNumberInput {{
        color: #ffffff !important;
      }}
      /* Make inputs slightly translucent so controls remain visible on dark background */
      section[data-testid="stSidebar"] input, section[data-testid="stSidebar"] .css-1aumxhk, section[data-testid="stSidebar"] .css-10trblm {{
        background-color: rgba(255,255,255,0.03) !important;
        color: #ffffff !important;
      }}
      /* Style buttons in the sidebar */
      section[data-testid="stSidebar"] .stButton>button, section[data-testid="stSidebar"] .css-1emrehy.edgvbvh3 {{
        background-color: #A51C30 !important;
        color: #ffffff !important;
        border: none !important;
      }}
    </style>
    """,
    unsafe_allow_html=True,
)

st.markdown('<div class="app-title">Headcount scenario simulator — prioritize by compensation</div>', unsafe_allow_html=True)
st.markdown('<div class="app-sub">Set a target headcount and prioritize hires by compensation to see the cost impact.</div>', unsafe_allow_html=True)
st.markdown('<div class="harvard-hr"></div>', unsafe_allow_html=True)


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

st.sidebar.markdown("Prioritization: **Highest compensation first** (fixed)")
ascending = False

# Select top N based on compensation ordering
selected = roster_df.sort_values("comp_usd", ascending=ascending).head(target_headcount)

total_cost = int(selected["comp_usd"].sum()) if not selected.empty else 0
average_cost = int(selected["comp_usd"].mean()) if not selected.empty else 0
median_cost = int(selected["comp_usd"].median()) if not selected.empty else 0

def _fmt(x: int) -> str:
    return f"${x:,.0f}"

# KPI cards
k1, k2, k3, k4 = st.columns([1,1,1,1])
card_template = '<div class="kpi-card"><div class="kpi-label">{label}</div><div class="kpi-value">{value}</div></div>'
k1.markdown(card_template.format(label="Selected headcount", value=f"{selected.shape[0]}/{total_employees}"), unsafe_allow_html=True)
k2.markdown(card_template.format(label="Total compensation", value=_fmt(total_cost)), unsafe_allow_html=True)
k3.markdown(card_template.format(label="Average compensation", value=_fmt(average_cost) if selected.shape[0] else "$0"), unsafe_allow_html=True)
k4.markdown(card_template.format(label="Median compensation", value=_fmt(median_cost) if selected.shape[0] else "$0"), unsafe_allow_html=True)

st.markdown("### Selected employees")
if selected.empty:
    st.info("No employees selected for the current headcount.")
else:
    display_cols = ["employee_id", "name", "role", "department", "location", "comp_usd"]
    display_df = selected[display_cols].copy().reset_index(drop=True)
    # Rename columns to readable English
    display_df = display_df.rename(
        columns={
            "employee_id": "ID",
            "name": "Name",
            "role": "Title",
            "department": "Department",
            "location": "Location",
            "comp_usd": "Compensation (USD)",
        }
    )
    display_df["Compensation (USD)"] = display_df["Compensation (USD)"].map(lambda x: _fmt(int(x)))
    # nicer table
    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.table(display_df)
    st.markdown("</div>", unsafe_allow_html=True)
    st.download_button(
        "Download selected as CSV",
        selected[display_cols].to_csv(index=False).encode("utf-8"),
        file_name="selected_employees.csv",
        mime="text/csv",
    )

# (Graph removed — selection table and KPIs provide the required information)

st.markdown("---")
st.caption(f"Roster source: `{CSV_PATH}` — total employees in roster: {total_employees}")

