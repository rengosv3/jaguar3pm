import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

from utils import load_draws, save_base_to_file
from strategies import generate_base

def get_1st_prize(date_str: str) -> str | None:
    """
    Scrape 1st prize 4D untuk tarikh YYYY-MM-DD.
    Pulangkan string 4-digit jika jumpa, else None.
    """
    url = f"https://gdlotto.net/results/ajax/_result.aspx?past=1&d={date_str}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Status bukan 200 untuk {date_str}: {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        prize_tag = soup.find("span", id="1stPz")
        txt = prize_tag.text.strip() if prize_tag else ""
        if txt.isdigit() and len(txt) == 4:
            print(f"✅ {date_str} → {txt}")
            return txt
        print(f"❌ Tidak jumpa 1st Prize untuk {date_str}")
    except Exception as e:
        print(f"❌ Ralat semasa request untuk {date_str}: {e}")
    return None

def update_draws(file_path: str = 'data/draws.txt', update_base: bool = False) -> str:
    """
    Update 'data/draws.txt' dengan draw baru dari 2020-08-01 hingga result terakhir yang mungkin keluar.
    Jika update_base=True, akan update 'data/base.txt' juga.
    """
    draws = load_draws(file_path)
    existing = {d['date'] for d in draws}

    # Masa semasa ikut waktu Malaysia
    tz = ZoneInfo("Asia/Kuala_Lumpur")
    now_my = datetime.now(tz)

    # Jika jam sekarang >= 20:00, ambil hingga hari ini; jika belum, ambil hingga semalam
    cutoff_hour = 20
    latest_date = now_my.date() if now_my.hour >= cutoff_hour else (now_my - timedelta(days=1)).date()

    # Paksa mula dari 2020-08-01
    last_date = datetime.strptime("2020-06-01", "%Y-%m-%d").date()
    current = last_date
    added = []

    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # Langkah 2: scrape & append
    with open(file_path, 'a') as f:
        while current <= latest_date:
            ds = current.strftime("%Y-%m-%d")
            current += timedelta(days=1)
            if ds in existing:
                continue
            prize = get_1st_prize(ds)
            if prize:
                f.write(f"{ds} {prize}\n")
                added.append(ds)

    # Langkah 3: jika ada draw baru, update base_last.txt
    if added:
        draws_updated = load_draws(file_path)
        if len(draws_updated) >= 51:
            base_before = generate_base(draws_updated[:-1], method='break', recent_n=50)
            save_base_to_file(base_before, 'data/base_last.txt')

    # Langkah 4: jika diminta, update base.txt
    if update_base:
        draws_updated = load_draws(file_path)
        if len(draws_updated) >= 50:
            base_now = generate_base(draws_updated, method='break', recent_n=50)
            save_base_to_file(base_now, 'data/base.txt')

    return f"✔️ {len(added)} draw baru ditambah." if added else "✔️ Tiada draw baru."
    
# Boleh run terus dari terminal
if __name__ == "__main__":
    print(update_draws(update_base=True))