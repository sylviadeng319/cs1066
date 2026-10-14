### m11/query3.py
import requests

query = """
SELECT column_name, datatype, description
FROM TAP_SCHEMA.columns
WHERE table_name = 'pscomppars'
"""
output_filename = "pscomppars_cols.txt"

response = requests.get(
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
    params={
        "query": query,
        "format": "json",
    },
)

response.raise_for_status()
rows = response.json()

with open(output_filename, "w") as output_file:
    for row in rows:
        output_file.write(f"{row}\n")
