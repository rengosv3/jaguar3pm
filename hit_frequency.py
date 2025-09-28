# hit_frequency.py

import streamlit as st
import pandas as pd
from collections import Counter
import os

def show_hit_frequency_tab(draws):
    st.header("📊 Hit Frequency (HF)")

    # Pilihan konfigurasi
    n_draws = st.slider("Jumlah draw terkini:", 10, min(120, len(draws)), 50, step=5, key="hf_draws")
    positions = {
        "P1": st.checkbox("P1", value=True, key="hf_p1"),
        "P2": st.checkbox("P2", value=True, key="hf_p2"),
        "P3": st.checkbox("P3", value=True, key="hf_p3"),
        "P4": st.checkbox("P4", value=True, key="hf_p4"),
    }

    # Subset draw
    recent_draws = draws[-n_draws:]
    selected_positions = [i for i, k in enumerate(positions.values()) if k]

    if not selected_positions:
        st.warning("⚠️ Pilih sekurang-kurangnya satu posisi.")
        return

    # Hitung frekuensi digit
    counter = Counter()
    total_slots = 0

    for draw in recent_draws:
        number = draw["number"]
        for i in selected_positions:
            counter[number[i]] += 1
            total_slots += 1

    if not counter:
        st.warning("❗ Tiada data untuk dikira.")
        return

    # Susun dan kira peratus
    df = pd.DataFrame(counter.items(), columns=["Number", "Times Hit"])
    df["Number"] = df["Number"].apply(lambda x: f"{int(x):02d}")
    df["Hit Frequency"] = df["Times Hit"] / total_slots * 100
    df.sort_values(["Times Hit", "Number"], ascending=[False, True], inplace=True)
    df.insert(0, "Rank", range(1, len(df) + 1))
    df["Hit Frequency"] = df["Hit Frequency"].map("{:.1f}%".format)

    st.dataframe(df, use_container_width=True)

    # Simpan ke fail
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/hit_frequency.txt", index=False, sep="\t")
    st.success("📁 Disimpan ke `data/hit_frequency.txt`")