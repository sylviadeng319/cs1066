### Scrape Google Trends data and save it to a CSV file (with bot detection)
### m01e/trends_save.py
###
### Author: Dhilan + GitHub Copilot + Mike
### Date: November 11, 2025
###
### Based on scrape_save.py but using the enhanced trends_scraper with bot detection
import csv
from pathlib import Path

from trends_scraper import get_driver, scrape_interest_data


def build_default_csv_name(query, geo):
    cleaned_query = ''.join(ch if ch.isalnum() or ch in ('-', '_', ' ') else '_' for ch in query.strip())
    cleaned_query = cleaned_query.strip().replace(' ', '_').lower()
    if not cleaned_query:
        cleaned_query = 'google_trends'
    geo_clean = ''.join(ch for ch in geo.strip() if ch.isalnum() or ch in ('-', '_')).lower()
    if not geo_clean:
        geo_clean = 'worldwide'
    return f"{cleaned_query}_{geo_clean}_scraped_data.csv"


def choose_output_file(query, geo):
    fname = Path(build_default_csv_name(query, geo))

    while fname.exists():
        choice = input(
            f"File '{fname.name}' already exists. Type 'overwrite' to replace it or enter a new CSV filename: "
        ).strip().lower()

        if choice == 'overwrite':
            return fname

        if not choice:
            print("A filename is required.")
            continue

        if not choice.lower().endswith('.csv'):
            choice += '.csv'
        fname = Path(choice)

    return fname


def main():
    # Build the URL for Google Trends. This is the page we'll scrape.
    date_range = "now%207-d"
    geo = "US"
    query = input("Enter a Google Trends query: ")
    site = "https://trends.google.com/trends/explore"
    url = f"{site}?date={date_range}&geo={geo}&q={query}&hl=en"

    # Build a driver for a browser
    driver = get_driver()

    # Scrape the interest data
    interest_data = scrape_interest_data(driver, url)

    # Save data to a CSV file
    fname = choose_output_file(query, geo)
    with open(fname, 'w', newline='') as fd:
        writer = csv.DictWriter(fd, fieldnames=['Region', 'Interest'])
        writer.writeheader()
        for region, interest in interest_data.items():
            writer.writerow({'Region': region, 'Interest': interest})
    print(f"Saved data to {fname}")

    driver.quit()


if __name__ == "__main__":
    main()
