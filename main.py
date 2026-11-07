
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

    else:
        return "No geomagnetic storm"


# ==========================================
# FETCH NOAA DATA
# ==========================================

def fetch_noaa_data():

    print("\nConnecting to NOAA...")

    response = requests.get(NOAA_URL, timeout=20)
    response.raise_for_status()

    data = response.json()

    if not data:
        raise ValueError("NOAA returned an empty response.")

    history = []

    for measurement in data:

        if not isinstance(measurement, dict):
            continue

        if "Kp" not in measurement or "time_tag" not in measurement:
            continue

        if measurement["Kp"] in (None, ""):
            continue

        kp = float(measurement["Kp"])
        date = measurement["time_tag"]

        history.append({
            "date": date,
            "kp": kp,
            "classification": classify_kp(kp),
            "source": "NOAA"
        })

    if not history:
        raise ValueError("No valid Kp measurements were received.")

    return history


# ==========================================
# SAVE HISTORICAL CSV
# ==========================================

def save_csv(history):

    existing_dates = set()

    if CSV_FILE.exists():

        with open(
            CSV_FILE, "r", newline="", encoding="utf-8"
        ) as file:

            reader = csv.DictReader(file)

            for row in reader:
                existing_dates.add(row["date"])

    new_records = []

    for record in history:

        if record["date"] not in existing_dates:

            new_records.append(record)
            existing_dates.add(record["date"])

    fieldnames = [
        "date",
        "kp",
        "classification",
        "source"
    ]

    with open(
        CSV_FILE, "a", newline="", encoding="utf-8"
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=fieldnames
        )

        if file.tell() == 0:
            writer.writeheader()

        writer.writerows(new_records)

    print("\nCSV historical data saved.")
    print("New measurements:", len(new_records))
    print("Historical records:", len(existing_dates))


# ==========================================
# READ COMPLETE HISTORY
# ==========================================

def load_historical_data():

    measurements = []

    if not CSV_FILE.exists():
        return measurements

    with open(
        CSV_FILE, "r", newline="", encoding="utf-8"
    ) as file:

        reader = csv.DictReader(file)

        for row in reader:

            measurements.append({
                "date": row["date"],
                "kp": float(row["kp"]),
                "classification": row["classification"],
                "source": row["source"]
            })

    return measurements


# ==========================================
# EXPORT JSON
# ==========================================

def export_json(history):

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    kp_values = [record["kp"] for record in history]

    statistics = {
        "maximum_kp": max(kp_values),
        "minimum_kp": min(kp_values),
        "average_kp": round(
            sum(kp_values) / len(kp_values), 2
        ),
        "measurements_analyzed": len(kp_values)
    }

    output = {
        "station": "Northernlight Research Station",
        "source": "NOAA SWPC",
        "updated_at": datetime.now(
            timezone.utc
        ).isoformat(),
        "statistics": statistics,
        "measurements": history
    }

    with open(
        JSON_FILE, "w", encoding="utf-8"
    ) as file:

        json.dump(
            output,
            file,
            indent=4,
            ensure_ascii=False
        )

    print("\nJSON export completed.")
    print("File:", JSON_FILE)
    print("Exported measurements:", len(history))


# ==========================================
# MAIN EXECUTION
# ==========================================

def main():

    print("\nNORTHERNLIGHT RESEARCH STATION")
    print("--------------------------------")

    # Obtain current NOAA measurements
    new_history = fetch_noaa_data()

    # Save historical records
    save_csv(new_history)

    # Load complete historical database
    complete_history = load_historical_data()

    # Calculate current NOAA statistics
    kp_values = [record["kp"] for record in new_history]

    print("\nGEOMAGNETIC ACTIVITY ANALYSIS")
    print("--------------------------------")

    print("Maximum Kp:", max(kp_values))
    print("Minimum Kp:", min(kp_values))

    print(
        "Average Kp:",
        round(sum(kp_values) / len(kp_values), 2)
    )

    print(
        "Historical measurements:",
        len(complete_history)
    )

    # Export complete history to JSON
    export_json(complete_history)

    print("\nNorthernlight execution completed.")


if __name__ == "__main__":
    main()
