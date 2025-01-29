import pandas as pd
import requests
import numpy as np
import matplotlib.pyplot as plt
import colorsys
import os

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

# Nome del file CSV
file_path = 'countries.csv'

# Controlla se il file esiste già
if not os.path.exists(file_path):
    df_countries.to_csv(file_path, index=False)
    print(f"File '{file_path}' salvato correttamente.")
else:
    print(f"Il file '{file_path}' esiste già. Nessun salvataggio effettuato.")

#######################################################################################
#Controllo luminosità colori usati nella heatmap
#definisco la scala colori
COLOR_BREWER_SCALE5 = np.array([
    [230, 0, 0],     
    [204, 0, 0],     
    [179, 0, 0],     
    [153, 0, 0],   
    [128, 0, 0],
    [102, 0, 0],
    [77, 0, 0],
    [51, 0, 0],
    [26, 0, 0]
]) / 255  # normalizza tra 0 e 1

# converti in HSL per estrarre la luminosità
luminosities = [colorsys.rgb_to_hls(r, g, b)[1] for r, g, b in COLOR_BREWER_SCALE5]

# plotta la luminosità
plt.figure(figsize=(6, 4))
plt.plot(luminosities, marker='o', linestyle='-', color='red')
plt.xlabel("Indice del colore")
plt.ylabel("Luminosità (HSL)")
plt.title("Luminosità della scala COLOR_BREWER_SCALE5")
plt.gca().invert_yaxis()  # Inverti l'asse se vuoi vedere la diminuzione
plt.show()
