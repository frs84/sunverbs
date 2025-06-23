import streamlit as st
import pandas as pd
import plotly.express as px

# Must be the very first Streamlit command
st.set_page_config(page_title="Sunverbs")

# CSS pour coches noires sans fond
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

# Chargement des données
df = pd.read_csv("sunverbs.csv")

# Vérification des colonnes nécessaires
required_cols = ['groupe', 'modèle', 'mode','temps', 'formes']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Colonne manquante : {col}")
        st.stop()

# Titre
st.title("🌞 Sunverbs")

# Listes uniques
groupes = sorted(df['groupe'].dropna().unique())
temps = sorted(df['temps'].dropna().unique())

# Initialisation session_state (tout sélectionné en mémoire)
if "selected_verbs" not in st.session_state:
    st.session_state.selected_verbs = {
        g: set(df[df["groupe"] == g]["modèle"].dropna().unique()) for g in groupes
    }
if "selected_temps" not in st.session_state:
    st.session_state.selected_temps = set(temps)

# Boutons Tout cocher / Tout décocher
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Tout cocher"):
        # Cocher tous les temps
        st.session_state.selected_temps = set(temps)
        # Cocher tous les verbes par groupe
        for g in groupes:
            st.session_state.selected_verbs[g] = set(df[df["groupe"] == g]["modèle"].dropna().unique())
        st.rerun()

with col2:
    if st.button("❌ Tout décocher"):
        # Décocher tous les temps
        st.session_state.selected_temps.clear()
        # Décocher tous les verbes par groupe
        for g in groupes:
            st.session_state.selected_verbs[g] = set()
        st.rerun()

st.markdown("### Temps")

# Checkbox "Tous les temps"
all_temps_selected = len(st.session_state.selected_temps) == len(temps)
new_all_temps = st.checkbox("**Tous les temps**", value=all_temps_selected, key="all_temps")

if new_all_temps != all_temps_selected:
    if new_all_temps:
        # Cocher tous les temps
        st.session_state.selected_temps = set(temps)
    else:
        # Décocher tous les temps
        st.session_state.selected_temps.clear()
    st.rerun()

# Checkboxes temps individuelles
for t in temps:
    checked = t in st.session_state.selected_temps
    new_val = st.checkbox(t, value=checked, key=f"temps_{t}")
    if new_val != checked:
        if new_val:
            st.session_state.selected_temps.add(t)
        else:
            st.session_state.selected_temps.discard(t)
        st.rerun()


# Section Groupes et verbes
st.markdown("### Groupes et verbes")
cols = st.columns(len(groupes))

for i, groupe in enumerate(groupes):
    with cols[i]:
        verbes = sorted(df[df["groupe"] == groupe]["modèle"].dropna().unique())

        # Checkbox groupe : cochée si tous les verbes sélectionnés
        all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
        new_all_selected = st.checkbox(f"**{groupe}**", value=all_selected, key=f"group_{groupe}")

        if new_all_selected != all_selected:
            # Mise à jour de la sélection des verbes du groupe en fonction de la case groupe
            if new_all_selected:
                st.session_state.selected_verbs[groupe] = set(verbes)
            else:
                st.session_state.selected_verbs[groupe] = set()

        # Checkbox pour chaque verbe
        for verbe in verbes:
            is_checked = verbe in st.session_state.selected_verbs[groupe]
            new_checked = st.checkbox(verbe, value=is_checked, key=f"{groupe}_{verbe}")
            if new_checked != is_checked:
                if new_checked:
                    st.session_state.selected_verbs[groupe].add(verbe)
                else:
                    st.session_state.selected_verbs[groupe].discard(verbe)


# Filtrer les données selon la sélection interne
mask = pd.Series(False, index=df.index)

for groupe in groupes:
    selected = st.session_state.selected_verbs[groupe]
    if selected:
        mask |= ((df['groupe'] == groupe) & df['modèle'].isin(selected))

if st.session_state.selected_temps:
    mask &= df['temps'].isin(st.session_state.selected_temps)

filtered_df = df if not mask.any() else df[mask]

# Graphique Sunburst
fig = px.sunburst(
    filtered_df,
    path=['groupe', 'modèle', 'temps', 'formes'],
    maxdepth=-1,
    width=900,
    height=800
)
st.plotly_chart(fig, use_container_width=True)
