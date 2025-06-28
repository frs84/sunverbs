import streamlit as st
import pandas as pd
import plotly.express as px
import locale
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
import random
from exercise import afficher_exercice


# Configuration de la page
st.set_page_config(page_title="Sunverbes")

# CSS : coches noires sans fond
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
#df = pd.read_csv("sunverbs.csv")
@st.cache_data
def charger_donnees():
    return pd.read_csv("sunverbs.csv")

df = charger_donnees()

# Vérification des colonnes nécessaires
required_cols = ['groupe', 'modèle', 'mode', 'temps', 'formes']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Colonne manquante : {col}")
        st.stop()

# Chargement des personnes
personnes_presentes = sorted(df["personne"].dropna().unique())

#st.image("photo.jpg", width=100)
st.write("""Bonjour, je m'appelle François Baeckelandt, je suis professeur de français et programmiste entre deux cours !
         Pour plus d'info, rendez-vous sur mon [site](https://bfrs-fle.tb.ru/) ! Bon travail !""") 
         
# Titre
st.title("🌞 Sunverbes")

# Valeurs uniques
groupes = sorted(df['groupe'].dropna().unique())

# Dictionnaire : mode → temps
mode_to_temps = {}
for _, row in df.iterrows():
    m, t = row['mode'], row['temps']
    if pd.notna(m) and pd.notna(t):
        mode_to_temps.setdefault(m, set()).add(t)
mode_to_temps = {m: sorted(ts) for m, ts in mode_to_temps.items()}

# Ordre spécifique des temps par mode
temps_order = {
    'indicatif': ['présent', 'passé composé', 'imparfait', 'passé simple','futur simple'],
    'conditionnel': ['présent', 'passé'],
    'subjonctif': ['présent', 'passé', 'imparfait', 'plus-que-parfait']
}

for mode in mode_to_temps:
    if mode in temps_order:
        # Ne garder que les temps réellement présents dans les données
        disponibles = mode_to_temps[mode]
        mode_to_temps[mode] = [t for t in temps_order[mode] if t in disponibles]
    else:
        mode_to_temps[mode] = sorted(mode_to_temps[mode])


# Ordre affiché des modes
ordered_modes = ['indicatif', 'conditionnel', 'subjonctif']
modes = [m for m in ordered_modes if m in mode_to_temps]

# Initialisation des sélections
if "selected_verbs" not in st.session_state:
    st.session_state.selected_verbs = {
        g: set(df[df["groupe"] == g]["modèle"].dropna().unique()) for g in groupes
    }

if "selected_modes_temps" not in st.session_state:
    st.session_state.selected_modes_temps = set(
        (m, t) for m in modes for t in mode_to_temps[m]
    )

# Boutons Tout cocher / Tout décocher
col1, col2 = st.columns(2)

with col1:
    if st.button("✅ Tout cocher"):
        for g in groupes:
            st.session_state.selected_verbs[g] = set(df[df["groupe"] == g]["modèle"].dropna().unique())
            st.session_state.selected_modes_temps = set((m, t) for m in modes for t in mode_to_temps[m])
            st.session_state.selected_personnes = set(personnes_presentes)
        st.rerun()

with col2:
    if st.button("❌ Tout décocher"):
        for g in groupes:
            st.session_state.selected_verbs[g] = set()
        st.session_state.selected_modes_temps.clear()
        st.session_state.selected_personnes.clear()
        st.rerun()

# Section temps et modes dans un expander
with st.expander("Temps et modes", expanded=False):
    cols = st.columns(3)
    for i, mode in enumerate(modes):
        with cols[i]:
            temps_liste = mode_to_temps[mode]
            tous_coches = all((mode, t) in st.session_state.selected_modes_temps for t in temps_liste)
            nouvelle_val = st.checkbox(f"{mode}", value=tous_coches, key=f"mode_{mode}")

            if nouvelle_val != tous_coches:
                if nouvelle_val:
                    for t in temps_liste:
                        st.session_state.selected_modes_temps.add((mode, t))
                else:
                    for t in temps_liste:
                        st.session_state.selected_modes_temps.discard((mode, t))
                st.rerun()

            for t in temps_liste:
                checked = (mode, t) in st.session_state.selected_modes_temps
                new_checked = st.checkbox(t, value=checked, key=f"{mode}_{t}")
                if new_checked != checked:
                    if new_checked:
                        st.session_state.selected_modes_temps.add((mode, t))
                    else:
                        st.session_state.selected_modes_temps.discard((mode, t))
                    st.rerun()


# Initialisation
if "selected_personnes" not in st.session_state:
    st.session_state.selected_personnes = set(personnes_presentes)

with st.expander("Personnes", expanded=False):
    col1, col2 = st.columns(2)

    groupe1 = ["je", "tu", "il", "elle"]
    groupe2 = ["nous", "vous", "ils", "elles"]

    all_selected = len(st.session_state.selected_personnes) == len(personnes_presentes)
    new_all = st.checkbox("Toutes les personnes", value=all_selected, key="all_personnes")

    if new_all != all_selected:
        if new_all:
            st.session_state.selected_personnes = set(personnes_presentes)
        else:
            st.session_state.selected_personnes.clear()
        st.rerun()

    with col1:
        for p in groupe1:
            if p in personnes_presentes:
                checked = p in st.session_state.selected_personnes
                new_val = st.checkbox(p, value=checked, key=f"personne_{p}")
                if new_val != checked:
                    if new_val:
                        st.session_state.selected_personnes.add(p)
                    else:
                        st.session_state.selected_personnes.discard(p)
                    st.rerun()

    with col2:
        for p in groupe2:
            if p in personnes_presentes:
                checked = p in st.session_state.selected_personnes
                new_val = st.checkbox(p, value=checked, key=f"personne_{p}")
                if new_val != checked:
                    if new_val:
                        st.session_state.selected_personnes.add(p)
                    else:
                        st.session_state.selected_personnes.discard(p)
                    st.rerun()



# Section groupes et verbes dans un expander
with st.expander("Groupes et verbes", expanded=False):
    cols = st.columns(len(groupes))
    for i, groupe in enumerate(groupes):
        with cols[i]:
            verbes = df[df["groupe"] == groupe]["modèle"].dropna().unique()
            verbes = sorted(verbes, key=locale.strxfrm)
            all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
            new_all_selected = st.checkbox(f"{groupe}", value=all_selected, key=f"group_{groupe}")

            if new_all_selected != all_selected:
                st.session_state.selected_verbs[groupe] = set(verbes) if new_all_selected else set()
                st.rerun()

            for verbe in verbes:
                is_checked = verbe in st.session_state.selected_verbs[groupe]
                new_checked = st.checkbox(verbe, value=is_checked, key=f"{groupe}_{verbe}")
                if new_checked != is_checked:
                    if new_checked:
                        st.session_state.selected_verbs[groupe].add(verbe)
                    else:
                        st.session_state.selected_verbs[groupe].discard(verbe)
                    st.rerun()

# --- Filtrage logique ---
mask = pd.Series(True, index=df.index)

# Filtrage verbes
selected_verbes = {
    (groupe, verbe)
    for groupe, verbes in st.session_state.selected_verbs.items()
    for verbe in verbes
}
if selected_verbes:
    verbe_mask = pd.Series(False, index=df.index)
    for groupe, verbe in selected_verbes:
        verbe_mask |= (df['groupe'] == groupe) & (df['modèle'] == verbe)
    mask &= verbe_mask

# Filtrage mode/temps
if st.session_state.selected_modes_temps:
    mask &= df.apply(
        lambda row: (row['mode'], row['temps']) in st.session_state.selected_modes_temps,
        axis=1
    )

# Filtrage par personne

if st.session_state.selected_personnes:
    mask &= df["personne"].isin(st.session_state.selected_personnes)

filtered_df = df[mask]

# --- Résultat ---
if filtered_df.empty:
    st.warning("Aucune donnée sélectionnée.")
else:
    fig = px.sunburst(
        filtered_df,
        path=['groupe', 'modèle', 'mode', 'temps', 'formes'],
        maxdepth=-1,
        width=850,
        height=750
    )
    fig.update_traces(hoverinfo='skip', hovertemplate=None)
    st.plotly_chart(fig, use_container_width=True)

#--- Exercice --- 
afficher_exercice(filtered_df)
