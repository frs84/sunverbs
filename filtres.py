import streamlit as st
import pandas as pd

class FiltreSunverbs:
    def __init__(self, df):
        self.df = df.drop_duplicates()
        self.groupes = sorted(df['groupe'].dropna().unique())
        self.verbes_par_groupe = {g: df[df["groupe"] == g]["modèle"].dropna().unique()
                                  for g in df["groupe"].dropna().unique()}

        self.personnes = sorted(df["personne"].dropna().unique())
        self.mode_et_temps = self._construire_mode_temps()
        self.modes = list(self.mode_et_temps.keys())

        self._init_session_state()

    def _construire_mode_temps(self):
        ordre = {
            'indicatif': ['présent', 'passé composé', 'imparfait', 'plus-que-parfait', 'passé simple', 'futur simple'],
            'conditionnel': ['présent', 'passé'],
            'subjonctif': ['présent', 'passé', 'imparfait', 'plus-que-parfait']}

        # On ne garde que les modes qui existent dans le DF
        modes_disponibles = self.df['mode'].dropna().unique()
        mode_et_temps = {m: ordre[m] for m in ordre if m in modes_disponibles}

        return mode_et_temps

    def _init_session_state(self):
        # Crée un dict de sets pour chaque groupe de verbes
        if "selected_verbs" not in st.session_state:
            st.session_state.selected_verbs = {g: set() for g in self.groupes}

        if "selected_modes_temps" not in st.session_state:
            st.session_state.selected_modes_temps = set()

        if "selected_personnes" not in st.session_state:
            st.session_state.selected_personnes = set()


    def tout_cocher(self):
        for g in self.groupes:
            st.session_state.selected_verbs[g] = set(self.verbes_par_groupe[g])
        st.session_state.selected_modes_temps = set((m, t) for m in self.modes for t in self.mode_et_temps[m])
        st.session_state.selected_personnes = set(self.personnes)

        for key in list(st.session_state.keys()):
            if key.startswith("case_"):
                st.session_state[key] = True
        st.rerun()

    def tout_decocher(self):
        for g in self.groupes:
            st.session_state.selected_verbs[g] = set()
        st.session_state.selected_modes_temps = set()
        st.session_state.selected_personnes = set()
        
        for k in list(st.session_state.keys()):
            if k.startswith('case'):
                st.session_state[k] = False 
        st.rerun()

    def expander_temps_et_mode(self):
        
        with st.expander("Temps et modes", expanded=False):
            cols = st.columns(3)
            for i, mode in enumerate(self.modes):
                with cols[i]:
                    temps_liste = self.mode_et_temps[mode]
                    key_mode = f"case_{mode}"
                    # créer la clé si elle n'existe pas encore
                    if key_mode not in st.session_state:
                        st.session_state[key_mode] = False

                    # calculer si tous les temps sont cochés (vrai ou faux)
                    tous_coches = all((mode, t) in st.session_state.selected_modes_temps for t in temps_liste)

                    # checkbox affichée selon session_state ou tous_coches
                    st.session_state[key_mode] = st.checkbox(f"{mode}", value=st.session_state[key_mode] or tous_coches)

                    # mettre à jour selected_modes_temps si l'utilisateur a changé l'état
                    if st.session_state[key_mode] != tous_coches:
                        if st.session_state[key_mode]:
                            for t in temps_liste:
                                st.session_state.selected_modes_temps.add((mode, t))
                        else:
                            for t in temps_liste:
                                st.session_state.selected_modes_temps.discard((mode, t))
                        st.rerun()

                    for t in temps_liste:
                        checked = (mode, t) in st.session_state.selected_modes_temps
                        new_checked = st.checkbox(t, value=checked, key=f"case_{mode}_{t}")
                        if new_checked != checked:
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
            new_all = st.checkbox("Toutes les personnes", value=all_selected, key="case_all_personnes")

            if new_all != all_selected:
                if new_all:
                    st.session_state.selected_personnes = set(self.personnes)
                else:
                    st.session_state.selected_personnes.clear()
                st.rerun()

            with col1:
                for p in groupe1:
                    if p in self.personnes:
                        checked = p in st.session_state.selected_personnes
                        new_val = st.checkbox(p, value=checked, key=f"case_personne_{p}")
                        if new_val != checked:
                            if new_val:
                                st.session_state.selected_personnes.add(p)
                            else:
                                st.session_state.selected_personnes.discard(p)
                            st.rerun()

            with col2:
                for p in groupe2:
                    if p in self.personnes:
                        checked = p in st.session_state.selected_personnes
                        new_val = st.checkbox(p, value=checked, key=f"case_personne_{p}")
                        if new_val != checked:
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
                    verbes = self.df[self.df["groupe"] == groupe]["modèle"].dropna().unique()
                    verbes = sorted(verbes)
                    all_selected = st.session_state.selected_verbs[groupe] == set(verbes)
                    new_all_selected = st.checkbox(f"{groupe}", value=all_selected, key=f"case_group_{groupe}")

                    if new_all_selected != all_selected:
                        st.session_state.selected_verbs[groupe] = set(verbes) if new_all_selected else set()
                        st.rerun()

                    for verbe in verbes:
                        is_checked = verbe in st.session_state.selected_verbs[groupe]
                        new_checked = st.checkbox(verbe, value=is_checked, key=f"case_{groupe}_{verbe}")
                        if new_checked != is_checked:
                            if new_checked:
                                st.session_state.selected_verbs[groupe].add(verbe)
                            else:
                                st.session_state.selected_verbs[groupe].discard(verbe)
                            st.rerun()
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
        has_verbes = any(len(v) > 0 for v in selected_verbes_dict.values())

        if has_verbes:
            selected_verbes = {
                (groupe, verbe)
                for groupe, verbes in selected_verbes_dict.items()
                for verbe in verbes
                }
            verbe_mask = pd.Series(False, index=df.index)
            for groupe, verbe in selected_verbes:
                verbe_mask |= (df['groupe'] == groupe) & (df['modèle'] == verbe)
            mask &= verbe_mask

        
        # Modes / temps
        if st.session_state.selected_modes_temps:
            mask &= df.apply(
                lambda row: (row['mode'], row['temps']) in st.session_state.selected_modes_temps,
                axis=1)
            # Si aucune sélection sur les verbes, modes/temps, ou personnes, renvoyer un df vide
        
                 # Personnes
        if st.session_state.selected_personnes:
            mask &= df["personne"].isin(st.session_state.selected_personnes)

           
        return df[mask].dropna()


