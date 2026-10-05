"""Forecast fraud harian 7 hari ke depan (ala Walmart: lag + kalender).
Model: rata-rata 7 hari x faktor weekday x boost gajian. Backtest 7 hari terakhir -> MAE.
"""
import csv, json
from collections import defaultdict

with open("data/mart_fraud_flags.csv") as f:
    rows = list(csv.DictReader(f))

daily = defaultdict(int)  # day -> total fraud semua tipe
for r in rows:
    daily[r["day"]] += int(r["count"])
days = sorted(daily)

wday_sum, wday_n = defaultdict(int), defaultdict(int)
for d in days:
    wd = __import__("datetime").date(*map(int, d.split("-"))).weekday()
    wday_sum[wd] += daily[d]
    wday_n[wd] += 1
wday_avg = {k: wday_sum[k] / max(wday_n[k], 1) for k in range(7)}
overall = sum(daily.values()) / max(len(daily), 1)
wday_f = {k: (wday_avg[k] / overall if overall else 1.0) for k in range(7)}


def predict(day_str, base):
    from datetime import date
    y, m, d = map(int, day_str.split("-"))
    wd = date(y, m, d).weekday()
    boost = 1.3 if d >= 25 or d <= 1 else 1.0  # minggu gajian
    return round(base * wday_f[wd] * boost, 1)


# backtest: ramal 7 hari terakhir pakai 7 hari sebelumnya
import datetime
maes = []
hist = days[:-7]
for d in days[-7:]:
    base = sum(daily[x] for x in hist[-7:]) / 7
    maes.append(abs(predict(d, base) - daily[d]))
mae = round(sum(maes) / len(maes), 2)

last_base = sum(daily[d] for d in days[-7:]) / 7
last = datetime.date(*map(int, days[-1].split("-")))
out = []
for i in range(1, 8):
    nxt = (last + datetime.timedelta(days=i)).isoformat()
    out.append({"day": nxt, "fraud_forecast": predict(nxt, last_base)})

with open("data/forecast_next7.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["day", "fraud_forecast"])
    w.writeheader()
    w.writerows(out)
json.dump({"mae_backtest_7d": mae, "last_7d_avg": round(last_base, 1)},
          open("reports/forecast_metrics.json", "w"), indent=2)
print(f"forecast OK, MAE backtest={mae}, avg={round(last_base,1)}")
