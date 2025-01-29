import json
import pandas as pd
import requests  # libreria per gestire richieste

# URL del TopoJSON
url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json'

# scarica il file JSON dall'URL
response = requests.get(url)

# verifica se la richiesta ha avuto successo
if response.status_code == 200:
    topojson = response.json()  # converte il contenuto in un dizionario Python
else:
    print(f"Errore durante il download del file: {response.status_code}")
    exit()

# crea una lista vuota per memorizzare i dati
countries_data = []

# itera attraverso le geometrie per estrarre i nomi dei paesi
for feature in topojson["objects"]["countries"]["geometries"]:
    country_name = feature["properties"].get("name", "Unknown")  # ottieni il nome del paese
    countries_data.append({"country": country_name, "region": "Null"})  # aggiungi 'Null' per la regione

# converti la lista in un DataFrame
df_countries = pd.DataFrame(countries_data)

# salva il DataFrame in un file CSV
df_countries.to_csv('countries.csv', index=False)

print("File salvato come 'countries.csv'.")
