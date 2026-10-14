### m11/query1.py
import requests

ROWS_TO_PRINT = 10

query = """
SELECT pl_name, pl_orbper
FROM ps
WHERE pl_orbper >= 10
  AND pl_orbper <= 20
ORDER BY pl_orbper
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

for i, row in enumerate(rows):
    print(row)
    if i >= ROWS_TO_PRINT - 1:
        break
