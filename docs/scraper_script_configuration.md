# Scrape_Water_Rates_Data.py configuration

---

## Overview
This script is the core coding piece of this project. It collects residential water rate data from 15 Oklahoma municipalities, standardizes them (methodology below), and outputs CSV files suitable for ArcGIS Dashboard and time-series analysis.

This script is implimented as an object-oriented Python class (`WaterRateScraper`) and supports:
- Web scraping (static HTML and embedded JSON/Nuxt data)
- PDF parsing
- CSV outputs
- Standardized rate calculations
- Logging and error handling
- Modular municipality scraper functions
- Togglable orchestration

---

## Imports and Dependencies
This script uses the following libraries:

Standard Library:
- `os`: File checks and environment variables
- `csv`: CSV writing
- `json`: Parsing embedded Nuxt JSON data
- `time`: Throttling requests
- `logging`: Structured runtime logging
- `datetime`: Timestamping and dynamic filenaming

Third-Party Libraries:
- `requests`: HTTP requests
- `BeautifulSoup4 (bs4)`: HTML parsing
- `pdfplumber`: PDF text extraction
- `certifi`: SSL certificate validation

SSL is explicitly configured using:
`os.environ["SSL_CERT_FILE"] = certifi.where()`
This ensures reliable HTTPS connections across environments and is more stable when updating the requests library

---

## Municipality Metadata
The `WaterRateScraper` class initializes three important dictionaries:
```
self.municipality_ids
self.municipality_names
self.municipality_coordinates
```
These provide:
- Stable numeric, unique IDs for dashboards
- Consistent naming
- Latitude/Longitude centroid data for map visualization
Having these dictionaries allows for future expansion by keeping information centralized to be referenced in each scraper method

---

## CSV Output Design
Each run of this script writes to:
1. `water_rates.csv` (master file)
2. `water_rates<MonthYYYY>.csv` (run-specific snapshot)
Example:
`water_rates_January2026.csv`
This aids in historical tracking of rate changes, reproducability, and monthly archiving. The schema is the same across both the master and run-specific csv. If you are interested in the data schema, see `data_schema.md`.

---

## Standardization Methodology
Each municipality features a calculated, standardized monthly water bill based on 6,000 gallons per month residential usage.
This enables easy comparisons across municipalities with:
- Different (or no) base fees
- Different volumetric tiers
- Different measurement units (gallons, cubic feet, MG)
Each scraper:
- Extracts a base charge (if applicable)
- Extracts volumetric tiers
- Applies tier logic to the 6,000 gallon threshold
- Computes total cost
- Writes one standardized value per municipality

---

## Helper Functions
`get_timestamp()`: Returns formatted date string for row-level tracking

`dollar_to_float(text)`: Converts strings like "$12.34" into "12.34" and can handle dollar signs, commas, and empty values

`safe_pause(seconds)`: Ensures pauses between batches will not be interrupted by an IDE KeyboardInterrupt

`write_to_csv(...)`: Centralized CSV writing logic

---

## Logging
Logging is initialized in `__init__()`:
```
logging.basicConfig(
            filename="scraper.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )
```
Logging captures:
- Start and completion of script and each scraper
- Successful writes
- Parsing failures
- Unhandled exceptions
This makes scheduled runs (such as with Windows Task Scheduler) trackable without console output.

---

## Error Handling
Each scraper is wrapped in:
```
try:
  ...
except Exception as e:
  self.logger.exception(...)
```
This ensures that one city failing does not stop the entire run or result in partial outputs, and errors are logged with stack traces. Additionally, the orchestator includes an outer try/except per scraper call to catch unexpected failures.

---

## Data Source Types Handled
This script demonstrates handling of multiple common municipal site structures:
| Source Type | Example Handling |
|-----------|-----------|
| Static HTML tables | BeautifulSoup parsing |
| List-based HTML content | UL/LI extraction |
| Embedded Nuxt JSON | Recursive object walk |
| PDF documents | pdf plumber extraction |
| Hardcoded annual rates | Direct dictionaries |

---

## Orchestration
The orchestrator `run_all_scrapers()` builds a list of scraper functions and executes them in batches.

Initially, this script was built to run all scrapers sequentially. However, during testing, this resulted in too many requests getting sent and the script failing despite the code itself having no issue. As a result, batch executation was implimented. Four batches of scrapers are launched sequentially, with 3 second pauses in between each batch, to ensure the script runs while not sending too many requests at one time. 

PDF-based scrapers use lambdas to pass file paths, for example: `lambda: self.scrape_stillwater("Local_Stillwater_PDF.pdf")`. This keeps the orchestration clean while supporting arguments.

---

## Execution Entry Point
This script runs via:
```
if __name__ == "__main__":
    scraper = WaterRateScraper()
    scraper.run_all_scrapers()
```
This allows for scheduled automation and future import into other modules if needed

---

## Design Advantages
- Object-oriented, modular structure
- Centralized output logic
- Standardized cross-city comparison
- Error handling
- Logging for automated execution
- Month/Year archiving
- Flexible data extraction techniques

---

## Potential Future Improvements
- Utilizing regex for more robust rate change handling
- Moving certain data components (such as municipality metadata) to an extrnal config file (JSON/YAML)
- Add HTTP Request Headers to reduce risk of future blocking
