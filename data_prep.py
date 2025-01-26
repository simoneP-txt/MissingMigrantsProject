import json
import pandas as pd
import requests  # Libreria per gestire richieste HTTP

# URL del TopoJSON
url = 'https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json'

# Scarica il file JSON dall'URL
response = requests.get(url)

# Verifica se la richiesta ha avuto successo
if response.status_code == 200:
    topojson = response.json()  # Converte il contenuto in un dizionario Python
else:
    print(f"Errore durante il download del file: {response.status_code}")
    exit()

# Crea una lista vuota per memorizzare i dati
countries_data = []

# Itera attraverso le geometrie per estrarre i nomi dei paesi
for feature in topojson["objects"]["countries"]["geometries"]:
    country_name = feature["properties"].get("name", "Unknown")  # Ottieni il nome del paese
    countries_data.append({"country": country_name, "region": "Null"})  # Aggiungi 'Null' per la regione

# Converti la lista in un DataFrame
df_countries = pd.DataFrame(countries_data)

# Salva il DataFrame in un file CSV
df_countries.to_csv('countries.csv', index=False)

print("File salvato come 'countries.csv'.")
