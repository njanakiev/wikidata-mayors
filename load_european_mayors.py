import pandas as pd
import numpy as np
import requests
import json
from datetime import datetime
from geopy.distance import distance
import utils


country_query = """
SELECT DISTINCT ?country ?countryLabel WHERE {
  { ?country wdt:P463 wd:Q166546 } UNION 
  { ?country wdt:P463 wd:Q458 } UNION 
  { VALUES ?country { wd:Q55 } }  # Add Netherlands
  FILTER( ?country != wd:Q29999 ) # Remove Kingdom of the Netherlands 
  SERVICE wikibase:label { 
      bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". 
  }
}
"""

mayor_query = """
SELECT DISTINCT 
  ?city ?cityLabel ?city_coordinates ?population 
  ?mayor ?mayorLabel ?genderLabel ?birth ?start_date
  ?birth_country ?birth_countryLabel 
  ?birth_city ?birth_cityLabel ?birth_city_coordinates 
WHERE {{
  ?city wdt:P17 wd:{0}.
  ?city wdt:P31/wdt:P279* wd:Q515.
  ?city p:P6 ?statement.
  ?city wdt:P1082 ?population.
  ?city wdt:P625 ?city_coordinates.
  
  ?statement ps:P6 ?mayor.
  ?statement pq:P580 ?start_date.
  
  OPTIONAL {{ ?mayor wdt:P569 ?birth. }}
  OPTIONAL {{ ?mayor wdt:P21 ?gender. }}
  
  # Remove all mayors that have an end time
  FILTER NOT EXISTS {{ ?statement pq:P582 ?y. }}
  # Remove all mayors that are not alive
  FILTER NOT EXISTS {{ ?mayor wdt:P570 ?z. }}
  
  OPTIONAL {{
    ?mayor wdt:P19 ?birth_city.
    ?birth_city wdt:P625 ?birth_city_coordinates.
    ?birth_city wdt:P17 ?birth_country.
    
    # Remove all historic countries
    FILTER NOT EXISTS {{ ?birth_country wdt:P31 wd:Q3024240. }}
  }}
  
  SERVICE wikibase:label {{
    bd:serviceParam wikibase:language "[AUTO_LANGUAGE],en". 
  }}
}}
"""


# Get Wikidata code from each country
df_countries = utils.wikidata_query(country_query)
df_countries['code'] = df_countries['country'].str.split('/').str[-1]

# Get mayors for each country
df_list = []
for index, (country, country_label, country_code) in df_countries.iterrows():
    print(country_label, country_code)
    df = utils.wikidata_query(mayor_query.format(country_code))
    
    # Replace unknown birth dates and calculate age
    df['birth'] = df['birth'].apply(
        lambda s : None if ((s is None) or s.startswith('t')) else s)
    df['birth'] = pd.to_datetime(df['birth'])
    df['age'] = df['birth'].apply(lambda x: datetime.now().year - x.year)
    
    # Replace unknown start dates and calculate duration
    df['start_date'] = df['start_date'].apply(
        lambda s : None if ((s is None) or s.startswith('t')) else s)
    df['start_date'] = pd.to_datetime(df['start_date'])
    df['duration'] = df['start_date'].apply(lambda x: datetime.now().year - x.year)
    
    df.insert(0, 'country', country_label)
    print('Entries :', len(df))
    print()
    
    df_list.append(df)

# Collect all rows into single table
df = pd.concat(df_list)

# Convert coordinates lon, lat columns
df[['city_lon', 'city_lat']] = df['city_coordinates'].str[6:-1].str.split(' ', expand=True)
df[['city_lon', 'city_lat']] = df[['city_lon', 'city_lat']].astype(float)
df[['birth_city_lon', 'birth_city_lat']] = df['birth_city_coordinates'].str[6:-1].str.split(' ', expand=True)
df[['birth_city_lon', 'birth_city_lat']] = df[['birth_city_lon', 'birth_city_lat']].astype(float)

# Drop original coordinates columns
df.drop(columns=['city_coordinates', 'birth_city_coordinates'], inplace=True)

# Calculate distance between city and birth city
def calc_distance(row):
    lon0, lat0 = row['city_lon'], row['city_lat']
    lon1, lat1 = row['birth_city_lon'], row['birth_city_lat']
    
    if np.isnan(lon1) or np.isnan(lat1):
        return None
    else:
        return distance((lat0, lon0), (lat1, lon1)).m
        
df['distance'] = df.apply(calc_distance, axis=1)

# Show some information about the table
print(df.info())

# Save table to file
df.to_csv('data/european_mayors.csv', index=False)
