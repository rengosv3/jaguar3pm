import streamlit as st
import pandas as pd
from collections import defaultdict
import os

def show_last_hit_tab(draws):
    st.header("📅 Last Hit Digit")

    # Slider jumlah draw
    n_draws = st.slider("Jumlah draw terkini:", 10, min(120, len(draws)), 120, step=5, key="lh_draws")

    # Pilihan posisi
    pos_check = {
        0: st.checkbox("P1", True, key="lh_p1"),
        1: st.checkbox("P2", True, key="lh_p2"),
        2: st.checkbox("P3", True, key="lh_p3"),
        3: st.checkbox("P4", True, key="lh_p4"),
    }
    selected_positions = [i for i, v in pos_check.items() if v]

    if not selected_positions:
        st.warning("⚠️ Sila pilih sekurang-kurangnya satu posisi.")
        return

    # Ambil draw terkini
    recent_draws = draws[-n_draws:]
    last_hit = {}

    # Cari tarikh & skip terakhir setiap digit (0–9)
    for d in range(10):
        digit_str = str(d)
        last_date = None
        last_index = None

        for idx in reversed(range(len(recent_draws))):
            number = f"{int(recent_draws[idx]['number']):04d}"
            for i in selected_positions:
                if number[i] == digit_str:
                    last_date = recent_draws[idx]["date"]
                    last_index = idx
                    break
            if last_date:
                break

        skipped = len(recent_draws) - 1 - last_index if last_index is not None else n_draws
        last_hit[digit_str] = {
            "Last Date Hit": last_date if last_date else "—",
            "Games Skipped": skipped
        }

    # Susun dataframe
    rows = []
    for d in range(10):
        digit = f"{d:02d}"
        info = last_hit[str(d)]
        rows.append({
            "Number": digit,
            "Last Date Hit": info["Last Date Hit"],
            "Games Skipped": info["Games Skipped"]
        })

    df = pd.DataFrame(rows)
    df.sort_values(["Games Skipped", "Number"], ascending=[False, True], inplace=True)
    df.insert(0, "Rank", range(1, len(df) + 1))

    # Papar & simpan
    st.dataframe(df, use_container_width=True)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/last_hit.txt", index=False, sep="\t")
    st.success("📁 Disimpan ke `data/last_hit.txt`")