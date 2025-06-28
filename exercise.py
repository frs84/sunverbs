# Formulaire réponse
    with st.form("form_exo"):
        reponse = st.text_input("Ta réponse :", key="reponse_exo")
        col1, col2 = st.columns([1, 1])
        valider = col1.form_submit_button("✅ Vérifier")
        nouvelle = col2.form_submit_button("🔄 Nouvelle question")

        if valider:
            bonne_reponse = forme.strip().lower()
            utilisateur = reponse.strip().lower().replace("’","'")

            if utilisateur == bonne_reponse:
                st.session_state.exercice_resultat = ("success", "✅ Bonne réponse !")
            else:
                st.session_state.exercice_resultat = (
                    "error",
                    f"❌ Oups. La bonne forme est : {forme}."
                )

        if nouvelle:
            nouvelle_question(df_exo)

    # Affichage du message de résultat
    if (
        "exercice_resultat" in st.session_state and
        st.session_state.exercice_resultat is not None and
        isinstance(st.session_state.exercice_resultat, (tuple, list)) and
        len(st.session_state.exercice_resultat) == 2
    ):
        niveau, message = st.session_state.exercice_resultat
        couleur = "green" if niveau == "success" else "black"
        st.markdown(f"<div style='color: {couleur}'>{message}</div>",
           unsafe_allow_html=True)


def gerer_interactions(df_exo):
    if "ligne_exercice" not in st.session_state:
        st.session_state.ligne_exercice = df_exo.sample(1).iloc[0]
        st.session_state.exercice_resultat = None
        st.session_state.reponse_exo = ""


def nouvelle_question(df_exo):
    st.session_state.ligne_exercice = df_exo.sample(1).iloc[0]
    st.session_state.exercice_resultat = None
    if "reponse_exo" in st.session_state:
        del st.session_state["reponse_exo"]
    st.rerun()
