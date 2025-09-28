import os
import requests
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from bs4 import BeautifulSoup

from utils import load_draws, save_base_to_file
from strategies import generate_base

MAX_DAYS_BACK = 60  # Hanya 60 hari terakhir

def get_1st_prize(date_str: str) -> str | None:
    """
    Scrape 1st prize 4D untuk tarikh YYYY-MM-DD dari link Jaguar4D baru.
    Pulangkan string 4-digit jika jumpa, else None.
    """
    url = f"http://live4d.jaguar20.biz/jaguarlive4d/?date={date_str}"
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        if resp.status_code != 200:
            print(f"❌ Status bukan 200 untuk {date_str}: {resp.status_code}")
            return None
        soup = BeautifulSoup(resp.text, "html.parser")
        
        # Cari nombor 1st prize — sesuaikan selector mengikut HTML sebenar
        # Contoh: span dengan class "first" atau id "firstPz"
        prize_tag = soup.find("span", class_="first")
        txt = prize_tag.text.strip() if prize_tag else ""
        if txt.isdigit() and len(txt) == 4:
            print(f"✅ {date_str} → 1st prize: {txt}")
            return txt
        print(f"❌ Tidak jumpa 1st Prize untuk {date_str}")
    except Exception as e:
        print(f"❌ Ralat semasa request untuk {date_str}: {e}")
    return None

def update_draws_60days(file_path: str = 'data/draws.txt', update_base: bool = False) -> str:
    """
    Update 'data/draws.txt' dengan draw baru untuk 60 hari terakhir sahaja.
    """
    draws = load_draws(file_path)
    existing = {d['date'] for d in draws}

    # Masa semasa ikut waktu Malaysia
    tz = ZoneInfo("Asia/Kuala_Lumpur")
    now_my = datetime.now(tz)

    # Tentukan tarikh mula dan tarikh akhir (60 hari terakhir)
    start_date = (now_my - timedelta(days=MAX_DAYS_BACK-1)).date()
    end_date = now_my.date()

    os.makedirs(os.path.dirname(file_path), exist_ok=True)
    added = []

    # Langkah scrape & append
    with open(file_path, 'a') as f:
        current = start_date
        while current <= end_date:
            ds = current.strftime("%Y-%m-%d")
            current += timedelta(days=1)
            if ds in existing:
                continue
            prize = get_1st_prize(ds)
            if prize:
                f.write(f"{ds} {prize}\n")
                added.append(ds)

    # Update base_last.txt jika ada draw baru
    if added:
        draws_updated = load_draws(file_path)
        if len(draws_updated) >= 51:
            base_before = generate_base(draws_updated[:-1], method='break', recent_n=50)
            save_base_to_file(base_before, 'data/base_last.txt')

    # Update base.txt jika diminta
    if update_base:
        draws_updated = load_draws(file_path)
        if len(draws_updated) >= 50:
            base_now = generate_base(draws_updated, method='break', recent_n=50)
            save_base_to_file(base_now, 'data/base.txt')

    return f"✔️ {len(added)} draw baru ditambah." if added else "✔️ Tiada draw baru."