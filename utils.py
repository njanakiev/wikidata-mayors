import pandas as pd
import requests
import json


def wikidata_query(query):
    url = 'https://query.wikidata.org/sparql'
    try:
        r = requests.get(url, params = {'format': 'json', 'query': query})
        data = r.json()
    except json.JSONDecodeError as e:
        raise Exception('Invalid query')
    
    if ('results' in data) and ('bindings' in data['results']):
        columns = data['head']['vars']
        rows = []
        for binding in data['results']['bindings']:
            row = [binding[col]['value'] if col in binding else None
                   for col in columns]
            rows.append(row)
    else:
        raise Exception('No results')
    
    return pd.DataFrame(rows, columns=columns)
