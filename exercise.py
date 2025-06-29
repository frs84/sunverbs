import streamlit as st
import pandas as pd

class Ligne:
    def __init__(self, ligne):
        self.forme = ligne["formes"]
        self.verbe = ligne["modèle"]
        self.mode = ligne["mode"]
        self.temps = ligne["temps"]
        self.personne = ligne["personne"]

    def afficher_question(self):
        st.markdown(
            f"Quelle est la forme correcte du verbe **{self.verbe}**, "
            f"{self.mode} {self.temps} : {self.personne} ?"
        )

    def check_reponse(self, reponse_utilisateur):
        def normaliser(texte):
            return texte.strip().lower().replace("’", "'")
        return normaliser(reponse_utilisateur) == normaliser(self.forme)

class ExoQuestion:
    def __init__(self, df, n=10):
        self.df_exo = df.drop_duplicates()
        nb = min(n, len(self.df_exo))
        self.lignes = [Ligne(ligne) for ligne in self.df_exo.sample(nb).to_dict(orient="records")]

        # Écrase l'état précédent sans condition
        st.session_state.exo_index = 0
        st.session_state.score = 0
        st.session_state.question_validee = False
        st.session_state.reponse_exo = ""

    def afficher_exercice(self):
        col1,col2= st.columns(2)

        suivant = col1.button("⏭ Question suivante",key="question suivante")
        recommencer = col2.button("🔁 Recommencer l'exercice", key="recommencer_en_dehors_form")
        
        if suivant:
            if st.session_state.exo_index >= (len(self.lignes)-1):
                st.stop()
            st.session_state.exo_index += 1
            st.session_state.question_validee = False
            st.session_state.reponse_exo = ""
        
        if recommencer:
            del st.session_state["exo_obj"]
            st.rerun()

        i = st.session_state.exo_index
        ligne = self.lignes[i]

        st.markdown(f"### 📝 Question {i + 1} sur {len(self.lignes)}")
        ligne.afficher_question()

        with st.form(f"form_{i}"):
            reponse = st.text_input(
                "Ta réponse :",
                value=st.session_state.get("reponse_exo", ""),
                key=f"reponse"
            )
            valider = st.form_submit_button("✅ Vérifier")
            
        if valider:
            if reponse.strip() == "":
                st.info(f"ℹ️ La réponse correcte est : {ligne.forme}")
            elif ligne.check_reponse(reponse):
                st.success("✅ Bonne réponse !")
                st.session_state.score += 1
            else:
                st.markdown(f"<div style='background-color:#ffdddd; padding:10px; border-radius:5px; color:#900;'>"f"❌ Oups. La réponse correcte est : {ligne.forme}."f"</div>",unsafe_allow_html=True)
            st.session_state.question_validee = True
            st.session_state.reponse_exo = reponse

        
        if i >= (len(self.lignes)-1) and (st.session_state.question_validee):
             st.success(f"✅ Exercice terminé ! Score : {st.session_state.score} / {len(self.lignes)}")
             st.stop()
