import pandas as pd
import requests
import time
import os

def get_schools_in_location(location_name):
    """
    Uses OpenStreetMap's Overpass API to find schools in a given location.
    """
    print(f"Searching for schools in {location_name}...")
    
    # Nominatim API to get area id for the location
    nominatim_url = f"https://nominatim.openstreetmap.org/search.php?q={location_name}&format=jsonv2"
    headers = {'User-Agent': 'SchoolDataCollector/1.0'}
    
    try:
        response = requests.get(nominatim_url, headers=headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            print(f"Location not found: {location_name}")
            return []
            
        # Get the first match
        area_id = int(data[0]['osm_id']) + 3600000000
        
        # Overpass API to get schools
        overpass_url = "http://overpass-api.de/api/interpreter"
        overpass_query = f"""
        [out:json][timeout:25];
        area({area_id})->.searchArea;
        (
          node["amenity"="school"](area.searchArea);
          way["amenity"="school"](area.searchArea);
          relation["amenity"="school"](area.searchArea);
        );
        out center;
        """
        
        resp = requests.post(overpass_url, data={'data': overpass_query}, headers={'User-Agent': 'SchoolDataCollector/1.0'})
        resp.raise_for_status()
        elements = resp.json().get('elements', [])
        
        schools = []
        for el in elements:
            tags = el.get('tags', {})
            name = tags.get('name')
            if not name:
                continue
                
            # Extract fields
            website = tags.get('website', '')
            phone = tags.get('phone', tags.get('contact:phone', ''))
            
            # Construct address
            addr_housenumber = tags.get('addr:housenumber', '')
            addr_street = tags.get('addr:street', '')
            addr_city = tags.get('addr:city', location_name)
            addr_postcode = tags.get('addr:postcode', '')
            
            address_parts = [p for p in [addr_housenumber, addr_street, addr_city, addr_postcode] if p]
            address = ", ".join(address_parts)
            
            description = tags.get('description', '')
            
            schools.append({
                'School': name,
                'city': addr_city,
                'category': 'Schools',
                'website': website,
                'description': description,
                'verification_status': 'Unverified',
                'address': address,
                'phone': phone
            })
            
        return schools
        
    except Exception as e:
        print(f"Error processing {location_name}: {e}")
        return []

def main():
    # Base directory is the current directory where the script is located
    base_dir = os.path.dirname(os.path.abspath(__file__))
    template_path = os.path.join(base_dir, "school_data.xlsx")
    output_path = os.path.join(base_dir, "school_data_completed.xlsx")
    
    # List of locations to process
    locations = ["New York", "Boston", "San Francisco"]
    
    all_schools = []
    missing_data_report = []
    
    # Load template data to retain it
    df_template_schools = pd.DataFrame()
    df_template_missing = pd.DataFrame()
    
    if os.path.exists(template_path):
        print(f"Loading template from {template_path}...")
        try:
            df_template_schools = pd.read_excel(template_path, sheet_name='Schools')
            print(f"Loaded {len(df_template_schools)} existing schools from template.")
        except Exception as e:
            print(f"Warning: Could not read 'Schools' sheet from template: {e}")
            
        try:
            df_template_missing = pd.read_excel(template_path, sheet_name='Missing Data Report')
            print(f"Loaded {len(df_template_missing)} existing missing report entries.")
        except Exception as e:
            print(f"Warning: Could not read 'Missing Data Report' sheet from template: {e}")
    else:
        print(f"Warning: Template file not found at {template_path}. Output will only contain newly collected data.")
    
    for loc in locations:
        schools = get_schools_in_location(loc)
        
        if not schools:
            missing_data_report.append({
                'Location': loc,
                'School Name': 'N/A',
                'Missing Field(s)': 'All',
                'Reason': 'No schools found for location or location not resolved.'
            })
            continue
            
        # We will only take a subset to avoid massive files during this assignment
        for school in schools[:10]: # Limiting to 10 per location for demonstration
            # Check for missing fields
            missing_fields = []
            if not school['website']: missing_fields.append('Website')
            if not school['phone']: missing_fields.append('Phone')
            if not school['address']: missing_fields.append('Address')
            
            if missing_fields:
                missing_data_report.append({
                    'Location': loc,
                    'School Name': school['School'],
                    'Missing Field(s)': ', '.join(missing_fields),
                    'Reason': 'Data not provided by OpenStreetMap'
                })
            
            # Map collected data to exact template schema fields
            all_schools.append({
                'School': school['School'],
                'City': school['city'],
                'Category': 'Private Schools' if 'private' in school['School'].lower() else ('Public Schools' if 'public' in school['School'].lower() or 'high school' in school['School'].lower() else 'Schools'),
                'Website': school['website'],
                'Description': school['description'] if school['description'] else f"School in {school['city']}",
                'Verification Status': 'Verified' if school['website'] and school['phone'] else 'Unverified',
                'Address': school['address'],
                'Phone': school['phone']
            })
            
        # Sleep to avoid hitting rate limits on public APIs
        time.sleep(2)
        
    # Convert newly scraped data to DataFrames
    df_scraped_schools = pd.DataFrame(all_schools)
    df_new_missing = pd.DataFrame(missing_data_report)
    
    # Merge template data and scraped data
    if not df_template_schools.empty:
        if not df_scraped_schools.empty:
            df_final_schools = pd.concat([df_template_schools, df_scraped_schools], ignore_index=True)
        else:
            df_final_schools = df_template_schools
    else:
        df_final_schools = df_scraped_schools
        
    if not df_template_missing.empty:
        if not df_new_missing.empty:
            df_final_missing = pd.concat([df_template_missing, df_new_missing], ignore_index=True)
        else:
            df_final_missing = df_template_missing
    else:
        df_final_missing = df_new_missing
        
    # Standardize columns and deduplicate
    cols_schools = ['School', 'City', 'Category', 'Website', 'Description', 'Verification Status', 'Address', 'Phone']
    if not df_final_schools.empty:
        # Standardize column naming and fill/reindex
        df_final_schools = df_final_schools.reindex(columns=cols_schools)
        # Drop duplicates based on School name and City
        df_final_schools = df_final_schools.drop_duplicates(subset=['School', 'City'], keep='first')
    else:
        df_final_schools = pd.DataFrame(columns=cols_schools)
        
    cols_missing = ['Location', 'School Name', 'Missing Field(s)', 'Reason']
    if not df_final_missing.empty:
        df_final_missing = df_final_missing.reindex(columns=cols_missing)
        df_final_missing = df_final_missing.drop_duplicates(subset=['Location', 'School Name', 'Missing Field(s)'], keep='first')
    else:
        df_final_missing = pd.DataFrame(columns=cols_missing)
        
    # Write both sheets back to school_data_completed.xlsx
    try:
        with pd.ExcelWriter(output_path, engine='openpyxl') as writer:
            df_final_schools.to_excel(writer, sheet_name='Schools', index=False)
            df_final_missing.to_excel(writer, sheet_name='Missing Data Report', index=False)
        print(f"Saved {len(df_final_schools)} schools to {output_path} (sheet: Schools)")
        print(f"Saved {len(df_final_missing)} missing report items to {output_path} (sheet: Missing Data Report)")
    except Exception as e:
        print(f"Error saving to Excel: {e}")


if __name__ == "__main__":
    main()
