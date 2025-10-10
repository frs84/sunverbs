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
                    if f'case_{mode}' not in st.session_state:
                        st.session_state[f'case_{mode}'] = False

                    else:
                        #checking if all verbs in this mode are ticked
                        keys = [k for k in list(st.session_state.keys()) if k.startswith(f'case_{mode}') 
                                and k != f'case_{mode}']
                        all_temps_checked = all(st.session_state[k] for k in keys)
                        all_temps_in_selected = all((mode, t) in st.session_state.selected_modes_temps 
                                                    for t in temps_liste)

                        #if the mode box is ticked
                        if st.session_state[f'case_{mode}']:
                            if all_temps_checked: 
                                if all_temps_in_selected:
                                    pass #alright, no change here
                                else:
                                    st.write('T T F I though it was impossible !')
                                    st.stop()
                            else:
                                if all_temps_in_selected:
                                    #j'ai déselectionné UN verbe, la case mode devient False
                                    st.session_state[f'case_{mode}'] = False
                                else:
                                    #j'ai appuye sur le bouton du mode, il faut selectionner tous les verbes !!
                                    for t in temps_liste:
                                        st.session_state[f'case_{mode}_{t}']=True
                                                                            
                        
                        #if the mode box is not ticked
                        else:
                            if all_temps_checked:
                                if all_temps_in_selected:
                                    for t in temps_liste:
                                        st.session_state[f'case_{mode}_{t}'] = False
                                else:
                                    st.session_state[f'case_{mode}'] = True

                            else:
                                if all_temps_in_selected:
                                    st.write('F F T I though it was impossible !')
                                    st.stop()
                                else:
                                    pass #alright, no change here"""
                    
                    st.checkbox(f'{mode}',key=f'case_{mode}')

                    #times
                    for t in self.mode_et_temps[mode]:
                        st.checkbox(f'{t}',key =f'case_{mode}_{t}')
                        if st.session_state[f'case_{mode}_{t}']:
                            st.session_state.selected_modes_temps.add((mode,t))
                        else: 
                            st.session_state.selected_modes_temps.discard((mode,t))

 
    def expander_personnes(self):
        if 'case_toutes les personnes' not in st.session_state:
            st.session_state['case_toutes les personnes'] = False
        
        else: 
            all_personnes_keys = [k for k in list(st.session_state.keys()) if k.startswith('case_pers')]
            all_personnes_checked = all([st.session_state.get(k,False) for k in all_personnes_keys])
            all_personnes_selected = all(personne in st.session_state.selected_personnes for personne in self.personnes)

            if st.session_state["case_toutes les personnes"]:
                if all_personnes_checked:
                    if all_personnes_selected:
                        pass # no problem her
                    else: 
                        st.write('TTF impossible !')
                        st.stop()
                else:
                    if all_personnes_selected:
                        #je viens de deselectionner une personne
                        st.session_state["case_toutes les personnes"] = False
                    else:
                        #je viens de selectionner toutes les personnes
                        for k in all_personnes_keys:
                            st.session_state[k]=True

            else:
                if all_personnes_checked:
                    if all_personnes_selected:
                        for k in all_personnes_keys:
                            st.session_state[k]=False
                    else:
                        st.session_state['case_toutes les personnes'] = True

                else:
                    if all_personnes_selected:
                        st.write('FFT impossible !')
                        st.stop()
                    else:
                        pass #no change here
        
        with st.expander("Personnes", expanded=False):    
            st.checkbox('Toutes les personnes',key='case_toutes les personnes')
            col1, col2 = st.columns(2)
            groupe1 = ["je", "j'","tu", "il", "elle"]
            groupe2 = ["nous", "vous", "ils", "elles"]
            
            with col1:
                for p in groupe1:
                    st.checkbox(p, key=f"case_personne_{p}")
                    if st.session_state[f"case_personne_{p}"]:
                        st.session_state['selected_personnes'].add(p)
                    else:
                        st.session_state['selected_personnes'].discard(p)
            with col2:
                for p in groupe2:
                    st.checkbox(p, key=f"case_personne_{p}")
                    if st.session_state[f"case_personne_{p}"]:
                        st.session_state['selected_personnes'].add(p)
                    else:
                        st.session_state['selected_personnes'].discard(p)
            
            

    def expander_groupes_et_verbes(self):
        with st.expander("Groupes et verbes", expanded=False):
            cols = st.columns(len(self.groupes))
            for i, groupe in enumerate(self.groupes):
                with cols[i]:
                    verbes = sorted(self.df[self.df["groupe"] == groupe]["modèle"].dropna().unique())

                    # Initialisation du state
                    if f"case_group_{groupe}" not in st.session_state:
                        st.session_state[f"case_group_{groupe}"] = False
                    if groupe not in st.session_state.selected_verbs:
                        st.session_state.selected_verbs[groupe] = set()

                    # États actuels
                    all_verbes_checked = all(
                        st.session_state.get(f"case_{groupe}_{v}", False) for v in verbes
                    )
                    all_verbes_selected = st.session_state.selected_verbs[groupe] == set(verbes)

                    # Logique de synchro groupe ↔ verbes
                    if st.session_state[f"case_group_{groupe}"]:
                        if all_verbes_checked:
                            if all_verbes_selected:
                                pass
                            else:
                                st.write('TTF Impossible!')
                                st.stop()
                        else:
                            if all_verbes_selected:
                                st.session_state[f"case_group_{groupe}"] = False
                            else:
                                for v in verbes:
                                    st.session_state[f'case_{groupe}_{v}'] = True
                    else:
                        if all_verbes_checked:
                            if all_verbes_selected:
                                for v in verbes:
                                    st.session_state[f'case_{groupe}_{v}']=False
                            else:
                                st.session_state[f'case_group_{groupe}']=True
                        else:
                            if all_verbes_selected:
                                st.write('FFT Impossible!')
                            else:
                                pass #no problem

                    # Checkbox groupe
                    st.checkbox(f"{groupe}", key=f"case_group_{groupe}")

                    # Checkbox verbes
                    for v in verbes:
                        st.checkbox(v, key=f"case_{groupe}_{v}")
                        if st.session_state[f"case_{groupe}_{v}"]:
                            st.session_state.selected_verbs[groupe].add(v)
                        else:
                            st.session_state.selected_verbs[groupe].discard(v)

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
