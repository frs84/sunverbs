import streamlit as st
import pandas as pd
import plotly.express as px

# Configuration de la page
st.set_page_config(page_title="Sunverbs")

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
df = pd.read_csv("sunverbs.csv")

# Vérification des colonnes nécessaires
required_cols = ['groupe', 'modèle', 'mode', 'temps', 'formes']
for col in required_cols:
    if col not in df.columns:
        st.error(f"Colonne manquante : {col}")
        st.stop()

# Titre
st.title("🌞 Sunverbs")

# Valeurs uniques
groupes = sorted(df['groupe'].dropna().unique())

# Dictionnaire : mode → temps
mode_to_temps = {}
for _, row in df.iterrows():
    m, t = row['mode'], row['temps']
    if pd.notna(m) and pd.notna(t):
        mode_to_temps.setdefault(m, set()).add(t)
mode_to_temps = {m: sorted(ts) for m, ts in mode_to_temps.items()}

# Ordre des modes à afficher
ordered_modes = ['indicatif', 'conditionnel', 'subjonctif']
modes = [m for m in ordered_modes if m in mode_to_temps]

# Initialisation des états mémorisés
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
        st.session_state.selected_modes_temps = set(
            (m, t) for m in modes for t in mode_to_temps[m]
        )
        st.rerun()

with col2:
    if st.button("❌ Tout décocher"):
        for g in groupes:
            st.session_state.selected_verbs[g] = set()
        st.session_state.selected_modes_temps.clear()
        st.rerun()

# --- Section Temps et modes ---
st.markdown("### Temps et modes")
cols = st.columns(3)  # trois colonnes fixes

for i, mode in enumerate(modes):
    with cols[i]:
        temps_liste = mode_to_temps[mode]
        tous_coches = all((mode, t) in st.session_state.selected_modes_temps for t in temps_liste)
        nouvelle_val = st.checkbox(f"**{mode}**", value=tous_coches, key=f"mode_{mode}")

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

# --- Section Groupes et verbes ---
st.markdown("### Groupes et verbes")
cols = st.columns(len(groupes))

for i, groupe in enumerate(groupes):
    with cols[i]:
        verbes = sorted(df[df["groupe"] == groupe]["modèle"].dropna().unique())
        all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
        new_all_selected = st.checkbox(f"**{groupe}**", value=all_selected, key=f"group_{groupe}")

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

# --- Filtrage des données ---
mask = pd.Series(False, index=df.index)

for groupe in groupes:
    selected = st.session_state.selected_verbs[groupe]
    if selected:
        mask |= ((df['groupe'] == groupe) & df['modèle'].isin(selected))

if st.session_state.selected_modes_temps:
    mask &= df.apply(
        lambda row: (row['mode'], row['temps']) in st.session_state.selected_modes_temps,
        axis=1
    )

filtered_df = df if not mask.any() else df[mask]

# --- Graphique Sunburst ---
fig = px.sunburst(
    filtered_df,
    path=['groupe', 'modèle', 'mode', 'temps', 'formes'],
    maxdepth=-1,
    width=900,
    height=800
)

fig.update_traces(hoverinfo='skip', hovertemplate=None)

st.plotly_chart(fig, use_container_width=True)
