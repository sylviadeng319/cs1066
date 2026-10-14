### m09f/people7.py
#
### Headcount Simulator App
### m03a/people_headcount_app.py
###
### Author: Sharon + GitHub Copilot
### Date: Jan 20, 2026
###
### Headcount app with test-validated equity percentage feature.

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


def detect_equity_format(df: pd.DataFrame) -> dict:
    """
    Detect the equity column and its format (percentage vs shares).
    Returns dict with keys: 'column_name', 'format' ('pct', 'shares', 'value', or None), 'raw_values'
    """
    result = {"column_name": None, "format": None, "raw_values": None}

    # Priority order for equity column detection
    equity_col_candidates = [
        # Percentage columns (highest priority if named explicitly)
        ("equity_pct", "pct"),
        ("equity_percent", "pct"),
        ("ownership_pct", "pct"),
        ("ownership_percent", "pct"),
        # Share columns
        ("equity_shares", "shares"),
        ("shares", "shares"),
        ("stock_options", "shares"),
        ("options", "shares"),
        # Value columns (RSU grants, etc.)
        ("rsu_grant_value", "value"),
        ("equity_value", "value"),
        ("grant_value", "value"),
        # Generic equity column - need to infer format
        ("equity", None),
    ]

    cols_lower = {c.lower(): c for c in df.columns}

    for candidate, fmt in equity_col_candidates:
        if candidate in cols_lower:
            actual_col = cols_lower[candidate]
            result["column_name"] = actual_col

            # Parse numeric values
            raw_values = pd.to_numeric(df[actual_col], errors="coerce")
            result["raw_values"] = raw_values

            if fmt is not None:
                result["format"] = fmt
            else:
                # Infer format from values for generic "equity" column
                max_val = raw_values.max()
                if pd.isna(max_val):
                    result["format"] = "pct"  # default to pct if no valid values
                elif max_val <= 100:
                    # Values are <= 100, likely percentages
                    result["format"] = "pct"
                else:
                    # Values > 100, likely shares
                    result["format"] = "shares"
            return result

    return result


@st.cache_data
def load_roster(csv_source) -> tuple[pd.DataFrame, dict]:
    """
    Load roster CSV and detect equity format.
    Returns (DataFrame, equity_info dict).
    """
    # Read CSV; file contains a "Summary Statistics" section at the bottom, so coerce comp_usd and drop non-employee rows.
    df = pd.read_csv(csv_source, dtype=str, keep_default_na=False)

    # Detect equity format BEFORE normalization (to preserve original column names)
    equity_info = detect_equity_format(df)

    # Normalize columns
    # map common alternative column names to expected schema
    def normalize_columns(df: pd.DataFrame, equity_info: dict) -> pd.DataFrame:
        mapping = {}
        if "employee_name" in df.columns and "name" not in df.columns:
            mapping["employee_name"] = "name"
        if "title" in df.columns and "role" not in df.columns:
            mapping["title"] = "role"
        if "position" in df.columns and "role" not in df.columns:
            mapping["position"] = "role"
        if "dept" in df.columns and "department" not in df.columns:
            mapping["dept"] = "department"
        if "team" in df.columns and "department" not in df.columns:
            mapping["team"] = "department"
        if "manager" in df.columns and "reports_to" not in df.columns:
            mapping["manager"] = "reports_to"
        if "manager_id" in df.columns and "reports_to" not in df.columns:
            mapping["manager_id"] = "reports_to"
        if "salary" in df.columns and "comp_usd" not in df.columns:
            mapping["salary"] = "comp_usd"
        if "total_comp" in df.columns and "comp_usd" not in df.columns:
            mapping["total_comp"] = "comp_usd"
        # Map detected equity column to equity_raw (we'll convert later)
        if equity_info["column_name"] is not None and equity_info["column_name"] != "equity_raw":
            mapping[equity_info["column_name"]] = "equity_raw"
        if "employee_id" not in df.columns:
            # try common id column names
            if "id" in df.columns:
                mapping["id"] = "employee_id"
        if mapping:
            df = df.rename(columns=mapping)
        return df

    df = normalize_columns(df, equity_info)

    if "comp_usd" not in df.columns:
        raise RuntimeError("Expected column 'comp_usd' in roster CSV (found: {})".format(", ".join(df.columns)))
    df["comp_usd"] = pd.to_numeric(df["comp_usd"], errors="coerce")
    # Keep rows that have an employee_id and a numeric compensation
    if "employee_id" in df.columns:
        df = df[df["employee_id"].str.startswith("E", na=False)]
    else:
        # if no employee_id, keep any non-empty row and create an index-based id
        df = df[df["comp_usd"].notna()]
        df = df.reset_index(drop=True)
        df["employee_id"] = ["U{:04d}".format(i + 1) for i in range(len(df))]
    df = df.dropna(subset=["comp_usd"])
    # Convert comp to integer
    df["comp_usd"] = df["comp_usd"].astype(int)
    return df, equity_info


try:
    # Allow user to upload an alternate roster CSV
    uploaded = st.sidebar.file_uploader("Upload employee roster CSV", type=["csv"])
    source = uploaded if uploaded is not None else CSV_PATH
    roster_df, equity_info = load_roster(source)
except Exception as exc:
    st.error(f"Could not load roster: {exc}")
    st.stop()

total_employees = int(roster_df.shape[0])

st.sidebar.header("Scenario inputs")

# Handle equity format detection and conversion
equity_format_detected = equity_info.get("format")
equity_col_name = equity_info.get("column_name")
total_shares_outstanding = None

if equity_format_detected == "shares":
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Equity detected as shares** (from `{equity_col_name}`)")
    total_shares_outstanding = st.sidebar.number_input(
        "Total shares outstanding",
        min_value=1,
        value=50_000_000,  # Default value; user should adjust
        step=1_000_000,
        help="Enter total shares outstanding to convert share counts to ownership percentages."
    )
    st.sidebar.markdown(f"<span class='small-note'>Shares will be converted to % ownership</span>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
elif equity_format_detected == "value":
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Equity detected as grant value** (from `{equity_col_name}`)")
    st.sidebar.markdown("<span class='small-note'>Grant values will be used for relative comparison (not % ownership)</span>", unsafe_allow_html=True)
    st.sidebar.markdown("---")
target_headcount = st.sidebar.slider(
    "Target headcount",
    min_value=0,
    max_value=total_employees,
    value=min(10, total_employees),
    step=1,
)

st.sidebar.markdown("Prioritization: **Impact score** (configurable weights)")

# Weight sliders (user-adjustable)
comp_weight = st.sidebar.slider("Compensation weight", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
tenure_weight = st.sidebar.slider("Tenure (years) weight", min_value=0.0, max_value=5.0, value=0.5, step=0.1)
level_weight = st.sidebar.slider("Seniority (level) weight", min_value=0.0, max_value=5.0, value=1.0, step=0.1)
reports_weight = st.sidebar.slider("Direct reports weight", min_value=0.0, max_value=5.0, value=0.5, step=0.1)
equity_weight = st.sidebar.slider("Equity % weight", min_value=0.0, max_value=5.0, value=0.2, step=0.1)
# Column mapping UI: allow users to map uploaded CSV columns to expected fields
with st.sidebar.expander("Column mapping (if uploader mis-detects)", expanded=False):
    st.write("If any expected columns are missing you can map them here.")
    expected = {
        "employee_id": "Employee ID",
        "name": "Name",
        "role": "Title / Role",
        "department": "Department",
        "location": "Location",
        "comp_usd": "Compensation (USD)",
        "reports_to": "Reports To",
        "start_date": "Start Date",
        "level": "Level",
    }
    mapping_choices = {}
    cols_list = list(roster_df.columns)
    none_opt = "(none)"
    for key, label in expected.items():
        if key in roster_df.columns:
            # show current mapping but allow change
            default = key
        else:
            default = none_opt
        opts = [none_opt] + cols_list
        mapping_choices[key] = st.selectbox(f"Map {label}", opts, index=opts.index(default) if default in opts else 0, key=f"map_{key}")

    # Apply mappings where user specified a column
    for key, chosen in mapping_choices.items():
        if chosen != none_opt:
            # copy mapped column into expected name
            roster_df[key] = roster_df[chosen]
        else:
            # ensure column exists (fill with empty values) to avoid later KeyErrors
            if key not in roster_df.columns:
                roster_df[key] = ""

# end mapping UI
def compute_tenure_years(start_date_series: pd.Series) -> pd.Series:
    parsed = pd.to_datetime(start_date_series, errors="coerce")
    now = pd.Timestamp.now()
    years = (now - parsed).dt.days / 365.25
    years = years.fillna(0.0).clip(lower=0.0)
    return years

def compute_direct_reports_count(df: pd.DataFrame) -> pd.Series:
    if "reports_to" not in df.columns:
        return pd.Series([0] * len(df))
    reports = df["reports_to"].fillna("").astype(str)
    counts = reports.value_counts()
    return df["employee_id"].map(counts).fillna(0).astype(int)

def map_level_to_score(level_series: pd.Series) -> pd.Series:
    mapping = {
        "C-Level": 5.0,
        "VP": 4.0,
        "Director": 3.0,
        "Manager": 2.0,
        "Staff": 3.0,
        "Senior": 3.0,
        "Mid": 1.5,
        "Junior": 1.0,
    }
    return level_series.map(lambda v: mapping.get(v, 1.0)).astype(float)

# (department/skill scoring removed per user request)

# Compute additional features for scoring
roster_df["tenure_years"] = compute_tenure_years(roster_df.get("start_date", pd.Series([""] * len(roster_df))))
roster_df["direct_reports"] = compute_direct_reports_count(roster_df)
roster_df["level_score"] = map_level_to_score(roster_df.get("level", pd.Series([""] * len(roster_df))))
# equity: convert to percentage based on detected format
if "equity_raw" in roster_df.columns:
    equity_raw = pd.to_numeric(roster_df["equity_raw"], errors="coerce").fillna(0.0)

    if equity_format_detected == "shares" and total_shares_outstanding is not None and total_shares_outstanding > 0:
        # Convert shares to percentage: (shares / total_shares_outstanding) * 100
        roster_df["equity_pct"] = (equity_raw / total_shares_outstanding) * 100
    elif equity_format_detected == "value":
        # For grant values, normalize to a 0-100 scale for relative comparison
        max_value = equity_raw.max()
        if max_value > 0:
            roster_df["equity_pct"] = (equity_raw / max_value) * 100
        else:
            roster_df["equity_pct"] = 0.0
    else:
        # Already percentage or unknown format - use as-is
        roster_df["equity_pct"] = equity_raw
elif "equity_pct" in roster_df.columns:
    roster_df["equity_pct"] = pd.to_numeric(roster_df["equity_pct"], errors="coerce").fillna(0.0)
else:
    roster_df["equity_pct"] = 0.0
# Compute additional features for scoring (department/skill omitted)
# Normalize components to 0..1
comp_norm = roster_df["comp_usd"] / max(1.0, roster_df["comp_usd"].max())
tenure_norm = roster_df["tenure_years"] / max(1.0, roster_df["tenure_years"].max())
level_norm = roster_df["level_score"] / max(1.0, roster_df["level_score"].max())
reports_norm = roster_df["direct_reports"] / max(1.0, roster_df["direct_reports"].max())
equity_norm = roster_df["equity_pct"] / max(1.0, roster_df["equity_pct"].max())
# Compute final impact score (weighted sum)
roster_df["impact_score"] = (
    comp_weight * comp_norm
    + tenure_weight * tenure_norm
    + level_weight * level_norm
    + reports_weight * reports_norm
    + equity_weight * equity_norm
)

# Sort by impact score (descending) and select top N
selected = roster_df.sort_values("impact_score", ascending=False).head(target_headcount)

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

# Show equity format info if shares were converted
if equity_format_detected == "shares" and total_shares_outstanding:
    st.info(f"**Equity conversion:** Share counts from `{equity_col_name}` converted to ownership % using {total_shares_outstanding:,} total shares outstanding.")
elif equity_format_detected == "value":
    st.info(f"**Equity format:** Grant values from `{equity_col_name}` normalized to relative scores (0-100) for comparison.")

st.markdown("### Selected employees")
if selected.empty:
    st.info("No employees selected for the current headcount.")
else:
    display_cols = ["employee_id", "name", "role", "department", "location", "comp_usd", "equity_pct", "impact_score"]
    # reindex to avoid KeyError if some columns are missing; missing columns will be filled with empty strings
    display_df = selected.reindex(columns=display_cols).fillna("").copy().reset_index(drop=True)
    # Rename columns to readable English
    display_df = display_df.rename(
        columns={
            "employee_id": "ID",
            "name": "Name",
            "role": "Title",
            "department": "Department",
            "location": "Location",
            "comp_usd": "Compensation (USD)",
            "equity_pct": "Equity %",
            "impact_score": "Impact score",
        }
    )
    # Show compensation as positive amounts (no negative signs)
    display_df["Compensation (USD)"] = display_df["Compensation (USD)"].map(lambda x: _fmt(int(x)))
    # Format impact score as a rounded float for display
    display_df["Impact score"] = display_df["Impact score"].map(lambda x: f"{float(x):.3f}" if x not in (None, "") else "")
    # Format equity based on detected format
    if equity_format_detected == "value":
        # For grant values, show as relative score (already normalized to 0-100)
        display_df = display_df.rename(columns={"Equity %": "Equity Score"})
        display_df["Equity Score"] = display_df["Equity Score"].map(lambda x: f"{float(x):.1f}" if x not in (None, "") and x != "" else "")
    else:
        # For shares (converted) or native percentages, show as percentage
        display_df["Equity %"] = display_df["Equity %"].map(lambda x: f"{float(x):.4f}%" if x not in (None, "") and x != "" else "")
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
source_label = uploaded.name if uploaded is not None else str(CSV_PATH)
st.caption(f"Roster source: `{source_label}` — total employees in roster: {total_employees}")

