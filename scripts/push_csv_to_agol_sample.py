# Note: user must run "pip install arcgis" in their virtual environment for this to work
from arcgis.gis import GIS
from arcgis.features import FeatureLayerCollection
from pathlib import Path

# Configuration

# Path to the CSV genenerated from scrape_water_rates_data.py
csv_path = Path(r"C:\path\to\water_rates.csv")

# ArcGIS Online credentials
AGOL_Username = "your_username"
AGOL_Password = "your_password"

# The item ID of the hosted table in ArcGIS Online
# To find this, view the details of the hosted table, view the URL, and copy the "Service ItemID" string
Hosted_csv_item_id = "your_item_id_here"

# Main Logic

def main():
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV not found: {csv_path}")

    print("Connecting to ArcGIS Online...")
    gis = GIS("https://www.arcgis.com", AGOL_Username, AGOL_Password)

    print(f"Fetching hosted item with ID {Hosted_csv_item_id}...")
    item = gis.content.get(Hosted_csv_item_id)
    if not item:
        raise ValueError(f"No item found with ID {Hosted_csv_item_id}")

    # Confirm it's a FeatureLayerCollection (hosted table)
    flc = FeatureLayerCollection.fromitem(item)
    print(f"Overwriting hosted table '{item.title}' with CSV: {csv_path}")

    # Overwrite the table
    flc.manager.overwrite(str(csv_path))

if __name__ == "__main__":
    main()
