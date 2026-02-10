import subprocess
import shutil
from pathlib import Path
from datetime import datetime

# Configuration

# Directory where scraper outputs CSVs
output_directory = Path(r"C:\path\to\csvs")

# Main CSV (always updated)
main_csv = "water_rates.csv"

# GitHub repo SSH URL
repo_ssh_url = "git@github.com:your-username/your-repo.git"

# Local directory where repo will be cloned
clone_directory = Path("./repo_clone")

# Data directory inside the repo
data_directory = "data"

# Helper Functions

def run_command(command, cwd=None):
    result = subprocess.run(
        command,
        cwd=cwd,
        shell=True,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    return result.stdout.strip()

# Main Logic

def main():
    main_csv_path = output_directory / main_csv

    if not main_csv_path.exists():
        raise FileNotFoundError(f"Main CSV not found: {main_csv_path}")

    # Find versioned CSV (e.g., water_rates_January2026.csv)
    run_csvs = sorted(
        output_directory.glob("water_rates_*.csv")
    )

    if not run_csvs:
        raise FileNotFoundError("No versioned CSV found.")

    # Assume the most recent run file is the one to push
    run_csv = run_csvs[-1]

    # Clone or update repo
    if not clone_directory.exists():
        print("Cloning repository...")
        run_command(f"git clone {repo_ssh_url} {clone_directory}")
    else:
        print("Repository already cloned, pulling latest changes...")
        run_command("git pull", cwd=clone_directory)

    data_dir = clone_directory / data_directory
    data_dir.mkdir(exist_ok=True)

    # Destination paths (inside repo)
    dest_main_csv_path = data_dir / main_csv
    dest_run_csv_path = data_dir / run_csv.name

    # Copy CSVs
    shutil.copy2(main_csv_path, dest_main_csv_path)
    shutil.copy2(run_csv, dest_run_csv_path)

    print("Copied CSVs:")
    print(f" - {dest_main_csv_path}")
    print(f" - {dest_run_csv_path}")

    # Git add, commit, push
    run_command("git add data", cwd=clone_directory)

    commit_message = f"Automated update of water rates data"
    run_command(f'git commit -m "{commit_message}"', cwd=clone_directory)

    run_command("git push", cwd=clone_directory)

    print("CSV files successfully pushed to GitHub.")

if __name__ == "__main__":
    main()