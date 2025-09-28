import pandas as pd
from strategies import generate_base

strategies = ['frequency', 'polarity_shift', 'hybrid', 'break', 'smartpattern', 'hitfq']

def match_insight(fp: str, base: list[list[str]], reverse: bool = False) -> list[str]:
    digits = list(fp[::-1] if reverse else fp)
    return ["✅" if digits[i] in base[i] else "❌" for i in range(4)]

def run_backtest(
    draws: list[dict],
    strategy: str = 'hybrid',
    recent_n: int = 50,
    arah: str = 'left',
    backtest_rounds: int = 10
) -> tuple[pd.DataFrame, int]:
    total = len(draws)
    min_req = {'frequency':50, 'hybrid':50, 'smartpattern':60, 'break':50, 'hitfq':50, 'polarity_shift':50}
    req = min_req.get(strategy, 50)

    if total < backtest_rounds + req:
        raise ValueError(f"Not enough draws for backtest '{strategy}': need {backtest_rounds + req}, have {total}")

    reverse = arah == 'right'
    records = []

    for i in range(backtest_rounds):
        test_draw = draws[-(i+1)]
        past_draws = draws[:-(i+1)]

        try:
            base = generate_base(past_draws, method=strategy, recent_n=recent_n)
        except:
            continue

        insight = match_insight(test_draw['number'], base, reverse)
        records.append({
            'Tarikh': test_draw['date'],
            'Result 1st': test_draw['number'],
            'Insight': ' '.join(f"P{j+1}:{s}" for j, s in enumerate(insight))
        })

    df = pd.DataFrame(records[::-1])

    # ✅ Kira hanya yang full 4x "✅"
    matched = sum(1 for r in records if all(s.endswith("✅") for s in r['Insight'].split()))
    return df, matched

def evaluate_strategies(draws: list[dict], test_n: int = 20) -> pd.DataFrame:
    results = []

    for method in strategies:
        full_hits = 0
        tested = 0

        for i in range(test_n):
            subset = draws[:-(test_n - i)]
            actual = draws[-(test_n - i)]['number']

            try:
                base = generate_base(subset, method)
            except:
                continue

            if all(actual[pos] in base[pos] for pos in range(4)):
                full_hits += 1

            tested += 1

        hit_rate = (full_hits / tested * 100) if tested else 0
        results.append({
            'Strategy': method,
            'Tested Draws': tested,
            'Total Full Hits': full_hits,
            'Hit Rate (%)': round(hit_rate, 2)
        })

    return pd.DataFrame(results).sort_values(by='Hit Rate (%)', ascending=False).reset_index(drop=True)