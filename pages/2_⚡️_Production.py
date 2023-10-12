import streamlit as st
import altair as alt
import plotly.express as px
from utils import *

df, df_by_day = load_data()

c_scale = alt.Scale(domain=list(color_scale_hex.keys()), range=list(color_scale_hex.values()))

st_category('Production')

st_graph_title('Energy production distribution over time')

choice_period = make_time_period_selector()
choice_region = st.selectbox('Select a region', get_region_list(df), key="energy_region")

energy_data = get_energy_sources_data(df, df_by_day, choice_period, choice_region)

if choice_period[0] == Period.WEEK:
    energy_data = energy_data.groupby(['energy_source', pd.Grouper(key='date', freq='6H')])
elif choice_period[0] == Period.MONTH:
    energy_data = energy_data.groupby(['energy_source', pd.Grouper(key='date', freq='D')])
elif choice_period[0] == Period.YEAR:
    energy_data = energy_data.groupby(['energy_source', pd.Grouper(key='date', freq='3D')])
else:
    energy_data = energy_data.groupby(['energy_source', pd.Grouper(key='date', freq='M')])

energy_data = energy_data \
    .agg({'energy_value': 'sum'}) \
    .reset_index()

chart = alt.Chart(energy_data).mark_area().encode(
    x=alt.X('date:T', title='Date'),
    y=alt.Y('sum(energy_value):Q', stack='zero', title='Energy (MW)'),
    color=alt.Color('energy_source', scale=c_scale, title='Energy source'),
    tooltip=[alt.Tooltip('date:T', title='Date'), alt.Tooltip('sum(energy_value):Q', title='Energy (MW)')],
)

st.altair_chart(chart, use_container_width=True)

st.markdown("""
            The graph above shows the distribution of energy sources over time. We can see that the nuclear
            energy source is the most used in France by far. We can also see that during the Christmas holidays,
            the consumption of electricity is much lower than usual. This is normal because companies are the
            biggest consumers of electricity, and during the Christmas holidays, most of them are closed.
            During winter, solar energy is also a lot lower than during summer. This is normal because the days
            are shorter in winter, and the sun is less present.

            If we look at the data by week, it is also interesting to see the variations in solar energy, of course
            due to the fact that they only produce electricity during the day.

            Finally, it is interesting to see the differences between the regions. For example, in Île-de-France,
            there isn't as much wind energy than in Bretagne.
            """)

st_graph_title('Energy sources distribution over a given period')

c_scale = alt.Scale(domain=list([*color_scale_hex.keys(), 'propre', 'sale']), range=list([*color_scale_hex.values(), '#00ff00', '#ff0000']))


energy_chart = alt.Chart(energy_data).mark_arc().encode(
    theta='sum(energy_value):Q',
    color=alt.Color('energy_source', scale=c_scale, title='Energy source'),
    tooltip=[alt.Tooltip('sum(energy_value):Q', title='Energy (MW)')],
).properties(
    width=300,
    height=300
)

clean_dirty_energy_data = energy_data.copy()
clean_dirty_energy_data['energy_source'] = clean_dirty_energy_data['energy_source'].replace(['eolien', 'solaire', 'hydraulique', 'bioenergies'], 'propre')
clean_dirty_energy_data['energy_source'] = clean_dirty_energy_data['energy_source'].replace(['thermique'], 'sale')

clean_dirty_energy_chart = alt.Chart(clean_dirty_energy_data).mark_arc().encode(
    theta='sum(energy_value):Q',
    color=alt.Color('energy_source', scale=c_scale, title='Energy source'),
    tooltip=[alt.Tooltip('sum(energy_value):Q', title='Energy (MW)')],
).properties(
    width=300,
    height=300
)

st.altair_chart(energy_chart | clean_dirty_energy_chart)

st_graph_title('Use of energy sources per region over a given period')

energy_sources_heatmap_data = get_energy_sources_data_with_region(df, df_by_day, choice_period, choice_region)
energy_sources_heatmap_data = energy_sources_heatmap_data.groupby(['libelle_region']).agg({
    'thermique': 'sum',
    'nucleaire': 'sum',
    'eolien': 'sum',
    'solaire': 'sum',
    'hydraulique': 'sum',
    'bioenergies': 'sum',
})

fig = px.imshow(energy_sources_heatmap_data.apply(lambda x: round(x, -4)),
                text_auto=True,
                aspect='auto',
                color_continuous_scale='Blues',
                labels=dict(x="Region", y="Energy source", color="Energy (MW)")
                )
st.plotly_chart(fig)
