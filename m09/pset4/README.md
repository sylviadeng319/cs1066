# Headcount Cost Planner

This Streamlit app selects the requested number of employees from
`../data_room/people/employee_roster.csv`, prioritizing the lowest base
compensation first. The displayed annual cost excludes equity and commission.

Run it from this directory with a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```
