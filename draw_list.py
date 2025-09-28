import streamlit as st
from utils import load_draws

def show_draw_list_tab():
    st.subheader("📜 Senarai Nombor Draw")

    draws = load_draws()
    if not draws:
        st.warning("Tiada data draw ditemui.")
        return

    # Pilihan bilangan draw untuk dipaparkan
    n = st.slider("Bilangan Draw Terkini Dipaparkan", 10, 500, 100, step=10)

    df = [{
        "Tarikh": draw["date"],
        "1st": draw["number"]
    } for draw in draws[-n:][::-1]]

    st.dataframe(df, use_container_width=True)