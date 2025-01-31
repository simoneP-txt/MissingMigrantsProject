import streamlit as st
import polars as pl
import altair as alt
import pandas as pd
import numpy as np
import datetime as dt
import pydeck as pdk
import math 
import matplotlib.pyplot as plt # utilizzata per la colorbar della heatmap
import io                        # utilizzata per la colorbar della heatmap
from scipy.spatial import ConvexHull # utilizzata per il poligono dei gruppi
from pathlib import Path

st.set_page_config(
    page_title="Missing Migrants Project",
    page_icon = "🌍"
)

#Preprocessing
@st.cache_data
def load_data():
    data = (
        pl.read_csv("MM_14_21.csv", null_values=["", "NA", " "])
        .select(["Region", "Incident Date", "Year", "Reported Month", "Number Dead",
        "Minimum Estimated Number of Missing", "Total Number of Dead and Missing", 
        "Number of Survivors", "Number of Females", "Number of Males", "Number of Children",
        "Cause of Death", "Coordinates", "Migrantion route", "UNSD Geographical Grouping", "URL"])
    )
    data = data.with_columns(
    data["Incident Date"]
    .str.extract(r"^(\w{3}, \d{2}/\d{2}/\d{4})")  # Estrarre solo giorno della settimana e data
    .alias("Incident Date")  # Sovrascrive la colonna esistente
    )
    datapd = data.to_pandas()
    return data, datapd

data, datapd = load_data()

def migration_tragedies():
    image_folder = Path("images")
    
    # Sezione su Alan Kurdi
    st.markdown("## Sotto agli occhi di tutti")
    st.markdown("""
    Nel 2014, la comunità internazionale è venuta a conoscenza dell’orribile realtà della morte di questi migranti, spesso attraverso immagini come questa, che si concentra su un rifugiato siriano di tre anni di nome Alan Kurdi.  
    Lui e la sua famiglia sono morti nel settembre del 2015 vicino a Bodrum, in Turchia. Erano in viaggio per il Canada.  
    """)
    
    image_path = image_folder / "Alan Kurdi.jpg"
    st.image(str(image_path), use_container_width=True)
    
    st.markdown("[Link alla pagina Wikipedia (EN)](https://en.wikipedia.org/wiki/Death_of_Alan_Kurdi)")
    
    # Sezione su Óscar e Valeria Martínez
    st.markdown("## Uno sguardo in Centro America")
    st.markdown("""
    Spostandoci in Centro America, troviamo un altro caso che ha suscitato profonda indignazione e ha reso evidente la pericolosità delle migrazioni forzate.  
    
    Óscar Alberto Martínez Ramírez e sua figlia Valeria sono morti mentre cercavano di attraversare il Rio Grande, la loro morte catturata da un'immagine orribile e inquietante.
    
    Padre e figlia giacciono a faccia in giù nell'acqua sulla riva del Rio Grande a Matamoros, in Messico, Valeria infilata nella maglietta di suo padre con il suo piccolo braccio avvolto attorno al suo collo.  
    """)
    
    image_path = image_folder / "Alberto e Valeria Martínez.jpg"
    st.image(str(image_path), use_container_width=True)
    st.markdown("[Link alla pagina su NBC News (EN)](https://www.nbcnews.com/news/latino/family-salvadoran-migrant-dad-child-who-drowned-say-he-loved-n1022226)")

    # Sezione sul Naufragio del 18 aprile 2015
    st.markdown("## Il disastro nel Canale di Sicilia")
    st.markdown("""
    La cosiddetta tragedia nel Canale di Sicilia è stato il naufragio di un'imbarcazione eritrea usata per il trasporto di migranti avvenuto la notte del 18 aprile 2015 al largo delle coste della Libia.  
    Il naufragio dell'imbarcazione ha provocato 58 vittime accertate, 28 superstiti salvati e fra i 700 e i 900 dispersi presunti, numeri che la pongono come una delle più gravi tragedie marittime nel Mediterraneo dall'inizio del 21° secolo.  
    """)
    
    image_path = image_folder / "naufragio canale di sicilia.jpeg"
    st.image(str(image_path), use_container_width=True)
    st.markdown("[Link alla pagina Wikipedia (IT)](https://it.wikipedia.org/wiki/Naufragio_nel_Canale_di_Sicilia_del_18_aprile_2015)")

def dataframe():
    st.markdown("""
    In questa applicazione web si cerca di fornire una breve analisi e di presentare alcuni dati su queste tragedie, cercando di renderli il più comprensibili possibile.  
    """)

    st.markdown("""
    Questo è il **dataframe** utilizzato per l'analisi, sotto ci sono le descrizioni delle variabili:
    """)

    st.dataframe(data, use_container_width=True)

    data_description = {
        "Variabili": [
            "Region", "Incident Date", "Year", "Reported Month", "Number Dead",
            "Minimum Estimated Number of Missing", "Total Number of Dead and Missing", 
            "Number of Survivors", "Number of Females", "Number of Males", "Number of Children",
            "Cause of Death", "Coordinates", "Migrantion route", "UNSD Geographical Grouping", "URL"
        ],
        "Descrizione": [
            "La regione in cui si è verificato l'incidente.",
            "La data stimata della morte indica il ritrovamento dei corpi o la data riportata da testimoni.",
            "L'anno in cui è avvenuto l'incidente.",
            "Il mese in cui si è verificato l'incidente.",
            "Il numero totale di persone confermate morte in un incidente, ovvero il numero di corpi recuperati. Se i migranti risultano dispersi e presunti morti, come nei casi di naufragi, viene lasciato vuoto.",
            "Il numero totale di coloro che risultano dispersi e quindi si presume siano morti. Questa variabile viene generalmente registrata negli incidenti che coinvolgono naufragi. Il numero dei dispersi si calcola sottraendo il numero dei corpi recuperati da un naufragio e il numero dei sopravvissuti dal numero totale dei migranti segnalati sulla barca. Questo numero può essere segnalato da migranti o testimoni sopravvissuti. Se non vengono segnalate persone scomparse, il campo viene lasciato vuoto.",
            'La somma delle variabili “Number Dead” e “Minimum Estimated Number of Missing”.',
            "Il numero di migranti sopravvissuti all'incidente, se noto. Se sconosciuto, viene lasciato vuoto",
            "Indica il numero di donne trovate morte o scomparse. Se sconosciuto, viene lasciato vuoto.",
            "Indica il numero di uomini trovati morti o dispersi. Se sconosciuto, viene lasciato vuoto.",
            "Indica il numero di individui di età inferiore ai 18 anni trovati morti o dispersi. Se sconosciuto, viene lasciato vuoto.",
            "La determinazione delle condizioni che hanno portato alla morte del migrante, ovvero le circostanze dell'evento che ha prodotto la lesione mortale. Se sconosciuto, il motivo è incluso ove possibile.",
            "Luogo in cui è avvenuta la morte o dove sono stati ritrovati il corpo o i corpi. In molte regioni, in particolare nel Mediterraneo, le coordinate geografiche vengono stimate poiché spesso le posizioni precise non sono note. La descrizione della posizione deve essere sempre confrontata con le coordinate della posizione.",
            "Nome della rotta migrante sulla quale si è verificato l'incidente, se noto. Se sconosciuto, viene lasciato vuoto.",
            "Regione geografica in cui è avvenuto l'incidente, come designato dal geoschema della United Nations Statistics Division (UNSD).",
            "URL della fonte originale dei dati. Se non disponibile, viene lasciato vuoto."
        ]
        }

    table_markdown = """
| Variabili         | Descrizione                                                                 |
|-------------------|-----------------------------------------------------------------------------|
""" + "\n".join([f"| {var} | {desc} |" for var, desc in zip(data_description["Variabili"], data_description["Descrizione"])])

    st.markdown(table_markdown)
    st.markdown('La fonte dei dati si trova a questo [link](https://www.kaggle.com/datasets/snocco/missing-migrants-project).', unsafe_allow_html=True)

    url_counts = datapd["URL"].value_counts().dropna()
    top_sources = url_counts.head(5)

    st.markdown("### Fonti principali del dataset")
    st.markdown("Il dataset è stato costruito a partire da diverse fonti. Ecco le principali:")
    
    for fonte, freq in top_sources.items():
        st.markdown(f"- [{fonte}]({fonte})")

###################################################################################################################################
# ANALISI DESCRITTIVA DEI DATI
#0. Mappa delle regioni del dataset
def hex_to_rgb(hex_color):
    #Converte un colore esadecimale in formato RGB.
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def regions_map():
    st.write("## Mappa delle Regioni")

    st.markdown(
        "Questa mappa mostra la suddivisione delle regioni nel dataset, "
        "consentendo di visualizzare le aree geografiche di riferimento. "
        "Successivamente nell'applicazione sarà possibile selezionare specifiche regioni per un'analisi più dettagliata."
    )

    # Carico il dataset aggiornato
    file_path = "countries.csv"
    df_countries = pd.read_csv(file_path)

    # Definisco la palette di colori
    color_palette = [
        "#FF0000", "#00FF00", "#0000FF", "#FFFF00", "#FF00FF",  # Rosso, Verde, Blu, Giallo, Magenta
        "#00FFFF", "#800000", "#008000", "#000080", "#808000",  # Ciano, Marrone scuro, Verde scuro, Blu scuro, Verde oliva
        "#FFA500", "#4B0082", "#FFC0CB", "#8B4513", "#209186",  # Arancione, Indaco, Rosa, Marrone cioccolato, Turchese
        "#FF00DD", "#ADD8E6", "#7FFF00", "#DC143C", "#00CED1",  # Fucsia, Azzurro chiaro, Verde lime, Cremisi, Turchese scuro
        "#8A2BE2", "#FFD700"  # Blu violetto, Oro
    ]

    # Assegno un colore a ogni regione
    region_list = df_countries["region"].dropna().unique().tolist()
    region_color_dict = {region: color_palette[i % len(color_palette)] for i, region in enumerate(region_list)}
    
    # Mappa principale
    countries_map_50 = alt.topo_feature("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json", 'countries')

    map_chart = (
        alt.Chart(countries_map_50)
        .mark_geoshape(stroke="black", strokeWidth=0.5)
        .encode(
            color=alt.condition(
                alt.datum.region != "Null",
                alt.Color("region:N", scale=alt.Scale(domain=list(region_color_dict.keys()), range=list(region_color_dict.values())), legend=None), 
                alt.value("transparent")  # Paesi con "Null" trasparenti
            ),
            tooltip=[
                alt.Tooltip("properties.name:N", title="Paese"),
                alt.Tooltip("region:N", title="Regione")
            ]
        )
        .transform_lookup(
            lookup="properties.name",
            from_=alt.LookupData(df_countries, "country", ["country", "region"])
        )
    )

    background = alt.Chart(countries_map_50).mark_geoshape(
        fill='lightgray',
        stroke='darkgray'
    ).encode(tooltip=alt.value(None))

    # Tolgo "Null" dalla legenda
    legend_df = pd.DataFrame({"region": list(region_color_dict.keys()), "color": list(region_color_dict.values())})
    legend_df = legend_df[legend_df["region"] != "Null"]

    # Creo la legenda con HTML + CSS
    legend_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
    for region, color in region_color_dict.items():
        if region != "Null":
            color_rgb = hex_to_rgb(color)
            color_rgb_str = f"rgb({color_rgb[0]}, {color_rgb[1]}, {color_rgb[2]})"
            legend_html += f"""
<div style='display: flex; align-items: center; margin-bottom: 5px;'>
    <div style='width: 20px; height: 20px; background-color: {color_rgb_str}; margin-right: 10px; border: 1px solid #000;'></div>
    <span style='font-size: 14px; color: white;'>{region}</span>
</div>
        """
    legend_html += "</div>"

    # Mostro la mappa
    combined_map = alt.layer(background, map_chart).project(
        type="mercator",
        scale=89,
        translate=[295, 166],
        center=[20, 50],
        clipExtent=[[0, 0], [800, 400]]
    ).properties(
        width=900,
        height=400
    )

    # Mostro la mappa in Streamlit
    st.altair_chart(combined_map, use_container_width=True)

    # Mostro la legenda HTML
    st.markdown(legend_html, unsafe_allow_html=True)

#1. Serie storica del numero totale di morti e dispersi per regione
def timeseries():
    st.markdown("---")
    st.write(
        "L'obiettivo di questa sezione è comprendere come il numero totale di morti e dispersi sia variato nel tempo "
        "nelle diverse regioni. Attraverso questa visualizzazione, è possibile individuare tendenze, variazioni significative "
        "e potenziali anomalie nei dati raccolti.")

    st.write("## Serie storica del numero totale di morti e dispersi per regione")
    
    st.markdown(
    "L'interfaccia consente di **selezionare una o più regioni** da analizzare e di **definire un intervallo temporale** "
    "per restringere il focus della visualizzazione. Tuttavia, si consiglia di **mantenere il Mediterraneo come unica selezione** "
    "per evitare la sovrapposizione di dati con scale molto diverse tra loro. Inoltre, si segnala che la regione **Central Asia** "
    "contiene una sola osservazione, risultando pertanto in un singolo punto all'interno del grafico."
    )
    
    # Conversione della data
    datapd['Incident_Date'] = pd.to_datetime(datapd['Incident Date'], format='%a, %m/%d/%Y', errors='coerce').dt.date
    datapd.dropna(subset=['Incident_Date'], inplace=True)

    # Selezione delle regioni
    regions = sorted(datapd['Region'].unique().tolist())
    selected_regions = st.multiselect(
        'Seleziona le regioni di interesse (max 4):',
        regions,
        default=["Mediterranean"],
        key="region_selector",
        max_selections=4
    )

    # Selezione dell'intervallo temporale
    start_date, end_date = st.slider(
        "Seleziona l'intervallo di tempo",
        min_value=dt.date(2014, 1, 1),
        max_value=dt.date(2021, 12, 31),
        value=(dt.date(2014, 1, 1), dt.date(2021, 12, 31)),
        format="DD-MM-YYYY",
        key="date_slider"
    )

    # Filtraggio dei dati
    filtered_data = datapd[
        (datapd['Region'].isin(selected_regions)) &
        (datapd['Incident_Date'] >= start_date) &
        (datapd['Incident_Date'] <= end_date)
    ].copy()

    if not filtered_data.empty:
        filtered_data["Incident_Date"] = pd.to_datetime(filtered_data["Incident_Date"], errors="coerce")
        filtered_data["Year_Month"] = filtered_data["Incident_Date"].dt.to_period("M")

        aggregated_data = filtered_data.groupby(["Year_Month", "Region"]).agg({
            "Total Number of Dead and Missing": "sum"
        }).reset_index()

        aggregated_data["Year_Month"] = aggregated_data["Year_Month"].dt.to_timestamp()

        #{"date": "", "title": "", "link": "", "total_deaths": 0}
        # Definizione degli eventi catastrofici
        events = {
            "Mediterranean": [
                {"date": "2015-04-18", "title": "Naufragio nel Canale di Sicilia", 
                 "link": "https://it.wikipedia.org/wiki/Naufragio_nel_Canale_di_Sicilia_del_18_aprile_2015",
                 "total_deaths": 1022},
                {"date": "2016-05-26", "title": "Naufragio nelle coste libiche",
                 "link": "https://www.rainews.it/archivio-rainews/articoli/Migranti-le-vittime-sono-centinaia-Arrestati-a-Palermo-due-scafisti-ultimo-naufragio-7c900850-ea75-46e8-99ee-9d9db7357ee5.html",
                 "total_deaths": 550},
            ],
            "South-eastern Asia": [
                {"date": "2014-12-31", "title": "Fonte incerta", 
                 "link": "https://www.nytimes.com/2014/12/31/world/asia/airasia-8501-jet-missing-indonesia.html", "total_deaths": 750}
            ]
        }

        # Filtraggio degli eventi per le regioni selezionate
        event_annotations = []
        event_links = []
        for region in selected_regions:
            if region in events:
                for event in events[region]:
                    event_date = pd.to_datetime(event["date"])
                    if start_date <= event_date.date() <= end_date:
                        event_annotations.append({
                            "Year_Month": event_date,
                            "Event": event["title"],
                            "Total_Deaths": event["total_deaths"]  
                        })
                        event_links.append({
                            "date": event["date"],
                            "region": region,
                            "title": event["title"],
                            "total_deaths": event["total_deaths"],
                            "link": event["link"]
                        })

        # Grafico della serie storica
        line = alt.Chart(aggregated_data).mark_line().encode(
            x=alt.X("Year_Month:T", title="Anno e Mese"),
            y=alt.Y("Total Number of Dead and Missing:Q", title="Somma mensile del numero totale di morti e dispersi"),
            color=alt.Color("Region:N", title="Regione"),
            tooltip=[
                alt.Tooltip("Year_Month:T", title="Data"),
                alt.Tooltip("Region:N", title="Regione"),
                alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".0f")
            ]
        )

        # Selettore per il tooltip interattivo
        nearest = alt.selection_point(
            nearest=True, on="pointerover", fields=["Year_Month"], empty="none"
        )
        selectors = alt.Chart(aggregated_data).mark_point().encode(
            x="Year_Month:T",
            opacity=alt.value(0)
        ).add_params(nearest)

        points = line.mark_point(size=100).encode(
            x="Year_Month:T",
            y="Total Number of Dead and Missing:Q",
            opacity=alt.condition(nearest, alt.value(1), alt.value(0)),
            tooltip=[
                alt.Tooltip("Year_Month:T", title="Data"),
                alt.Tooltip("Region:N", title="Regione"),
                alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".0f")
            ]
        )

        text = line.mark_text(align="left", dx=5, dy=-5).encode(
            text=alt.condition(nearest, alt.Text("Total Number of Dead and Missing:Q", format=".0f"), alt.value(""))
        )

        rules = alt.Chart(aggregated_data).mark_rule(color="gray").encode(
            x="Year_Month:T",
            tooltip=[
                alt.Tooltip("Year_Month:T", title="Data"),
                alt.Tooltip("Region:N", title="Regione"),
                alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".0f")
            ]
        ).transform_filter(nearest)

        # Aggiunta delle linee verticali tratteggiate per eventi storici
        if event_annotations:
            event_df = pd.DataFrame(event_annotations)
            event_rules = alt.Chart(event_df).mark_rule(strokeDash=[4, 4], color="darkgray", strokeWidth=2).encode(
                x="Year_Month:T",
                tooltip=[
                    alt.Tooltip("Event:N", title="Evento"),
                    alt.Tooltip("Year_Month:T", title="Data"),
                    alt.Tooltip("Total_Deaths:Q", title="Morti e dispersi", format=".0f")
                ]
            )
            timeseries = alt.layer(line, selectors, points, rules, text, event_rules).properties(width=600, height=400)
        else:
            timeseries = alt.layer(line, selectors, points, rules, text).properties(width=600, height=400)

        st.altair_chart(timeseries, use_container_width=True)

        # Aggiunta del link agli eventi storici
        if event_links:
            st.markdown("#### Fatti di cronaca nera correlati:")
            for event in event_links:
                st.markdown(f"📅 **{event['date']}** | 📍 **{event['region']}** |  **{event['total_deaths']} tra morti e dispersi** - [{event['title']}]({event['link']})"
                            , unsafe_allow_html=True)
    else:
        st.warning("Nessuna regione selezionata.")

    st.markdown(
    "Dall'analisi dei dati emerge chiaramente come le regioni del **Mediterraneo, del Nord America e del Nord Africa** "
    "rappresentino le aree con il più alto numero di morti e dispersi. Queste zone si configurano come i principali epicentri "
    "della crisi migratoria, caratterizzandosi per condizioni di viaggio estremamente pericolose e per un elevato numero di incidenti mortali. "
    "Come verrà approfondito nelle sezioni successive, il **Mediterraneo** continua a essere una delle rotte più letali per i migranti, "
    "mentre il confine tra **Messico e Stati Uniti**, così come il **Nord Africa**, si distinguono per la numerosità di volte che appaiono nel dataset, "
    "come vedremo anche successivamente."
)

#2. Distribuzione delle variabili categoriche
def barchart():
    st.markdown("---")
    st.write("## Distribuzione delle variabili categoriche")

    st.markdown(
    "Questa sezione permette di analizzare la distribuzione delle variabili categoriali presenti nel dataset, "
    "offrendo una panoramica sulla frequenza. "
    "Ciò consente di individuare quali regioni, cause di morte o rotte migratorie siano maggiormente rappresentate nei dati."
    )

    columns = ['Region', 'Cause of Death', 'Migrantion route']

    selected_variable = st.pills(
        'Seleziona una variabile per visualizzare la distribuzione',
        columns,
        default="Region"
    )

    if not selected_variable:
        st.warning("Seleziona una variabile per visualizzare la distribuzione.")
        return
    
    filtered_data1 = data[[selected_variable]].drop_nans()

    highlight = alt.selection_point(
        name="highlight",
        on="pointerover",
        fields=[selected_variable],
        nearest=True,
        empty="none",
        clear="mouseout"
    )

    click = alt.selection_point(
        name="click",
        on="click",
        fields=[selected_variable],
        empty="all",
        clear="mouseout"
    )

    change_color = alt.condition(
        highlight,
        alt.value("yellow"),
        alt.value("blue")
    )

    change_opacity = alt.condition(
        click,
        alt.value(1),
        alt.value(0.4)
    )

    histogram = (
        alt.Chart(filtered_data1)
        .mark_bar(stroke='lightgray', cursor="pointer")
        .encode(
            y=alt.Y(f'{selected_variable}:N', sort='-x', title=selected_variable),
            x=alt.X('count()', title='Frequenza dell\'osservazione nel dataset'),
            color=change_color,
            opacity=change_opacity
        )
        .properties(
            width=600,
            height=400
        )
        .add_params(
            highlight,
            click 
        )
    )

    st.altair_chart(histogram, use_container_width=True)

    st.markdown(
    "Analizzando la distribuzione delle osservazioni in base alla **regione** e alla **rotta migratoria**, si nota che "
    "le categorie più frequenti sono rispettivamente **North America** e il **confine tra Stati Uniti e Messico**. "
    "Tuttavia, come verrà evidenziato nelle analisi successive, il **Mediterraneo** registra un numero significativamente "
    "più alto di morti e dispersi totali. Questo potrebbe indicare che, nel caso del **Nord America**, si tratta perlopiù "
    "di un'elevata quantità di **registrazioni di casi isolati e di persone singole**, mentre nel Mediterraneo gli incidenti "
    "coinvolgono un numero molto più elevato di vittime per singolo evento. \n\n"
    
    "Per quanto riguarda la **causa di morte**, non sorprende che la categoria più frequente sia **Mixed or unknown**. "
    "Molto spesso, infatti, i corpi delle vittime vengono rinvenuti quando l'evento si è già verificato, rendendo difficile "
    "determinare con precisione le circostanze della morte. In molti altri casi, invece, i corpi non vengono recuperati affatto, "
    "lasciando l'esatta causa del decesso sconosciuta."
    )

#3. Distribuzione assoluta delle vittime per regione
def piechart():
    st.markdown("---")
    st.write("## Distribuzione assoluta delle vittime per regione")

    st.markdown(
    "Questo grafico rappresenta la distribuzione del numero di vittime per ciascuna regione, suddivise in quattro categorie: "
    "**uomini, donne, minori di 18 anni e individui di genere sconosciuto**. "
    "Al centro di ogni diagramma è riportato il numero totale di morti e dispersi per quella specifica area geografica. "
    "Le regioni sono ordinate in modo decrescente in base al numero complessivo di vittime, permettendo così di evidenziare "
    "le aree maggiormente colpite dal fenomeno."
    )

    def prepare_data_for_alt(df):
        regions = df['Region'].unique()
        chart_data = []

        for region in regions:
            regional_data = df[df['Region'] == region]
            total_deaths = regional_data['Total Number of Dead and Missing'].sum()
            male_deaths = regional_data['Number of Males'].sum()
            female_deaths = regional_data['Number of Females'].sum()
            children_deaths = regional_data['Number of Children'].sum()
            unknown_deaths = total_deaths - (male_deaths + female_deaths + children_deaths)

            chart_data.extend([
                {"Region": region, "Category": "Male", "Count": male_deaths, "Total": total_deaths},
                {"Region": region, "Category": "Female", "Count": female_deaths, "Total": total_deaths},
                {"Region": region, "Category": "Children", "Count": children_deaths, "Total": total_deaths},
                {"Region": region, "Category": "Unknown", "Count": unknown_deaths, "Total": total_deaths}
            ])
        
        return pd.DataFrame(chart_data)

    altair_data = prepare_data_for_alt(datapd)
    total_deaths_order = altair_data.groupby("Region")["Total"].max().sort_values(ascending=False).index.tolist()
    
    base_chart = alt.Chart(altair_data).transform_aggregate(
        total="sum(Count)", groupby=["Region", "Category", "Total"]
    )

    base_pie = (
        base_chart.mark_arc(innerRadius=50, outerRadius=80, stroke="white", strokeWidth=0.5).encode(
            theta=alt.Theta("total:Q", stack=True),
            color=alt.Color("Category:N", scale=alt.Scale(scheme="category10"), title="Categoria"),
            tooltip=["Region:N", "Category:N", alt.Tooltip("total:Q", title="Numero")],
        )
    )

    text_pie = (
       base_chart.mark_text(size=12, color="white").encode(
           theta=alt.Theta("total:Q", stack=True),
           text=alt.Text("total:Q", format=".0f"),
           radius=alt.value(65),  # sposta le etichette

       )
    )

    text_total = (
        base_chart.mark_text(size=18, fontWeight="bold").encode(
            text=alt.Text("Total:Q", format=".0f"),
            color=alt.value("white")
        ).transform_filter(alt.datum.Category == "Male")
    )

    chart = (
        base_pie  + text_total
    ).properties(
        width=150,
        height=150
    ).facet(
        facet=alt.Facet("Region:N", title="Regione", sort=total_deaths_order),
        columns=4
    )

    st.altair_chart(chart, use_container_width=True)

    st.markdown(
    "Dal grafico emerge in modo evidente l'enorme numero di vittime registrate nel **Mediterraneo**, che rappresenta la regione "
    "con il più alto bilancio di morti e dispersi. Un aspetto particolarmente significativo è la predominanza della categoria **Unknown**, "
    "molto probabilmente dovuta al fatto che molte delle vittime non vengono mai recuperate e restano disperse nelle profondità del mare.\n\n"
    
    "Si osserva inoltre una **grande prevalenza di vittime di sesso maschile** nelle regioni del **Nord e Centro America**, "
    "suggerendo che il fenomeno migratorio in queste aree coinvolga in larga parte uomini. Un altro elemento degno di nota è il caso del "
    "**Sud-est asiatico**, che si distingue come un **outlier** per il numero di **minori di 18 anni** coinvolti, con **428 vittime** registrate, "
    "un valore significativamente più alto rispetto ad altre regioni.\n\n"
    
    "_Nota:_ Per ragioni di leggibilità, non sono state inserite etichette numeriche per ogni fetta del grafico, poiché avrebbero compromesso "
    "l'aspetto visivo complessivo. Tuttavia, per chi utilizza un **PC**, è possibile visualizzare il valore esatto di ciascuna categoria "
    "passando il mouse sopra le sezioni del grafico."
    )
#NON riesco a sistemare bene le etichette all'interno di ogni torta.

#4. Causa di morte per regione
def stackedbarchart():
    st.markdown("---")
    st.write("## Distribuzione Percentuale delle Cause di Morte per Regione")

    st.markdown(
    "Il grafico presentato è un **istogramma a barre impilate** che mostra la distribuzione percentuale delle **cause di morte** "
    "per ciascuna regione. Ogni barra rappresenta una regione e le diverse sezioni colorate indicano la proporzione delle varie "
    "cause di decesso rispetto al totale registrato in quella specifica area geografica.\n\n"
    
    "L'interfaccia ha la possibilità di **selezionare fino a 14 regioni** da includere nel grafico, consentendo un'analisi mirata "
    "delle aree di interesse. Inoltre, è disponibile una funzione di **ordinamento per causa di morte**, che permette di "
    "riorganizzare le regioni in base alla prevalenza di una specifica categoria di decesso, facilitando il confronto tra le diverse "
    "aree geografiche."
    )

    # Calcolo della percentuale
    datapd_counts = datapd.groupby(['Region', 'Cause of Death']).size().reset_index(name='Count')
    datapd_counts['Percent'] = datapd_counts.groupby('Region')['Count'].transform(lambda x: x / x.sum() * 100)

    # Definizione della mappatura colore personalizzata per ogni causa di morte
    color_mapping = {
        "Drowning": "#392F5A",
        "Vehicle accident / death linked to hazardous transport": "#FF8811",
        "Violence": "#9DD9D2",
        "Sickness / lack of access to adequate healthcare": "#FFF8F0",
        "Harsh environmental conditions / lack of adequate shelter, food, water": "#f4d06f",
        "Mixed or unknown": "#0F7968",
        "Accidental death": "#664712"
    }

    # Creazione della scala dei colori basata sulla mappatura
    color_scale = alt.Scale(domain=list(color_mapping.keys()), range=list(color_mapping.values()))

    # Selezione delle regioni (max 14)
    selected_regions = st.multiselect(
        'Seleziona le regioni da includere (max 14):',
        options=datapd_counts['Region'].unique(),
        default=datapd_counts['Region'].unique()[:8],
        max_selections=14
    )

    # Filtra i dati in base alle regioni selezionate
    filtered_data = datapd_counts[datapd_counts['Region'].isin(selected_regions)]

    # Selezione della causa di morte tramite st.pills
    selected_cause = st.pills(
        "Seleziona la causa di morte per ordinare le regioni:",
        options=["None"] + datapd_counts['Cause of Death'].unique().tolist(),
        default="None"
    )

    if not selected_cause:
        st.warning("Devi selezionare una causa di morte per procedere.")
        return  # Esce dalla funzione se la selezione è vuota

    if not filtered_data.empty:
        # Ordina solo se una causa di morte è selezionata
        if selected_cause != "None":
            # Aggiungi tutte le regioni con percentuale 0 per la causa selezionata
            all_regions = pd.DataFrame({
                'Region': selected_regions,
                'Cause of Death': selected_cause,
                'Count': 0,
                'Percent': 0
            })
            filtered_data = pd.concat([filtered_data, all_regions], ignore_index=True)
            filtered_data = filtered_data.drop_duplicates(subset=['Region', 'Cause of Death'], keep='first')

            ordered_regions = (
                filtered_data[filtered_data['Cause of Death'] == selected_cause]
                .sort_values(by='Percent', ascending=False)['Region']
                .tolist()
            )

            # Mantieni l'ordine delle regioni
            filtered_data['Region'] = pd.Categorical(filtered_data['Region'], categories=ordered_regions, ordered=True)
        else:
            # Se "None", lascia l'ordine normale
            ordered_regions = filtered_data['Region'].unique().tolist()

        # assegna un valore numerico per l'ordinamento della causa di morte
        filtered_data = filtered_data.copy()  # evita il warning di pandas
        filtered_data.loc[:, "sort_order"] = filtered_data["Cause of Death"].apply(lambda x: 0 if x == selected_cause else 1)

        # Creazione del grafico a barre impilate con colori espliciti
        chart = alt.Chart(filtered_data).mark_bar().encode(
            y=alt.X('Region:N', title='Regione', sort=ordered_regions),
            x=alt.Y('Percent:Q', title='Percentuale', stack="normalize"),
            color=alt.Color('Cause of Death:N', title='Causa di Morte', scale=color_scale),
            order=alt.Order('sort_order:Q', sort='ascending'),
            tooltip=[
                alt.Tooltip('Region:N', title='Regione'),
                alt.Tooltip('Cause of Death:N', title='Causa di Morte'),
                alt.Tooltip('Percent:Q', title='Percentuale', format='.2f')
            ]
        ).properties(
            width=600,
            height=400,
            title=f"Percentuale delle Cause di Morte per Regione (ordinato per '{selected_cause}')"
        )

        # Mostra il grafico
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Nessuna regione selezionata.")

    st.markdown(
    "Ordinando il grafico in base alla causa di morte **Drowning (annegamento)**, emergono in prima posizione le regioni del "
    "**Mediterraneo** e dei **Caraibi**, un risultato pienamente in linea con le aspettative. Queste due aree sono infatti caratterizzate "
    "da pericolose rotte marittime, lungo le quali il rischio di naufragi è estremamente elevato.\n\n"
    
    "D'altro canto, se si seleziona l'ordinamento per **Mixed or unknown**, le regioni con la percentuale più alta risultano essere il "
    "**Nord Africa** e il **Nord America**. Questo dato è particolarmente significativo, in quanto suggerisce che in queste zone "
    "le circostanze esatte del decesso rimangono spesso sconosciute, probabilmente a causa della difficoltà nel recupero dei corpi "
    "o della mancanza di informazioni dettagliate sugli eventi che hanno portato alla morte dei migranti.\n\n"
    
    "Questa differenza evidenzia come le **dinamiche della mortalità migratoria** varino sensibilmente in base alla regione, "
    "riflettendo sia le condizioni ambientali che il livello di tracciabilità degli incidenti."
    )

###################################################################################################################################
# ANALISI GEOSPAZIALE
#1. Mappa dei punti sulla base delle coordinate
def points_map(map_style):
    st.markdown("---")
    st.write("## Mappa dei punti sulla base delle coordinate")

    st.write("""
    Questa mappa è completamente interattiva e può essere ingrandita o rimpicciolita a piacere per analizzare con maggiore dettaglio le diverse aree geografiche. 
    Ogni punto rappresenta un evento registrato e la sua dimensione è proporzionale al numero totale di morti e dispersi associati all'incidente: 
    eventi con un maggior numero di vittime sono visualizzati con punti più grandi.
    """)

    #pulizia del DataFrame eliminando righe con NaN in 'Coordinates', creazione copia
    datapd_cleaned = datapd.dropna(subset=["Coordinates"]).copy()

    #conversione delle coordinate in liste di float (invertendo ordine lat/lon)
    datapd_cleaned["Coordinates"] = datapd_cleaned["Coordinates"].apply(
        lambda x: [float(coord.strip()) for coord in x.split(",")][::-1]  # Inverte l'ordine lat/lon
    )

    #calcolo del raggio usando la radice quadrata
    datapd_cleaned["radius"] = datapd_cleaned["Total Number of Dead and Missing"].apply(
        lambda x: math.sqrt(x)
    )

    datapd_cleaned[["lng", "lat"]] = pd.DataFrame(datapd_cleaned["Coordinates"].tolist(), index=datapd_cleaned.index)

    #creazione del layer Pydeck
    layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_cleaned,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,  # amplifica il raggio calcolato
        radius_min_pixels=1.5,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position="Coordinates",  # ordine corretto: [longitudine, latitudine]
        get_radius="radius",
        get_fill_color=[204, 0, 0],
        get_line_color=[0, 0, 0],
        aggregation=pdk.types.String("SUM")
    )

    #configurazione della vista iniziale della mappa
    view = pdk.data_utils.compute_view(datapd_cleaned[["lng", "lat"]])
    view.zoom = 1  #maggiore dettaglio
    view.latitude=30
    view.longitude=-8
    view.max_zoom=8
    view.min_zoom=0.7

    #configurazione della mappa Pydeck
    map_deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip={"html": "Totale di morti e dispersi: {Total Number of Dead and Missing}<br>Data della tragedia: {Incident Date}"},
    map_provider="mapbox",
    map_style=map_style
    )

    st.pydeck_chart(map_deck)

    st.write("""
    Questa mappa mette in evidenza come il fenomeno delle tragedie migratorie non sia limitato all’Europa o al Nord America, 
    ma rappresenti una crisi umanitaria su scala globale. Gli eventi segnati si distribuiscono lungo molteplici rotte migratorie, 
    attraversando continenti e mostrando come regioni dell’Africa, del Medio Oriente, dell’Asia e dell’America Latina siano 
    altrettanto colpite. Il Mediterraneo, il deserto del Sahara, il confine tra Messico e Stati Uniti e le rotte marittime 
    dell’Asia sud-orientale sono solo alcune delle aree dove i migranti affrontano pericoli estremi nel tentativo di trovare 
    sicurezza e migliori condizioni di vita.

    Questa visualizzazione aiuta a comprendere che la crisi migratoria è una questione universale, che coinvolge governi, 
    organizzazioni internazionali e società civili di tutto il mondo. La sua risoluzione richiede una cooperazione globale 
    per affrontare le cause profonde delle migrazioni forzate e garantire percorsi più sicuri per chi è costretto a fuggire.
    """)

    return datapd_cleaned

#2. Heatmap dei punti sulla base delle coordinate
def heatmap(datapd_cleaned, map_style):
    st.markdown("---")
    st.write("## Heatmap delle regioni geografiche più colpite")

    st.write("""
    Questo grafico rappresenta una heatmap che evidenzia le aree geografiche con il maggior numero di morti e dispersi 
    registrati lungo le rotte migratorie. Le zone più scure indicano una densità più elevata di tragedie, mostrando i luoghi 
    dove il fenomeno è particolarmente critico. La mappa è interattiva e si adatta dinamicamente allo zoom, permettendo 
    di osservare i dettagli con maggiore precisione a seconda del livello di ingrandimento. Questa funzionalità consente 
    di esplorare l’impatto della crisi migratoria sia a livello globale che locale.
    """)

    # Calcolo dei pesi (amplificati per una maggiore visibilità)
    datapd_cleaned["weight"] = (
        datapd_cleaned["Total Number of Dead and Missing"] / datapd_cleaned["Total Number of Dead and Missing"].max()
    ) * 100

    # Configuro la vista iniziale della mappa
    view = pdk.data_utils.compute_view(datapd_cleaned[["lng", "lat"]])
    view.zoom = 1.4 
    view.latitude = 30
    view.longitude = -43
    view.max_zoom=8
    view.min_zoom=0.7

    # Definizione della scala di colori IDENTICA alla heatmap
    COLOR_BREWER_SCALE5 = [
        [230, 0, 0],     
        [204, 0, 0],     
        [179, 0, 0],     
        [153, 0, 0],   
        [128, 0, 0],
        [102, 0, 0],
        [77, 0, 0],
        [51, 0, 0],
        [26, 0, 0]
    ]

    # Configura il layer Heatmap
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=datapd_cleaned,
        opacity=0.9,
        get_position=["lng", "lat"],  # Coordinate lat/lon
        aggregation=pdk.types.String("SUM"),  # Aggregazione basata sulla somma
        color_range=COLOR_BREWER_SCALE5,  # Usa la lista di colori senza NumPy
        threshold=0.07,  # Soglia abbassata per intensificare la visibilità
        get_weight="weight",  # Peso per ogni punto
        pickable=True,  # Abilita il tooltip per ogni punto
        stroked=True  
    )

    # Crea la mappa Pydeck
    heatmap_map = pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view,
        map_provider="mapbox",
        map_style=map_style,
        tooltip={"text": "Heatmap basata sui pesi calcolati"},
    )

    # Layout con colonna per Heatmap + Colorbar a fianco
    col1, col2 = st.columns([5, 1])  # Più spazio alla mappa

    with col1:
        st.pydeck_chart(heatmap_map, use_container_width=True)

    with col2:
        # **Creazione della colorbar**
        fig, ax = plt.subplots(figsize=(0.6, 8))  # Aumentata altezza per allinearla alla mappa
        cmap = plt.matplotlib.colors.LinearSegmentedColormap.from_list("custom_cmap", np.array(COLOR_BREWER_SCALE5) / 255)
        norm = plt.Normalize(vmin=0, vmax=100)  # Normalizza tra 0 e 100

        # Crea la barra dei colori
        cb = plt.colorbar(plt.cm.ScalarMappable(norm=norm, cmap=cmap), cax=ax, orientation='vertical')
        cb.set_label("Densità relativa di morti e dispersi", fontsize=10, labelpad=10, color="white")

        # Imposta il colore del testo e dei numeri in bianco
        cb.ax.yaxis.set_tick_params(color='white')
        cb.ax.yaxis.label.set_color('white')
        plt.setp(ax.yaxis.get_ticklabels(), color="white")

        # **Rendi i bordi della colorbar bianchi**
        cb.outline.set_edgecolor("white")

        # **Allineamento della barra alla mappa**
        ax.set_aspect(0.35)  # Proporzione verticale migliorata
        plt.subplots_adjust(left=0.4, right=0.6, top=1, bottom=0)  # Rimuove spazio in eccesso

        # Salva l'immagine in un buffer
        buf = io.BytesIO()
        plt.savefig(buf, format="png", bbox_inches="tight", transparent=True)
        buf.seek(0)
        
        # Mostra la colorbar in Streamlit
        st.image(buf, use_container_width=True)
    
    st.write("""
    Questa heatmap fornisce un'evidenza visiva dell'entità della crisi migratoria, mettendo in luce le regioni del mondo 
    dove il numero di vittime è particolarmente elevato. Le concentrazioni più intense di morti e dispersi non sono casuali, 
    ma riflettono i pericoli estremi affrontati dai migranti in specifiche rotte, come il Mediterraneo centrale, il deserto del 
    Sahara e il confine tra Messico e Stati Uniti. Questa rappresentazione non solo aiuta a identificare le aree più colpite, 
    ma solleva anche interrogativi fondamentali sulle cause e sulle possibili soluzioni per mitigare queste tragedie. 
    
    A differenza della mappa a punti, che mostra la localizzazione esatta degli eventi registrati, la heatmap permette di 
    visualizzare le aree in cui si concentra il maggior numero di tragedie, rendendo più immediata la percezione dell'impatto 
    geografico complessivo e facilitando il riconoscimento delle zone più critiche.
    """)

#3. Mappa dei punti colorati per categoria
def points_map_by_cat(datapd_cleaned, map_style):
    st.markdown("---")
    st.write("## Mappa dei punti colorati per categoria")

    st.write("""
    Questa mappa interattiva offre la possibilità di visualizzare gli eventi migratori secondo due diverse categorie: 
    la **causa di morte** o la **rotta migratoria**. Selezionando una delle opzioni disponibili, i punti sulla mappa verranno 
    colorati in base alla variabile scelta, permettendo di identificare rapidamente le dinamiche degli eventi registrati.  

    La colorazione per **causa di morte** consente di distinguere le circostanze delle tragedie, come annegamenti, violenze o 
    condizioni ambientali estreme. In alternativa, la classificazione per **rotta migratoria** aiuta a comprendere le traiettorie 
    seguite dai migranti e le zone in cui gli incidenti avvengono con maggiore frequenza.
    """)

    #opzioni per la selezione della categoria
    categories = ["Cause of Death", "Migrantion route"]
    selected_category = st.pills(
        "Seleziona una categoria per colorare i punti sulla mappa",
        options=categories,
        default="Cause of Death"
    )

    # se l'utente non seleziona una categoria, mostra un avviso
    if not selected_category:
        st.warning("Seleziona una categoria per procedere.")
        return
    
    # rimuoviamo eventuali righe con NaN nella categoria selezionata
    datapd_filtered = datapd_cleaned.dropna(subset=[selected_category]).copy()

    # mappatura dei colori univoci per la categoria selezionata
    unique_categories = datapd_filtered[selected_category].unique()
    color_palette = [
    [255, 0, 0],    # Rosso
    [0, 255, 0],    # Verde
    [255, 255, 0],  # Giallo
    [255, 0, 255],  # Magenta
    [0, 255, 255],  # Ciano
    [128, 0, 0],    # Rosso scuro
    [139, 69, 19],  # Marrone cioccolato
    [128, 128, 0],  # Verde oliva
    [255, 165, 0],  # Arancione
    [75, 0, 130],   # Indaco
    [255, 192, 203],# Rosa
    [173, 216, 230],# Azzurro chiaro
    [32, 145, 134], # Turchese
    [255, 0, 221],  # Fucsia
    [127, 255, 0],  # Verde lime
    [220, 20, 60],  # Cremisi
    [0, 206, 209],  # Turchese scuro
    [138, 43, 226], # Blu violetto
    [255, 215, 0],  # Oro
    [0, 0, 255],    # Blu
    [0, 0, 128],    # Blu scuro
    [0, 128, 0],    # Verde scuro
    ]
 
    color_mapping = {category: color_palette[i % len(color_palette)] for i, category in enumerate(unique_categories)}
    datapd_filtered["color"] = datapd_filtered[selected_category].map(color_mapping)

    # creazione del layer Pydeck
    layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_filtered,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,
        radius_min_pixels=1.5,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position=["lng", "lat"],  #lng e lat
        get_radius="radius",
        get_fill_color="color",
        get_line_color=[0, 0, 0],
    )

    # configurazione della vista iniziale della mappa
    view = pdk.ViewState(latitude=30, longitude=-8, zoom=1, max_zoom=8, min_zoom=0.7)

    # configurazione della mappa Pydeck
    map_deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "html": f"{selected_category}: {{{selected_category}}}<br>Totale morti e dispersi: {{Total Number of Dead and Missing}}",
            "style": {"color": "white"},
        },
        map_provider="mapbox",
        map_style=map_style
    )

    # mostra la mappa
    st.pydeck_chart(map_deck)

    # aggiunta della legenda con i colori associati alle categorie
    st.write("#### Legenda dei colori")

    # creazione della legenda usando Markdown e HTML
    legend_html = "<div style='display: flex; flex-wrap: wrap; gap: 10px;'>"
    for category, color in color_mapping.items():
        color_rgb = f"rgb({color[0]}, {color[1]}, {color[2]})"
        legend_html += f"""
<div style='display: flex; align-items: center; margin-bottom: 5px;'>
    <div style='width: 20px; height: 20px; background-color: {color_rgb}; margin-right: 10px; border: 1px solid #000;'></div>
    <span style='font-size: 14px;'>{category}</span>
</div>
        """
    legend_html += "</div>"

    st.markdown(legend_html, unsafe_allow_html=True)

    st.write("""
    Come evidenziato anche nel grafico a barre sovrapposte, la causa di morte più frequente nelle tragedie migratorie è l’annegamento (**Drowning**). 
    Questa tendenza è particolarmente evidente nelle rotte che attraversano il **Mediterraneo centrale** e la **regione caraibica**, 
    dove i viaggi in mare avvengono spesso in condizioni estreme e con imbarcazioni precarie.  
    
    Un altro aspetto rilevante è l'alta frequenza della categoria **Mixed or Unknown** lungo il **confine tra Messico e Stati Uniti**, 
    dove molte morti di migranti non vengono chiaramente attribuite a una causa specifica. Questo riflette le difficoltà nel determinare 
    le circostanze esatte degli incidenti, spesso legati a condizioni ambientali estreme o alla violenza.  
    
    Selezionando invece la variabile **Migration route**, i punti vengono suddivisi in gruppi ben distinti, 
    permettendo di visualizzare chiaramente le principali rotte seguite dai migranti e le aree in cui si verificano i maggiori eventi tragici.
    """)


################################################################################################################
# ANALISI DEI GRUPPI
#1. Gruppo del mediterraneo
def mediterranean_group(map_style):
    st.markdown("---")
    st.write("### Gruppo dei punti nel Mediterraneo")

    # Filtriamo il dataframe per la regione "Mediterranean"
    datapd_med = datapd[datapd["Region"] == "Mediterranean"].dropna(subset=["Coordinates"]).copy()

    # Conversione delle coordinate in liste di float e creazione di colonne separate per lat/lon
    datapd_med["Coordinates"] = datapd_med["Coordinates"].apply(
        lambda x: [float(coord.strip()) for coord in x.split(",")][::-1]  # Invertiamo l'ordine lat/lon
    )

    datapd_med["radius"] = datapd_med["Total Number of Dead and Missing"].apply(
        lambda x: math.sqrt(x)
    )

    datapd_med[["lng", "lat"]] = pd.DataFrame(datapd_med["Coordinates"].tolist(), index=datapd_med.index)

    # Creiamo un array numpy con tutte le coordinate aggiornate
    points = np.array(datapd_med[["lng", "lat"]])

    # Calcoliamo l'inviluppo convesso (convex hull)
    hull = ConvexHull(points)
    hull_coordinates = [points[i].tolist() for i in hull.vertices]

    # Chiudiamo il poligono tornando al primo punto
    hull_coordinates.append(hull_coordinates[0])

    # Creiamo il layer con i punti
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_med,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,  # Amplifica il raggio calcolato
        radius_min_pixels=2,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position="Coordinates",
        get_radius="radius",
        get_fill_color=[204, 0, 0],
        get_line_color=[0, 0, 0],
    )

    # Creiamo il layer con il poligono che racchiude i punti
    polygon_data = [
        {"polygon": hull_coordinates, "name": "Mediterranean Convex Hull"}
    ]

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        polygon_data,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_polygon="polygon",
        get_fill_color=[255, 255, 255, 150],  # Bianco semi-trasparente
        get_line_color=[255, 255, 255],  # Bordo bianco
    )

    # Configurazione della vista iniziale della mappa
    view = pdk.ViewState(latitude=37, longitude=13.7, zoom=3.4, min_zoom=3.1, max_zoom=8)

    # Creazione della mappa Pydeck con entrambi i layer
    map_deck = pdk.Deck(
        layers=[polygon_layer, points_layer],  # Sovrapposizione dei layer
        initial_view_state=view,
        tooltip={"html": "Morti e dispersi: {Total Number of Dead and Missing}<br>Data: {Incident Date}"},
        map_provider="mapbox",
        map_style=map_style
    )

    # Mostriamo la mappa
    st.pydeck_chart(map_deck)

#2. Gruppo del confine tra Messico e Stati Uniti
def mexico_us_border_group(map_style):
    st.markdown("---")
    st.write("### Gruppo dei punti sul confine tra Messico e Stati Uniti")

    # Filtriamo il dataframe per le regioni North America e Central America
    datapd_border = datapd[datapd["Region"].isin(["North America", "Central America"])].dropna(subset=["Coordinates"]).copy()

    # Conversione delle coordinate in liste di float e creazione di colonne separate per lat/lon
    datapd_border["Coordinates"] = datapd_border["Coordinates"].apply(
        lambda x: [float(coord.strip()) for coord in x.split(",")][::-1]  # Invertiamo l'ordine lat/lon
    )

    datapd_border["radius"] = datapd_border["Total Number of Dead and Missing"].apply(
        lambda x: math.sqrt(x)
    )

    datapd_border[["lng", "lat"]] = pd.DataFrame(datapd_border["Coordinates"].tolist(), index=datapd_border.index)

    # **Filtriamo i punti per prendere solo quelli vicini al confine Messico-USA**
    datapd_border = datapd_border[
        (datapd_border["lat"] >= 25) & (datapd_border["lat"] <= 33) &  # Limiti di latitudine
        (datapd_border["lng"] >= -118) & (datapd_border["lng"] <= -95)  # Limiti di longitudine
    ]

    # **Rettangolo 1: Rimuoviamo i punti nella Bassa California (Sud-Ovest)**
    datapd_border = datapd_border[
        ~((datapd_border["lat"] < 30) & (datapd_border["lng"] < -104))  # Sud-Ovest, Baja California
    ]

    datapd_border = datapd_border[
    ~((datapd_border["lat"] > 25) & (datapd_border["lat"] < 29) & 
      (datapd_border["lng"] > -107) & (datapd_border["lng"] < -102))
    ]

    datapd_border = datapd_border[
    ~((datapd_border["lat"] > 24) & (datapd_border["lat"] < 27) & 
      (datapd_border["lng"] > -101.5) & (datapd_border["lng"] < -99))
    ]

    # Creiamo un array numpy con tutte le coordinate aggiornate
    points = np.array(datapd_border[["lng", "lat"]])

    # Calcoliamo l'inviluppo convesso (convex hull)
    hull = ConvexHull(points)
    hull_coordinates = [points[i].tolist() for i in hull.vertices]

    # Chiudiamo il poligono tornando al primo punto
    hull_coordinates.append(hull_coordinates[0])

    # Creiamo il layer con i punti
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_border,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,  # Amplifica il raggio calcolato
        radius_min_pixels=2,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position="Coordinates",
        get_radius="radius",
        get_fill_color=[204, 0, 0],  # Punti rossi
        get_line_color=[0, 0, 0],
    )

    # Creiamo il layer con il poligono che racchiude i punti
    polygon_data = [
        {"polygon": hull_coordinates, "name": "Mexico-US Border Convex Hull"}
    ]

    polygon_layer = pdk.Layer(
        "PolygonLayer",
        polygon_data,
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_polygon="polygon",
        get_fill_color=[255, 255, 255, 150],  # Bianco semi-trasparente
        get_line_color=[255, 255, 255],  # Bordo bianco
    )

    # Configurazione della vista iniziale della mappa centrata sulla zona del confine
    view = pdk.ViewState(latitude=29, longitude=-107, zoom=4.5, min_zoom=4.1,  max_zoom=8)

    # Creazione della mappa Pydeck con entrambi i layer
    map_deck = pdk.Deck(
        layers=[polygon_layer, points_layer],  # Sovrapposizione dei layer
        initial_view_state=view,
        tooltip={"html": "Morti e dispersi: {Total Number of Dead and Missing}<br>Data: {Incident Date}"},
        map_provider="mapbox",
        map_style=map_style
    )

    # Mostriamo la mappa
    st.pydeck_chart(map_deck)

#3. Gruppo del deserto del Sahara
def sahara_desert_group(map_style):
    st.markdown("---")
    st.write("### Gruppo dei punti nel Deserto del Sahara")

    # Definizione del bounding box (rettangolo verde)
    lat_min, lat_max = 12, 35  # Limiti di latitudine
    lng_min, lng_max = -15, 40  # Limiti di longitudine

    # Filtro per la rotta migratoria
    datapd_sahara = datapd[datapd["Migrantion route"] == "Sahara Desert crossing"].dropna(subset=["Coordinates"]).copy()

    # Parsing delle coordinate
    def parse_coordinates(coord):
        try:
            lat, lng = map(float, coord.split(","))
            return [lng, lat]  # Inversione corretta lat/lng
        except (ValueError, AttributeError):
            return None

    datapd_sahara["Coordinates"] = datapd_sahara["Coordinates"].apply(parse_coordinates)
    datapd_sahara = datapd_sahara.dropna(subset=["Coordinates"])

    # Creazione colonne lng/lat
    datapd_sahara[["lng", "lat"]] = pd.DataFrame(datapd_sahara["Coordinates"].tolist(), index=datapd_sahara.index)

    # Filtro per il bounding box
    datapd_sahara = datapd_sahara[
        (datapd_sahara["lat"] >= lat_min) & (datapd_sahara["lat"] <= lat_max) &
        (datapd_sahara["lng"] >= lng_min) & (datapd_sahara["lng"] <= lng_max)
    ]

    # Calcolo raggio
    datapd_sahara["radius"] = datapd_sahara["Total Number of Dead and Missing"].apply(math.sqrt)

    points = np.array(datapd_sahara[["lng", "lat"]])
    hull = ConvexHull(points)
    hull_coordinates = [points[i].tolist() for i in hull.vertices] + [points[hull.vertices[0]].tolist()]
    
    # Layer punti
    points_layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_sahara,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,
        radius_min_pixels=2,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position=["lng", "lat"],
        get_radius="radius",
        get_fill_color=[204, 0, 0],
        get_line_color=[0, 0, 0],
    )

    # Layer poligono
    polygon_layer = pdk.Layer(
        "PolygonLayer",
        [{"polygon": hull_coordinates}] if hull_coordinates else [],
        stroked=True,
        filled=True,
        line_width_min_pixels=2,
        get_polygon="polygon",
        get_fill_color=[255, 255, 255, 150],
        get_line_color=[255, 255, 255]
    )

    # Configurazione mappa
    view = pdk.ViewState(latitude=24, longitude=13, zoom=3.2, max_zoom=8, min_zoom=3)
    map_deck = pdk.Deck(
        layers=[polygon_layer, points_layer],
        initial_view_state=view,
        tooltip={"html": "Morti e dispersi: {Total Number of Dead and Missing}<br>Data: {Incident Date}"},
        map_provider="mapbox",
        map_style=map_style
    )

    st.pydeck_chart(map_deck)

## Implementazione Pagine ######################################################################################
def page_introduction():
    st.title(":red[Missing] Migrants Project")
    st.markdown("""
    <div style="border: 1px solid white; padding: 15px; background-color: #2b2b2b; margin-bottom: 15px;">
        <b>Nota:</b> Attiva il tema scuro per una migliore esperienza. Vai su <b>Menu (in alto a destra)</b> > <b>Settings</b> > <b>Theme</b> > <b>Dark</b>.
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("""
    Il mondo sta affrontando una crisi migratoria. In un’era di esodi e sfollamenti forzati, i governi ospitanti nei paesi sviluppati si sono sempre più impegnati a respingere i migranti.
    """)

    total_dead_missing = datapd["Total Number of Dead and Missing"].sum()
    st.markdown(f"""
    ### Dal 2014 al 2021, oltre **:red[{total_dead_missing}]** migranti sono morti o scomparsi nel loro viaggio verso una vita migliore.
    """)
    
    migration_tragedies()
    dataframe()
    st.markdown("""
    #### Prosegui con l'analisi
    Per approfondire ulteriormente, esplora le altre sezioni disponibili nel menu a sinistra.
    """)
    
def page_descriptive_analysis():
    st.title("Analisi Descrittive")

    st.markdown(
        "In questa sezione si propone un'analisi descrittiva delle variabili presenti nel dataset, "
        "con l'obiettivo di fornire una panoramica generale sulla loro distribuzione e sulle caratteristiche principali dei dati raccolti."
    )

    regions_map()
    timeseries()
    barchart()
    piechart()
    stackedbarchart()

    st.markdown("""
    #### Prosegui con l'analisi
    Per approfondire ulteriormente, esplora le altre sezioni disponibili nel menu a sinistra.
    """)

def page_geo_analysis():
    st.title("Visualizzazione Geospaziale delle Tragedie Migratorie")

    st.write("""
    In questa sezione si offre una rappresentazione visiva degli eventi tragici legati alla migrazione a livello globale. 
    Attraverso una serie di mappe interattive, è possibile individuare i punti in cui si sono verificati incidenti, 
    fornendo così un quadro chiaro dell’impatto geografico del fenomeno. 
    L'obiettivo è quello di evidenziare la distribuzione delle tragedie nel contesto mondiale, 
    permettendo una comprensione più approfondita della crisi umanitaria legata ai flussi migratori.

    A supporto dell’analisi, viene riportata un’immagine rappresentativa delle principali rotte migratorie globali. 
    Questa mappa, pur essendo semplificata, offre un'indicazione chiara e immediata delle traiettorie percorse dai migranti 
    e delle aree di maggiore transito e rischio.
    """)

    image_folder = Path("images")
    image_path = image_folder / "flussi migratori2.png"
    st.image(str(image_path), use_container_width=True)

    st.write("""
    È inoltre possibile personalizzare la visualizzazione selezionando la tipologia di mappa preferita, 
    scegliendo tra una mappa politica e una mappa satellitare, 
    in modo da adattare l’analisi alle proprie esigenze di esplorazione dei dati.
    """)

    map_style_options = ["Mappa Politica", "Mappa Satellitare"]
    selected_map_style = st.pills(
        "Seleziona il tipo di mappa",
        map_style_options,
        default="Mappa Satellitare"
    )

    # controllo se l'utente ha selezionato un'opzione
    if not selected_map_style:
        st.warning("Seleziona un tipo di mappa per visualizzarle.")
        return
    
    if selected_map_style == "Mappa Politica":
        map_style = pdk.map_styles.CARTO_DARK
    elif selected_map_style == "Mappa Satellitare":
        map_style = pdk.map_styles.SATELLITE

    datapd_cleaned = points_map(map_style)
    heatmap(datapd_cleaned, map_style)
    points_map_by_cat(datapd_cleaned, map_style)

    st.markdown("""
    #### Prosegui con l'analisi
    Per approfondire ulteriormente, esplora le altre sezioni disponibili nel menu a sinistra.
    """)

def page_group_analysis():
    st.title("Analisi dei gruppi")
    map_style_options = ["Mappa Politica", "Mappa Satellitare"]
    selected_map_style = st.pills(
        "Seleziona il tipo di mappa",
        map_style_options,
        default="Mappa Politica"
    )

    # controllo se l'utente ha selezionato un'opzione
    if not selected_map_style:
        st.warning("Seleziona un tipo di mappa per visualizzarle.")
        return
    
    if selected_map_style == "Mappa Politica":
        map_style = pdk.map_styles.CARTO_DARK
    elif selected_map_style == "Mappa Satellitare":
        map_style = pdk.map_styles.SATELLITE

    mediterranean_group(map_style)
    mexico_us_border_group(map_style)
    sahara_desert_group(map_style)

# configurazione navigazione
pages = {
    "Introduzione": page_introduction,
    "Analisi descrittive": page_descriptive_analysis,
    "Analisi geospaziali": page_geo_analysis,
    "Analisi dei gruppi": page_group_analysis
}

st.sidebar.title("Navigazione")
selection = st.sidebar.radio("Vai a:", list(pages.keys()))

# esegue la pagina selezionata
pages[selection]()