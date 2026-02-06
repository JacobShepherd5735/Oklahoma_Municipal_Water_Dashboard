# ArcGIS Dashboard Overview

This document provides a brief, general overview of the core components used in the ArcGIS Dashboard for this project and how they relate to one another. It is intended as an architectural reference rather than a step-by-step configuration guide.

---

## Dashboard Purpose

The dashboard visualizes municipal residential water rate data across Oklahoma, allowing users to explore spatial patterns and observe changes in rates over time. All data displayed in the dashboard originates from externally collected and maintained datasets.

---

## Core Components

The dashboard is built from three primary ArcGIS Online components:

- A Web Map  
- A Hosted Feature Layer (municipal boundaries)  
- A Hosted Table (water rate data)

---

## Hosted Feature Layer

The hosted feature layer contains polygon geometries representing municipal boundaries. Each feature corresponds to a single municipality and includes a unique identifier field (`unique_id`).

Primary roles:
- Provides the spatial context for the dashboard
- Drives map-based interaction and filtering

---

## Hosted Table

The hosted table stores time-stamped residential water rate data. Unlike the feature layer, the table contains no geometry and includes multiple records per municipality to support temporal analysis.

Primary roles:
- Stores historical and current rate observations
- Serves as the data source for charts, indicators, and time-series elements

---

## Web Map

The web map bridges the gap between the hosted feature layer and hosted table. It is used as the primary data source for the dashboard map element and provides the interaction context for other widgets.

Primary roles:
- Manages layer relationships
- Enables cross-widget filtering through map interactions

---

## Dashboard Behavior

Dashboard elements reference either the web map or the hosted table, depending on their purpose:

- Map elements reference the web map
- Charts and indicators reference the hosted table

This structure allows the dashboard to support both spatial exploration and time-series analysis while maintaining a clear separation of responsibilities.

---

## Update Philosophy

Under normal operations, the dashboard is designed so that data updates occur at the table level. When the hosted table is updated with new records, the dashboard reflects those changes without requiring modifications to the feature layer or web map.

To update the data, the easiest method is to overwrite the hosted table with the most recent version of the water_rates.csv file. The process of doing this automatically is described in `docs/fully_automated_workflow.md`. To update the table manually in ArcGIS Online:
* Select the hosted table from your contents.
* In the "Overview" tab, click the "Update data" button.
* Select "Overwrite entire feature layer" from the options presented.
* Search for and select the most recently run water_rates.csv file (do not select a versioned (dated) csv as this could cause issues with certain indicators).
* The overwrite should occur automatically after this step. Confirm by reviewing the hosted table and looking for the newly added data.
* Confirm within the dashboard that any indicators and charts accepted the overwrite. These elements can be finicky, and even though no schema change occurred, they could still lose field name formatting or forget which field to reference.

The number of municipalities displayed and studied can be expanded on, however. This requires changes to the hosted feature layer, ideally appending new municipality polygon geometries via ArcGIS Pro. This process is straightforward so long as the data schema within your feature classes is maintained.

---

## Scope of This Document

This document does not contain:
- Styling and layout decisions
- Widget-specific configuration details
- Analytical expressions and calculations

These topics depend on user preference and are not needed to understand the core structure of the dashboard.
