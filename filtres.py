import streamlit as st
import pandas as pd

def check_colonnes(df):
    required_cols = ['groupe', 'modèle', 'mode', 'temps', 'formes', 'personne']
    for col in required_cols:
        if col not in df.columns:
            st.error(f"Colonne manquante : {col}")
            st.stop()

class FiltreSunverbs:
    def __init__(self, df):
        self.df = df.drop_duplicates()
        self.groupes = sorted(df['groupe'].dropna().unique())
        self.verbes_par_groupe = {g: df[df["groupe"] == g]["modèle"].dropna().unique()
                                  for g in self.groupes}
        self.personnes = sorted(df["personne"].dropna().unique())
        self.mode_to_temps = self._construire_mode_temps()
        self.modes = self._ordonner_modes()
        self._init_session_state()

    def _construire_mode_temps(self):
        mode_to_temps = {}
        for _, row in self.df.iterrows():
            m, t = row['mode'], row['temps']
            if pd.notna(m) and pd.notna(t):
                mode_to_temps.setdefault(m, set()).add(t)
        mode_to_temps = {m: sorted(ts) for m, ts in mode_to_temps.items()}

        temps_order = {'indicatif': ['présent', 'passé composé', 'imparfait', 'plus-que-parfait','passé simple','futur simple'],
                       'conditionnel': ['présent', 'passé'],
                       'subjonctif': ['présent', 'passé', 'imparfait', 'plus-que-parfait']}

        for mode in mode_to_temps:
            if mode in temps_order:
                disponibles = mode_to_temps[mode]
                mode_to_temps[mode] = [t for t in temps_order[mode] if t in disponibles]
            else:
                mode_to_temps[mode] = sorted(mode_to_temps[mode])
        return mode_to_temps

    def _ordonner_modes(self):
        ordre = ['indicatif', 'conditionnel', 'subjonctif']
        return [m for m in ordre if m in self.mode_to_temps]

    def _init_session_state(self):
        ss = st.session_state
        if "selected_verbs" not in ss:
            ss.selected_verbs = {g: set(self.verbes_par_groupe[g]) for g in self.groupes}
        if "selected_modes_temps" not in ss:
            ss.selected_modes_temps = set((m, t) for m in self.modes for t in self.mode_to_temps[m] if m == "indicatif")
        if "selected_personnes" not in ss:
            ss.selected_personnes = set(self.personnes)

    # ------------------------------------------
    # Tout cocher / Tout décocher
    # ------------------------------------------
    def tout_decocher(self):
        # Verbes
        for g in self.groupes:
            st.session_state.selected_verbs[g] = set()
            for v in self.verbes_par_groupe[g]:
                st.session_state[f"{g}_{v}"] = False
    
        # Modes et temps
        st.session_state.selected_modes_temps.clear()
        for m in self.modes:
            st.session_state[f"mode_{m}"] = False
            for t in self.mode_to_temps[m]:
                st.session_state[f"{m}_{t}"] = False
    
        # Personnes
        st.session_state.selected_personnes.clear()
        for p in self.personnes:
            st.session_state[f"personne_{p}"] = False
    
        # Checkbox “Toutes les personnes”
        st.session_state["all_personnes"] = False
    
        st.rerun()

    def tout_decocher(self):
        for g in self.groupes:
            st.session_state.selected_verbs[g] = set()
            for v in self.verbes_par_groupe[g]:
                st.session_state[f"{g}_{v}"] = False
        st.session_state.selected_modes_temps.clear()
        for m in self.modes:
            st.session_state[f"mode_{m}"] = False
            for t in self.mode_to_temps[m]:
                st.session_state[f"{m}_{t}"] = False
        st.session_state.selected_personnes.clear()
        for p in self.personnes:
            st.session_state[f"personne_{p}"] = False
        st.rerun()

    # ------------------------------------------
    # Expanders
    # ------------------------------------------
    def expander_temps_et_mode(self):
        with st.expander("Temps et modes", expanded=False):
            cols = st.columns(3)
            for i, mode in enumerate(self.modes):
                with cols[i]:
                    temps_liste = self.mode_to_temps[mode]
                    # Checkbox du mode
                    key_mode = f"mode_{mode}"
                    if key_mode not in st.session_state:
                        st.session_state[key_mode] = all((mode, t) in st.session_state.selected_modes_temps for t in temps_liste)
                    nouvelle_val = st.checkbox(f"{mode}", value=st.session_state[key_mode], key=key_mode)
                    if nouvelle_val != st.session_state[key_mode]:
                        st.session_state[key_mode] = nouvelle_val
                        for t in temps_liste:
                            if nouvelle_val:
                                st.session_state.selected_modes_temps.add((mode, t))
                                st.session_state[f"{mode}_{t}"] = True
                            else:
                                st.session_state.selected_modes_temps.discard((mode, t))
                                st.session_state[f"{mode}_{t}"] = False
                        st.rerun()
                    # Checkbox par temps
                    for t in temps_liste:
                        key_t = f"{mode}_{t}"
                        if key_t not in st.session_state:
                            st.session_state[key_t] = (mode, t) in st.session_state.selected_modes_temps
                        new_checked = st.checkbox(t, value=st.session_state[key_t], key=key_t)
                        if new_checked != st.session_state[key_t]:
                            st.session_state[key_t] = new_checked
                            if new_checked:
                                st.session_state.selected_modes_temps.add((mode, t))
                            else:
                                st.session_state.selected_modes_temps.discard((mode, t))
                            st.rerun()

    def expander_personnes(self):
        with st.expander("Personnes", expanded=False):
            col1, col2 = st.columns(2)
            groupe1 = ["je", "tu", "il", "elle"]
            groupe2 = ["nous", "vous", "ils", "elles"]

            all_selected = len(st.session_state.selected_personnes) == len(self.personnes)
            new_all = st.checkbox("Toutes les personnes", value=all_selected, key="all_personnes")
            if new_all != all_selected:
                if new_all:
                    st.session_state.selected_personnes = set(self.personnes)
                    for p in self.personnes:
                        st.session_state[f"personne_{p}"] = True
                else:
                    st.session_state.selected_personnes.clear()
                    for p in self.personnes:
                        st.session_state[f"personne_{p}"] = False
                st.rerun()

            for col, groupe in zip([col1, col2], [groupe1, groupe2]):
                with col:
                    for p in groupe:
                        if p in self.personnes:
                            key_p = f"personne_{p}"
                            if key_p not in st.session_state:
                                st.session_state[key_p] = p in st.session_state.selected_personnes
                            new_val = st.checkbox(p, value=st.session_state[key_p], key=key_p)
                            if new_val != st.session_state[key_p]:
                                st.session_state[key_p] = new_val
                                if new_val:
                                    st.session_state.selected_personnes.add(p)
                                else:
                                    st.session_state.selected_personnes.discard(p)
                                st.rerun()

    def expander_groupes_et_verbes(self):
        with st.expander("Groupes et verbes", expanded=False):
            cols = st.columns(len(self.groupes))
            for i, groupe in enumerate(self.groupes):
                with cols[i]:
                    verbes = sorted(self.verbes_par_groupe[groupe])
                    all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
                    key_groupe = f"group_{groupe}"
                    new_all_selected = st.checkbox(groupe, value=all_selected, key=key_groupe)
                    if new_all_selected != all_selected:
                        if new_all_selected:
                            st.session_state.selected_verbs[groupe] = set(verbes)
                            for v in verbes:
                                st.session_state[f"{groupe}_{v}"] = True
                        else:
                            st.session_state.selected_verbs[groupe] = set()
                            for v in verbes:
                                st.session_state[f"{groupe}_{v}"] = False
                        st.rerun()
                    for verbe in verbes:
                        key_v = f"{groupe}_{verbe}"
                        if key_v not in st.session_state:
                            st.session_state[key_v] = verbe in st.session_state.selected_verbs[groupe]
                        new_checked = st.checkbox(verbe, value=st.session_state[key_v], key=key_v)
                        if new_checked != st.session_state[key_v]:
                            st.session_state[key_v] = new_checked
                            if new_checked:
                                st.session_state.selected_verbs[groupe].add(verbe)
                            else:
                                st.session_state.selected_verbs[groupe].discard(verbe)
                            st.rerun()

    # ------------------------------------------
    # Filtrage final
    # ------------------------------------------
    def get_filtre_df(self):
        if (
            not any(st.session_state.selected_verbs.values()) and
            not st.session_state.selected_modes_temps and
            not st.session_state.selected_personnes):
            return self.df.iloc[0:0]

        df = self.df
        mask = pd.Series(True, index=df.index)

        # Verbes
        selected_verbes_dict = st.session_state.selected_verbs
        if any(len(v) > 0 for v in selected_verbes_dict.values()):
            verbe_mask = pd.Series(False, index=df.index)
            for groupe, verbes in selected_verbes_dict.items():
                for verbe in verbes:
                    verbe_mask |= (df['groupe'] == groupe) & (df['modèle'] == verbe)
            mask &= verbe_mask

        # Modes / temps
        if st.session_state.selected_modes_temps:
            mask &= df.apply(lambda row: (row['mode'], row['temps']) in st.session_state.selected_modes_temps, axis=1)

        # Personnes
        if st.session_state.selected_personnes:
            mask &= df["personne"].isin(st.session_state.selected_personnes)

        return df[mask].dropna()


