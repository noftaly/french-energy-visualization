# https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def/analyze/?disjunctive.libelle_region&disjunctive.nature&sort=-date_heure&dataChart=eyJxdWVyaWVzIjpbeyJjaGFydHMiOlt7InR5cGUiOiJsaW5lIiwiZnVuYyI6IlNVTSIsInlBeGlzIjoiY29uc29tbWF0aW9uIiwiY29sb3IiOiIjZWE1MjU0Iiwic2NpZW50aWZpY0Rpc3BsYXkiOnRydWV9XSwieEF4aXMiOiJkYXRlX2hldXJlIiwibWF4cG9pbnRzIjpudWxsLCJ0aW1lc2NhbGUiOiJtb250aCIsInNvcnQiOiIiLCJjb25maWciOnsiZGF0YXNldCI6ImVjbzJtaXgtcmVnaW9uYWwtY29ucy1kZWYiLCJvcHRpb25zIjp7ImRpc2p1bmN0aXZlLmxpYmVsbGVfcmVnaW9uIjp0cnVlLCJkaXNqdW5jdGl2ZS5uYXR1cmUiOnRydWUsInNvcnQiOiItZGF0ZV9oZXVyZSJ9fX1dLCJ0aW1lc2NhbGUiOiIiLCJkaXNwbGF5TGVnZW5kIjp0cnVlLCJhbGlnbk1vbnRoIjp0cnVlfQ%3D%3D
# https://www.rte-france.com/eco2mix
# https://www.data.gouv.fr/fr/datasets/donnees-eco2mix-regionales-temps-reel-1/

# Columns available:
#   - code_insee_region[text] : INSEE region ID
#   - libelle_region[text] : Region name
#   - date_heure[datetime] : Date and time
#   - consommation[int] : Consumption (MW)
#   - thermique[int] : Thermal (MW)
#   - nucleaire[int] : Nuclear (MW)
#   - eolien[int] : Wind (MW)
#   - solaire[int] : Solar (MW)
#   - hydraulique[int] : Hydraulic (MW)
#   - bioenergies[int] : Bioenergies (MW)
#   - ech_physiques[int] : Physical exchanges (MW) (Balance of physical exchanges with neighboring regions. Exporter if negative, importer if positive.)

import streamlit as st
from utils import load_data
import time

before_load = time.time()
df, df_by_day = load_data()

if time.time() - before_load > 2:
    st.balloons()

st.title('Energy statistics in France')

st.caption("""
            Data from [data.gouv.fr: éCO2mix](https://www.data.gouv.fr/fr/datasets/donnees-eco2mix-regionales-temps-reel-1/).\\
            Document by Elliot MAISL, M1 DE2. 2023.
            """)

st.write('Date range: ', df['date'].min().strftime('%d/%m/%Y'), ' - ', df['date'].max().strftime('%d/%m/%Y'))

st.markdown("""
            Let's analyze the energy consumption in France over time. For that, we will use the data from
            [data.gouv.fr: éCO2mix](https://www.data.gouv.fr/fr/datasets/donnees-eco2mix-regionales-temps-reel-1/).
            This data can be found on [RTE](https://www.rte-france.com/eco2mix) website, but also on
            [Open Data](https://odre.opendatasoft.com/explore/dataset/eco2mix-regional-cons-def).

            This dataset is very complete. It has the advantage of having a breakdown by region, but also by energy
            source. It is also updated every hour, which allows us to have a very precise view of the energy
            consumption in France.

            It also includes energy exchanges with neighboring countries, which allows us to know if France is
            exporting or importing energy.

            This dataset is available from 2013 to june 2022 if we take the data from the Open Data website, and from
            june 2022 to now if we take the data from data.gouv.fr. For that reason, I manually merged the two
            datasets to have a complete dataset from 2013 to now. Because of the sheer size of the dataset, (300MB+) I
            had to drop some columns and modify some things in place as it would be too long to do it with pandas in
            the script. So the dataset "eco2mix-regional.csv" is not exactly the same as the one you would get when
            merging the two datasets from Open Data and data.gouv.fr.

            This dataset being very large, it is necessary to make a selection of the data to be displayed. For
            this, we will use the following filters:
            - Time period: Week, Month, Year to date, All time
            - Region: All Region, Auvergne-Rhône-Alpes, Bourgogne-Franche-Comté, Bretagne, Centre-Val de Loire,
            Corse, Grand Est, Hauts-de-France, Île-de-France, Normandie, Nouvelle-Aquitaine, Occitanie,
            Pays de la Loire, Provence-Alpes-Côte d'Azur.
            """)
