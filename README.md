# School and Restaurant Data Pipeline

This repository contains automated data collection and extraction pipelines for two primary domains:
1. **School Data Collection** - Powered by OpenStreetMap's Nominatim and Overpass APIs to find and extract schools, address records, phone numbers, and website details.
2. **Restaurant Data Enrichment** - Processes county-wise Google Places datasets, queries DuckDuckGo HTML search for online ordering links (Uber Eats, DoorDash, Grubhub), and extracts menu information and pricing directly from official restaurant websites.

---

## Folder Structure

```text
school-data-pipeline/
├── school/
│   ├── school_scraper.py             # Automates OpenStreetMap querying and processing
│   ├── school_data.xlsx              # Input template containing sample Verified schools
│   └── school_data_completed.xlsx    # Final output matching template sheets & capitalized schemas
├── restaurant/
│   ├── restaurant_scraper.py         # Automates ZIP extraction, link search, and menu parsing
│   ├── missing_report.xlsx           # Missing menus and platforms link logs
│   └── output/
│       ├── menu_data.xlsx            # Extracted menu items
│       ├── ordering_links.xlsx       # Extracted ordering links
│       └── restaurant_data_completed.xlsx # Combined template-compliant spreadsheet
├── requirements.txt                  # Python dependencies
└── README.md                         # Setup and execution guide
```

---

## Setup Instructions

1. Ensure you have Python 3.10+ installed.
2. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

---

## Execution Instructions

### 1. School Scraper
To collect school information using Nominatim and OpenStreetMap's Overpass API:
```bash
python3 school/school_scraper.py
```
This script will:
- Load the template `school_data.xlsx` to retain existing data and sheet formatting.
- Query OpenStreetMap for school records in target locations ("New York", "Boston", "San Francisco").
- Save results to `school/school_data_completed.xlsx` in two worksheets:
  - **`Schools`**: Complete school profiles. Columns: `School`, `City`, `Category`, `Website`, `Description`, `Verification Status`, `Address`, `Phone`.
  - **`Missing Data Report`**: Records with missing details. Columns: `Location`, `School Name`, `Missing Field(s)`, `Reason`.

### 2. Restaurant Scraper
To enrich Google Places datasets with platform links and menus:
```bash
python3 restaurant/restaurant_scraper.py
```
*Note: Drop county-wise Google Places ZIP files in the `restaurant/` directory before running. If no ZIP files are present, the script will use built-in sample records (Starbucks & Haute Coffee) to demonstrate formatting and validation.*

This script will:
- Extract ZIP files, find and parse internal CSV/JSON datasets.
- Search DuckDuckGo HTML queries for Uber Eats, DoorDash, and Grubhub links.
- Scrape menu items (Name, Description, Price) from official restaurant websites via heuristic HTML pattern parsing.
- Perform HTTP HEAD/GET checks to validate that search links are active.
- Write standard separate sheets:
  - `restaurant/output/menu_data.xlsx`
  - `restaurant/output/ordering_links.xlsx`
  - `restaurant/missing_report.xlsx`
- Generate a unified `restaurant/output/restaurant_data_completed.xlsx` containing:
  - **`Menu Sheet`**: columns `Shop Name`, `Shop Code`, `Name`, `Description`, `Price`
  - **`External Shop Links Sheet`**: columns `Shop Name`, `Shop Code`, `Ubareats Links`, `Doordash Links`

---

## Output Schemas

### School Pipeline — `school_data_completed.xlsx`
| Sheet | Columns |
|-------|---------|
| Schools | School, City, Category, Website, Description, Verification Status, Address, Phone |
| Missing Data Report | Location, School Name, Missing Field(s), Reason |

### Restaurant Pipeline — `restaurant_data_completed.xlsx`
| Sheet | Columns |
|-------|---------|
| Menu Sheet | Shop Name, Shop Code, Name, Description, Price |
| External Shop Links Sheet | Shop Name, Shop Code, Ubareats Links, Doordash Links |

---

## Data Sources
- OpenStreetMap Nominatim (geocoding) and Overpass API (school discovery)
- DuckDuckGo HTML search (automated platform link lookup)
- Official restaurant websites (heuristic menu scraping)

## Notes
- No fabricated or estimated data
- All URLs are validated before inclusion
- Duplicates are removed at all output stages
- Rate limiting delays are built in to respect public API fair-use policies
