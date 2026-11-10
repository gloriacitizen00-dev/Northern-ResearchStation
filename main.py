
import requests
import csv
import os
import json

from pathlib import Path
from datetime import datetime, timezone


# ==========================================
# NORTHERNLIGHT RESEARCH STATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent

CSV_FILE = BASE_DIR / "kp_history.csv"
DATA_DIR = BASE_DIR / "data"
JSON_FILE = DATA_DIR / "northernlight.json"

NOAA_URL = (
    "https://services.swpc.noaa.gov/"
    "products/noaa-planetary-k-index.json"
)

FIELDNAMES = [
    "date",
    "kp",
    "classification",
    "a_running",
    "station_count",
    "source"
]


# ==========================================
# GEOMAGNETIC CLASSIFICATION
# ==========================================

def classify_kp(kp):

    if kp >= 9:
        return "G5 - Extreme"
    elif kp >= 8:
        return "G4 - Severe"
    elif kp >= 7:
        return "G3 - Strong"
    elif kp >= 6:
        return "G2 - Moderate"
    elif kp >= 5:
        return "G1 - Minor"

    return "No geomagnetic storm"


# ==========================================
# OPTIONAL NOAA VALUES
# ==========================================

def optional_number(value):

    if value in (None, ""):
        return None

    try:
        return int(float(value))
    except (ValueError, TypeError):
        return None


# ==========================================
# FETCH NOAA DATA
# ==========================================

def fetch_noaa_data():

    print("\nConnecting to NOAA SWPC...")

    response = requests.get(
        NOAA_URL,
        timeout=20
    )

    response.raise_for_status()

    data = response.json()

    if not isinstance(data, list) or not data:
        raise ValueError("Invalid NOAA response.")

    history = []

    for measurement in data:

        if not isinstance(measurement, dict):
            continue

        date = measurement.get("time_tag")
        kp_value = measurement.get("Kp")

        if not date or kp_value in (None, ""):
            continue

        try:
            kp = float(kp_value)
        except (ValueError, TypeError):
            continue

        if not 0 <= kp <= 9:
            continue

        history.append({
            "date": date,
            "kp": kp,
            "classification": classify_kp(kp),
            "a_running": optional_number(
                measurement.get("a_running")
            ),
            "station_count": optional_number(
                measurement.get("station_count")
            ),
            "source": "NOAA"
        })

    if not history:
        raise ValueError("No valid NOAA measurements.")

    return history


# ==========================================
# READ EXISTING CSV
# ==========================================

def read_csv_history():

    records = {}

    if not CSV_FILE.exists():
        return records

    with open(
        CSV_FILE,
        "r",
        newline="",
        encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            date = row.get("date")

            if not date:
                continue

            try:
                kp = float(row["kp"])
            except (ValueError, TypeError, KeyError):
                continue

            records[date] = {
                "date": date,
                "kp": kp,
                "classification": (
                    row.get("classification")
                    or classify_kp(kp)
                ),
                "a_running": optional_number(
                    row.get("a_running")
                ),
                "station_count": optional_number(
                    row.get("station_count")
                ),
                "source": row.get("source") or "NOAA"
            }

    return records


# ==========================================
# UPDATE HISTORICAL CSV
# ==========================================

def save_csv(history):

    records = read_csv_history()

    new_records = 0
    updated_records = 0

    for measurement in history:

        date = measurement["date"]

        if date in records:

            previous = records[date].copy()

            updated = previous.copy()
            updated.update(measurement)

            # Preserve existing optional values
            # if NOAA does not provide them.

            for field in ("a_running", "station_count"):

                if measurement[field] is None:
                    updated[field] = previous[field]

            if updated != previous:
                updated_records += 1

            records[date] = updated

        else:

            records[date] = measurement
            new_records += 1

    ordered_records = sorted(
        records.values(),
        key=lambda item: item["date"]
    )

    temporary_file = CSV_FILE.with_suffix(".tmp")

    with open(
        temporary_file,
        "w",
        newline="",
        encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=FIELDNAMES
        )

        writer.writeheader()
        writer.writerows(ordered_records)

    os.replace(temporary_file, CSV_FILE)

    print("\nCSV historical database updated.")
    print("New measurements:", new_records)
    print("Updated measurements:", updated_records)
    print("Total historical records:", len(records))

    return ordered_records


# ==========================================
# CALCULATE STATISTICS
# ==========================================

def calculate_statistics(history):

    if not history:
        raise ValueError("No measurements available.")

    values = [
        record["kp"]
        for record in history
    ]

    return {
        "maximum_kp": max(values),
        "minimum_kp": min(values),
        "average_kp": round(
            sum(values) / len(values), 2
        ),
        "measurements_analyzed": len(values)
    }


# ==========================================
# EXPORT JSON
# ==========================================

def export_json(history, latest_history):

    DATA_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    ordered_latest = sorted(
        latest_history,
        key=lambda item: item["date"]
    )

    latest_measurement = ordered_latest[-1]

    output = {
        "station": "Northernlight Research Station",

        "source": "NOAA SWPC",

        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),

        "statistics": calculate_statistics(history),

        "latest_noaa": {
            "statistics": calculate_statistics(
                latest_history
            ),
            "latest_measurement": latest_measurement
        },

        "measurements": history
    }

    temporary_file = JSON_FILE.with_suffix(".tmp")

    with open(
        temporary_file,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    os.replace(temporary_file, JSON_FILE)

    print("\nJSON export completed.")
    print("File:", JSON_FILE)
    print("Exported measurements:", len(history))


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():

    print("\nNORTHERNLIGHT RESEARCH STATION")
    print("=" * 45)

    # 1. Obtain NOAA measurements

    new_history = fetch_noaa_data()

    # 2. Update historical database

    complete_history = save_csv(new_history)

    # 3. Calculate current statistics

    current_statistics = calculate_statistics(
        new_history
    )

    print("\nCURRENT NOAA ANALYSIS")
    print("-" * 35)

    for key, value in current_statistics.items():
        print(f"{key}: {value}")

    # 4. Export complete JSON database

    export_json(
        complete_history,
        new_history
    )

    print("\nNorthernlight execution completed.")


if __name__ == "__main__":
    main()
