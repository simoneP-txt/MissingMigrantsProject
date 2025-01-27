import streamlit as st
import polars as pl
import altair as alt
import pandas as pd
import numpy as np
import datetime as dt
import pydeck as pdk
import math

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
        "Cause of Death", "Coordinates", "Migrantion route", "UNSD Geographical Grouping"])
    )
    data = data.with_columns(
    data["Incident Date"]
    .str.extract(r"^(\w{3}, \d{2}/\d{2}/\d{4})")  # Estrarre solo giorno della settimana e data
    .alias("Incident Date")  # Sovrascrive la colonna esistente
    )
    datapd = data.to_pandas()
    return data, datapd

data, datapd = load_data()

def dataframe():
    st.dataframe(data, use_container_width=True)

    data_description = {
        "Variabili": [
            "Region", "Incident Date", "Year", "Reported Month", "Number Dead",
            "Minimum Estimated Number of Missing", "Total Number of Dead and Missing", 
            "Number of Survivors", "Number of Females", "Number of Males", "Number of Children",
            "Cause of Death", "Coordinates", "Migrantion route", "UNSD Geographical Grouping"
        ],
        "Descrizione": [
            "La regione in cui si è verificato l'incidente.",
            "La data stimata della morte indica il ritrovamento dei corpi o la data riportata da testimoni; se aggregata, viene segnata come 'totale cumulativo'.",
            "L'anno in cui è avvenuto l'incidente.",
            "Il mese in cui si è verificato l'incidente.",
            "Il numero totale di persone confermate morte in un incidente, ovvero il numero di corpi recuperati. Se i migranti risultano dispersi e presunti morti, come nei casi di naufragi, viene lasciato vuoto.",
            "Il numero totale di coloro che risultano dispersi e quindi si presume siano morti. Questa variabile viene generalmente registrata negli incidenti che coinvolgono naufragi. Il numero dei dispersi si calcola sottraendo il numero dei corpi recuperati da un naufragio e il numero dei sopravvissuti dal numero totale dei migranti segnalati sulla barca. Questo numero può essere segnalato da migranti o testimoni sopravvissuti. Se non vengono segnalate persone scomparse, il campo viene lasciato vuoto.",
            "La somma delle variabili “numero morti” e “numero mancante”.",
            "Il numero di migranti sopravvissuti all'incidente, se noto. L'età, il sesso e il paese di origine dei sopravvissuti sono registrati nella variabile 'Commenti', se noti. Se sconosciuto, viene lasciato vuoto",
            "Indica il numero di femmine trovate morte o scomparse. Se sconosciuto, viene lasciato vuoto.",
            "Indica il numero di maschi trovati morti o dispersi. Se sconosciuto, viene lasciato vuoto.",
            "Indica il numero di individui di età inferiore ai 18 anni trovati morti o dispersi. Se sconosciuto, viene lasciato vuoto.",
            "La determinazione delle condizioni che hanno portato alla morte del migrante ovvero le circostanze dell'evento che ha prodotto la lesione mortale. Se sconosciuto, il motivo è incluso ove possibile. Ad esempio, “Sconosciuto – solo resti scheletrici”, viene utilizzato nei casi in cui è stato ritrovato solo lo scheletro del defunto.",
            "Luogo in cui è avvenuta la morte o dove sono stati ritrovati il corpo o i corpi. In molte regioni, in particolare nel Mediterraneo, le coordinate geografiche vengono stimate poiché spesso le posizioni precise non sono note. La descrizione della posizione deve essere sempre confrontata con le coordinate della posizione.",
            "Nome della rotta migrante sulla quale si è verificato l'incidente, se noto. Se sconosciuto, viene lasciato vuoto.",
            "Regione geografica in cui è avvenuto l'incidente, come designato dal geoschema della United Nations Statistics Division (UNSD).",
        ]
        }

    table_markdown = """
| Variabili         | Descrizione                                                                 |
|-------------------|-----------------------------------------------------------------------------|
""" + "\n".join([f"| {var} | {desc} |" for var, desc in zip(data_description["Variabili"], data_description["Descrizione"])])

    st.markdown(table_markdown)
    st.markdown('La fonte dei dati si trova a questo [link](https://www.kaggle.com/datasets/snocco/missing-migrants-project).', unsafe_allow_html=True)

###################################################################################################################################
# ANALISI DESCRITTIVA DEI DATI
#0. Mappa delle regioni del dataset

# def map():
#     st.write("### Mappa delle Regioni")
#     st.write("sezione in fase di sviluppo.")
#     #https://gist.github.com/jrrickard/8755532505a40f3b8317?short_path=999f34b#file-oceans-topo-json
#     #https://gist.githubusercontent.com/jrrickard/8755532505a40f3b8317/raw/ecd98849d3a5f4502b773b986254f19af3b8d8fb/oceans.json
#     #https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json

#     countries_map_50 = alt.topo_feature("https://cdn.jsdelivr.net/npm/world-atlas@2/countries-50m.json", 'countries')
#     #print(datapd['Region'].unique())
#     #map50 = (alt.Chart(countries_map_50)
#     #         .mark_geoshape(stroke = "black").encode(
#     #    color=alt.Color('lifeExp:Q', scale=alt.Scale(scheme='plasma', reverse = True)),
#     #    tooltip=['country:N', 'lifeExp:Q']  # tooltip per visualizzare informazioni
#     #    ).transform_lookup(
#     #    lookup='properties.name',  # chiave comune per unire (nel TopoJSON)
#     #    from_=alt.LookupData(data_07_new, 'country', ['lifeExp'])  # fonte dei dati
#     #    ).project(
#     #    type='mercator'
#     #    ).properties(
#     #    width=800,
#     #    height=600,
#     #    title="Aspettativa di vita nel 2007"
#     #    )
#     #)

#     background = alt.Chart(countries_map_50).mark_geoshape(
#         fill='lightgray',
#         stroke='darkgray'
#     ).project(
#         type= 'mercator'
#     ).properties(
#         width=800, 
#         height=600
#     ).encode(tooltip=alt.value(None))

#     data = pd.DataFrame({
#         'x': [0],   # Coordinata x
#         'y': [0],   # Coordinata y
#         'width': [800],  # Larghezza del rettangolo
#         'height': [600]  # Altezza del rettangolo
#     })

#     # Creazione del grafico
#     rect = alt.Chart(data).mark_rect(
#         cornerRadius=215,
#         color="whitesmoke"
#     ).encode(
#         x=alt.X('x:Q', scale=alt.Scale(domain=[0, 800]), axis = None),  # Scala per l'asse x
#         x2=alt.X2('width'),  # Fine del rettangolo sull'asse x
#         y=alt.Y('y:Q', scale=alt.Scale(domain=[0, 600]), axis = None),  # Scala per l'asse y
#         y2=alt.Y2('height')  # Fine del rettangolo sull'asse y
#     )

#     st.altair_chart(
#         background,
#         use_container_width=True
#     )


#1. Serie storica del numero totale di morti e dispersi per regione
def timeseries():
    st.write("### Serie storica del numero totale di morti e dispersi per regione")
    
    datapd['Incident_Date'] = pd.to_datetime(datapd['Incident Date'], format='%a, %m/%d/%Y', errors='coerce').dt.date
    datapd.dropna(subset=['Incident_Date'], inplace=True)

    regions = data['Region'].unique().sort().to_list()
    selected_regions = st.multiselect(
        'Seleziona le regioni di interesse (max 4):',
        regions,
        default="Mediterranean",
        key="region_selector",
        max_selections=4
    )

    start_date, end_date = st.slider(
        'Seleziona l\'intervallo di tempo',
        min_value=dt.date(2014, 1, 1),
        max_value=dt.date(2021, 12, 31),
        value=(dt.date(2014, 1, 1), dt.date(2021, 12, 31)),
        format="DD-MM-YYYY",
        key="date_slider"
    )

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

        nearest = alt.selection_point(
            nearest=True, on="pointerover", fields=["Year_Month"], empty="none"
        )

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

        timeseries = alt.layer(
            line, selectors, points, rules, text
        ).properties(
            width=600, height=400
        )

        st.altair_chart(timeseries, use_container_width=True)
    else:
        st.warning("Nessuna regione selezionata.")

#2. Distribuzione delle variabili categoriche
def barchart():
    st.write("### Distribuzione delle variabili categoriche")
    columns = ['Region', 'Cause of Death', 'Migrantion route']

    selected_variable = st.pills(
        'Seleziona una variabile per visualizzare la distribuzione',
        columns,
        default="Region"
    )

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

#3. Distribuzione assoluta delle vittime per regione
def piechart():
    st.write("### Distribuzione assoluta delle vittime per regione")

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
    
    highlight = alt.selection_point(
        name="highlight",
        fields=["Region", "Category"], 
        on="pointerover", 
        nearest=True, 
        empty="none",
        clear="mouseout"
        )
    
    change_stroke = alt.condition(
        highlight,
        alt.value(3),
        alt.value(0.5)
    )

    base_chart = alt.Chart(altair_data).transform_aggregate(
        total="sum(Count)", groupby=["Region", "Category", "Total"]
    )

    base_pie = (
        base_chart.mark_arc(innerRadius=50, outerRadius=80, stroke="white", strokeWidth=0.5).encode(
            theta=alt.Theta("total:Q", stack=True),
            color=alt.Color("Category:N", scale=alt.Scale(scheme="category10"), title="Categoria"),
            tooltip=["Region:N", "Category:N", alt.Tooltip("total:Q", title="Numero")],
            #strokeWidth=change_stroke
        )#.add_params(
        #     highlight
        # )
    )

    text_pie = (
        base_chart.mark_text(radius=100, size=14).encode(
            theta=alt.Theta("total:Q", stack=True),
            text=alt.Text("total:Q", format=".0f"),
            color=alt.value("white")
        )
    )

    text_total = (
        base_chart.mark_text(size=20, fontWeight="bold").encode(
            text=alt.Text("Total:Q", format=".0f"),
            color=alt.value("white")
        ).transform_filter(alt.datum.Category == "Male")
    )

    chart = (
            base_pie + text_pie + text_total
        ).properties(
            width=150,
            height=150
        ).facet(
            facet=alt.Facet("Region:N", title="Regione", sort=total_deaths_order),
            columns=4
        )

    st.altair_chart(chart, use_container_width=True)

#4. Causa di morte per regione
def stackedbarchart():
    st.write("### Percentuale delle Cause di Morte per Regione")

    # Calcolo della percentuale
    datapd_counts = datapd.groupby(['Region', 'Cause of Death']).size().reset_index(name='Count')
    datapd_counts['Percent'] = datapd_counts.groupby('Region')['Count'].transform(lambda x: x / x.sum() * 100)

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

    #selection = alt.selection_point(
    #    name="selection",
    #    on="pointerover",
    #    fields=['Region', 'Cause of Death'],
    #    nearest=True,
    #    empty="none",
    #    clear="mouseout"
    #    )
    #
    #change_opacity = alt.condition(
    #    selection,
    #    alt.value(1),
    #    alt.value(0.4)
    #)

    if not selected_cause:
        st.warning("Devi selezionare una causa di morte per procedere.")
        return  # Esce dalla funzione se la selezione è vuota

    if not filtered_data.empty:
        # Ordina solo se una causa di morte è selezionata
        if selected_cause != "None":
            # Aggiungi tutte le regioni con percentuale 0 per la causa selezionata
            filtered_data = filtered_data.copy()
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
            ordered_regions = None

        # Creazione del grafico a barre impilate
        chart = alt.Chart(filtered_data).mark_bar().encode(
            y=alt.X('Region:N', title='Regione', sort=ordered_regions),
            x=alt.Y('Percent:Q', title='Percentuale', stack="normalize"),
            color=alt.Color('Cause of Death:N', title='Causa di Morte'),
            #opacity=change_opacity,
            tooltip=[
                alt.Tooltip('Region:N', title='Regione'),
                alt.Tooltip('Cause of Death:N', title='Causa di Morte'),
                alt.Tooltip('Percent:Q', title='Percentuale', format='.2f')
            ]
        ).add_params(
            #selection
        ).properties(
            width=600,
            height=400,
            title=f"Percentuale delle Cause di Morte per Regione (ordinato per '{selected_cause}')"
        )

        # Mostra il grafico
        st.altair_chart(chart, use_container_width=True)
    else:
        st.warning("Nessuna regione selezionata.")
#NON riesco ad implentare il fatto che la causa di morte selezionata sia la osservazione più a
#sinistra del grafico

###################################################################################################################################
# ANALISI GEOSPAZIALE
#1. Mappa dei punti sulla base delle coordinate
def map_points():
    st.write("### Mappa dei punti sulla base delle coordinate")

    # Pulizia del DataFrame eliminando righe con NaN in 'Coordinates' e creando una copia
    datapd_cleaned = datapd.dropna(subset=["Coordinates"]).copy()

    # Conversione delle coordinate in liste di float (invertendo ordine lat/lon)
    datapd_cleaned["Coordinates"] = datapd_cleaned["Coordinates"].apply(
        lambda x: [float(coord.strip()) for coord in x.split(",")][::-1]  # Inverte l'ordine lat/lon
    )

    # Calcolo del raggio usando la radice quadrata
    datapd_cleaned["radius"] = datapd_cleaned["Total Number of Dead and Missing"].apply(
        lambda x: math.sqrt(x)
    )

    datapd_cleaned[["lng", "lat"]] = pd.DataFrame(datapd_cleaned["Coordinates"].tolist(), index=datapd_cleaned.index)

    # Creazione del layer Pydeck
    layer = pdk.Layer(
        "ScatterplotLayer",
        datapd_cleaned,
        pickable=True,
        opacity=1,
        stroked=True,
        filled=True,
        radius_scale=1000,  # Amplifica il raggio calcolato
        radius_min_pixels=1.5,
        radius_max_pixels=1000,
        line_width_min_pixels=1,
        get_position="Coordinates",  # L'ordine è ora corretto: [longitudine, latitudine]
        get_radius="radius",
        get_fill_color=[180, 0, 0],
        get_line_color=[0, 0, 0],
        aggregation=pdk.types.String("SUM")
    )

    # Configurazione della vista iniziale della mappa
    view = pdk.data_utils.compute_view(datapd_cleaned[["lng", "lat"]])
    view.zoom = 1  # Maggiore dettaglio
    view.latitude=30
    view.longitude=-8

    # Configurazione della mappa Pydeck
    map_deck = pdk.Deck(
    layers=[layer],
    initial_view_state=view,
    tooltip={"html": "Totale di morti e dispersi: {Total Number of Dead and Missing}<br>Data della tragedia: {Incident Date}"},
    map_provider="mapbox",
    map_style=pdk.map_styles.SATELLITE
    )


    # Mostra la mappa nell'app Streamlit
    st.pydeck_chart(map_deck)

    return datapd_cleaned

#2. Heatmap dei punti sulla base delle coordinate
def heatmap(datapd_cleaned):
    # Calcolo dei pesi (amplificati per una maggiore visibilità)
    datapd_cleaned["weight"] = (
        datapd_cleaned["Total Number of Dead and Missing"] / datapd_cleaned["Total Number of Dead and Missing"].max()
    ) * 100  # Fattore di scala per aumentare i pesi

    # Dividi "Coordinates" in colonne separate per lat e lng
    datapd_cleaned[["lng", "lat"]] = pd.DataFrame(datapd_cleaned["Coordinates"].tolist(), index=datapd_cleaned.index)

    # Configura la vista iniziale della mappa
    view = pdk.data_utils.compute_view(datapd_cleaned[["lng", "lat"]])
    view.zoom = 1.7  # Maggiore dettaglio
    view.latitude=30
    view.longitude=-43

    COLOR_BREWER_SCALE2 = [
    [255, 99, 71],    # Rosso leggermente più chiaro
    [255, 69, 0],     # Rosso acceso
    [220, 20, 60],    # Rosso scuro
    [139, 0, 139],    # Viola intenso
    [75, 0, 130],     # Viola super scuro (indaco)
    [30, 0, 45],      # Colore molto scuro tendente al nero
    ]

    COLOR_BREWER_SCALE3 = [
    [255, 102, 10],   # Arancione vivace
    [255, 69, 0],     # Rosso chiaro intenso
    [220, 20, 60],    # Rosso scuro
    [139, 0, 139],    # Viola intenso
    [75, 0, 130],     # Viola super scuro (indaco)
    [30, 0, 45],      # Colore scurissimo tendente al nero
    ]


    # Configura il layer Heatmap
    heatmap_layer = pdk.Layer(
        "HeatmapLayer",
        data=datapd_cleaned,
        opacity=1,
        get_position=["lng", "lat"],  # Coordinate lat/lon
        aggregation=pdk.types.String("SUM"),  # Aggregazione basata sulla somma
        color_range=COLOR_BREWER_SCALE2,  # Nuova scala di colori
        threshold=0.1,  # Soglia abbassata per intensificare la visibilità
        get_weight="weight",  # Peso per ogni punto
        pickable=True,  # Abilita il tooltip per ogni punto
    )

    # Crea la mappa Pydeck
    heatmap_map = pdk.Deck(
        layers=[heatmap_layer],
        initial_view_state=view,
        map_provider="mapbox",
        map_style=pdk.map_styles.SATELLITE,
        tooltip={"text": "Heatmap basata sui pesi calcolati"},
    )

    # Mostra la mappa in Streamlit
    st.pydeck_chart(heatmap_map)

## Implementazione Pagine ######################################################################################
def page_introduction():
    st.title(":red[Missing] Migrants Project")
    st.markdown("""
    #### Nota: Attiva il tema scuro
    Per una migliore esperienza, ti consigliamo di abilitare il tema scuro.  
    Vai su **Menu (in alto a destra)** > **Settings** > **Theme** > **Dark**.
    Grazie!
    """)
    dataframe()
    

def page_descriptive_analysis():
    st.title("Analisi Descrittive")
    #map()
    timeseries()
    barchart()
    piechart()
    stackedbarchart()

def page_geo_analysis():
    st.title("Analisi geospaziali")
    datapd_cleaned = map_points()
    heatmap(datapd_cleaned)

def page_group_analysis():
    st.title("Analisi dei gruppi")
    st.write("sezione in fase di sviluppo.")

# Configurazione della navigazione
pages = {
    "Introduzione": page_introduction,
    "Analisi descrittive": page_descriptive_analysis,
    "Analisi geospaziali": page_geo_analysis,
    "Analisi dei gruppi": page_group_analysis
}

st.sidebar.title("Navigazione")
selection = st.sidebar.radio("Vai a:", list(pages.keys()))

# Esegue la pagina selezionata
pages[selection]()