import streamlit as st
import pandas as pd
from exo_ecris_forme import Ligne
from streamlit_plotly_events import plotly_events
import plotly.express as px

#---CSS---#



class Exo_devine_temps:
    def __init__(self,df,n=10):
        self.df_exo = df
        nb = min(n, len(self.df_exo))
        self.lignes = [Ligne(ligne) for ligne in self.df_exo.sample(nb).to_dict(orient="records")]
        self.modes = self.df_exo["mode"].unique()
        self.df_MT = self.mode_et_temps()
        self.fig=self.choix_mode_et_temps()
        
    
        # Écrase l'état précédent sans condition
        st.session_state.exo2_index = 0
        st.session_state.exo2_score = 0
        st.session_state.exo2_question_validee = False
        st.session_state.exo2_reponse_exo = None
    
    def afficher_question(self,ligne):
        st.markdown(
            f"Quelle est le mode et le temps du verbe suivant : **{ligne.verbe}** - {ligne.forme} ?")
    
    def mode_et_temps(self):
        unique = self.df_exo[["mode", "temps"]].drop_duplicates()
        unique["valeur"] = 1
        return unique
    
    def choix_mode_et_temps(self):
        if len(self.df_MT["mode"].unique())==1:
            couleur ="temps"
        else: 
            couleur = "mode"

        fig = px.sunburst(
            self.df_MT,
            path=["mode", "temps"],
            values="valeur",
            color=couleur,
            color_discrete_sequence=px.colors.qualitative.Plotly)

#       fig.update_layout(height=500,width=500)
        fig.update_layout(margin=dict(t=10, b=10, l=10, r=10))
        fig.update_traces(hoverinfo='skip', hovertemplate=None)
        return fig
    
    def check_reponse(self,ligne, parent, label):
        possibles = self.df_exo[self.df_exo["formes"]== ligne.forme]
        modes_possibles = possibles["mode"].unique()
        temps_possibles = possibles["temps"].unique()

        if parent in modes_possibles and label in temps_possibles:
            return "Correct"
        elif label in self.modes:
                st.rerun()
        else:
            return False
         
        
    def afficher_exercice(self):
        st.divider()
        st.subheader("""\nExercice 2.""")
        col1,col2= st.columns(2)

        recommencer = col2.button("🔁 Recommencer l'exercice", key="exo2 recommencer_en_dehors_form")
        suivant = col1.button("⏭ Question suivante",key="exo2 question suivante")
        
        if suivant:
            if st.session_state.exo2_index >= (len(self.lignes)-1):
                pass
            else:
                st.session_state.exo2_index += 1
                st.session_state.exo2_question_validee = False
                st.session_state.exo2_reponse = None
                st.rerun()
        
        if recommencer:
            del st.session_state["exo2_obj"]
            st.rerun()

        i = st.session_state.exo2_index
        ligne = self.lignes[i]

        st.write(f"### 📝 Question {i + 1} sur {len(self.lignes)}")
        self.afficher_question(ligne)
        
        
        # Capture des événements
        selected = plotly_events(self.fig, click_event=True, hover_event=False)
        
        if selected and not st.session_state.exo2_question_validee:
        
            point = selected[0]
            point_idx = point.get('pointNumber')  # ⚠️ 'pointNumber' pour les sunburst

            if point_idx is not None:
                data = self.fig.data[0]

                label = data.labels[point_idx]
                parent = data.parents[point_idx]
                
                reponse=self.check_reponse(ligne, parent, label)
                if reponse == "Correct":
                    st.success("✅ Bonne réponse !")
                    st.session_state.exo2_score += 1
                else:
                    st.markdown(f"<div style='background-color:#ffdddd; padding:10px; border-radius:5px; color:#900;'>"f"❌ Oups. La réponse correcte est : {ligne.mode} {ligne.temps}."f"</div>",unsafe_allow_html=True)
            st.session_state.exo2_question_validee = True

            
        
            if i >= (len(self.lignes)-1) and (st.session_state.exo2_question_validee):
                st.success(f"✅ Exercice terminé ! Score : {st.session_state.exo2_score} / {len(self.lignes)}")
                st.stop()
                    