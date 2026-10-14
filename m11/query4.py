### m11/query4.py
import requests

# query = """
# SELECT pl_name, COUNT(*) AS number_of_rows
# FROM pscomppars
# GROUP BY pl_name
# HAVING COUNT(*) > 1
# ORDER BY number_of_rows DESC
# """
query = """
SELECT pl_name, COUNT(*) AS number_of_rows
FROM ps
GROUP BY pl_name
HAVING COUNT(*) > 1
ORDER BY number_of_rows DESC
"""
output_filename = "pl_rowcnt.txt"


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
