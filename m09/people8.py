### m09f/people8.py
#
### Headcount Simulator App
### m03b/people_headcount_app.py
###
### Author: Sharon + GitHub Copilot
### Date: Jan 20, 2026
###
### Headcount app with BLS job/salary benchmarking.

import streamlit as st
import pandas as pd
import requests
from pathlib import Path

CSV_PATH = Path(__file__).parent / "data_room/people/employee_roster.csv"

# =============================================================================
# BLS Salary Benchmarking Data (Source: BLS OEWS May 2024)
# SOC codes mapped to common startup roles with national wage percentiles
# =============================================================================
BLS_SALARY_BENCHMARKS = {
    # Format: "role_keyword": {"soc_code": "XX-XXXX", "title": "BLS Title",
    #                          "p10": X, "p25": X, "median": X, "p75": X, "p90": X, "mean": X}
    # All values are annual wages in USD

    # Executive / C-Suite
    "ceo": {"soc_code": "11-1011", "title": "Chief Executives",
            "p10": 81850, "p25": 134380, "median": 206680, "p75": 276730, "p90": 276730, "mean": 246440},
    "cfo": {"soc_code": "11-3031", "title": "Financial Managers",
            "p10": 79050, "p25": 107770, "median": 156100, "p75": 208000, "p90": 276730, "mean": 166050},
    "cto": {"soc_code": "11-3021", "title": "Computer and Information Systems Managers",
            "p10": 99720, "p25": 133420, "median": 169510, "p75": 212830, "p90": 239200, "mean": 173670},

    # VP Level
    "vp engineering": {"soc_code": "11-3021", "title": "Computer and Information Systems Managers",
                       "p10": 99720, "p25": 133420, "median": 169510, "p75": 212830, "p90": 239200, "mean": 173670},
    "vp sales": {"soc_code": "11-2022", "title": "Sales Managers",
                 "p10": 65020, "p25": 97830, "median": 135160, "p75": 185830, "p90": 239200, "mean": 154390},
    "vp product": {"soc_code": "11-2021", "title": "Marketing Managers",
                   "p10": 78500, "p25": 111110, "median": 156580, "p75": 205330, "p90": 239200, "mean": 166410},
    "vp marketing": {"soc_code": "11-2021", "title": "Marketing Managers",
                     "p10": 78500, "p25": 111110, "median": 156580, "p75": 205330, "p90": 239200, "mean": 166410},

    # Directors / Managers
    "director": {"soc_code": "11-1021", "title": "General and Operations Managers",
                 "p10": 57390, "p25": 80450, "median": 101280, "p75": 142020, "p90": 208000, "mean": 122860},
    "engineering manager": {"soc_code": "11-3021", "title": "Computer and Information Systems Managers",
                            "p10": 99720, "p25": 133420, "median": 169510, "p75": 212830, "p90": 239200, "mean": 173670},
    "product manager": {"soc_code": "15-1299", "title": "Computer Occupations, All Other",
                        "p10": 57360, "p25": 79690, "median": 107360, "p75": 143240, "p90": 175990, "mean": 111320},
    "sales manager": {"soc_code": "11-2022", "title": "Sales Managers",
                      "p10": 65020, "p25": 97830, "median": 135160, "p75": 185830, "p90": 239200, "mean": 154390},

    # Engineering Roles
    "software engineer": {"soc_code": "15-1252", "title": "Software Developers",
                          "p10": 74970, "p25": 98540, "median": 132270, "p75": 168570, "p90": 208620, "mean": 136620},
    "ml engineer": {"soc_code": "15-2051", "title": "Data Scientists",
                    "p10": 63890, "p25": 85660, "median": 112590, "p75": 145080, "p90": 184090, "mean": 119040},
    "data scientist": {"soc_code": "15-2051", "title": "Data Scientists",
                       "p10": 63890, "p25": 85660, "median": 112590, "p75": 145080, "p90": 184090, "mean": 119040},
    "data engineer": {"soc_code": "15-1243", "title": "Database Architects",
                      "p10": 66770, "p25": 93040, "median": 127070, "p75": 162790, "p90": 197570, "mean": 129560},
    "backend engineer": {"soc_code": "15-1252", "title": "Software Developers",
                         "p10": 74970, "p25": 98540, "median": 132270, "p75": 168570, "p90": 208620, "mean": 136620},
    "frontend engineer": {"soc_code": "15-1254", "title": "Web Developers",
                          "p10": 45890, "p25": 58180, "median": 80730, "p75": 107410, "p90": 146990, "mean": 86130},
    "full stack engineer": {"soc_code": "15-1252", "title": "Software Developers",
                            "p10": 74970, "p25": 98540, "median": 132270, "p75": 168570, "p90": 208620, "mean": 136620},
    "devops engineer": {"soc_code": "15-1244", "title": "Network and Computer Systems Administrators",
                        "p10": 53960, "p25": 68580, "median": 91360, "p75": 117310, "p90": 147890, "mean": 95350},
    "security engineer": {"soc_code": "15-1212", "title": "Information Security Analysts",
                          "p10": 64500, "p25": 86250, "median": 120360, "p75": 156030, "p90": 186090, "mean": 124740},
    "infrastructure engineer": {"soc_code": "15-1244", "title": "Network and Computer Systems Administrators",
                                "p10": 53960, "p25": 68580, "median": 91360, "p75": 117310, "p90": 147890, "mean": 95350},
    "platform engineer": {"soc_code": "15-1252", "title": "Software Developers",
                          "p10": 74970, "p25": 98540, "median": 132270, "p75": 168570, "p90": 208620, "mean": 136620},

    # Sales Roles
    "account executive": {"soc_code": "41-3091", "title": "Sales Representatives, Services",
                          "p10": 34110, "p25": 48330, "median": 72070, "p75": 109780, "p90": 154570, "mean": 84490},
    "sales development": {"soc_code": "41-3091", "title": "Sales Representatives, Services",
                          "p10": 34110, "p25": 48330, "median": 72070, "p75": 109780, "p90": 154570, "mean": 84490},

    # Marketing Roles
    "marketing manager": {"soc_code": "11-2021", "title": "Marketing Managers",
                          "p10": 78500, "p25": 111110, "median": 156580, "p75": 205330, "p90": 239200, "mean": 166410},
    "marketing analyst": {"soc_code": "13-1161", "title": "Market Research Analysts",
                          "p10": 42170, "p25": 54930, "median": 74680, "p75": 101530, "p90": 131850, "mean": 81020},

    # Finance Roles
    "financial analyst": {"soc_code": "13-2051", "title": "Financial Analysts",
                          "p10": 54100, "p25": 68620, "median": 99890, "p75": 135030, "p90": 176420, "mean": 108790},
    "accountant": {"soc_code": "13-2011", "title": "Accountants and Auditors",
                   "p10": 49250, "p25": 60840, "median": 79880, "p75": 103990, "p90": 132690, "mean": 86080},
    "controller": {"soc_code": "11-3031", "title": "Financial Managers",
                   "p10": 79050, "p25": 107770, "median": 156100, "p75": 208000, "p90": 276730, "mean": 166050},

    # HR / Operations
    "recruiter": {"soc_code": "13-1071", "title": "Human Resources Specialists",
                  "p10": 42720, "p25": 52990, "median": 67650, "p75": 87200, "p90": 109820, "mean": 71170},
    "people ops": {"soc_code": "11-3121", "title": "Human Resources Managers",
                   "p10": 78680, "p25": 103750, "median": 136350, "p75": 180710, "p90": 224360, "mean": 145750},
    "it support": {"soc_code": "15-1232", "title": "Computer User Support Specialists",
                   "p10": 38650, "p25": 47970, "median": 59660, "p75": 75080, "p90": 93700, "mean": 61930},
    "office manager": {"soc_code": "43-1011", "title": "First-Line Supervisors of Office Workers",
                       "p10": 39490, "p25": 50030, "median": 62590, "p75": 79020, "p90": 99100, "mean": 65040},

    # Default fallback
    "default": {"soc_code": "00-0000", "title": "All Occupations",
                "p10": 30930, "p25": 40580, "median": 48060, "p75": 77540, "p90": 115530, "mean": 65470},
}


def match_role_to_benchmark(role: str) -> dict:
    """
    Match an employee role to the closest BLS benchmark.
    Returns the benchmark dict with SOC code, title, and percentile wages.
    """
    if pd.isna(role) or role == "":
        return BLS_SALARY_BENCHMARKS["default"]

    role_lower = role.lower()

    # Priority matching - check most specific first
    priority_keywords = [
        "ceo", "cfo", "cto",
        "vp engineering", "vp sales", "vp product", "vp marketing",
        "engineering manager", "product manager", "sales manager",
        "ml engineer", "data scientist", "data engineer",
        "security engineer", "devops engineer", "infrastructure engineer",
        "backend engineer", "frontend engineer", "full stack engineer", "platform engineer",
        "software engineer",  # More general, after specific types
        "account executive", "sales development",
        "marketing manager", "marketing analyst",
        "financial analyst", "accountant", "controller",
        "recruiter", "people ops", "it support", "office manager",
        "director",  # General fallback for directors
    ]

    for keyword in priority_keywords:
        if keyword in role_lower:
            return BLS_SALARY_BENCHMARKS[keyword]

    # Fallback heuristics
    if "engineer" in role_lower or "developer" in role_lower:
        return BLS_SALARY_BENCHMARKS["software engineer"]
    if "sales" in role_lower:
        return BLS_SALARY_BENCHMARKS["account executive"]
    if "marketing" in role_lower:
        return BLS_SALARY_BENCHMARKS["marketing analyst"]
    if "product" in role_lower:
        return BLS_SALARY_BENCHMARKS["product manager"]
    if "finance" in role_lower or "fp&a" in role_lower:
        return BLS_SALARY_BENCHMARKS["financial analyst"]
    if "hr" in role_lower or "human resources" in role_lower:
        return BLS_SALARY_BENCHMARKS["recruiter"]

    return BLS_SALARY_BENCHMARKS["default"]


def calculate_percentile_position(salary: float, benchmark: dict) -> tuple[str, float]:
    """
    Calculate where the salary falls in the BLS percentile distribution.
    Returns (label, percentile_estimate).
    """
    p10, p25, p50, p75, p90 = benchmark["p10"], benchmark["p25"], benchmark["median"], benchmark["p75"], benchmark["p90"]

    if salary <= p10:
        return "Below 10th", 5.0
    elif salary <= p25:
        # Linear interpolation between p10 and p25
        pct = 10 + (salary - p10) / (p25 - p10) * 15
        return "10th-25th", pct
    elif salary <= p50:
        pct = 25 + (salary - p25) / (p50 - p25) * 25
        return "25th-50th", pct
    elif salary <= p75:
        pct = 50 + (salary - p50) / (p75 - p50) * 25
        return "50th-75th", pct
    elif salary <= p90:
        pct = 75 + (salary - p75) / (p90 - p75) * 15
        return "75th-90th", pct
    else:
        return "Above 90th", 95.0

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

# =============================================================================
# BLS Salary Benchmarking Section
# =============================================================================
st.markdown("### Salary Benchmarking vs. BLS National Data")
st.markdown(
    '<p class="small-note">Compare compensation to Bureau of Labor Statistics OEWS May 2024 national wage percentiles</p>',
    unsafe_allow_html=True,
)

# Add benchmarking data to the selected employees
if not selected.empty:
    benchmark_data = []
    for _, row in selected.iterrows():
        role = row.get("role", "")
        salary = row["comp_usd"]
        benchmark = match_role_to_benchmark(role)
        percentile_label, percentile_est = calculate_percentile_position(salary, benchmark)

        # Calculate premium/discount vs median
        median = benchmark["median"]
        premium_pct = ((salary - median) / median) * 100 if median > 0 else 0

        benchmark_data.append({
            "ID": row.get("employee_id", ""),
            "Name": row.get("name", ""),
            "Role": role,
            "Actual Salary": salary,
            "BLS Occupation": benchmark["title"],
            "SOC Code": benchmark["soc_code"],
            "BLS 25th": benchmark["p25"],
            "BLS Median": median,
            "BLS 75th": benchmark["p75"],
            "Percentile Range": percentile_label,
            "Est. Percentile": percentile_est,
            "vs. Median": premium_pct,
        })

    bench_df = pd.DataFrame(benchmark_data)

    # Summary metrics
    avg_premium = bench_df["vs. Median"].mean()
    above_median_pct = (bench_df["vs. Median"] > 0).sum() / len(bench_df) * 100
    above_75th = (bench_df["Est. Percentile"] >= 75).sum()
    below_25th = (bench_df["Est. Percentile"] <= 25).sum()

    # KPI row for benchmarking
    b1, b2, b3, b4 = st.columns([1, 1, 1, 1])
    b1.markdown(
        card_template.format(label="Avg. Premium vs. BLS Median", value=f"{avg_premium:+.1f}%"),
        unsafe_allow_html=True,
    )
    b2.markdown(
        card_template.format(label="% Paid Above Median", value=f"{above_median_pct:.0f}%"),
        unsafe_allow_html=True,
    )
    b3.markdown(
        card_template.format(label="Above 75th Percentile", value=f"{above_75th}"),
        unsafe_allow_html=True,
    )
    b4.markdown(
        card_template.format(label="Below 25th Percentile", value=f"{below_25th}"),
        unsafe_allow_html=True,
    )

    st.markdown("#### Detailed Compensation Benchmarking")

    # Format the display dataframe
    display_bench = bench_df.copy()
    display_bench["Actual Salary"] = display_bench["Actual Salary"].apply(lambda x: f"${x:,.0f}")
    display_bench["BLS 25th"] = display_bench["BLS 25th"].apply(lambda x: f"${x:,.0f}")
    display_bench["BLS Median"] = display_bench["BLS Median"].apply(lambda x: f"${x:,.0f}")
    display_bench["BLS 75th"] = display_bench["BLS 75th"].apply(lambda x: f"${x:,.0f}")
    display_bench["vs. Median"] = display_bench["vs. Median"].apply(lambda x: f"{x:+.1f}%")
    display_bench["Est. Percentile"] = display_bench["Est. Percentile"].apply(lambda x: f"{x:.0f}th")

    # Select columns for display
    display_cols_bench = [
        "Name", "Role", "Actual Salary", "BLS Occupation",
        "BLS 25th", "BLS Median", "BLS 75th", "Percentile Range", "vs. Median"
    ]

    st.markdown('<div class="data-table">', unsafe_allow_html=True)
    st.dataframe(display_bench[display_cols_bench], use_container_width=True, hide_index=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Insights callout
    if avg_premium > 20:
        st.warning(
            f"**Compensation Risk:** Selected employees are paid {avg_premium:.1f}% above BLS median on average. "
            "This may indicate retention-focused compensation but could impact post-acquisition cost synergies."
        )
    elif avg_premium < -10:
        st.warning(
            f"**Retention Risk:** Selected employees are paid {abs(avg_premium):.1f}% below BLS median on average. "
            "This may indicate flight risk post-acquisition if market-rate adjustments are expected."
        )
    else:
        st.success(
            f"**Market-Aligned:** Selected employees are paid within ±20% of BLS median ({avg_premium:+.1f}% avg). "
            "Compensation appears aligned with national benchmarks."
        )

    # Download benchmarking data
    st.download_button(
        "Download benchmarking analysis CSV",
        bench_df.to_csv(index=False).encode("utf-8"),
        file_name="salary_benchmarking.csv",
        mime="text/csv",
    )

    st.caption(
        "**Data source:** U.S. Bureau of Labor Statistics, Occupational Employment and Wage Statistics (OEWS), May 2024. "
        "National wage estimates. BLS SOC codes mapped to startup roles using keyword matching. "
        "[BLS OEWS Documentation](https://www.bls.gov/oes/)"
    )

else:
    st.info("Select employees above to see salary benchmarking analysis.")

st.markdown("---")
source_label = uploaded.name if uploaded is not None else str(CSV_PATH)
st.caption(f"Roster source: `{source_label}` — total employees in roster: {total_employees}")

