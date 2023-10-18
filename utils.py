import streamlit as st
import pandas as pd
import datetime
import time

class Period:
    WEEK = "Last Week"
    MONTH = "Last Month"
    YEAR = "A Given Year"
    ALL_TIME = "All Time"


class Region:
    ALL_REGION = 'All Region'


last_day = pd.to_datetime('2023-10-05T00:00:00+00:00').date()

is_local = True

def log_execution_time(filename="log.csv"):
    def decorator(func):
        def wrapped(*args, **kwargs):
            if is_local:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time
                timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

                with open(filename, 'a') as log_file:
                    log_file.write(f"{timestamp},{func.__name__},{execution_time:.6f}\n")

                return result
            else:
                return func(*args, **kwargs)

        return wrapped

    return decorator


@log_execution_time()
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('eco2mix-regional.csv')
    except FileNotFoundError:
        is_local = False
        df = pd.read_csv('https://elliotmv.s3.fr-par.scw.cloud/eco2mix-regional.csv')

    df_by_day = df.drop(['date_heure'], axis=1).groupby(['code_insee_region', 'libelle_region', 'date']).agg({
        'consommation': 'sum',
        'thermique': 'sum',
        'nucleaire': 'sum',
        'eolien': 'sum',
        'solaire': 'sum',
        'hydraulique': 'sum',
        'bioenergies': 'sum',
        'ech_physiques': 'sum',
    }).reset_index()
    df_by_day['date'] = pd.to_datetime(df_by_day['date'], utc=True)

    df['date'] = pd.to_datetime(df['date_heure'], utc=True)
    df = df.drop(['date_heure'], axis=1)

    # Remove data after last_day
    df = df[df['date'].dt.date <= last_day]
    df_by_day = df_by_day[df_by_day['date'].dt.date <= last_day]

    return df, df_by_day


@log_execution_time()
@st.cache_data
def total_consumption_today(df):
    df = df[df['date'].dt.date == last_day]
    return df['consommation'].sum()


@log_execution_time()
@st.cache_data
def total_consumption_yesterday(df):
    df = df[df['date'].dt.date == last_day - datetime.timedelta(days=1)]
    return df['consommation'].sum()


@log_execution_time()
@st.cache_data
def total_consumption_this_year(df):
    current_year = last_day.year
    df = df[df['date'].dt.year == current_year]
    return df['consommation'].sum()


@log_execution_time()
@st.cache_data
def total_consumption_last_year(df):
    last_year = last_day.year - 1
    last_day_last_year = last_day - datetime.timedelta(days=365)
    df = df[df['date'].dt.year == last_year]
    df = df[df['date'].dt.date <= last_day_last_year]
    return df['consommation'].sum()


@log_execution_time()
@st.cache_data
def total_exchanges_today(df):
    df = df[df['date'].dt.date == last_day]
    return df['ech_physiques'].sum()


@log_execution_time()
@st.cache_data
def total_exchanges_yesterday(df):
    df = df[df['date'].dt.date == last_day - datetime.timedelta(days=1)]
    return df['ech_physiques'].sum()


@log_execution_time()
@st.cache_data
def get_data_for_region_and_period(df, df_by_day, choice_period, choice_region):
    period, year = choice_period

    if period == Period.WEEK:
        start_date = last_day - datetime.timedelta(days=7)
        df_asked = df[df['date'].dt.date >= start_date]
    elif period == Period.MONTH:
        start_date = last_day - datetime.timedelta(days=30)
        df_asked = df[df['date'].dt.date >= start_date]
    elif period == Period.YEAR:
        start_year = pd.to_datetime(f'{year}-01-01', utc=True).date()
        end_year = pd.to_datetime(f'{year}-12-31', utc=True).date()
        df_asked = df_by_day[df_by_day['date'].dt.date >= start_year]
        df_asked = df_asked[df_asked['date'].dt.date <= end_year]
    else:
        df_asked = df_by_day

    if choice_region != Region.ALL_REGION:
        df_asked = df_asked[df_asked['libelle_region'] == choice_region]

    return df_asked


@log_execution_time()
@st.cache_data
def get_consumption_data(df, df_by_day, choice_period, choice_region):
    return get_data_for_region_and_period(df, df_by_day, choice_period, choice_region) \
        .groupby('date') \
        .agg({ 'consommation': 'sum' })['consommation']


@log_execution_time()
@st.cache_data
def get_energy_sources_data_with_region(df, df_by_day, choice_period, choice_region):
    return get_data_for_region_and_period(df, df_by_day, choice_period, choice_region) \
        .drop(['code_insee_region', 'consommation', 'ech_physiques'], axis=1)


@log_execution_time()
@st.cache_data
def get_energy_sources_data(df, df_by_day, choice_period, choice_region):
    return get_energy_sources_data_with_region(df, df_by_day, choice_period, choice_region) \
        .drop(['libelle_region'], axis=1) \
        .melt(id_vars=['date'], var_name='energy_source', value_name='energy_value')


@log_execution_time()
@st.cache_data
def get_exchange_data(df, df_by_day, choice_period, choice_region):
    return get_data_for_region_and_period(df, df_by_day, choice_period, choice_region)[['date', 'libelle_region', 'ech_physiques']].reset_index()


@log_execution_time()
@st.cache_data
def get_region_list(df):
    return [Region.ALL_REGION, *[value for value in df['libelle_region'].unique()]]


def make_time_period_selector():
    col1, col2 = st.columns(2)

    period = col1.selectbox('Select a period', [Period.WEEK, Period.MONTH, Period.YEAR, Period.ALL_TIME])
    # year = col2.selectbox('Select a year', [2013, 2014, 2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022], disabled=period != 'A Given Year')
    year = col2.slider('Select a year', 2013, 2023, 2023, disabled=period != 'A Given Year')

    return (period, year) if period == 'A Given Year' else (period, None)


def format_watts(value):
    if value >= 1000000:
        return f'{value / 1000000:.1f} TW'
    if value >= 1000:
        return f'{value / 1000:.1f} GW'
    return f'{value:.1f} MW'


def st_category(name):
    st.header(name, divider='rainbow')


def st_graph_title(name):
    st.markdown(f'#### <center style="margin-top: 50px">{name}</center>', unsafe_allow_html=True)


region_coordinates = pd.DataFrame.from_dict({
    'Auvergne-Rhône-Alpes': [45.75, 4.85],
    'Bourgogne-Franche-Comté': [47.25, 5.95],
    'Bretagne': [48.25, -2.75],
    'Centre-Val de Loire': [47.75, 1.75],
    'Corse': [42.25, 9.25],
    'Grand Est': [48.75, 5.75],
    'Hauts-de-France': [50.5, 2.75],
    'Île-de-France': [48.75, 2.25],
    'Normandie': [49.25, 0.25],
    'Nouvelle-Aquitaine': [45.25, 0.25],
    'Occitanie': [43.75, 1.75],
    'Pays de la Loire': [47.5, -0.75],
    "Provence-Alpes-Côte d'Azur": [43.75, 6.25],
}, orient='index', columns=['lat', 'lon'])

color_scale_rgb = {
    'thermique': [255, 82, 88],
    'nucleaire': [255, 187, 74],
    'eolien': [144, 248, 255],
    'solaire': [249, 255, 114],
    'hydraulique': [0, 149, 255],
    'bioenergies': [121, 255, 105],
}

color_scale_hex = {
    'thermique': '#FF5258',
    'nucleaire': '#FFBB4A',
    'eolien': '#90F8FF',
    'solaire': '#F9FF72',
    'hydraulique': '#0095FF',
    'bioenergies': '#79FF69',
}

npp_coordinates = pd.DataFrame.from_dict({
    'Belleville': [47.510534, 2.8761864],
    'Blayais': [45.255833, -0.693056],
    'Bugey': [45.798333, 5.270833],
    'Cattenom': [49.4158, 6.2181],
    'Chinon': [47.230556, 0.170556],
    'Chooz-B': [50.09, 4.789444],
    'Civaux': [46.456667, 0.652778],
    'Cruas': [44.633056, 4.756667],
    'Dampierre': [47.7336808, 2.5172853],
    'Fessenheim': [47.9032247, 7.5623059],
    'Flamanville': [49.536389, -1.881667],
    'Golfech': [44.1067, 0.8453],
    'Gravelines': [51.015278, 2.136111],
    'Nogent': [48.515278, 3.517778],
    'Paluel': [49.858056, 0.635556],
    'Penly': [49.976667, 1.211944],
    'Saint-Alban': [45.4042957, 4.7555351],
    'Saint-Laurent-B': [47.72, 1.5775],
    'Tricastin': [44.329722, 4.732222],
}, orient='index', columns=['lat', 'lon'])
