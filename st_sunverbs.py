import streamlit as st
import pandas as pd
import plotly.express as px

# Must be the very first Streamlit command
st.set_page_config(page_title="Sunverbs")

# CSS pour coches noires sans fond + réduire espacement vertical
st.markdown("""
    <style>
    /* Couleur coche noire */
    input[type="checkbox"] {
        accent-color: black !important;
    }
    /* Pas de fond rouge sur label */
    div.stCheckbox > div > label > div {
        color: inherit !important;
        background: none !important;
    }
    /* Réduire l'espacement vertical des checkbox */
    .stCheckbox > div {
        margin-bottom: 2px !important;
        padding-bottom: 0 !important;
        padding-top: 0 !important;
    }
    </style>
""", unsafe_allow_html=True)

# Chargement des données
df = pd.read_csv("sunverbs.csv")

# Vérification colonnes requises
required_cols = ['groupe', 'modèle', 'temps', 'formes']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Colonne manquante : {col}")
        st.stop()

# Initialisation des groupes et temps
groupes = sorted(df['groupe'].dropna().unique())
temps = sorted(df['temps'].dropna().unique())

# Initialisation sélection interne : tout sélectionné par défaut
if "selected_verbs" not in st.session_state:
    st.session_state.selected_verbs = {
        g: set(df[df["groupe"] == g]["modèle"].dropna().unique()) for g in groupes
    }
if "selected_temps" not in st.session_state:
    st.session_state.selected_temps = set(temps)

# Gérer la réinitialisation via flag et rerun (avant tout affichage)
if st.session_state.get("reset_requested", False):
    # On vide la sélection (décocher toutes cases)
    for g in groupes:
        st.session_state.selected_verbs[g] = set()
    st.session_state.selected_temps = set()
    st.session_state["reset_requested"] = False
    st.experimental_rerun()

# Titre
st.title("🌞 Sunverbs")

# Bouton Réinitialiser (ne fait QUE poser le flag)
if st.button("↺ Réinitialiser les sélections"):
    st.session_state["reset_requested"] = True

# Section Temps
st.markdown("### Temps")
for t in temps:
    checked = t in st.session_state.selected_temps
    checked_new = st.checkbox(t, value=checked, key=f"temps_{t}")
    if checked_new and not checked:
        st.session_state.selected_temps.add(t)
    elif not checked_new and checked:
        st.session_state.selected_temps.discard(t)

# Section Groupes et verbes
st.markdown("### Groupes et verbes")
cols = st.columns(len(groupes))

for i, groupe in enumerate(groupes):
    with cols[i]:
        verbes = sorted(df[df["groupe"] == groupe]["modèle"].dropna().unique())

        all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
        new_all_selected = st.checkbox(f"**{groupe}**", value=all_selected, key=f"group_{groupe}")

        if new_all_selected != all_selected:
            if new_all_selected:
                st.session_state.selected_verbs[groupe] = set(verbes)
            else:
                st.session_state.selected_verbs[groupe] = set()

        for verbe in verbes:
            is_checked = verbe in st.session_state.selected_verbs[groupe]
            new_checked = st.checkbox(verbe, value=is_checked, key=f"{groupe}_{verbe}")
            if new_checked and not is_checked:
                st.session_state.selected_verbs[groupe].add(verbe)
            elif not new_checked and is_checked:
                st.session_state.selected_verbs[groupe].discard(verbe)

# Filtrage des données selon sélection
mask = pd.Series(True, index=df.index)  # tout True = tout afficher

# Si au moins un verbe sélectionné, on filtre
if any(st.session_state.selected_verbs[g] for g in groupes):
    mask = pd.Series(False, index=df.index)
    for groupe in groupes:
        selected = st.session_state.selected_verbs[groupe]
        if selected:
            mask |= ((df['groupe'] == groupe) & df['modèle'].isin(selected))

# Si au moins un temps sélectionné, on filtre
if st.session_state.selected_temps:
    mask &= df['temps'].isin(st.session_state.selected_temps)

# Si masque tout True => on garde tout le df, sinon on filtre
filtered_df = df if mask.all() else df[mask]

# Graphique Sunburst
fig = px.sunburst(
    filtered_df,
    path=['groupe', 'modèle', 'temps', 'formes'],
    maxdepth=-1,
    width=900,
    height=800
)
st.plotly_chart(fig, use_container_width=True)
