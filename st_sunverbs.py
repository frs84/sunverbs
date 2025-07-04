import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from exo_ecris_forme import ExoQuestion
from filtres import check_colonnes, FiltreSunverbs

try:
    # Linux (Streamlit Cloud)
    locale.setlocale(locale.LC_ALL, 'fr_FR.UTF-8')
except locale.Error:
    try:
        # Windows
        locale.setlocale(locale.LC_ALL, 'French_France.1252')
    except locale.Error:
        # Fallback : pas de tri accentué
        locale.setlocale(locale.LC_ALL, '')

# Configuration de la page
st.set_page_config(page_title="Sunverbs")

#---CSS : coches noires sans fond---#
st.markdown("""
    <style>
    input[type="checkbox"] {
        accent-color: black !important;
    }
    div.stCheckbox > div > label > div {
        color: inherit !important;
        background: none !important;
    }
    </style>
""", unsafe_allow_html=True)



#---Titre---#
st.title("🌞 Sunverbes")
st.write("""Bonjour, je m'appelle François Baeckelandt, je suis professeur de français et programmiste entre deux cours !
         Pour plus d'info, rendez-vous sur mon [site](https://bfrs-fle.tb.ru/) ! Bon travail !""") 

#---Charger les données et filtrer---#
@st.cache_data
def charger_donnees():
    return pd.read_csv("sunverbs.csv")

df = charger_donnees().drop_duplicates()


if "filtre" not in st.session_state:
    st.session_state.filtre = FiltreSunverbs(df)

filtre = st.session_state.filtre

col1, col2 = st.columns(2)
with col1:
    if st.button("✅ Tout cocher"):
        filtre.tout_cocher()
        st.rerun()
with col2:
    if st.button("❌ Tout décocher"):
        filtre.tout_decocher()
        st.rerun()

filtre.expander_temps_et_mode()
filtre.expander_personnes()
filtre.expander_groupes_et_verbes()

filtered_df = filtre.get_filtre_df()

# --- Afficher le graphique --- #

if 'show_graph' not in st.session_state:
    st.session_state.show_graph = False
if filtered_df.empty:
    st.warning("Aucune donnée sélectionnée.")
    st.stop()
else:
    if st.button("🌞"):
        st.session_state.show_graph = not st.session_state.show_graph
    if st.session_state.show_graph:
        fig = px.sunburst(
        filtered_df,
        path=['groupe', 'modèle', 'mode', 'temps', 'formes'],
        maxdepth=-1,
        width=800,
        height=700)
        
        fig.update_traces(hoverinfo='skip', hovertemplate=None)
        st.plotly_chart(fig, use_container_width=True)
        
st.divider()
#--- Exercice ---

# --- après avoir construit filtered_df ---

if filtered_df.empty:
    st.warning("Aucune donnée sélectionnée pour générer l'exercice.")
else:

#---Premier exo ---#
    if (
        "exo_obj" not in st.session_state
        or len(filtered_df) != len(st.session_state.exo_obj.df_exo)
        or st.session_state.get("recommencer_exo", False)
    ):
        st.session_state.exo_obj = ExoQuestion(filtered_df, n=10)
        st.session_state.recommencer_exo = False

    exo = st.session_state.exo_obj

    if 'show_exo1' not in st.session_state:
        st.session_state.show_exo1 = False
    if st.button("✏️ Exercice 1"):
        st.session_state.show_exo1 = not st.session_state.show_exo1
    if st.session_state.show_exo1 == True:
        exo.afficher_exercice()

#---deuxième exo---#

    if (
        "exo2_obj" not in st.session_state
        or len(filtered_df) != len(st.session_state.exo2_obj.df_exo)
        or st.session_state.get("recommencer_exo2", False)
    ):
        st.session_state.exo2_obj = Exo_devine_temps(filtered_df, n=10)
        st.session_state.exo2_recommencer = False

    # Afficher l'exercice
    exo2 = st.session_state.exo2_obj

    if 'show_exo2' not in st.session_state:
        st.session_state.show_exo2 = False
    if st.button("🎯 Exercice 2"):
        st.session_state.show_exo2 = not st.session_state.show_exo2
    if st.session_state.show_exo2 == True:
        exo2.afficher_exercice()


