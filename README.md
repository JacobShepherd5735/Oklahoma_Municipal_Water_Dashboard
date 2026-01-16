# Oklahoma Municipal Water Rates Dashboard
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
/scripts/
/data/
/docs/
README.md
requirements.txt
```

### 3. Features
* Web scraping with support for HTML, PDF, and JavaScript-rendered water rates
* Standardized monthly water cost calculation (assuming 6,000 gallons used per month)
* CSV output for use in the project's ArcGIS Dashboard and for tracking historical water rates
* Automation using Windows Task Scheduler

### 4. Installation
```
python -m venv venv # replace first "venv" with desired virtual environment name
```
