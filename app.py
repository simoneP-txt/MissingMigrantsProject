import streamlit as st
import polars as pl
import altair as alt
import pandas as pd
import numpy as np
import datetime as dt

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
    return data

data = load_data()
datapd = data.to_pandas()

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
def timeseries():
    st.title("Analisi Descrittive")
    
    # Serie storica del numero totale di morti e dispersi
    datapd['Incident_Date'] = pd.to_datetime(datapd['Incident Date'], format='%a, %m/%d/%Y - %H:%M', errors='coerce').dt.date
    datapd.dropna(subset=['Incident_Date'], inplace=True)

    regions = data['Region'].unique().sort().to_list()
    selected_regions = st.multiselect(
        'Seleziona le regioni di interesse',
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
    ]

    filtered_data["Incident_Date"] = pd.to_datetime(filtered_data["Incident_Date"], errors="coerce")
    filtered_data["Year_Month"] = filtered_data["Incident_Date"].dt.to_period("M")

    aggregated_data = filtered_data.groupby(["Year_Month", "Region"]).agg({
        "Total Number of Dead and Missing": "mean"
    }).reset_index()

    aggregated_data["Year_Month"] = aggregated_data["Year_Month"].dt.to_timestamp()

    nearest = alt.selection_point(
        nearest=True, on="pointerover", fields=["Year_Month"], empty="none"
    )

    line = alt.Chart(aggregated_data).mark_line().encode(
        x=alt.X("Year_Month:T", title="Anno e Mese"),
        y=alt.Y("Total Number of Dead and Missing:Q", title="Media mensile del numero totale di morti e dispersi"),
        color=alt.Color("Region:N", title="Regione"),
        tooltip=[
            alt.Tooltip("Year_Month:T", title="Data"),
            alt.Tooltip("Region:N", title="Regione"),
            alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".2f")
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
            alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".2f")
        ]
    )

    text = line.mark_text(align="left", dx=5, dy=-5).encode(
        text=alt.condition(nearest, alt.Text("Total Number of Dead and Missing:Q", format=".2f"), alt.value(""))
    )

    rules = alt.Chart(aggregated_data).mark_rule(color="gray").encode(
        x="Year_Month:T",
        tooltip=[
            alt.Tooltip("Year_Month:T", title="Data"),
            alt.Tooltip("Region:N", title="Regione"),
            alt.Tooltip("Total Number of Dead and Missing:Q", title="Morti e dispersi", format=".2f")
        ]
    ).transform_filter(nearest)

    timeseries = alt.layer(
        line, selectors, points, rules, text
    ).properties(
        width=600, height=400
    )

    st.altair_chart(timeseries, use_container_width=True)

def barchart():
    # Distribuzione delle variabili categoriche
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

def piechart():
    # Distribuzione assoluta delle vittime per regione
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

    base_chart = alt.Chart(altair_data).transform_aggregate(
        total="sum(Count)", groupby=["Region", "Category", "Total"]
    )

    base_pie = (
        base_chart.mark_arc(innerRadius=50, outerRadius=80, stroke="white", strokeWidth=0.5).encode(
            theta=alt.Theta("total:Q", stack=True),
            color=alt.Color("Category:N", scale=alt.Scale(scheme="category10"), title="Categoria"),
            tooltip=["Region:N", "Category:N", alt.Tooltip("total:Q", title="Numero")]
        )
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

    chart = (base_pie + text_pie + text_total).properties(
        width=150,
        height=150
    ).facet(
        facet=alt.Facet("Region:N", title="Regione"),
        columns=4
    )

    st.altair_chart(chart, use_container_width=True)
    
####################################################################
#4. Causa di morte per regione



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
    timeseries()
    barchart()
    piechart()

def page_geo_analysis():
    st.title("Analisi geospaziali")
    st.write("sezione in fase di sviluppo.")

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