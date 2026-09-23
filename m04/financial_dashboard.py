"""Ask for a CIK and create a financial dashboard from SEC EDGAR data."""

from datetime import date
from html import escape
from pathlib import Path
import re

import plotly.graph_objects as go
import requests


SEC_URL = "https://data.sec.gov/api/xbrl/companyfacts/CIK{}.json"
USER_AGENT = "UniversityStudent your.email@harvard.edu"
OUTPUT_DIRECTORY = Path(__file__).parent


def validate_cik(cik):
    """Return a CIK unchanged, or raise ValueError if it is not 10 digits."""
    if len(cik) != 10 or not cik.isdigit():
        raise ValueError("CIK must contain exactly 10 digits.")
    return cik


def prompt_for_cik():
    """Prompt repeatedly until the user enters a valid CIK."""
    while True:
        try:
            return validate_cik(input("Enter the company's 10-digit CIK: ").strip())
        except ValueError as error:
            print(f"Invalid CIK: {error}")


def fetch_company_facts(cik):
    """Request a company's facts from the SEC EDGAR API."""
    try:
        response = requests.get(
            SEC_URL.format(cik),
            headers={"User-Agent": USER_AGENT},
            timeout=30,
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as error:
        raise RuntimeError(f"SEC request failed: {error}") from error
    except ValueError as error:
        raise RuntimeError("The SEC response was not valid JSON.") from error


def annual_values(facts, tags):
    """Get up to 10 annual USD values, ordered from oldest to newest."""
    us_gaap = facts.get("facts", {}).get("us-gaap", {})
    candidate_facts = []
    for tag in tags:
        candidate_facts.extend(us_gaap.get(tag, {}).get("units", {}).get("USD", []))

    values_by_year = {}
    for fact in candidate_facts:
        if fact.get("form") != "10-K" or fact.get("fp") != "FY":
            continue
        if not fact.get("fy") or not fact.get("end"):
            continue

        # A duration of about one year distinguishes annual facts from quarters.
        if fact.get("start"):
            duration = (date.fromisoformat(fact["end"]) - date.fromisoformat(fact["start"])).days
            if not 300 <= duration <= 400:
                continue

        year = int(fact["fy"])
        if year not in values_by_year or fact.get("filed", "") > values_by_year[year].get("filed", ""):
            values_by_year[year] = fact

    return [(year, values_by_year[year]["val"]) for year in sorted(values_by_year)[-10:]]


def make_plot(years, values, title):
    """Create one readable line plot."""
    figure = go.Figure(go.Scatter(x=years, y=values, mode="lines+markers"))
    figure.update_layout(
        title=title,
        xaxis_title="Fiscal year",
        yaxis_title="US dollars",
        height=360,
        margin={"l": 70, "r": 30, "t": 65, "b": 55},
    )
    return figure


def create_dashboard(facts, output_file=None):
    """Write a webpage with vertically stacked revenue, income, and asset plots."""
    metric_tags = {
        "Revenue": [
            "Revenue",
            "Revenues",
            "SalesRevenueNet",
            "RevenueFromContractWithCustomerExcludingAssessedTax",
        ],
        "Net income": ["NetIncomeLoss"],
        "Total assets": ["Assets"],
    }
    extracted = {name: annual_values(facts, tags) for name, tags in metric_tags.items()}
    missing = [name for name, values in extracted.items() if not values]
    if missing:
        raise RuntimeError("No annual data was found for: " + ", ".join(missing) + ".")

    company_name = facts.get("entityName", "Unknown company")
    cik = str(facts.get("cik", "unknown")).zfill(10)
    if output_file is None:
        safe_filename = re.sub(r"[^A-Za-z0-9]+", "_", str(company_name)).strip("_")
        output_file = OUTPUT_DIRECTORY / f"{safe_filename}_{cik}_financial_dashboard.html"

    plots = []
    for name, values in extracted.items():
        years, amounts = zip(*values)
        plots.append(make_plot(years, amounts, name).to_html(full_html=False, include_plotlyjs=False))

    safe_name = escape(str(company_name))
    html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{safe_name} financial dashboard</title>
  <script src="https://cdn.plot.ly/plotly-2.35.2.min.js"></script>
  <style>
    body {{ font-family: sans-serif; margin: 2rem auto; max-width: 1100px; padding: 0 1rem; }}
    h1 {{ margin-bottom: 0.25rem; }}
    .subtitle {{ color: #555; margin-top: 0; }}
  </style>
</head>
<body>
  <h1>{safe_name}</h1>
  <p class="subtitle">CIK: {escape(cik)}</p>
  {''.join(plots)}
</body>
</html>
"""
    output_file = Path(output_file)
    output_file.write_text(html, encoding="utf-8")
    return output_file


def main():
    cik = prompt_for_cik()
    try:
        facts = fetch_company_facts(cik)
        output_file = create_dashboard(facts)
    except RuntimeError as error:
        print(f"Could not create dashboard: {error}")
        return
    print(f"Dashboard created at {output_file}")


if __name__ == "__main__":
    main()
