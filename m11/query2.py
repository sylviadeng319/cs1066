### m11/query2.py
import requests

query = """
SELECT schema_name, table_name
FROM TAP_SCHEMA.tables
"""

response = requests.get(
    "https://exoplanetarchive.ipac.caltech.edu/TAP/sync",
    params={
        "query": query,
        "format": "json",
    },
)

response.raise_for_status()
rows = response.json()

for row in rows:
    print(row)
