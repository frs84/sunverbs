import streamlit as st
import pandas as pd
from exo_ecris import Ligne
from streamlit_echarts import st_echarts
import json

class Exo_devine_temps:
    def __init__(self, df, n=10):
        self.df_exo = df
        nb = min(n, len(self.df_exo))
        self.lignes = [Ligne(ligne) for ligne in self.df_exo.sample(nb).to_dict(orient="records")]
        self.modes = self.df_exo["mode"].unique()
        self.df_MT = self.mode_et_temps()
        self.option = self.build_option()

        # Initialisation de session_state
        st.session_state.exo_devine_index = 0
        st.session_state.exo_devine_score = 0
        st.session_state.exo_devine_question_validee = False
        st.session_state.exo_devine_reponse = None
    
    def afficher_question(self, ligne):
        st.markdown(f"Quelle est le mode et le temps du verbe suivant : **{ligne.verbe}** - {ligne.forme} ?")
    
    def mode_et_temps(self):
        unique = self.df_exo[["mode", "temps"]].drop_duplicates()
        # Construire la structure pour ECharts
        return unique

    def build_option(self):
        plotly_colors = [
            "#C40C0C",  # rouge orangé
            "#0713C0",  # bleu
            "#21A884",  # vert
           ]

        modes = self.df_MT["mode"].unique()
        data = []
        un_seul_mode = len(modes) == 1

        if un_seul_mode:
            # Un seul mode : créer un nœud racine unique avec value et label center
            mode = modes[0]
            couleur = plotly_colors[0]
            enfants = []
            temps_list = self.df_MT[self.df_MT["mode"] == mode]["temps"]
            for temps in temps_list:
                enfants.append({"name": temps, "value": 1,"parent_name":mode})

            data = [{
                "name": mode,
                "value": len(enfants),  # OBLIGATOIRE pour que ce nœud occupe le centre
                "itemStyle": {"color": couleur},
                "label": {
                    "show": True,
                    "position": "center",
                    "fontSize": 20,
                    "formatter": "{b}",
                    "rotate": 0,
                    "align": "center",
                    },
                "children": enfants
            }]
        else:
            for mode in modes:
                enfants = []
                temps_list = self.df_MT[self.df_MT["mode"] == mode]["temps"]
                for temps in temps_list:
                    enfants.append({"name": temps, "value": 1,"parent_name":mode})
                data.append({
                    "name": mode,
                    "value": len(enfants),
                    "children": enfants
                })

        option = {
            "color": plotly_colors,
            "series": [{
                "type": "sunburst",
                "data": data,
                "radius": ["20%", "90%"],
                "label": {
                    "rotate": """function(params) {
                        if(params.data.depth === 1){
                            return 'radial';}
                        if(params.data.depth === 2){
                            return 0;}
                        return 0;}"""},
                "emphasis": {"focus": "none"},
                "nodeClick": False
            }],
            "tooltip": {"show": False}
        }
        return option

    def check_reponse(self, ligne, parent, label):
        if parent is None and label in self.modes:
            return None
    
        possibles = self.df_exo[self.df_exo["formes"] == ligne.forme]
        modes_possibles = possibles["mode"].unique()
        temps_possibles = possibles["temps"].unique()
    
        if parent in modes_possibles and label in temps_possibles:
            return "Correct"
        else:
            return False

    def afficher_exercice(self):
        
        recommencer = st.button("🔁 Recommencer l'exercice", key="exo2 recommencer")
        if recommencer:
            del st.session_state["exo2_obj"]
            st.rerun()
        
        suivant = st.button("⏭ Question suivante", key="exo_devine question suivante")
        if suivant:
            if st.session_state.exo_devine_index >= (len(self.lignes) - 1):
                pass
            else:
                st.session_state.exo_devine_index += 1
                st.session_state.exo_devine_question_validee = False
                st.session_state.exo_devine_reponse = None
                st.rerun()

        
        i = st.session_state.exo_devine_index
        ligne = self.lignes[i]

        st.write(f"### 📝 Question {i + 1} sur {len(self.lignes)}")
        self.afficher_question(ligne)

        # Afficher le Sunburst avec st_echarts
        # Écoute des clics sur les secteurs
        key = f"sunburst_{st.session_state.get('exo_devine_index', 0)}"
        events = st_echarts(
            self.option,
            height=450,
            key=key,
            events={"click": "function(params) {return params.data;}"})
        
        # 'events' contient la donnée du dernier clic (ou None)
        if events and not st.session_state.exo_devine_question_validee:
            label = events.get("name")
            parent = events.get("parent_name")
                        
            reponse = self.check_reponse(ligne, parent, label)
            if reponse == "Correct":
                st.toast("✅ Bonne réponse !")
                st.session_state.exo_devine_score += 1
                st.session_state.exo_devine_question_validee = True
                
            elif reponse is False:
                st.toast(f"""❌ Oups. La réponse correcte est :
                         \n{ligne.mode.capitalize()} {ligne.temps}.""")
                #st.markdown(f"<div style='background-color:#ffdddd; padding:10px; border-radius:5px; color:#900;'>❌ Oups. La réponse correcte est : {ligne.mode} {ligne.temps}.</div>", unsafe_allow_html=True)
                st.session_state.exo_devine_question_validee = True

            if i >= (len(self.lignes) - 1) and st.session_state.exo_devine_question_validee:
                st.toast(f"✅ Exercice terminé ! Score : {st.session_state.exo_devine_score} / {len(self.lignes)}")
                st.stop()
        st.divider()
        
