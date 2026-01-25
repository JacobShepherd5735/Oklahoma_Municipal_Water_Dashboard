# Data Schema and Field Definitions

This dataset contains time-stamped residential water rate data collected from municipal sources across Oklahoma. Each row represents a single rate component associated with a municipality at the time of collection. The schema is consistent across both the primary CSV (```water_rates.csv```) and all versioned historical CSV files.


| Field Name | Data Type | Description |
|-----------|-----------|-------------|
| Timestamp | Date | Date the rate was collected |
| ID | Integer | Unique municipality identifier |
| Name | Text | Municipality name |
| Latitude | Float | Approximate centroid coordinate |
| Longitude | Float | Approximate centroid coordinate |
| Category | Text | Type of rate (base, volume, etc.) |
| Type | Text | Rate subcategory (meter size, volumetric tier, etc.) |
| Amount | Text | Cost in USD |
| Standardized Rate (6,000 Gallons / Month) | Float | Estimated monthly cost for 6,000 gallons of water used |
| Standardized Rate (Dashboard Widget) | Float | Same as previous standardized rate but lacking formatting to be used with ArcGIS Dashboard Widgets |

## Timestamp
Records the date the data were scraped. This field enables temporal tracking of rate changes and historical analysis opportunities.

## ID
A unique numeric identifier used to link tabular data to municipal boundary geometries in ArcGIS Online. This field serves as the primary join key.

## Category and Type
These fields capture the structure of municipal rate systems, which vary widely between municipalities. The Category field indicates the general type of rate (e.g., base charge or volumetric rate), while Type provides additional detail, such as meter size or usage tier.

## Standardized Rate (6,000 Gallons / Month)
This field represents an estimated monthly water cost assuming 6,000 gallons of water used per month, an amount used throughout several water-related studies referenced for the literature review for this project. This value is intended to make comparing the cost of water across municipalities easier, as several factors make such comparisons traditionally difficult. Neither sewer nor stormwater costs are included in this value. Rate structures vary widely, and simplifications were necessary to enable comparison. Users should interpret standardized values as estimates rather than exact household costs.

## Standardized Rate (Dashboard Widget)
This field contains the same standardized value as the formatted standardized rate field, but is stored as a numeric value without currency symbols. This allows the field to be used in ArcGIS Dashboard indicators and charts.

## Additional Notes
A single municipality may be represented by multiple rows within the dataset, each corresponding to a distinct rate component. The standardized rate field, however, appears only once per municipality per collection date. 

Null values indicate that a rate component does not apply to a given municipality or that a value was not scraped at the time the scraper was initialized.
