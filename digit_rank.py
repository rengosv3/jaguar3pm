import streamlit as st
import pandas as pd
from collections import Counter
import os

def show_digit_rank_tab(draws):
    st.header("📊 Digit Rank")

    n_draws = st.slider("Jumlah draw terkini:", 10, min(120, len(draws)), 50, step=5, key="dr_draws")

    pos_check = {
        0: st.checkbox("P1", True, key="dr_p1"),
        1: st.checkbox("P2", True, key="dr_p2"),
        2: st.checkbox("P3", True, key="dr_p3"),
        3: st.checkbox("P4", True, key="dr_p4"),
    }
    selected_positions = [i for i, v in pos_check.items() if v]

    if not selected_positions:
        st.warning("⚠️ Sila pilih sekurang-kurangnya satu posisi.")
        return

    recent_draws = draws[-n_draws:]
    os.makedirs("data", exist_ok=True)

    for pos in selected_positions:
        # Hit Frequency
        counter = Counter()
        for draw in recent_draws:
            number = f"{int(draw['number']):04d}"
            digit = f"{int(number[pos]):02d}"
            counter[digit] += 1

        freq_df = pd.DataFrame(counter.items(), columns=["Digit", "Times Hit"])
        freq_df["Hit Frequency"] = freq_df["Times Hit"] / len(recent_draws) * 100

        # Last Hit ala last_hit.py
        last_hit = {}
        for d in range(10):
            digit_str = f"{d}"
            last_index = None

            for idx in reversed(range(len(recent_draws))):
                number = f"{int(recent_draws[idx]['number']):04d}"
                if number[pos] == digit_str:
                    last_index = idx
                    break

            skipped = len(recent_draws) - 1 - last_index if last_index is not None else n_draws
            last_hit[f"{d:02d}"] = skipped

        # Gabung semua
        rows = []
        for d in range(10):
            digit = f"{d:02d}"
            freq = freq_df[freq_df["Digit"] == digit]["Hit Frequency"].values
            freq = float(freq[0]) if len(freq) > 0 else 0.0
            skipped = last_hit[digit]

            if freq >= 12.0 and skipped <= 3:
                status = "🔥 Hot"
            elif freq <= 5.0 and skipped >= 20:
                status = "🧊 Cold"
            elif skipped >= 25:
                status = "🧓 Stale"
            elif skipped <= 2:
                status = "🌱 Fresh"
            else:
                status = "—"

            rows.append({
                "Digit": digit,
                "Hit Frequency (%)": round(freq, 1),
                "Games Skipped": skipped,
                "Status": status
            })

        df = pd.DataFrame(rows)
        df.sort_values(["Status", "Games Skipped"], ascending=[True, False], inplace=True)
        df.insert(0, "Rank", range(1, len(df) + 1))

        st.subheader(f"📌 Posisi P{pos + 1}")
        st.dataframe(df, use_container_width=True)

        path = f"data/digit_rank_p{pos+1}.txt"
        df.to_csv(path, index=False, sep="\t")
        st.success(f"📁 Disimpan ke `{path}`")