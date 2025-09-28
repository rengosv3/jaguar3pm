import streamlit as st
from utils import load_draws, load_base_from_file
from strategies import generate_base

def show_insight_tab():
    st.subheader("📊 Insight Draw Terkini")

    draws = load_draws()
    if not draws or len(draws) < 51:
        st.warning("❗ Data draw tidak mencukupi (minimum 51) untuk analisis insight.")
        return

    last_draw = draws[-1]
    base_digits = load_base_from_file()
    base_set = set(''.join(d) for d in base_digits)

    result = last_draw['number']
    match_count = 0
    for d in base_set:
        if all(x in result for x in d):
            match_count += 1

    st.markdown(f"**Tarikh:** {last_draw['date']}")
    st.markdown(f"**Nombor Menang (1st):** `{result}`")
    st.markdown(f"**Jumlah Kombinasi Base Hari Ini:** {len(base_digits)}")
    st.markdown(f"**Padanan Kombinasi Tepat:** {match_count}")

    # Papar base semalam untuk bandingan
    base_last = generate_base(draws[:-1], method='break', recent_n=50)
    base_today = generate_base(draws, method='break', recent_n=50)

    st.markdown("### 🔁 Perbandingan Base Semalam vs Hari Ini")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**Base Semalam (tanpa draw terkini):**")
        st.code('\n'.join([' '.join(b) for b in base_last]), language='text')

    with col2:
        st.markdown("**Base Hari Ini (termasuk draw terkini):**")
        st.code('\n'.join([' '.join(b) for b in base_today]), language='text')