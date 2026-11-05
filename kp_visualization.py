
import csv
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from datetime import datetime

# Load historical Kp measurements
csv_file = "kp_history.csv"

dates = []
kp_values = []

with open(csv_file, "r", newline="", encoding="utf-8") as file:

    reader = csv.DictReader(file)

    for row in reader:

        date = datetime.fromisoformat(
            row["date"].replace("Z", "+00:00")
        )

        kp = float(row["kp"])

        dates.append(date)
        kp_values.append(kp)

# Sort measurements chronologically
measurements = sorted(zip(dates, kp_values))

dates = [item[0] for item in measurements]
kp_values = [item[1] for item in measurements]

# Create scientific visualization
fig, ax = plt.subplots(figsize=(12, 6))

ax.plot(
    dates,
    kp_values,
    marker="o",
    markersize=3,
    linewidth=1.8,
    label="Planetary Kp Index"
)

# Geomagnetic storm thresholds
thresholds = [5, 6, 7, 8, 9]

for threshold in thresholds:
    ax.axhline(
        y=threshold,
        linestyle="--",
        linewidth=0.8,
        alpha=0.6
    )

# Chart configuration
ax.set_title(
    "NORTHERNLIGHT - Geomagnetic Activity",
    fontsize=14
)

ax.set_xlabel("Date and Time")
ax.set_ylabel("Planetary Kp Index")

ax.set_ylim(0, 9.5)
ax.set_yticks(range(10))

ax.xaxis.set_major_formatter(
    mdates.DateFormatter("%m-%d %H:%M")
)

fig.autofmt_xdate()

ax.grid(True, alpha=0.3)
ax.legend()

plt.tight_layout()

# Save visualization
output_file = "kp_history.png"

plt.savefig(
    output_file,
    dpi=150,
    bbox_inches="tight"
)

print("Graph saved successfully:", output_file)
print("Measurements plotted:", len(kp_values))

plt.close(fig)
