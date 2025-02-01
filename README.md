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

