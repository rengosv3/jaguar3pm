import itertools
import random
from collections import Counter

from utils import load_draws

def generate_predictions_from_base(base, max_preds=10):
    combos = [''.join(p) for p in itertools.product(*base)]
    return combos[:max_preds]

def generate_ai_predictions(draws_path="data/draws.txt", top_n=5):
    draws = load_draws(draws_path)
    
    # Kumpul semua digit dari setiap draw
    all_digits = []
    for draw in draws:
        num = draw.get("number", "")
        all_digits.extend(list(num))
    
    # Ambil 6 digit paling kerap
    freq = Counter(all_digits)
    hot_digits = [d for d, _ in freq.most_common(6)]

    preds = set()
    while len(preds) < top_n:
        preds.add("".join(random.sample(hot_digits, 4)))
    
    return sorted(preds)