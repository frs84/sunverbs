import streamlit as st
import pandas as pd
from exo_ecris_forme import Ligne
from streamlit_echarts import st_echarts
class Exo_devine_temps:
    def __init__(self, df, n=10):
        self.df_exo = df
        nb = min(n, len(self.df_exo))
        self.lignes = [Ligne(ligne) for ligne in self.df_exo.sample(nb).to_dict(orient="records")]
        self.modes = self.df_exo["mode"].unique()
        self.df_MT = self.mode_et_temps()
        self.option = self.build_option()

        # Initialisation de session_state
        st.session_state.exo2_index = 0
        st.session_state.exo2_score = 0
        st.session_state.exo2_question_validee = False
        st.session_state.exo2_reponse_exo = None
    
    def afficher_question(self, ligne):
        st.markdown(f"Quelle est le mode et le temps du verbe suivant : **{ligne.verbe}** - {ligne.forme} ?")
    
    def mode_et_temps(self):
        unique = self.df_exo[["mode", "temps"]].drop_duplicates()
        # Construire la structure pour ECharts
        return unique

    def build_option(self):
        plotly_like_colors = ["#4e79a7",  # bleu doux
                              "#f28e2c",  # orange
                              "#e15759",  # rouge
                              "#76b7b2",  # vert/bleu
                              "#59a14f",  # vert
                              "#edc949",  # jaune
                              "#af7aa1",  # violet
                              "#ff9da7",  # rose clair
                              "#9c755f",  # brun clair
                              "#bab0ab",  # gris doux]

        data = []
        modes = self.df_MT["mode"].unique()

        for mode in modes:
            enfants = []
            temps_list = self.df_MT[self.df_MT["mode"] == mode]["temps"]
            for i, temps in enumerate(temps_list):
                couleur = plotly_colors[i % len(plotly_colors)]
                enfants.append({
                    "name": temps,
                    "value": 1,
                    "itemStyle": {"color": couleur}
                })
            data.append({"name": mode, "children": enfants})

        option = {
            "color": plotly_colors,  # utile si plusieurs modes
            "series": [{
                "type": "sunburst",
                "data": data,
                "radius": ["10%", "90%"],
                "label": {
                    "rotate": """function(params) {
                        if(params.data.depth === 1){
                            return 'radial';
                        }
                        if(params.data.depth === 2){
                            return 0;
                        }
                        return 0;
                    }"""
                },
                "emphasis": {"focus": "ancestor"},
                "nodeClick": False
            }],
            "tooltip": {"show": False},
        }

        return option



    def check_reponse(self, ligne, parent, label):
        possibles = self.df_exo[self.df_exo["formes"] == ligne.forme]
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
        col1, col2 = st.columns(2)

        recommencer = col2.button("🔁 Recommencer l'exercice", key="exo2 recommencer_en_dehors_form")
        suivant = col1.button("⏭ Question suivante", key="exo2 question suivante")

        if suivant:
            if st.session_state.exo2_index >= (len(self.lignes) - 1):
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

        # Afficher le Sunburst avec st_echarts
        # Écoute des clics sur les secteurs
        events = st_echarts(
    self.option,
    height=500,
    key="sunburst",
    events={
        "click": "function(params) { return params.data; }"
    }
)

        # 'events' contient la donnée du dernier clic (ou None)
        if events and not st.session_state.exo2_question_validee:
            # Exemple de structure event: {"name":"présent","dataIndex":1,...}
            label = events.get("name")
            parent = None

            # Trouver le parent mode
            # Ici on cherche dans self.option['series'][0]['data']
            for item in self.option["series"][0]["data"]:
                if label == item["name"]:
                    parent = None  # mode cliqué (pas temps)
                    break
                for child in item.get("children", []):
                    if label == child["name"]:
                        parent = item["name"]
                        break
            
            reponse = self.check_reponse(ligne, parent, label)
            if reponse == "Correct":
                st.success("✅ Bonne réponse !")
                st.session_state.exo2_score += 1
            else:
                st.markdown(f"<div style='background-color:#ffdddd; padding:10px; border-radius:5px; color:#900;'>❌ Oups. La réponse correcte est : {ligne.mode} {ligne.temps}.</div>", unsafe_allow_html=True)
            st.session_state.exo2_question_validee = True

            if i >= (len(self.lignes) - 1) and st.session_state.exo2_question_validee:
                st.success(f"✅ Exercice terminé ! Score : {st.session_state.exo2_score} / {len(self.lignes)}")
                st.stop()
