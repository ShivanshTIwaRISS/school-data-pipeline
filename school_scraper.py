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
    # List of locations to process
    locations = ["New York", "Boston", "San Francisco"] # Example locations
    
    all_schools = []
    missing_data_report = []
    
    for loc in locations:
        schools = get_schools_in_location(loc)
        
        if not schools:
            missing_data_report.append({
                'Location Name': loc,
                'School Name': 'N/A',
                'Missing Field(s)': 'All',
                'Reason': 'No schools found for location or location not resolved.'
            })
            continue
            
        # We will only take a subset to avoid massive files during this assignment
        for school in schools[:10]: # Limiting to 10 per location for demonstration
            # Check for missing fields
            missing_fields = []
            if not school['website']: missing_fields.append('website')
            if not school['phone']: missing_fields.append('phone')
            if not school['address']: missing_fields.append('address')
            
            if missing_fields:
                missing_data_report.append({
                    'Location Name': loc,
                    'School Name': school['School'],
                    'Missing Field(s)': ', '.join(missing_fields),
                    'Reason': 'Data not provided by OpenStreetMap'
                })
            
            all_schools.append(school)
            
        # Sleep to avoid hitting rate limits on public APIs
        time.sleep(2)
        
    # Convert to DataFrames
    df_schools = pd.DataFrame(all_schools)
    df_missing = pd.DataFrame(missing_data_report)
    
    # Reorder columns to match template
    cols = ['School', 'city', 'category', 'website', 'description', 'verification_status', 'address', 'phone']
    if not df_schools.empty:
        df_schools = df_schools[cols]
    
    # Save to Excel
    output_file = "school_data_collected.xlsx"
    df_schools.to_excel(output_file, index=False)
    print(f"Saved {len(df_schools)} records to {output_file}")
    
    missing_file = "missing_data_report.xlsx"
    df_missing.to_excel(missing_file, index=False)
    print(f"Saved missing data report to {missing_file}")

if __name__ == "__main__":
    main()
