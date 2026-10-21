#!/usr/bin/env python3

import csv
import re
import sys
from pathlib import Path

DATASETS = {
    "A": "datasetA.csv",
    "B": "datasetB.csv",
    "C": "datasetC.csv",
}


def clean_text(value):
    return (value or "").strip()


def email_key(value):
    return clean_text(value).lower()


def phone_key(value):
    digits = re.sub(r"\D", "", clean_text(value))
    if len(digits) == 11 and digits.startswith("1"):
        digits = digits[1:]
    return digits


def normalize_name(value):
    text = clean_text(value).lower().replace(".", " ")
    text = re.sub(r"[^a-z\s]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def name_variants(value):
    text = normalize_name(value)
    if not text:
        return set()

    parts = text.split()
    if len(parts) == 1:
        return {parts[0], parts[0][0]}

    first, last = parts[0], parts[-1]
    variants = {
        text,
        first,
        last,
        f"{first} {last}",
        f"{first[0]} {last}",
        f"{first} {last[0]}",
        f"{first[0]} {last[0]}",
    }
    return variants


def names_match(left_name, right_name):
    left_variants = name_variants(left_name)
    right_variants = name_variants(right_name)
    if not left_variants or not right_variants:
        return False
    return bool(left_variants & right_variants)


def row_match(left, right):
    left_keys = set(left.keys())
    right_keys = set(right.keys())

    if "email" in left_keys and "email" in right_keys:
        if email_key(left.get("email")) and email_key(left.get("email")) == email_key(right.get("email")):
            return True

    if "phone" in left_keys and "phone" in right_keys:
        left_phone = phone_key(left.get("phone"))
        right_phone = phone_key(right.get("phone"))
        if left_phone and left_phone == right_phone:
            return True

    if "name" in left_keys and "name" in right_keys:
        if names_match(left.get("name"), right.get("name")):
            return True

    return False


def merge_rows(left_rows, right_rows):
    if not left_rows:
        return [dict(row) for row in right_rows]
    if not right_rows:
        return [dict(row) for row in left_rows]

    merged_rows = [dict(row) for row in left_rows]

    for right_row in right_rows:
        match_index = None
        for index, left_row in enumerate(left_rows):
            if row_match(left_row, right_row):
                match_index = index
                break

        if match_index is None:
            merged_rows.append(dict(right_row))
        else:
            merged_row = dict(merged_rows[match_index])
            for key, value in right_row.items():
                if not merged_row.get(key):
                    merged_row[key] = value
            merged_rows[match_index] = merged_row

    return merged_rows


def read_dataset(letter):
    file_name = DATASETS.get(letter.upper())
    if file_name is None:
        raise ValueError(f"Unknown dataset: {letter!r}")
    path = Path(__file__).resolve().parent / file_name
    with path.open(newline="") as csv_file:
        return list(csv.DictReader(csv_file))


def ordered_fields(rows):
    field_order = []
    seen = set()
    for row in rows:
        for key in row.keys():
            if key not in seen:
                field_order.append(key)
                seen.add(key)
    return field_order


def write_rows(rows, stream):
    fieldnames = ordered_fields(rows)
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})


def main(argv):
    if len(argv) < 2:
        print(f"Usage: python3 {Path(argv[0]).name} A B [C]", file=sys.stderr)
        print("Example: python3 combine_csv.py A B C", file=sys.stderr)
        return 1

    selected = []
    for value in argv[1:]:
        letter = value.strip().upper()
        if letter not in DATASETS:
            print(f"Unknown dataset selector: {value!r}; expected A, B, or C.", file=sys.stderr)
            return 1
        selected.append(letter)

    combined = read_dataset(selected[0])
    for letter in selected[1:]:
        combined = merge_rows(combined, read_dataset(letter))

    write_rows(combined, sys.stdout)
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
