import os
import csv
import json
import logging
import certifi
import requests
import pdfplumber
from datetime import datetime
from bs4 import BeautifulSoup

os.environ["SSL_CERT_FILE"] = certifi.where()

class WaterRateScraper:
    def __init__(self, output_file="water_rates.csv"):
        self.output_file = output_file

        run_suffix = datetime.now().strftime("%B%Y")
        self.run_output_file = f"water_rates_{run_suffix}.csv"

        logging.basicConfig(
            filename="scraper.log",
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s"
        )

        self.logger = logging.getLogger("WaterRateScraper")

        # Municipality data
        self.municipality_ids = {
            "Oklahoma City": 1, 
            "Tulsa": 2, 
            "Stillwater": 3, 
            "Altus": 4, 
            "Guymon": 5, 
            "Broken Bow": 6, 
            "Broken Arrow": 7, 
            "Edmond": 8, 
            "Norman": 9, 
            "Pryor": 10, 
            "Piedmont": 11, 
            "Enid": 12, 
            "Muskogee": 13, 
            "McAlester": 14, 
            "Clinton": 15, 
        }

        self.municipality_names = {
            "Oklahoma City": "Oklahoma City",
            "Tulsa": "Tulsa",
            "Stillwater": "Stillwater",
            "Altus": "Altus",
            "Guymon": "Guymon",
            "Broken Bow": "Broken Bow",
            "Broken Arrow": "Broken Arrow",
            "Edmond": "Edmond",
            "Norman": "Norman",
            "Pryor": "Pryor",
            "Piedmont": "Piedmont",
            "Enid": "Enid",
            "Muskogee": "Muskogee",
            "McAlester": "McAlester",
            "Clinton": "Clinton",
        }

        # All of these coordinates represent either city hall locations or "city of cityname" municipal services locations
        self.municipality_coordinates = {
            "Oklahoma City": (35.46755, -97.52065),
            "Tulsa": (36.15518, -95.98954),
            "Stillwater": (36.11393, -97.05681),
            "Altus": (34.63305, -99.33469),
            "Guymon": (36.68258, -101.48171),
            "Broken Bow": (34.02916, -94.73822),
            "Broken Arrow": (36.05106, -95.78998),
            "Edmond": (35.65488, -97.48011),
            "Norman": (35.22179, -97.44702),
            "Pryor": (36.30797, -95.31454),
            "Piedmont": (35.65240, -97.74925),
            "Enid": (36.39054, -97.88309),
            "Muskogee": (35.74853, -95.37151),
            "McAlester": (34.93390, -95.76814),
            "Clinton": (35.51578, -98.96539),
        }

    # Helpers

    def get_timestamp(self):
        return datetime.now().strftime("%m-%d-%Y")

    def dollar_to_float(self, text):
        if not text:
            return 0.0
        return float(text.replace("$", "").replace(",", "").strip())

    def write_to_csv(self, unique_id, name, latitude, longitude, category, type_label, amount, standard_rate, standard_rate_clean):
        # Append a row to the main CSV and the run-specific CSV.
        try:
            header = [
                "Timestamp", "ID", "Name", "Latitude", "Longitude",
                "Category", "Type", "Amount",
                "Standardized Rate (6,000 Gallons / Month)",
                "Standardized Rate (Dashboard Widget)"
            ]

            if type_label is not None:
                type_label = (str(type_label)
                            .replace("¾", "3/4")
                            .replace("–", "-"))

            row = [
                self.get_timestamp(),
                unique_id, name, latitude, longitude,
                category, type_label,
                amount, standard_rate, standard_rate_clean
            ]

            for filename in [self.output_file, self.run_output_file]:
                file_exists = os.path.isfile(filename)

                with open(filename, "a", newline="", encoding="utf-8") as f:
                    writer = csv.writer(f)
                    if not file_exists:
                        writer.writerow(header)
                    writer.writerow(row)

            self.logger.info(
                f"Wrote: {name} | {category} | {type_label}"
            )

        except Exception as e:
            self.logger.error(f"CSV write failed: {e}", exc_info=True)


    # Oklahoma City scraper

    def scrape_okc(self):
        try:
            self.logger.info("Starting Oklahoma City scraper...")
            url = "https://www.okc.gov/Services/Water-Trash-Recycling/Pay-Bill/Utilities-Rates-Fees"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            base_charges_water = {}
            for meter_size in ['5/8"', '3/4"', '1"']:
                cell = soup.find("td", string=lambda text: text and meter_size in text)
                if cell:
                    row = cell.find_parent("tr")
                    price_cell = row.find_all("td")[3]
                    price_text = price_cell.get_text(strip=True)
                    base_charges_water[meter_size] = price_text.strip() if price_text else None

            volume_rates_water = {}
            ranges = ["0-2,000", "2,001-10,000", "10,0001-25,000", "Above 25,000"]
            for range_label in ranges:
                cell = soup.find("td", string=lambda text: text and range_label in text)
                if cell:
                    row = cell.find_parent("tr")
                    price_cell = row.find_all("td")[3]
                    price_text = price_cell.get_text(strip=True)
                    volume_rates_water[range_label] = price_text if "$" in price_text else None

            lat, lon = self.municipality_coordinates["Oklahoma City"]
            uid = self.municipality_ids["Oklahoma City"]
            name = self.municipality_names["Oklahoma City"]

            base_charge = self.dollar_to_float(base_charges_water.get('5/8"', 0))
            rate_0_2k = self.dollar_to_float(volume_rates_water.get("0-2,000", 0))
            rate_2k_10k = self.dollar_to_float(volume_rates_water.get("2,001-10,000", 0))
            final_standard = base_charge + (2 * rate_0_2k) + (4 * rate_2k_10k)
            standard_display = f"${final_standard:.2f}"

            for meter_size, amt in base_charges_water.items():
                write_std = standard_display if meter_size == '5/8"' else ""
                write_std_clean = final_standard if meter_size == '5/8"' else ""
                self.write_to_csv(uid, name, lat, lon,
                                  "Monthly Meter Base Charge",
                                  f"{meter_size} meter", amt,
                                  write_std, write_std_clean)

            for range_label, amt in volume_rates_water.items():
                self.write_to_csv(uid, name, lat, lon,
                                  "Volume Rate (per 1,000 gallons)",
                                  f"{range_label} gallons", amt,
                                  "", "")

            self.logger.info("Oklahoma City scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Oklahoma City scraper failed: {e}")

    # Tulsa scraper
    # Hardcoded data; Tulsa updates rates yearly on October 1st

    def scrape_tulsa(self):
        try:
            self.logger.info("Starting Tulsa scraper...")

            monthly_minimum = {
                '3/4" meter': 7.36,
                '1" meter': 10.57,
                '1-1/2" meter': 16.68
            }

            quantity_charge = {
                'Single Family Residential': 4.57
            }

            lat, lon = self.municipality_coordinates["Tulsa"]
            uid = self.municipality_ids["Tulsa"]
            name = self.municipality_names["Tulsa"]

            base_charge = monthly_minimum['3/4" meter']
            volume = quantity_charge['Single Family Residential']

            final_standard = base_charge + (volume * 6)
            standard_display = f"${final_standard:.2f}"

            for meter_size, rate in monthly_minimum.items():
                write_std = standard_display if meter_size == '3/4" meter' else ""
                write_std_clean = final_standard if meter_size == '3/4" meter' else ""
                self.write_to_csv(uid, name, lat, lon,
                                  "Monthly Meter Base Charge",
                                  meter_size, f"${rate}",
                                  write_std, write_std_clean)

            for usage_label, rate in quantity_charge.items():
                self.write_to_csv(uid, name, lat, lon,
                                  "Volume Rate (per 1,000 gallons)",
                                  usage_label, f"${rate}",
                                  "", "")

            self.logger.info("Tulsa scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Tulsa scraper failed: {e}")

    # Stillwater scraper

    def scrape_stillwater(self, pdf_path):
        try:
            self.logger.info("Starting Stillwater scraper...")

            with pdfplumber.open(pdf_path) as pdf:
                page = pdf.pages[0]
                text = page.extract_text()

            if not text:
                raise ValueError("Stillwater PDF text extraction returned None")

            lines = text.splitlines()

            monthly_minimum = {}
            start_tag = "Monthly minimum"
            meter_sizes = ["3/4 inch", "1 inch", "1 1/2 inches"]
            capturing = False

            for line in lines:
                if start_tag in line:
                    capturing = True
                    continue
                if capturing:
                    for size in meter_sizes:
                        if size in line and "$" in line:
                            meter, amount = line.split("$", 1)
                            monthly_minimum[size] = amount.strip()

            volume_data = {}
            sections = [
                ("¾ inch meter", "1 inch meter", "3/4 inch meter"),
                ("1 inch meter", "1 1/2 inches or larger meter", "1 inch meter")
            ]

            for start_volume, stop_volume, meter_size in sections:
                capturing = False
                captured_lines = []
                for line in lines:
                    if start_volume in line:
                        capturing = True
                        line = line.replace(start_volume, "").strip()
                        if line:
                            captured_lines.append(line)
                        continue
                    if stop_volume in line and capturing:
                        break
                    if capturing:
                        captured_lines.append(line.strip())

                for line in captured_lines:
                    if "$" in line and ":" in line:
                        dollar, range_text = line.split(":", 1)
                        rate = dollar.strip().replace("$", "")
                        usage_range = range_text.strip()

                        if meter_size not in volume_data:
                            volume_data[meter_size] = {}
                        volume_data[meter_size][usage_range] = rate

            for line in lines:
                if "1 1/2 inches or larger meter" in line and "$" in line:
                    rate = line.split("$")[1].strip()
                    volume_data["1 1/2 inches or larger meter"] = {"per 1,000 gallons": rate}

            lat, lon = self.municipality_coordinates["Stillwater"]
            uid = self.municipality_ids["Stillwater"]
            name = self.municipality_names["Stillwater"]

            base_charge = self.dollar_to_float(monthly_minimum.get("3/4 inch"))
            rate_0_5 = self.dollar_to_float(volume_data.get("3/4 inch meter", {}).get("up to 5,000 gallons", 0))
            rate_5_12 = self.dollar_to_float(volume_data.get("3/4 inch meter", {}).get("5,000 – 12,000 gallons", 0))

            final_standard = base_charge + (rate_0_5 * 5) + (rate_5_12 * 1)
            standard_display = f"${final_standard:.2f}"

            for size, rate in monthly_minimum.items():
                write_std = standard_display if size == "3/4 inch" else ""
                write_std_clean = final_standard if size == "3/4 inch" else ""
                self.write_to_csv(
                    uid, name, lat, lon,
                    "Monthly Meter Base Charge",
                    f"{size} meter", f"${rate}",
                    write_std, write_std_clean
                )

            for meter_size, ranges in volume_data.items():
                for usage_label, rate in ranges.items():
                    self.write_to_csv(
                        uid, name, lat, lon,
                        f"Volume Rate at {meter_size}",
                        usage_label, f"${rate}",
                        "", ""
                    )

            self.logger.info("Stillwater scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Stillwater scraper failed: {e}")

    # Altus scraper

    def scrape_altus(self):
        try:
            self.logger.info("Starting Altus scraper...")

            url = "https://www.altusok.gov/o/coa/page/utility-rates"
            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            nuxt_script = soup.find("script", {"id": "__NUXT_DATA__"})
            if not nuxt_script or not nuxt_script.string:
                raise ValueError("Nuxt data script not found or empty")

            nuxt_data = json.loads(nuxt_script.string)

            embedded_html_blocks = []

            def walk(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)
                elif isinstance(obj, str) and "Water Rates" in obj:
                    embedded_html_blocks.append(obj)

            walk(nuxt_data)

            if not embedded_html_blocks:
                raise ValueError("Water Rates HTML block not found in Nuxt data")

            embedded_html = embedded_html_blocks[0]

            embedded_soup = BeautifulSoup(embedded_html, "html.parser")
            text = embedded_soup.get_text("\n")

            lines = [l.strip() for l in text.splitlines() if l.strip()]

            base_rates = {}
            volume_rates = {}

            in_residential = False

            for line in lines:

                if "Residential Rates" in line:
                    in_residential = True
                    continue

                if any(x in line for x in ["Commercial Rates", "Outside City Limits"]):
                    break

                if not in_residential:
                    continue

                if "Customer Charge" in line and "$" in line:
                    base_rates["minimum"] = "$" + line.split("$")[1].split()[0]

                elif "0 – 2,000 Gallons" in line or "0-2,000 Gallons" in line:
                    volume_rates["0-2,000"] = "$0"

                elif "Over 2,000 Gallons" in line:
                    volume_rates["Over 2,000"] = "$" + line.split("$")[1].split()[0]

            if not base_rates or not volume_rates:
                raise ValueError("Residential water rates parsed but incomplete")

            lat, lon = self.municipality_coordinates["Altus"]
            uid = self.municipality_ids["Altus"]
            name = self.municipality_names["Altus"]

            base_charge = self.dollar_to_float(base_rates["minimum"])
            over_rate = self.dollar_to_float(volume_rates["Over 2,000"])
            final_standard = base_charge + (4 * over_rate)
            std_display = f"${final_standard:.2f}"

            self.write_to_csv(uid, name, lat, lon, "Monthly Minimum", 'Minimum Bill', base_rates['minimum'], std_display, final_standard)

            for tier, amt in volume_rates.items():
                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", tier, amt, "", "")

            self.logger.info("Altus scraper completed successfully.")

        except Exception as e:
            self.logger.exception(f"Altus scraper failed: {e}")

    # Guymon scraper

    def scrape_guymon(self):
        try:
            self.logger.info("Starting Guymon scraper (Nuxt final version)...")

            url = "https://www.guymonok.org/o/cog/page/drinking-water"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, "html.parser")

            nuxt_script = soup.find("script", {"id": "__NUXT_DATA__"})
            if not nuxt_script or not nuxt_script.string:
                raise ValueError("Nuxt data script not found")

            nuxt_data = json.loads(nuxt_script.string)

            embedded_tables = []

            def walk(obj):
                if isinstance(obj, dict):
                    for v in obj.values():
                        walk(v)
                elif isinstance(obj, list):
                    for v in obj:
                        walk(v)
                elif isinstance(obj, str) and "<table" in obj and "0-5 MG" in obj:
                    embedded_tables.append(obj)

            walk(nuxt_data)

            if not embedded_tables:
                raise ValueError("Residential water table not found in Nuxt data")

            embedded_soup = BeautifulSoup(embedded_tables[0], "html.parser")
            table = embedded_soup.find("table")

            rows = table.find_all("tr")

            target_tiers = [
                "0-5 MG",
                "6-20 MG",
                "21-35 MG",
                "36-50 MG",
                "51-100 MG",
                "all over 100"
            ]

            amounts = {}

            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]
                if len(cols) != 2:
                    continue

                usage, cost = cols

                if usage in target_tiers:
                    cleaned_cost = cost.replace(" per MG", "").strip()
                    amounts[usage] = cleaned_cost

            if not amounts:
                raise ValueError("No residential usage tiers parsed")

            lat, lon = self.municipality_coordinates["Guymon"]
            uid = self.municipality_ids["Guymon"]
            name = self.municipality_names["Guymon"]

            minimum_raw = amounts.get("0-5 MG", "0")
            tier_raw = amounts.get("6-20 MG", "0")

            minimum_charge = float(minimum_raw.replace("$", "").split()[0])
            tier_6_20 = float(tier_raw.replace("$", "").split()[0])

            final_standard = minimum_charge + tier_6_20
            standard_display = f"${final_standard:.2f}"

            for tier, cost in amounts.items():
                write_std = standard_display if tier == "0-5 MG" else ""
                write_std_clean = final_standard if tier == "0-5 MG" else ""

                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", tier, cost, write_std, write_std_clean)

            self.logger.info("Guymon scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Guymon scraper failed: {e}")

    # Broken Bow scraper

    def scrape_broken_bow(self):
        try:
            self.logger.info("Starting Broken Bow scraper...")
            url = "https://cityofbrokenbow.com/public-works-authority/"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            category_header = None
            for p in soup.find_all("p"):
                if "Residential/Commercial" in p.get_text():
                    category_header = p
                    break

            gallon_ranges = ["0-1,500", "1,501-2,500", "2,501-4,500", "4,501-6,500", "6,501+"]
            amount = {}

            if category_header:
                next_tags = category_header.find_next_siblings("p")[:5]
                for p_tag, type_label in zip(next_tags, gallon_ranges):
                    text = p_tag.get_text(strip=True)
                    if "$" in text:
                        dollar_index = text.find("$")
                        amt_text = text[dollar_index + 1:]
                        amt = "$"
                        for char in amt_text:
                            if char.isdigit() or char in [".", ","]:
                                amt += char
                            else:
                                break
                        amount[type_label] = amt

            lat, lon = self.municipality_coordinates["Broken Bow"]
            uid = self.municipality_ids["Broken Bow"]
            name = self.municipality_names["Broken Bow"]

            base = self.dollar_to_float(amount.get("0-1,500", 0))
            tier1 = self.dollar_to_float(amount.get("1,501-2,500", 0))
            tier2 = self.dollar_to_float(amount.get("2,501-4,500", 0))
            tier3 = self.dollar_to_float(amount.get("4,501-6,500", 0))
            final_standard = round(base + tier1 + (2 * tier2) + ((1500 / 2000) * tier3), 2)
            standard_display = f"${final_standard:.2f}"

            for range_label, amt in amount.items():
                write_std = standard_display if range_label == "0-1,500" else ""
                write_std_clean = final_standard if range_label == "0-1,500" else ""
                self.write_to_csv(uid, name, lat, lon,
                                  "Volume Rate (per 1,000 gallons)",
                                  f"{range_label} gallons", amt,
                                  write_std, write_std_clean)

            self.logger.info("Broken Bow scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Broken Bow scraper failed: {e}")

    # Broken Arrow scraper
    # Hardcoded data; Broken Arrow updates rates yearly on October 1st

    def scrape_broken_arrow(self):
        try:
            self.logger.info("Starting Broken Arrow scraper...")

            monthly_minimum = {
                '3/4" or less in size meter': 13.05,
                '1" meter': 14.25,
            }

            quantity_charge = {
                'Residential': 6.86
            }

            lat, lon = self.municipality_coordinates["Broken Arrow"]
            uid = self.municipality_ids["Broken Arrow"]
            name = self.municipality_names["Broken Arrow"]

            base_charge = monthly_minimum['3/4" or less in size meter']
            volume = quantity_charge['Residential']

            final_standard = base_charge + (volume * 6)
            standard_display = f"${final_standard:.2f}"

            for meter_size, rate in monthly_minimum.items():
                write_std = standard_display if meter_size == '3/4" or less in size meter' else ""
                write_std_clean = final_standard if meter_size == '3/4" or less in size meter' else ""
                self.write_to_csv(uid, name, lat, lon,
                                  "Monthly Meter Base Charge",
                                  meter_size, f"${rate}",
                                  write_std, write_std_clean)

            for usage_label, rate in quantity_charge.items():
                self.write_to_csv(uid, name, lat, lon,
                                  "Volume Rate (per 1,000 gallons)",
                                  usage_label, f"${rate}",
                                  "", "")

            self.logger.info("Broken Arrow scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Broken Arrow scraper failed: {e}")

    # Clinton scraper

    def scrape_clinton(self):
        try:
            self.logger.info("Starting Clinton scraper...")

            url = "https://clintonok.gov/utilities/utility-rates/"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            inside_header = soup.find("h3",string=lambda text: text and "Inside City Limits" in text)
            if not inside_header:
                raise ValueError("Inside City Limits header not found")

            rate_list = inside_header.find_next("ul")
            if not rate_list:
                raise ValueError("Rate list under Inside City Limits not found")

            items = [li.get_text(strip=True) for li in rate_list.find_all("li")]

            volume_rates = {}

            for item in items:
                if "$" not in item:
                    continue

                amount = "$" + item.split("$")[1].split()[0]

                if "first 2,000 gallons" in item:
                    volume_rates["0-2,000"] = amount
                elif "2,001 - 4,000" in item:
                    volume_rates["2,001-4,000"] = amount
                elif "4,001 - 14,000" in item:
                    volume_rates["4,001-14,000"] = amount
                elif "14,001 - 100,000" in item:
                    volume_rates["14,001-100,000"] = amount
                elif "100,001 - 500,000" in item:
                    volume_rates["100,001-500,000"] = amount
                elif "over 500,000" in item.lower():
                    volume_rates["Over 500,000"] = amount

            if not volume_rates:
                raise ValueError("No Inside City Limits volume rates parsed")

            lat, lon = self.municipality_coordinates["Clinton"]
            uid = self.municipality_ids["Clinton"]
            name = self.municipality_names["Clinton"]

            base_0_2k = self.dollar_to_float(volume_rates.get("0-2,000", 0))
            tier_2k_4k = self.dollar_to_float(volume_rates.get("2,001-4,000", 0))
            tier_4k_14k = self.dollar_to_float(volume_rates.get("4,001-14,000", 0))

            final_standard = base_0_2k + (2 * tier_2k_4k) + (2 * tier_4k_14k)
            standard_display = f"${final_standard:.2f}"

            for range_label, amt in volume_rates.items():
                write_std = standard_display if range_label == "0-2,000" else ""
                write_std_clean = final_standard if range_label == "0-2,000" else ""

                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", f"{range_label} gallons", amt, write_std, write_std_clean)

            self.logger.info("Clinton scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Clinton scraper failed: {e}")

    # McAlester scraper

    def scrape_mcalester(self):
        try:
            self.logger.info("Starting McAlester scraper...")

            url = "https://www.cityofmcalester.com/residents/utilities/utility_billing___collection/utility_rates.php"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            inside_header = None
            for span in soup.find_all("span", class_="Headline subheader"):
                if "Inside City Limits" in span.get_text():
                    inside_header = span
                    break

            if not inside_header:
                raise ValueError("Inside City Limits section not found")

            container = inside_header.parent
            full_text = container.get_text("\n", strip=True)

            inside_block = full_text.split("Inside City Limits", 1)[-1]
            inside_block = inside_block.split("Outside City Limits", 1)[0]

            lines = [l.strip() for l in inside_block.splitlines() if l.strip()]

            volume_rates = {}

            in_water = False
            for line in lines:
                if line.startswith("Water:"):
                    in_water = True
                    continue

                if line.startswith("Sewer:"):
                    break

                if not in_water:
                    continue

                if "gallons" in line.lower() and "cu ft" not in line.lower():
                    amount = "$" + line.split("$")[1].split()[0]

                    if "Up to" in line:
                        volume_rates["0-2,244"] = amount
                    elif "Over" in line:
                        volume_rates["Over 2,244"] = amount

            if not volume_rates:
                raise ValueError("No gallon-based water rates parsed")

            lat, lon = self.municipality_coordinates["McAlester"]
            uid = self.municipality_ids["McAlester"]
            name = self.municipality_names["McAlester"]

            tier_0_2244 = self.dollar_to_float(volume_rates["0-2,244"])
            over_rate = self.dollar_to_float(volume_rates["Over 2,244"])

            # 6000 gallons - 2244 = 3756 (also need to round here unlike in most scrapers)
            final_standard = tier_0_2244 + (3.756 * over_rate)
            final_standard_rounded = round(final_standard, 2)
            standard_display = f"${final_standard_rounded:.2f}"

            for tier, amt in volume_rates.items():
                write_std = standard_display if tier == "0-2,244" else ""
                write_std_clean = final_standard_rounded if tier == "0-2,244" else ""

                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", f"{tier} gallons", amt, write_std, write_std_clean)

            self.logger.info("McAlester scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"McAlester scraper failed: {e}")

    # Pryor scraper

    def scrape_pryor(self):
        try:
            self.logger.info("Starting Pryor scraper...")

            url = "https://mubpryor.org/resources/utility-rates/"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            water_header = soup.find("h4", string=lambda t: t and t.strip().upper() == "WATER")
            if not water_header:
                raise ValueError("WATER header not found")

            water_block = water_header.find_next("p")
            if not water_block:
                raise ValueError("CITY CUSTOMERS block not found")

            text = water_block.get_text("\n", strip=True)
            lines = [l.strip() for l in text.splitlines() if "$" in l]

            base_charge = None
            volume_rate = None

            for line in lines:
                if "minimum" in line.lower():
                    base_charge = "$" + line.split("$")[1].split()[0]
                elif "per 1,000" in line.lower():
                    volume_rate = "$" + line.split("$")[1].split()[0]

            if not base_charge or not volume_rate:
                raise ValueError("Failed to parse Pryor water rates")

            lat, lon = self.municipality_coordinates["Pryor"]
            uid = self.municipality_ids["Pryor"]
            name = self.municipality_names["Pryor"]

            base_val = self.dollar_to_float(base_charge)
            volume_val = self.dollar_to_float(volume_rate)

            final_standard = base_val + (4 * volume_val)
            standard_display = f"${final_standard:.2f}"

            self.write_to_csv(uid, name, lat, lon, "Monthly Base Charge", "Residential", base_charge, standard_display, final_standard)

            self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", "All additional usage", volume_rate, "", "")

            self.logger.info("Pryor scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Pryor scraper failed: {e}")
  
    # Edmond scraper
    def scrape_edmond(self, pdf_path):
        try:
            self.logger.info("Starting Edmond scraper...")

            target_index = 3 # Change to 4 after 10/1/26 run

            with pdfplumber.open(pdf_path) as pdf:
                text = pdf.pages[0].extract_text()

            lines = [line.strip() for line in text.split("\n")]

            def extract_value(label):
                for line in lines:
                    if line.startswith(label):
                        values = line.split()[-5:]
                        return values[target_index]
                return None

            base_raw = extract_value("5/8, 3/4, & Multi Family")
            vol_1_raw = extract_value("2,000 to 10,000")
            vol_2_raw = extract_value("11,000 to 20,000")
            vol_3_raw = extract_value("21,000 & over")

            if not all([base_raw, vol_1_raw, vol_2_raw, vol_3_raw]):
                raise ValueError("Failed to extract Edmond rates from PDF")

            base = self.dollar_to_float(base_raw)
            v1 = self.dollar_to_float(vol_1_raw)
            v2 = self.dollar_to_float(vol_2_raw)
            v3 = self.dollar_to_float(vol_3_raw)

            standardized = base + (5 * v1)
            standardized_display = f"${standardized:.2f}"

            lat, lon = self.municipality_coordinates["Edmond"]
            uid = self.municipality_ids["Edmond"]
            name = self.municipality_names["Edmond"]

            self.write_to_csv(uid, name, lat, lon, "Monthly Meter Base Charge", "5/8, 3/4, & Multi Family", f"${base_raw}", standardized_display, standardized)

            self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", "2,000 to 10,000 gallons", f"${vol_1_raw}", "", "")

            self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", "11,000 to 20,000 gallons", f"${vol_2_raw}", "", "")

            self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", "21,000 & over gallons", f"${vol_3_raw}", "", "")

            self.logger.info(f"Edmond scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Edmond scraper failed: {e}")

    # Muskogee scraper

    def scrape_muskogee(self):
        try:
            self.logger.info("Starting Muskogee scraper...")

            url = "https://www.muskogeeok.gov/departments/city_clerk/water_services/rates.php"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            volume_rates = {}
            volume_table = None

            for table in soup.find_all("table"):
                text = table.get_text()
                if (
                    "Next 1,600 Cubic Feet" in text
                    and "Over 40,000 Cubic Feet" in text
                    and "per 100 Cubic Feet" in text
                ):
                    volume_table = table
                    break

            if not volume_table:
                raise ValueError("Water volumetric rate table not found")

            rows = volume_table.find_all("tr")

            for row in rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]

                if not cols:
                    continue

                if "Outside City Limits" in cols[0]:
                    break

                if "Inside City Limits" in cols[0]:
                    continue

                if "Base Charge per Meter Size" in row.get_text():
                    continue

                if len(cols) >= 2 and "$" in cols[1]:
                    tier_label = cols[0]
                    rate = cols[1].split(" ")[0]  # Keep only "$6.29"
                    volume_rates[tier_label] = rate

            if not volume_rates:
                raise ValueError("No inside water volume rates parsed")

            base_charges = {}
            base_table = None

            for table in soup.find_all("table"):
                text = table.get_text()
                if "Meter Size in Inches" in text and "Inside City Base Charge" in text:
                    base_table = table
                    break

            if not base_table:
                raise ValueError("Base meter table not found")

            base_rows = base_table.find_all("tr")

            for row in base_rows:
                cols = [c.get_text(strip=True) for c in row.find_all("td")]

                if len(cols) < 3:
                    continue

                meter_size = (
                    cols[0]
                    .replace("”", '"')
                    .replace("“", '"')
                    .replace("″", '"')
                    .strip()
                )

                inside_charge = cols[1]

                if meter_size == '5/8"':
                    base_charges['5/8" meter'] = inside_charge

                elif meter_size == '1"':
                    base_charges['1" meter'] = inside_charge

            if not base_charges:
                raise ValueError("No Inside base meter charges parsed")

            gallons_to_cuft = 1 / 7.48052
            target_cuft = 6000 * gallons_to_cuft

            remaining = target_cuft
            total_volume_cost = 0

            cubic_foot_ranges = [
                "Next 100 Cubic Feet",
                "Next 100 Cubic Feet",
                "Next 1,600 Cubic Feet",
                "Next 4,000 Cubic Feet",
                "Next 4,000 Cubic Feet",
                "Next 10,000 Cubic Feet",
                "Next 20,000 Cubic Feet",
                "Over 40,000 Cubic Feet",
            ]

            tier_volumes = [100, 100, 1600, 4000, 4000, 10000, 20000]

            for tier_label, tier_size in zip(cubic_foot_ranges, tier_volumes):
                if tier_label not in volume_rates:
                    continue

                rate_per_100 = self.dollar_to_float(volume_rates[tier_label])
                rate_per_cuft = rate_per_100 / 100

                used = min(remaining, tier_size)
                total_volume_cost += rate_per_cuft * used
                remaining -= used

                if remaining <= 0:
                    break

            base_58 = self.dollar_to_float(base_charges.get('5/8" meter', 0))
            final_standard = round(base_58 + total_volume_cost, 2)
            standard_display = f"${final_standard:.2f}"

            lat, lon = self.municipality_coordinates["Muskogee"]
            uid = self.municipality_ids["Muskogee"]
            name = self.municipality_names["Muskogee"]

            for meter_size, amt in base_charges.items():
                write_std = standard_display if meter_size == '5/8" meter' else ""
                write_std_clean = final_standard if meter_size == '5/8" meter' else ""

                self.write_to_csv(uid, name, lat, lon, "Monthly Meter Base Charge", meter_size, amt, write_std, write_std_clean)

            for range_label, amt in volume_rates.items():
                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 100 cubic feet)", range_label, amt, "", "")

            self.logger.info("Muskogee scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Muskogee scraper failed: {e}")

    # Norman Scraper

    def scrape_norman(self):
        try:
            self.logger.info("Starting Norman scraper...")

            url = "https://www.normanok.gov/your-government/departments/finance/utility-rates-and-information"

            r = requests.get(url, timeout=30)
            r.raise_for_status()
            html = r.text

            soup = BeautifulSoup(html, "html.parser")

            residential_header = soup.find("em", string=lambda t: t and "Residential" in t)
            if not residential_header:
                raise ValueError("Residential section not found")

            rate_list = residential_header.find_next("ul")
            if not rate_list:
                raise ValueError("Residential rate list not found")

            items = [li.get_text(strip=True) for li in rate_list.find_all("li")]

            base_charge = None
            volume_rates = {}

            for item in items:
                if "Low Income" in item:
                        continue

                if "Base Fee per Unit" in item:
                    base_charge = "$" + item.split("$")[1].split()[0]

                elif "up to 5,000" in item:
                    volume_rates["0-5,000"] = "$" + item.split("$")[1].split()[0]

                elif "5,001 to 15,000" in item:
                    volume_rates["5,001-15,000"] = "$" + item.split("$")[1].split()[0]

                elif "15,001 to 20,000" in item:
                    volume_rates["15,001-20,000"] = "$" + item.split("$")[1].split()[0]

                elif "over 20,000" in item.lower():
                    volume_rates["Over 20,000"] = "$" + item.split("$")[1].split()[0]

            if not base_charge or not volume_rates:
                raise ValueError("Failed to parse Norman residential rates")

            lat, lon = self.municipality_coordinates["Norman"]
            uid = self.municipality_ids["Norman"]
            name = self.municipality_names["Norman"]

            base_val = self.dollar_to_float(base_charge)
            tier1 = self.dollar_to_float(volume_rates["0-5,000"])
            tier2 = self.dollar_to_float(volume_rates["5,001-15,000"])

            final_standard = base_val + (5 * tier1) + (1 * tier2)
            standard_display = f"${final_standard:.2f}"

            self.write_to_csv(uid, name, lat, lon, "Monthly Meter Base Charge", "Residential Base Fee", base_charge, standard_display, final_standard)

            for tier, amt in volume_rates.items():
                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", f"{tier} gallons", amt, "", "")

            self.logger.info("Norman scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Norman scraper failed: {e}")

    # Piedmont scraper
    def scrape_piedmont(self, pdf_path):
        try:
            self.logger.info("Starting Piedmont scraper...")

            with pdfplumber.open(pdf_path) as pdf:
                full_text = ""
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        full_text += text + "\n"

            if "WATER RATES" not in full_text:
                raise ValueError("WATER RATES section not found in PDF")

            water_block = full_text.split("WATER RATES", 1)[1]
            water_block = water_block.split("Sewer Rates", 1)[0]

            lines = [
                line.strip()
                for line in water_block.splitlines()
                if "$" in line
            ]

            volume_rates = {}

            for line in lines:
                parts = line.split("$")
                tier = parts[0].replace("gallons", "").strip()
                amount = "$" + parts[1].split()[0]
                volume_rates[tier] = amount

            if not volume_rates:
                raise ValueError("No volumetric water rates parsed")

            lat, lon = self.municipality_coordinates["Piedmont"]
            uid = self.municipality_ids["Piedmont"]
            name = self.municipality_names["Piedmont"]

            tier_0_2k = self.dollar_to_float(volume_rates.get("0-2,000"))
            tier_2k_10k = self.dollar_to_float(volume_rates.get("2,001-10,000"))

            final_standard = tier_0_2k + (4 * tier_2k_10k)
            standard_display = f"${final_standard:.2f}"

            for tier, amt in volume_rates.items():
                write_std = standard_display if tier == "0-2,000" else ""
                write_std_clean = final_standard if tier == "0-2,000" else ""

                self.write_to_csv(uid, name, lat, lon, "Volume Rate (per 1,000 gallons)", f"{tier} gallons", amt, write_std, write_std_clean)

            self.logger.info("Piedmont scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Piedmont scraper failed: {e}")

    def scrape_enid(self):
    # Hardcoded data; Enid updates rates yearly around January 1st
        try:
            self.logger.info("Starting Enid scraper...")

            monthly_minimum = {
                'Base Rate': 13.28,
            }

            quantity_charge = {
                'From 2,000 Gallons': 8.67
            }

            lat, lon = self.municipality_coordinates["Enid"]
            uid = self.municipality_ids["Enid"]
            name = self.municipality_names["Enid"]

            base_charge = monthly_minimum['Base Rate']
            volume = quantity_charge['From 2,000 Gallons']

            final_standard = base_charge + (volume * 4)
            standard_display = f"${final_standard:.2f}"

            for meter_size, rate in monthly_minimum.items():
                write_std = standard_display if meter_size == 'Base Rate' else ""
                write_std_clean = final_standard if meter_size == 'Base Rate' else ""
                self.write_to_csv(uid, name, lat, lon,
                                  "Monthly Meter Base Charge",
                                  meter_size, f"${rate}",
                                  write_std, write_std_clean)

            for usage_label, rate in quantity_charge.items():
                self.write_to_csv(uid, name, lat, lon,
                                  "Volume Rate (per 1,000 gallons)",
                                  usage_label, f"${rate}",
                                  "", "")

            self.logger.info("Enid scraper finished successfully.")

        except Exception as e:
            self.logger.exception(f"Enid scraper failed: {e}")
        print()

    # Orchestrator

    def run_all_scrapers(self):
        self.logger.info("Starting Scraper Script.")

        scrapers = [
            self.scrape_okc,
            self.scrape_tulsa,
            lambda: self.scrape_stillwater("Stillwater_PDF.pdf"),
            self.scrape_altus,
            self.scrape_guymon,
            self.scrape_broken_bow,
            self.scrape_broken_arrow,
            lambda: self.scrape_edmond("Edmond_PDF.pdf"),
            self.scrape_norman,
            self.scrape_pryor,
            lambda: self.scrape_piedmont("Piedmont_PDF.pdf"),
            self.scrape_enid,
            self.scrape_muskogee,
            self.scrape_mcalester,
            self.scrape_clinton,
        ]

        for scraper in scrapers:
            try:
                scraper()
            except Exception as e:
                self.logger.exception(f"Unhandled exception in {scraper.__name__}: {e}")

        self.logger.info("Scraper Run Completed.")

# Main
if __name__ == "__main__":
    scraper = WaterRateScraper()
    scraper.run_all_scrapers()