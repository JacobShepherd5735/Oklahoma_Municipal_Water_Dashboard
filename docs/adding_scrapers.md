# Extending the Existing Scraper Script

The scraper script is designed so that adding additional scrapers is straightforward. Below are step-by-step instructions to add an additional scraper:

**Note:** "new_municipality" is a placeholder name throughout these instructions. Please remember to replace this with the actual name of the municipality you are wishing to scrape.

1. In `class WaterRateScraper`, for each additional scraper, you must add:
  - A unique municipality ID under `self.municipality_ids`
  - The municipality's name under `self.municipality_names`
  - A centroid representing that municipality under `self.municipality_coordinates`
2. Scroll down through the script. After reaching the last scraper, just before `def run_all_scrapers(self)`, you can create a new scraper:
  - Add `def scrape_new_municipality(self):`
  - Under this function is where you will add the unique scraper code to scrape that municipality's data. You can choose to continue the logging and try/except logic or opt out of it. If you do wish to extend those, you may reference an already-made scraper to see how to incorporate those into the new scraper function.
  - After developing the scraper code, make sure to include the following code block to reference the necessary information when writing the results to the CSV:
`lat, lon = self.municipality_coordinates["new_municipality"]`
`uid = self.municipality_ids["new_municipality"]`
`name = self.municipality_names["new_municipality"]`
3. In `def run_all_scrapers(self)`, locate the scrapers list and add `self.scrape_new_municipality` to the end of the list.

If you wish to test this new municipality without running the entire script, you can comment out `scraper.run_all_scrapers()` under `if __name__ == "__main__"` and replace it with `scraper.scrape_new_municipality()`
