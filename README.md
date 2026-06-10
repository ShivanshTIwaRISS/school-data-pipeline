# School Data Collection Pipeline

Automated pipeline to collect, validate, and export school information to Excel.

## Files
- `school_scraper.py` — Main automation script (web scraping + data collection)
- `school_data.xlsx` — Final output with verified school records
- `school_data_collected.xlsx` — Raw collected dataset
- `missing_data_report.xlsx` — Records that could not be verified
- `requirements.txt` — Python dependencies

## Setup & Execution

### Install dependencies
pip install -r requirements.txt

### Run the pipeline
python school_scraper.py

## Output Columns
School | City | Category | Website | Description | Verification Status | Address | Phone

## Data Sources
- Verified public school directories
- Official school websites
- OpenStreetMap Nominatim for address validation

## Notes
- No fabricated or estimated data
- Phone numbers formatted as (XXX) XXX-XXXX
- Websites stored without https:// or www. prefix
