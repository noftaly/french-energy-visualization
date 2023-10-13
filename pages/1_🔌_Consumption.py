import streamlit as st
from utils import *

df, df_by_day = load_data()

st_category('Consumption')

col1, col2 = st.columns(2)
col1.metric(label="Total consumption today", value=format_watts(total_consumption_today(df)), delta=format_watts(total_consumption_today(df) - total_consumption_yesterday(df)))
col2.metric(label="Total consumption this year", value=format_watts(total_consumption_this_year(df)), delta=format_watts(total_consumption_this_year(df) - total_consumption_last_year(df)))

st_graph_title('Consumption of electricity in France over time')

choice_period = make_time_period_selector()
choice_region = st.selectbox('Select a region', get_region_list(df), key="consumption_region")

st.line_chart(get_consumption_data(df, df_by_day, choice_period, choice_region))

st.markdown("""
            We can see that the consumption of electricity in France is quite stable over time. We can also see
            that the consumption of electricity in France is higher in winter than in summer. This is normal
            because in winter, the days are shorter and the temperatures are lower, which leads to a greater
            consumption of electricity for heating and lighting.

            Of course, we can also see that the consumption of electricity in France is much higher during the day
            than during the night. For some reasone, this is much harder to see in some region, like in
            Pays de la Loire, if we select the time period "Week", it is not possible to see the difference
            between day and night. On the other hand, for Île-de-France, the difference is very visible.
            """)
