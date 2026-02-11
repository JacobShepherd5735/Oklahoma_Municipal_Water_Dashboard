import subprocess
import sys
from pathlib import Path
from datetime import datetime

# Configuration

# Paths to scripts
Script_1 = Path(r"C:\path\to\scrape_water_rates_data.py")
Script_2 = Path(r"C:\path\to\push_csv_to_github.py")
# Optional script (set to None to disable AGOL automation)
Script_3 = None
# Example if using: Script_3 = Path(r"C:\path\to\push_csv_to_agol.py")

# Log file to record execution output
Log = Path(r"C:\path\to\sequence_log.txt")

# Helper Function

def run_script(script_path):
    # Run a Python script and return True if it succeeds, False otherwise.
    print(f"\nRunning: {script_path}")
    try:
        result = subprocess.run(
            [sys.executable, str(script_path)],
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        # Log output
        with Log.open("a") as f:
            f.write(f"\n[{datetime.now()}] Output of {script_path}:\n")
            f.write(result.stdout)
            f.write(result.stderr)
        print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        # Log errors
        with Log.open("a") as f:
            f.write(f"\n[{datetime.now()}] Error running {script_path}:\n")
            f.write(e.stdout or "")
            f.write(e.stderr or "")
        print(f"Error running {script_path}:\n{e.stderr}")
        return False

# Main Logic

def main():
    print("Starting script sequence.")

    if not Script_1.exists():
        print(f"Error: Script 1 not found at {Script_1}")
        return

    if not Script_2.exists():
        print(f"Error: Script 2 not found at {Script_2}")
        return

    if Script_3:
        if not Script_3.exists():
            print(f"Error: Optional script not found at {Script_3}")
            return

    # Run first script
    if not run_script(Script_1):
        print("First script failed. Aborting sequence.")
        return

    # Run second script
    if not run_script(Script_2):
        print("Second script failed.")
        return

    # Run Script 3 if enabled
    if Script_3:
        if not run_script(Script_3):
            print("Optional third script failed.")
            return

    print("Script sequence completed successfully.")

if __name__ == "__main__":
    main()
