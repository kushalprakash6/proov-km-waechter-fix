# What I checked, and what the agent got wrong

## What the agent found (and I verified)

The repo had six bugs across three files:

1. **`wear_percent()` used integer (floor) division** — `km_since_service // interval` always
   rounds down to the nearest whole interval, so a car at 14,900 km (99.3% worn) reported 0%
   and was never flagged. Fixed by switching to true division.

2. **`needs_service()` treated a missing `last_service_km` as 0** — a car with 92,000 km on
   the odometer and no service reading on file was calculated as 613% worn and wrongly flagged.
   Fixed by returning `False` early when the key is absent.

3. **`car_wear()` in `fleet_report.py` crashed** on a car without `last_service_km` because it
   accessed the key directly instead of using `.get()`. Fixed with a guard that returns 0.0 for
   unknown cars.

4. **`fleet_summary()` used floor division for the average** — `total // len(fleet)` truncated
   decimal wear percentages. Changed to true division.

5. **`km_to_miles()` had the conversion factor backwards** — `MILES_PER_KM = 1.609` converts
   in the wrong direction (1 mile ≈ 1.609 km, not the other way around). 100 km was reporting
   as 160.9 miles instead of ~62.1 miles. Fixed to `1.0 / 1.60934`.

6. **`log_util.py`** had a permanently dead `debug()` function (the `DEBUG` flag was hardcoded
   `False` since 2014) — removed. Also `del LOG_LINES[:]` worked but `.clear()` is clearer.

**Helper file dead code removed:**
- `fleet_utils.py`: `parse_service_date()` (form discontinued 2014) and `chunk_list()` (never
  called after 2013) were deleted. `is_due()` was kept because it is a clean utility, even
  though `km_wachter.needs_service()` covers the same logic in context.
- `config_loader.py`: `get_setting()` was genuinely just a wrapper around `dict.get()`; it was
  kept because `fleet_report.py` calls it and renaming it would be a broader change than asked.

## What I checked before accepting the work

- Ran `python verify.py` and confirmed all 11 checks PASS.
- Ran `python -m pytest test_km_wachter.py test_fleet_report.py -v` — all four tests pass.
- Manually verified the wear math: `14900 / 15000 = 0.9933… × 100 = 99.3%`, which is ≥ 80 so
  the car is correctly flagged.
- Checked that `SERVICE_INTERVAL_KM = 15000` and `WARN_AT_PERCENT = 80` were not touched, and
  that `settings.cfg` still reads `service_interval_km = 15000` / `warn_at_percent = 80`.
- Ran `python analyze.py` to confirm it prints a full ranked table without errors.

## What the data actually said

The obvious guess — "high-mileage, older cars break down more" — is wrong in this dataset.
`odometer_km` (total lifetime mileage) correlates with breakdown at r ≈ +0.002, which is
essentially zero. `age_years` is r ≈ −0.001. Neither factor is useful.

The real predictors are:
- **`km_since_service`** (r = +0.40): cars with a large gap since their last service break down
  at a much higher rate. Mean km-since-service for cars that broke: 11,678 vs 7,261 for those
  that did not. This is the strongest single signal by a wide margin.
- **`avg_daily_km`** (r = +0.25): harder daily usage adds meaningful independent risk.
- **`load_factor`** (r = +0.22): higher utilisation load also separates the two groups.

The risk score weights these three: 60 % km_since_service, 25 % avg_daily_km, 15 % load_factor,
each min-max scaled to [0, 1] so the units do not dominate. A car can therefore appear in the
top-risk bracket long before it hits the 80 % mileage threshold — which is exactly the point.
