import requests
import csv
import os

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

print(classify_kp(6.0))
print(classify_kp(8.0))
print(classify_kp(3.0)) 

url = "https://services.swpc.noaa.gov/products/noaa-planetary-k-index.json"

response = requests.get(url, timeout=20)
response.raise_for_status()

data = response.json()

# Excluir los encabezados y extraer los valores Kp
measurements = data

kp_values = []
history = []

for measurement in measurements:
    kp = float(measurement["Kp"])
    date = measurement["time_tag"]

    kp_values.append(kp)

    classification = classify_kp(kp)

    history.append({
        "date": date,
        "kp": kp,
        "classification": classification,
        "source": "NOAA"
    })

    print(
        "Date:", date,
        "| Kp:", kp,
        "| Classification:", classification
    )

# Calcular indicadores
kp_max = max(kp_values)
kp_min = min(kp_values)
kp_average = sum(kp_values) / len(kp_values)

# Mostrar resultados
print("NORTHERN LIGHT RESEARCH STATION")
print("--------------------------------")

print("Measurements analyzed:", len(kp_values))

print("\nGEOMAGNETIC ACTIVITY ANALYSIS")
print("--------------------------------")

print("Maximum Kp:", kp_max)
print("Minimum Kp:", kp_min)
print("Average Kp:", round(kp_average, 2))
# Save historical measurements to CSV

csv_file = "kp_history.csv"

# Check existing historical records
existing_dates = set()

if os.path.exists(csv_file):

    with open(csv_file, "r", newline="", encoding="utf-8") as file:

        reader = csv.DictReader(file)

        for row in reader:
            existing_dates.add(row["date"])


# Identify new measurements
new_records = []

for record in history:

    if record["date"] not in existing_dates:

        new_records.append(record)
        existing_dates.add(record["date"])


# Append new measurements without deleting previous records
with open(csv_file, "a", newline="", encoding="utf-8") as file:

    fieldnames = ["date", "kp", "classification", "source"]

    writer = csv.DictWriter(file, fieldnames=fieldnames)

    if file.tell() == 0:
        writer.writeheader()

    writer.writerows(new_records)


print("\nHistorical data saved to", csv_file)
print("New measurements added:", len(new_records))
print("Total historical records:", len(existing_dates))