import streamlit as st
import pandas as pd
import re
import random
from exo_ecris import Ligne

class Exo_relie:
    def __init__(self, df):
        self.df_exo = df[["personne", "formes"]]
        self.toutes_personnes = self.personnes_presentes()

        if len(self.toutes_personnes)<6:
            st.error("Plus on est de fous, plus on rit ! Ajoutez d'autres personnes, temps, verbe !")
            st.stop()
        self.lignes = self.list_lignes()

        # Initialisation de session_state
        st.session_state.exo_relie_index = 0
        st.session_state.exo_relie_score = 0
        st.session_state.exo_relie_question_validee = False
        st.session_state.exo_relie_reponse = None
    
    def personnes_presentes(self):
        lespersonnes = sorted(self.df_exo['personne'].unique().tolist()) 
        if "je" in lespersonnes and "j'" not in lespersonnes:
            lespersonnes.append("j'")
        ordre_standard = ["je", "j'", "tu", "il", "elle", "nous", "vous", "ils", "elles"]
        return [p for p in ordre_standard if p in lespersonnes]

    def afficher_question(self, ligne):
        st.markdown(f'Quelle est le pronom sujet de **{ligne["verbe"]}** ?')
    
    def check_reponse(self, ligne, reponses_dict):
        bonnes_personnes = set(ligne.get("personnes_possibles", [ligne["personne"]]))
        personnes_cochees = {p for p, cochee in reponses_dict.items() if cochee}

        # Limite à 3 coches max
        if len(personnes_cochees) > 3:
            return "trop de choix"  # Trop de coches = réponse incorrecte
        # Correct si au moins un bon pronom est coché
        if personnes_cochees & bonnes_personnes:
            return "Correct"
        else:
            return "Incorrect"

            
    def list_lignes(self):
        def separer_pronom_forme(chaine):
            match = re.match(r"^(je|j'|tu|il|elle|nous|vous|ils|elles)\s+(.*)", chaine)
            if match:
                return match.group(1), match.group(2)
            return None, None

        df = self.df_exo.copy()
        deja_vus = set()
        lignes = []

        for personne in self.toutes_personnes:
            sous_df = df[df['personne'] == personne].sample(frac=1).reset_index(drop=True)
            
            for _, row in sous_df.iterrows():
                pronom, verbe = separer_pronom_forme(row['formes'])
                if not pronom or not verbe:
                    continue
                if verbe in deja_vus:
                    continue
                deja_vus.add(verbe)
                lignes.append({
                    "forme": row['formes'],
                    "personne": pronom,
                    "personnes_possibles":self.pronoms_possibles_depuis_ligne(pronom,verbe),
                    "verbe":verbe
                })
                break

        return lignes

    def pronoms_possibles_depuis_ligne(self,personne, verbe):
        mots = verbe.split()
        # Liste des formes conjuguées de "être"
        formes_etre = {
            "suis", "es", "est", "sommes", "êtes", "sont",
            "étais", "était", "étions", "étiez", "étaient",
            "fus", "fut", "fûmes", "fûtes", "furent",
            "serai", "seras", "sera", "serons", "serez", "seront",
            "serais", "serait", "serions", "seriez", "seraient",
            "sois", "soit", "soyons", "soyez", "soient",
            "fusse", "fusses", "fût", "fussions", "fussiez", "fussent"
        }

        # Temps simple
        if len(mots) == 1:
            if personne in {"il", "elle"}:
                return ["il", "elle"]
            elif personne in {"ils", "elles"}:
                return ["ils", "elles"]
            else:
                return [personne]

        # Temps composé
        auxiliaire = mots[0]
        if auxiliaire in formes_etre:
            # Auxiliaire être → on garde uniquement la personne réelle
            return [personne]
        else:
            # Avoir ou autre → appliquer même règle que temps simple
            if personne in {"il", "elle"}:
                return ["il", "elle"]
            elif personne in {"ils", "elles"}:
                return ["ils", "elles"]
            else:
                return [personne]
        

    def afficher_exercice(self):
        recommencer = st.button("🔁 Recommencer l'exercice", key="exo_relie recommencer")
        if recommencer:
            del st.session_state["exo1_obj"]
            st.session_state.exo_relie_question_validee = False
            st.rerun()
        
        suivant = st.button("⏭ Question suivante", key="exo_relie question suivante")
        if suivant:
            if st.session_state.exo_relie_index >= (len(self.lignes) - 1):
                pass
            else:
                st.session_state.exo_relie_index += 1
                st.session_state.exo_relie_question_validee = False
                st.session_state.exo_relie_reponse = None
                st.rerun()

        
        i = st.session_state.exo_relie_index
        ligne = self.lignes[i]

        st.write(f"### 📝 Question {i + 1} sur {len(self.lignes)}")
        self.afficher_question(ligne)

        with st.form("form_relie"):
            reponses = {}

            # Choix du nombre de colonnes (6 max si ≤6, sinon 4)
            n_cols = 6 if len(self.toutes_personnes) <= 6 else 5
            cols = st.columns(n_cols)

            # Affichage des checkbox dans les colonnes
            for idx, personne in enumerate(self.toutes_personnes):
                col = cols[idx % n_cols]
                with col:
                    key = f'checkbox_{ligne["forme"]}_{personne}'
                    reponses[personne] = st.checkbox(personne, key=key)

            valider = st.form_submit_button("Valider")

        if valider:
            st.session_state.exo_relie_reponse = self.check_reponse(ligne,reponses)
            if st.session_state.exo_relie_reponse == "Correct" and not st.session_state.exo_relie_question_validee:
                    st.toast("✅ Bonne réponse !")
                    st.session_state.exo_relie_score += 1
                    st.session_state.exo_relie_question_validee = True
            if st.session_state.exo_relie_reponse == "trop de choix":
                st.info("Trop de choix tue le choix.")

            if st.session_state.exo_relie_reponse == "Incorrect":
                    #st.toast(f"""❌ Oups. La réponse correcte est :
                    #         \n{ligne.mode.capitalize()} {ligne.temps}.""")
                st.markdown(f"""<div style='background-color:#ffdddd; padding:10px; border-radius:5px; color:#900;
                            '>❌ Oups. La réponse correcte est : {ligne["forme"].capitalize()}.</div>""", unsafe_allow_html=True)
                st.session_state.exo_relie_question_validee = True

            if i >= (len(self.lignes) - 1) and st.session_state.exo_relie_question_validee:
                    st.toast(f"✅ Exercice terminé ! Score : {st.session_state.exo_relie_score} / {len(self.lignes)}")
                    st.stop()
        st.divider()
        
    
        
        

            
