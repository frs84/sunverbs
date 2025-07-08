import streamlit as st
import pandas as pd
import plotly.express as px
import locale
from exo_ecris import ExoQuestion
from exo_devine import Exo_devine_temps
from exo_relie import Exo_relie
from filtres import FiltreSunverbs


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

with st.sidebar:
    st.header("Menu pour le futur")
    

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
    if st.button("❌ Tout effacer"):
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
        with st.spinner("Une seconde..."):
            fig = px.sunburst(
            filtered_df,
            path=['groupe', 'modèle', 'mode', 'temps', 'formes'],
            maxdepth=-1,
            width=800,
            height=700)
            used_colors = []
        
            fig.update_traces(hoverinfo='skip', hovertemplate=None)
            st.plotly_chart(fig, use_container_width=True)
            
st.divider()
#--- Exercice ---

# --- après avoir construit filtered_df ---

if filtered_df.empty:
    st.warning("Aucune donnée sélectionnée pour générer l'exercice.")
    st.stop()

#---Afficher les exercices---#

# Liste des exercices : (clé session_state, clé recommencer, classe, label bouton)
liste_exos = [
    ("exo1", Exo_relie, "🔍 Exercice 1"),
    ("exo2", Exo_devine_temps, "🎯 Exercice 2"),
    ("exo3", ExoQuestion, "✏️ Exercice 3"),
]

for exo_key, ExoClasse, bouton_label in liste_exos:
    obj_key = f"{exo_key}_obj"
    show_key = f"show_{exo_key}"

    # Création ou recréation de l'objet exercice
    if (obj_key not in st.session_state or len(filtered_df) != len(st.session_state[obj_key].df_exo)):
        if ExoClasse == Exo_relie:
            st.session_state[obj_key] = ExoClasse(filtered_df)
        else:
            st.session_state[obj_key] = ExoClasse(filtered_df, n=10)
        
    exo = st.session_state[obj_key]

    if show_key not in st.session_state:
        st.session_state[show_key] = False
    if st.button(bouton_label):
        st.session_state[show_key] = not st.session_state[show_key]
    if st.session_state[show_key]:
        exo.afficher_exercice()
