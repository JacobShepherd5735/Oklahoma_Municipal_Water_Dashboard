# Oklahoma Municipal Water Rates Dashboard

### Link to Project ArcGIS Dashboard (Copy and paste link to avoid 403 error): https://www.arcgis.com/apps/dashboards/38364b5628914dbc8b5145df3d99f680

A Python-based data pipeline and ArcGIS Dashboard for tracking and visualizing municipal water rates across Oklahoma.

### 1. Overview
This project is a semi-automated pipeline that collects, standardizes, and visualizes  municipal water rates across Oklahoma. These rates vary across Oklahoma for several reasons, including the use of different meter sizes, whether there is a base or minimum charge, whether uniform, declining, or inclining block rates are employed, and if water is measured in gallons or cubic feet. In addition, this project provides a central source for comparing and monitoring water rates over time, something that was easy to do before this project. 
This repository contains:
* A Python scraper script for 15 municipalities
* A standardization method to compare rates using a 6,000-gallon per month benchmark
* A sample Python script for how to automatically update the hosted table used by the ArcGIS Dashboard
* Automated GitHub updating for versioned CSVs
* Documentation and instructions for installing and configuring this project to be expanded upon or used for other municipal utilies in the future.

### 2. Repository Structure
```
/scripts/           # All scripts associated with this project

/data/              # CSV outputs (main and versioned)

/docs/              # Documentation files

LICENSE.md          # MIT License

README.md           # This document

requirements.txt    # Python dependencies
```

### 3. Features
* Web scraping with support for HTML, PDF, and JavaScript-rendered water rates
* Standardized monthly water cost calculation (assuming 6,000 gallons used per month)
* CSV output for use in the project's ArcGIS Dashboard and for tracking historical water rates
* Automation using Windows Task Scheduler

### 4. Installation
Create a virtual environment
```
python -m venv venv        # replace first "venv" with desired virtual environment name
venv\Scripts\activate      # Windows (if you renamed your virtual environment, replace "venv" here with your virtual environment name)
source venv/bin/activate   # Mac/Linux (if you renamed your virtual environment, replace "venv" here with your virtual environment name)
```
Once your virtual environment has been created and activate, install dependencies
```
pip install -r requirements.txt
```

### 5. Running the Scraper Script
To run the primary scraper script:
```
python scrape_water_rates_data.py
```
Output will be written with the filename "water_rates.csv"

### 6. Automation Workflow
A Windows Task Scheduler job can run the scraper at whatever frequency you desire. For this project, the Windows Task Scheduler job is set to run quarterly.
The Windows Task Scheduler job will:
1. Scrape all available municipalities
2. Standardize rates
3. Update the main CSV
4. Push the main CSV and a versioned CSV to this GitHub repository via and secondary script
Due to limitations, for this project, the user must manually update the AGOL hosted table with the main CSV to update the dashboard. See **docs/fully_automated_workflow.md** for instructions on how to fully automate the workflow.

### 7. ArcGIS Online Dashboard
The ```/docs/arcgis_dashboard_setup.md``` file describes:
* Publishing municipality boundaries
* Creating the initial hosted table from the CSV
* Targeting the hosted table, list, and map
* Update instructions for each new CSV upload
These instructions do not include information for specific dashboard formatting, including colors, element sizing, etc., due to personal preference and monitor size differences

### 8. Project Limitations
* Some water rates are in the form of scanned-image PDFs, which were found to require Optical Character Recognition (OCR) software. OCR was not included in this project due to the system-level dependency required, which would significantly reduce this project's replicability.
* Updating the ArcGIS Dashboard's hosted table requires manual action at present due to dual-factor authentication (2FA) and AGOL role limitations. If you do not face these same limitations, see **docs/fully_automated_workflow.md** for instructions on how to fully automate the workflow.
* Extensive website redesigns may temporarily break scrapers. Logic and logging are included within the primary scraper script to assist with determining which scrapers encountered an issue so that you may identify and fix any potential issues caused by website updates.

### 9. License
See LICENSE.md file

### 10. Contact Information
Jacob Shepherd
Department of Geography
Oklahoma State University
Jacob.Shepherd@okstate.edu
