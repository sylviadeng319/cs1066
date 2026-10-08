# Headcount Cost Planner

This Streamlit app selects the requested number of employees from
`../data_room/people/employee_roster.csv`. It prioritizes employees by highest
base compensation by default; turn off the priority toggle to select the lowest
compensation first. The annual cost excludes equity and commission.

Optionally choose must-have positions. The app includes one employee for each
selected role, then fills remaining headcount according to the compensation
priority. If the number of must-have roles exceeds headcount, the app asks you
to increase headcount or choose fewer roles.

Use the view selector to display the selected team as a table or a hierarchy
diagram based on the roster's reporting relationships. Hover over or keyboard
focus an employee in the diagram to see their name, role, department, and annual
base compensation.
Employees whose manager is not in the selected team are grouped separately;
employees without a rostered manager are shown as roots in the chart.

Run it from this directory with a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run app.py
```
