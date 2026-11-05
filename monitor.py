
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

# Project directory
PROJECT_DIR = Path(__file__).resolve().parent

# Update interval: 15 minutes
UPDATE_INTERVAL = 15 * 60


def run_cycle():

    print("\n" + "=" * 45)
    print("NORTHERNLIGHT MONITOR")
    print("=" * 45)

    print("Update started:", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    # Collect NOAA data
    print("\n[1/2] Collecting NOAA measurements...")

    result = subprocess.run(
        [sys.executable, "main.py"],
        cwd=PROJECT_DIR
    )

    if result.returncode != 0:
        print("ERROR: Data collection failed.")
        return

    # Generate updated graph
    print("\n[2/2] Updating scientific visualization...")

    result = subprocess.run(
        [sys.executable, "kp_visualization.py"],
        cwd=PROJECT_DIR
    )

    if result.returncode != 0:
        print("ERROR: Graph generation failed.")
        return

    print("\nUpdate completed successfully.")
    print("Next update in 15 minutes.")


try:

    while True:

        run_cycle()

        print("\nMonitor is running...")
        print("Press CTRL + C to stop.")

        time.sleep(UPDATE_INTERVAL)

except KeyboardInterrupt:

    print("\nNorthernLight Monitor stopped safely.")
