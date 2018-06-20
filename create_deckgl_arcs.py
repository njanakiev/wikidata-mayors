import json
import pandas as pd
from matplotlib import cm


df = pd.read_csv('data/european_mayors.csv')
df_subset = df[['country', 
                'city_lon', 'city_lat', 
                'birth_city_lon', 'birth_city_lat', 
                'distance']].dropna()
df_subset.rename(columns={'city_lon':'lon0', 
                          'city_lat':'lat0', 
                          'birth_city_lon':'lon1', 
                          'birth_city_lat':'lat1'}, inplace=True)

# If we want to filter our data set for a single country
#df_subset = df_subset[df_subset['country'] == 'Germany']

# Choose a colormap
# https://matplotlib.org/users/colormaps.html
colors = list(cm.tab10.colors)
colors.pop(7) # remove gray color
colors.pop(5) # remove brown color

# Ordering of countries for the colors (sorted by longitude)
country_list = ['Austria', 'Belgium', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic',
    'Denmark', 'Estonia', 'Finland', 'France', 'Germany', 'Greece', 'Hungary',
    'Iceland', 'Ireland', 'Italy', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
    'Netherlands', 'Norway', 'Poland', 'Portugal', 'Romania', 'Slovakia',
    'Slovenia', 'Spain', 'Sweden', 'Switzerland', 'United Kingdom']

# Create a color mapping for each country
n_countries = len(country_list)
country_colormap = {}
for i, country in enumerate(country_list): 
    color = colors[i % len(colors)]
    color = [int(c * 255) for c in color]
    country_colormap[country] = color

# Create a list of arcs
arcs = []
for i, (country, lon0, lat0, lon1, lat1, distance) in df_subset.iterrows():
    arcs.append({
        'source': [lon1, lat1],
        'target': [lon0, lat0], 
        'color': country_colormap[country],
        'distance': distance
    })
    
with open('data/arcs.json', 'w') as f:
    json.dump(arcs, f)

# The file can be stored directly in the visualization folder
#with open('../wikidata-mayors-visualization/arcs.json', 'w') as f:
#    json.dump(arcs, f)
