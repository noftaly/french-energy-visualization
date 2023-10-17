import streamlit as st
import pydeck as pdk
from utils import *

df, df_by_day = load_data()

st_category('Map')

st_graph_title('Map of energy sources per region')

choice_period = make_time_period_selector()

sources_data = get_energy_sources_data_with_region(df, df_by_day, choice_period, Region.ALL_REGION) \
    .groupby('libelle_region') \
    .agg({
        "thermique": "sum",
        "nucleaire": "sum",
        "eolien": "sum",
        "solaire": "sum",
        "hydraulique": "sum",
        "bioenergies": "sum",
    }) \
    .join(region_coordinates, on='libelle_region') \
    .reset_index()

for energy_type in ['thermique', 'nucleaire', 'eolien', 'solaire', 'hydraulique', 'bioenergies']:
    sources_data[energy_type] = sources_data.groupby('libelle_region')[energy_type].cumsum()

scale_dynamically = st.toggle('Scale dynamically', value=False, help="""
                              If you scale dynamically, the columns will be scaled to fit into the screen, without any
                              relation from one time period to another. If the option is disabled, then the columns
                              will be scaled accordingly from one time period to another.
                              """)
def scale_factor():
    if not scale_dynamically:
        return 0.01
    if choice_period[0] == Period.WEEK:
        return 0.1
    if choice_period[0] == Period.MONTH:
        return 0.04
    if choice_period[0] == Period.YEAR:
        return 0.005
    return 0.0008

chart_layers = [pdk.Layer(
    'ColumnLayer',
    data=sources_data,
    get_position=['lon', 'lat'],
    get_elevation=energy_type,
    elevation_scale=scale_factor(),
    get_fill_color=color_scale_rgb[energy_type],
    radius=20000,
    pickable=False,
    auto_highlight=False,
) for energy_type in ['thermique', 'nucleaire', 'eolien', 'solaire', 'hydraulique', 'bioenergies']]

st.pydeck_chart(pdk.Deck(
    map_style='',
    initial_view_state=pdk.ViewState(
        latitude=47.5,
        longitude=2,
        zoom=4,
        pitch=30,
    ),
    layers=[
        *chart_layers,
        pdk.Layer(
            'ScatterplotLayer',
            data=npp_coordinates,
            get_position=['lon', 'lat'],
            get_radius=10000,
            get_fill_color=[255, 255, 255],
            pickable=False,
            auto_highlight=False,
        )
    ],
))

legend = """
    <style>
    .dot {{
        height: 15px;
        width: 15px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 6px;
    }}
    .thermal {{ background-color: {}; }}
    .nuclear {{ background-color: {}; }}
    .wind {{ background-color: {}; }}
    .solar {{ background-color: {}; }}
    .hydraulic {{ background-color: {}; }}
    .bioenergies {{ background-color: {}; }}
    .npp {{ background-color: white; }}
    </style>

    ### Legend
    <span class="dot thermal"></span>  Thermal<br>
    <span class="dot nuclear"></span>  Nuclear<br>
    <span class="dot wind"></span>  Wind<br>
    <span class="dot solar"></span>  Solar<br>
    <span class="dot hydraulic"></span>  Hydraulic<br>
    <span class="dot bioenergies"></span>  Bioenergies
    <br><br>
    <span class="dot npp"></span>  Nuclear Power Plant
    """.format(*map(lambda x: 'rgb({})'.format(', '.join([str(c) for c in x])), list(color_scale_rgb.values())))

st.markdown(legend, unsafe_allow_html=True)

st.markdown("""
            As usual, we can see a lot of interesting data. First, something that might strike you is the proportion of
            hydraulic energy in Auvergnes-Rhône-Alpes, and the proportion of wind in Hauts-de-France.
            """)
