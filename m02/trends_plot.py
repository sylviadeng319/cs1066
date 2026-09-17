### Plot the scraped and saved Google Trends data
### m01e/trends_plot.py
### 
### Author: Sharon Zhou and Mike Smith
### Date: 20250916
###
### Original idea and code from https://brightdata.com/blog/web-data/how-to-scrape-google-trends

from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


def choose_input_file():
    csv_files = sorted(Path('.').glob('*_scraped_data.csv'), key=lambda p: p.stat().st_mtime, reverse=True)

    if csv_files:
        default_file = csv_files[0]
        choice = input(
            f"Use '{default_file.name}' as the input CSV? Press Enter to use it, or type a different CSV filename: "
        ).strip()
        if choice:
            return choice
        return str(default_file)

    while True:
        input_file = input("Enter the CSV file to plot: ").strip()
        if input_file:
            return input_file
        print("A CSV filename is required.")


def choose_output_file(input_file):
    csv_path = Path(input_file)
    stem = csv_path.stem.replace('_scraped_data', '')
    output = Path(f"{stem}.png")

    while output.exists():
        choice = input(
            f"File '{output.name}' already exists. Type 'overwrite' to replace it or enter a new image filename: "
        ).strip().lower()

        if choice == 'overwrite':
            return output

        if not choice:
            print("A filename is required.")
            continue

        if not choice.lower().endswith('.png'):
            choice += '.png'
        output = Path(choice)

    return output


def main():
    input_file = choose_input_file()
    output_file = choose_output_file(input_file)

    # Read the CSV file into a pandas dataframe
    df = pd.read_csv(input_file)
    print(f"Read data from {input_file}")
    print(df.head())    # Sanity check

    # Plot the data in a bar chart
    plt.figure(figsize=(10, 6))
    plt.bar(df['Region'], df['Interest'], color='skyblue')

    # Add labels and title
    plt.xlabel('Region')
    plt.ylabel('Interest')
    plt.title('Google Trends Interest by Region')

    # Rotate the x-axis labels for readability
    plt.xticks(rotation=90)
    plt.tight_layout()

    # Save the plot to a file
    plt.savefig(output_file)
    print(f"Saved plot to {output_file}")

if __name__ == "__main__":
    main()