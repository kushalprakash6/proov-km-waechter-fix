# analyze.py
#
# FINDINGS (from the data, not from assumptions):
#   - km_since_service is the strongest predictor of breakdown (r = +0.40): cars with more
#     kilometres since their last service break down at a much higher rate.
#   - avg_daily_km (r = +0.25) and load_factor (r = +0.22) add independent signal.
#   - Total odometer (r ≈ 0.002) and age_years (r ≈ −0.001) are useless predictors —
#     a high-mileage old car is no more likely to break than a new one at the same service stage.
#
# RISK SCORE (0–100):
#   Weighted sum of the three significant factors, each min-max scaled to [0, 1]:
#     60 % km_since_service  +  25 % avg_daily_km  +  15 % load_factor
#   Multiplied by 100 and rounded to one decimal place.

import pandas as pd


def min_max_scale(series: pd.Series) -> pd.Series:
    """Scale a series to the [0, 1] range."""
    lo, hi = series.min(), series.max()
    if hi == lo:
        return pd.Series(0.5, index=series.index)
    return (series - lo) / (hi - lo)


def main() -> None:
    df = pd.read_csv("fleet_history.csv")

    # ── 1. Show which factors actually separate the two groups ───────────────
    print("=== Correlation with breakdown (r, point-biserial) ===")
    predictors = ["odometer_km", "km_since_service", "avg_daily_km", "load_factor", "age_years"]
    for col in predictors:
        r = df[col].corr(df["broke_down"])
        print(f"  {col:25s}  r = {r:+.3f}")

    print()
    print("=== Mean value — did NOT break down vs DID break down ===")
    summary = df.groupby("broke_down")[predictors].mean()
    summary.index = ["no breakdown", "breakdown"]
    print(summary.T.to_string())
    print()
    print("Key insight: odometer_km and age_years have near-zero correlation with")
    print("breakdown. km_since_service, avg_daily_km, and load_factor are the real signals.")
    print()

    # ── 2. Build risk score ──────────────────────────────────────────────────
    df["risk_score"] = (
        0.60 * min_max_scale(df["km_since_service"])
        + 0.25 * min_max_scale(df["avg_daily_km"])
        + 0.15 * min_max_scale(df["load_factor"])
    ) * 100

    # ── 3. Print cars ranked by risk (highest first) ─────────────────────────
    ranked = df[["car_id", "risk_score", "km_since_service", "avg_daily_km",
                 "load_factor", "broke_down"]].sort_values("risk_score", ascending=False)
    ranked = ranked.reset_index(drop=True)
    ranked["risk_score"] = ranked["risk_score"].round(1)

    print("=== Cars ranked by risk score (highest first) ===")
    print(f"{'#':<4} {'car_id':<12} {'risk':>6}  {'km_since_svc':>13}  {'daily_km':>9}  {'load':>6}  broke_down")
    print("-" * 72)
    for i, row in ranked.iterrows():
        flag = " ← BROKE DOWN" if row["broke_down"] == 1 else ""
        print(
            f"{i+1:<4} {row['car_id']:<12} {row['risk_score']:>6.1f}  "
            f"{int(row['km_since_service']):>13,}  {int(row['avg_daily_km']):>9,}  "
            f"{row['load_factor']:>6.2f}{flag}"
        )


if __name__ == "__main__":
    main()
