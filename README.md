# **Missing Migrants Project**  
Analisi delle tragedie migratorie globali attraverso un dataset di eventi documentati.

## **Descrizione**
Questo progetto esplora i dati relativi agli incidenti migratori avvenuti tra il 2014 e il 2021. L'obiettivo è fornire una rappresentazione visiva e analitica delle tragedie che coinvolgono i migranti attraverso l'uso di tecniche statistiche e di visualizzazione geospaziale.  

L'applicazione web sviluppata con **Streamlit** permette di interagire con i dati, analizzando tendenze storiche, distribuzioni geografiche e le principali cause di morte lungo diverse rotte migratorie.  
Sono state implementate visualizzazioni interattive, tra cui:  

- **Serie storiche** del numero di morti e dispersi per regione  
- **Mappe geospaziali** per evidenziare le aree più colpite  
- **Heatmap e cluster analysis** per individuare le concentrazioni più critiche  
- **Distribuzione delle cause di morte e dei gruppi vulnerabili**  

L'analisi copre alcune delle rotte migratorie più pericolose, tra cui il **Mediterraneo, il confine tra Messico e Stati Uniti e il deserto del Sahara**, evidenziando i rischi e le condizioni che portano a migliaia di vittime ogni anno.

## **Dataset**
I dati utilizzati per questa analisi provengono dal dataset **Missing Migrants Project**, disponibile su Kaggle:  
🔗 [Missing Migrants Project - Kaggle](https://www.kaggle.com/datasets/snocco/missing-migrants-project)  

Il dataset raccoglie informazioni su incidenti migratori avvenuti tra il 2014 e il 2021, documentando il numero di morti, dispersi e sopravvissuti, oltre alle cause e alla localizzazione degli eventi.

### **Variabili utilizzate**
Di seguito, l'elenco delle variabili selezionate per l'analisi e la loro descrizione:

| **Variabile**                                       | **Descrizione** |
|----------------------------------------------------|----------------------------------------------------------------------------------------------|
| `Region`                                          | La regione in cui si è verificato l'incidente. |
| `Incident Date`                                   | La data stimata della morte, che indica il ritrovamento dei corpi o la data riportata da testimoni. |
| `Year`                                            | L'anno in cui è avvenuto l'incidente. |
| `Reported Month`                                  | Il mese in cui si è verificato l'incidente. |
| `Number Dead`                                     | Il numero totale di persone confermate morte in un incidente (numero di corpi recuperati). Se sconosciuto, il valore è assente. |
| `Minimum Estimated Number of Missing`            | Il numero minimo stimato di persone disperse e presumibilmente morte (tipicamente in naufragi). |
| `Total Number of Dead and Missing`               | Somma delle variabili `Number Dead` e `Minimum Estimated Number of Missing`. |
| `Number of Survivors`                             | Il numero di migranti sopravvissuti all'incidente, se noto. Se sconosciuto, il valore è assente. |
| `Number of Females`                               | Il numero di donne trovate morte o scomparse. Se sconosciuto, il valore è assente. |
| `Number of Males`                                 | Il numero di uomini trovati morti o dispersi. Se sconosciuto, il valore è assente. |
| `Number of Children`                              | Il numero di individui di età inferiore ai 18 anni trovati morti o dispersi. Se sconosciuto, il valore è assente. |
| `Cause of Death`                                  | La causa del decesso dei migranti (es. annegamento, incidenti stradali, violenza, ecc.). Se sconosciuta, il valore è specificato come `Mixed or unknown`. |
| `Coordinates`                                     | Le coordinate geografiche dell'evento. Spesso stimate in caso di informazioni incomplete. |
| `Migrantion route`                                | La rotta migratoria lungo la quale si è verificato l'incidente, se nota. Se sconosciuto, il valore è assente. |
| `UNSD Geographical Grouping`                     | Regione geografica in cui è avvenuto l'incidente, secondo il geoschema della **United Nations Statistics Division (UNSD)**. |
| `URL`                                            | URL della fonte originale dei dati. Se non disponibile, il valore è assente. |

Le informazioni contenute nel dataset forniscono una base solida per analizzare le tendenze della crisi migratoria e individuare i punti critici lungo le rotte più pericolose.

## **Come far funzionare il codice**

Per eseguire il progetto in locale, segui questi passaggi:

### **1️⃣ Clonare la repository**
Apri il terminale e clona la cartella del progetto utilizzando **Git**:

```bash
git clone https://github.com/simoneP-txt/MissingMigrantsProject.git
```

### **2️⃣ Spostarsi nella cartella del progetto**
Dopo aver clonato la repository, entra nella cartella corretta. Su Windows, il comando è **cd**

Esempio:
```bash
cd C:\Users\NomeUtente\MissingMigrantsProject
```

Su macOS/Linux, usa:
```bash
cd ~/MissingMigrantsProject
```

### **3️⃣ Avviare l'applicazione**
All'interno della cartella del progetto, esegui il seguente comando per avviare l'app:
```bash
uv run streamlit run app.py
```
Il sito verrà aperto automaticamente nel browser.

### **💡 Alternativa: usare il sito web**
Se non sei interessato al codice e vuoi solo utilizzare l'applicazione, puoi accedere direttamente al sito tramite il link disponibile nella repository GitHub.

## **Descrizione dei file principali**

### **📌 app.py**
`app.py` è il file principale del progetto. È il codice che viene eseguito ogni volta per avviare l'applicazione web sviluppata con **Streamlit**.  
Contiene la logica per il caricamento dei dati, l'elaborazione delle informazioni e la visualizzazione interattiva attraverso mappe e grafici.  

### **📌 data_prep.py**
`data_prep.py` è uno script dedicato alla **preparazione dei dati** e al pre-processing di alcuni elementi chiave utilizzati nel progetto.  
Ecco le principali funzionalità del file:

- **Download del TopoJSON**: lo script scarica un file **TopoJSON** contenente i confini geografici dei paesi, utile per la visualizzazione delle mappe.
- **Creazione di un DataFrame**: i dati estratti dal TopoJSON vengono convertiti in un **DataFrame Pandas**, assegnando inizialmente `"Null"` come valore per la regione di appartenenza.
- **Esportazione in CSV**: se il file `countries.csv` non esiste già, viene creato e salvato localmente.
- **Analisi della luminosità dei colori della heatmap**:  
  - Viene definita una scala di colori **COLOR_BREWER_SCALE5**, utilizzata nella heatmap.  
  - I colori vengono convertiti nel modello **HSL** per analizzare la loro luminosità.
  - Un **grafico a linee** mostra la variazione della luminosità lungo la scala di colori, per garantire che la heatmap sia visivamente efficace.

---

## **📦 Librerie utilizzate**
Nel progetto vengono utilizzate diverse librerie per la gestione dei dati, la visualizzazione e l'interattività:

| **Libreria**         | **Utilizzo** |
|----------------------|-------------------------------------------------------------------|
| `streamlit`         | Creazione dell'interfaccia web interattiva. |
| `polars`            | Gestione efficiente dei dati tabellari. |
| `altair`            | Creazione di visualizzazioni interattive. |
| `pandas`            | Manipolazione e analisi dei dati. |
| `numpy`             | Calcoli numerici e gestione di array multidimensionali. |
| `datetime`          | Gestione delle date e delle operazioni temporali. |
| `pydeck`            | Visualizzazioni geospaziali interattive su mappe. |
| `math`              | Operazioni matematiche di base. |
| `matplotlib.pyplot` | Creazione di grafici statici e gestione delle colorbar. |
| `io`                | Gestione dell'I/O per generare immagini. |
| `scipy.spatial.ConvexHull` | Calcolo del **convex hull**, utile per analizzare i gruppi geografici. |
| `pathlib.Path`      | Gestione dei percorsi dei file nel sistema operativo. |
| `requests`          | Scaricamento di dati da URL esterni, come il file TopoJSON. |
| `colorsys`          | Conversione dei colori tra diversi modelli di colore (RGB, HSL). |
| `os`               | Interazione con il filesystem, ad esempio per controllare l'esistenza di file. |
