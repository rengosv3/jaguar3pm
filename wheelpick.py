# wheelpick.py

import itertools
from collections import Counter

def get_like_dislike_digits(draws, recent_n=30):
    """
    Dari `draws` (list of {'date','number'}) ambil top-3 paling kerap (like)
    dan bottom-3 paling jarang (dislike) dari `recent_n` terakhir.
    """
    recent = [d['number'] for d in draws[-recent_n:] if 'number' in d and len(d['number']) == 4]
    cnt = Counter()
    for num in recent:
        cnt.update(num)
    most = [d for d, _ in cnt.most_common(3)]
    least = [d for d, _ in cnt.most_common()[-3:]] if len(cnt) >= 3 else []
    return most, least

def generate_wheel_combos(base, lot="0.10", arah="kiri"):
    """
    Dari `base` (list of 4 lists), hasilkan semua kombinasi
    dalam format "<num>#####<lot>" ikut arah:
      - 'kiri': P1 → P4
      - 'kanan': P4 → P1
    """
    if arah == "kanan":
        base = list(reversed(base))
    elif arah != "kiri":
        raise ValueError("arah mesti 'kiri' atau 'kanan'")

    combos = []
    for digits in itertools.product(*base):
        num = ''.join(digits)
        combos.append(f"{num}#####{lot}")
    return combos

def filter_wheel_combos(
    combos, draws,
    no_repeat=False,      # buang digit berulang
    no_triple=False,      # buang ada triple
    no_pair=False,        # buang ada pair
    no_ascend=False,      # buang menaik
    use_history=False,    # buang yang pernah keluar
    sim_limit=4,          # max sama posisi dengan last draw
    likes=None,           # wajib ada sekurang-kurangnya satu digit ini
    dislikes=None         # buang kalau ada digit ini
):
    """
    Tapis `combos` (list of "NNNN#####lot") mengikut kriteria.
    `draws` adalah history untuk sebarang penapisan.
    `likes`/`dislikes` adalah list digit (strings).
    `sim_limit`: max persamaan posisi dgn draw terakhir.
    """
    past = {d['number'] for d in draws}
    last = draws[-1]['number'] if draws else "0000"
    out = []
    likes = likes or []
    dislikes = dislikes or []

    for entry in combos:
        num, _ = entry.split("#####")
        digs = list(num)

        if no_repeat and len(set(digs)) < 4:
            continue
        if no_triple and any(digs.count(d) >= 3 for d in set(digs)):
            continue
        if no_pair and any(digs.count(d) == 2 for d in set(digs)):
            continue
        if no_ascend and num in ["0123", "1234", "2345", "3456", "4567", "5678", "6789"]:
            continue
        if use_history and num in past:
            continue
        sim = sum(1 for a, b in zip(num, last) if a == b)
        if sim > sim_limit:
            continue
        if likes and not any(d in likes for d in digs):
            continue
        if dislikes and any(d in dislikes for d in digs):
            continue

        out.append(entry)
    return out

def pick_from_base(base, index, arah="kiri"):
    """
    Pilih satu digit dari setiap P1–P4 pada posisi `index`,
    dan susun mengikut `arah`:
      - 'kiri': P1 → P4
      - 'kanan': P4 → P1

    Returns:
        String 4-digit hasil susunan.
    """
    if not (0 <= index < len(base[0])):
        raise IndexError("index di luar julat panjang base")

    if arah == "kiri":
        order = [0, 1, 2, 3]
    elif arah == "kanan":
        order = [3, 2, 1, 0]
    else:
        raise ValueError("arah mesti 'kiri' atau 'kanan'")

    digits = [base[i][index] for i in order]
    return ''.join(digits)