import os
import pandas as pd
from collections import Counter
from wheelpick import get_like_dislike_digits

def generate_base(draws, method='frequency', recent_n=50):
    total = len(draws)

    requirements = {
        'frequency': recent_n,
        'polarity_shift': recent_n,
        'hybrid': recent_n,
        'break': recent_n,
        'smartpattern': 60,
        'hitfq': recent_n
    }

    if method not in requirements:
        raise ValueError(f"Unknown strategy '{method}'")
    if total < requirements[method]:
        raise ValueError(f"Not enough draws for '{method}' (need {requirements[method]}, have {total})")

    # === FREQUENCY ===
    def freq_method(draws_slice, n):
        counters = [Counter() for _ in range(4)]
        for d in draws_slice[-n:]:
            for i, digit in enumerate(d['number']):
                counters[i][digit] += 1
        return [[d for d, _ in c.most_common(5)] for c in counters]

    # === POLARITY SHIFT (replace GAP) ===
    def polarity_shift_method(draws_slice, n):
        recent_half = draws_slice[-n:]
        past_half = draws_slice[-(2*n):-n] if len(draws_slice) >= 2 * n else draws_slice[:-(n)]

        recent_counter = [Counter() for _ in range(4)]
        past_counter = [Counter() for _ in range(4)]

        for d in recent_half:
            for i, digit in enumerate(d['number']):
                recent_counter[i][digit] += 1

        for d in past_half:
            for i, digit in enumerate(d['number']):
                past_counter[i][digit] += 1

        shifted_digits = []
        for pos in range(4):
            delta = {}
            for digit in map(str, range(10)):
                diff = recent_counter[pos][digit] - past_counter[pos][digit]
                delta[digit] = diff
            top5 = sorted(delta.items(), key=lambda x: -x[1])[:5]
            shifted_digits.append([d for d, _ in top5])
        return shifted_digits

    # === HYBRID ===
    def hybrid_method(draws_slice, n):
        f = freq_method(draws_slice, n)
        p = polarity_shift_method(draws_slice, n)
        combined = []
        for f_list, p_list in zip(f, p):
            cnt = Counter(f_list + p_list)
            combined.append([d for d, _ in cnt.most_common(5)])
        return combined

    # === BREAK ===
    def generate_break_base(draws_slice, n):
        recent_draws = draws_slice[-n:]
        result = []

        for i in range(4):
            pos_digits = [f"{int(d['number']):04d}"[i] for d in recent_draws]
            counter = Counter(pos_digits)
            top10 = counter.most_common(10)
            selected = [digit for digit, _ in top10[5:10]]  # Rank 6–10
            result.append(selected)

        return result

    # === SMARTPATTERN ===
    def smartpattern_method(draws_slice):
        strategies = [
            generate_base(draws_slice, 'frequency', 50),
            generate_base(draws_slice, 'polarity_shift', 50),
            generate_base(draws_slice, 'hybrid', 40),
            generate_base(draws_slice, 'hitfq', 30),
        ]
        result = []
        for pos in range(4):
            votes = Counter()
            for strat in strategies:
                for digit in strat[pos]:
                    votes[digit] += 1
            top5 = [d for d, _ in votes.most_common(5)]
            result.append(top5)
        return result

    # === HIT FREQUENCY ===
    def hitfq_method(draws_slice, n):
        recent_draws = draws_slice[-n:]
        counters = [Counter() for _ in range(4)]
        for draw in recent_draws:
            for i, digit in enumerate(draw['number']):
                counters[i][digit] += 1
        base = []
        for c in counters:
            ranked = sorted(c.items(), key=lambda x: (-x[1], int(x[0])))
            base.append([d for d, _ in ranked[:5]])
        return base

    # === STRATEGY DISPATCH ===
    if method == 'frequency':
        return freq_method(draws, recent_n)
    elif method == 'polarity_shift':
        return polarity_shift_method(draws, recent_n)
    elif method == 'hybrid':
        return hybrid_method(draws, recent_n)
    elif method == 'break':
        return generate_break_base(draws, recent_n)
    elif method == 'smartpattern':
        return smartpattern_method(draws)
    elif method == 'hitfq':
        return hitfq_method(draws, recent_n)
    else:
        raise ValueError(f"Unsupported method '{method}'")