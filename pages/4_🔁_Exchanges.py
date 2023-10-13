import streamlit as st
import pandas as pd
import altair as alt
from utils import *

df, df_by_day = load_data()

st_category('Exchanges')

@st.cache_data()
def render_metrics():
    exch_today = int(total_exchanges_today(df))
    exch_yesterday = int(total_exchanges_yesterday(df))

    col1, col2 = st.columns(2)
    col1.metric(label=f"Total export today", value=format_watts(abs(min(exch_today, 0))), delta=format_watts(abs(min(exch_today - exch_yesterday, 0))))
    col2.metric(label=f"Total import today", value=format_watts(max(exch_today, 0)), delta=format_watts(max(exch_today - exch_yesterday, 0)))

render_metrics()

st_graph_title('Energy exchanges with neighboring countries over time')

choice_period = make_time_period_selector()

exchange_data = get_exchange_data(df, df_by_day, choice_period, Region.ALL_REGION)

if choice_period[0] == Period.WEEK:
    exchange_data = exchange_data.groupby(pd.Grouper(key='date', freq='6H'))
elif choice_period[0] == Period.MONTH:
    exchange_data = exchange_data.groupby(pd.Grouper(key='date', freq='D'))
elif choice_period[0] == Period.YEAR:
    exchange_data = exchange_data.groupby(pd.Grouper(key='date', freq='3D'))
else:
    exchange_data = exchange_data.groupby(pd.Grouper(key='date', freq='M'))

exchange_data_agg = exchange_data \
    .agg({'ech_physiques': 'sum'}) \
    .reset_index()

color_scale = alt.Scale(
    domain=[-20_000_000, 0, 20_000_000],  # Define the color transitions at -50, 0, and 50
    range=['green', 'white', 'red']  # Define the colors for negative, zero, and positive values
)

chart = alt.Chart(exchange_data_agg).mark_bar().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('ech_physiques:Q', title='Exchanges (MW)'),
    # Shade of green if negative (lighter the closer to 0, darker the more negative), red if positive (lighter the closer to 0, darker the more positive)
    color=alt.Color('ech_physiques:Q', scale=color_scale, title='Exchanges (MW)'),
    tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('ech_physiques:Q', title='Exchanges (MW)')],
)

st.altair_chart(chart, use_container_width=True)
st.write("Exporter if negative, importer if positive")
