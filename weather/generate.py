"""Write a synthetic weather network under data/raw.

A 100 km square of land, with the sea to its west and a ridge across its north,
holds 16 sites in three regions. The weather is simulated for every hour of
2025, and each site keeps an hourly temperature file for every fourth day, beside a calibration file for its sensor and a file saying where it
stands; the landscape itself is in terrain.csv, and a file for each alert gives
its threshold. The same seed gives the same files on every run.

Each hour's temperature is the sum of signals, each set by where the site is:

- a yearly cycle, whose swing grows with the region's distance from the sea;
- a day-night cycle, larger inland and on clear days;
- weather: fronts the whole network shares, which the sea damps on the coast,
  with a gradient that moves from west to east, plus each region's own fronts
  and cloud;
- the lapse rate, 6.5 °C colder for each kilometre of height;
- a microclimate at some sites: a town that holds its heat at night, a shaded
  site that misses the afternoon sun, and a valley floor that pools cold air on
  clear nights.

The sensors add their own faults: a gain and offset that calibration undoes,
dropouts and spikes, and one that drifts warmer. One site starts late, one
loses its battery for three weeks, and the recipe excludes two days at another.
"""

import argparse
import datetime
import json
import math
import random
from pathlib import Path

YEAR = 2025
DAYS = 365
SIZE = 100  # km

# The sites, by region, and the part of the map each region covers: (x0, y0, x1, y1) in km.
REGIONS = {
    "coast": ((2, 6, 20, 66), ["alder", "clover", "dune", "kelp", "thrift"]),
    "valley": ((30, 12, 88, 62), ["birch", "elm", "hazel", "poppy", "sedge", "willow"]),
    "highland": ((38, 82, 90, 97), ["aspen", "fir", "heather", "juniper", "larch"]),
}
EVERY = 4  # days between the files a site keeps

# Sites with something of their own.
TOWN, SHADED, POOLING, DRIFTING = "elm", "fir", "sedge", "poppy"
LATE = ("clover", 60)  # installed on 2 March
BATTERY = ("heather", range(14, 35))  # three weeks in January without files

ALERTS = {"frost": {"below": 0.0}, "heat": {"above": 27.0}}

SEA_LEVEL_MEAN = 11.0  # °C, the yearly mean at sea level
LAPSE = 6.5 / 1000  # °C a metre


def elevation(x, y):
    """The land's height in metres: rising from the coast, with a ridge across the north and a shallow valley."""
    rise = 4 + 2.2 * x
    ridge = 750 * math.exp(-((x - 62) ** 2) / (2 * 40 ** 2) - ((y - 90) ** 2) / (2 * 11 ** 2))
    trough = -60 * math.exp(-((x - 45) ** 2) / (2 * 12 ** 2) - ((y - 42) ** 2) / (2 * 14 ** 2))
    return max(2.0, rise + ridge + trough)


def continentality(x):
    """How far from the sea's influence a place is, from 0 on the coast to near 1 far inland.

    Each site takes its region's, from the middle of the region's box, so that sites in one
    region share a climate and differ only by their elevation and microclimate.
    """
    return 1 - math.exp(-x / 30)


def ar1(rng, n, keep, scale):
    """A series that wanders: each value keeps a share of the last, plus fresh noise."""
    series, value = [], 0.0
    for _ in range(n):
        value = keep * value + rng.gauss(0, scale)
        series.append(value)
    return series


def weather(rng, regions):
    """The day-to-day weather, each region's a mix of what the network shares and its own.

    Fronts: a share for the whole network, and a smaller one for each region.
    Gradient: a west-east difference across the network that moves day to day.
    Cloud: each region's sky, partly the network's and partly its own, from 0 clear to 1 overcast.
    """
    shared_front = ar1(rng, DAYS, 0.75, 1.4)
    gradient = ar1(rng, DAYS, 0.6, 1.0)
    shared_cloud = ar1(rng, DAYS, 0.7, 0.9)
    fronts, clouds = {}, {}
    for region in regions:
        own_front = ar1(rng, DAYS, 0.7, 1.0)
        own_cloud = ar1(rng, DAYS, 0.6, 1.0)
        fronts[region] = (shared_front, own_front)
        clouds[region] = [1 / (1 + math.exp(-(a + b))) for a, b in zip(shared_cloud, own_cloud)]
    return fronts, gradient, clouds


def temperature(site, inland, x, metres, local, day, hour, front, gradient, cloud):
    """The true temperature at a site in one hour, as the sum of its signals.

    `front` is the network's fronts and the region's own; the sea damps the network's on the coast.
    """
    season_swing = 3.5 + 7.5 * inland
    lag = 30 - 12 * inland  # the sea lags the season
    yearly = -season_swing * math.cos(2 * math.pi * (day - lag) / 365)
    summer = 0.5 * (1 - math.cos(2 * math.pi * (day - lag) / 365))  # 0 in winter, 1 in summer
    sky = cloud[day]
    day_swing = (1.5 + 4.5 * inland) * (0.7 + 0.6 * summer) * (1 - 0.65 * sky)
    daily = -day_swing * math.cos(2 * math.pi * (hour - 3) / 24)  # coldest near 3 am, warmest near 3 pm
    shared, own = front
    weather_now = (0.5 + 0.5 * inland) * shared[day] + own[day] + gradient[day] * (x - 50) / 50
    t = SEA_LEVEL_MEAN + yearly + daily + weather_now - LAPSE * metres + local

    night = hour < 7 or hour > 19
    if site == TOWN:
        t += 3.5 if night else 0.8
    if site == SHADED:
        t -= 3.5 * max(0.0, math.sin(math.pi * (hour - 6) / 12)) * (1 - 0.4 * sky)
    if site == POOLING and night:
        t -= 5.0 * (1 - sky)  # a hollow on a clear, calm night
    return t


def place(rng, box, count, taken):
    """Spots for a region's sites, at least 6 km from any other site."""
    x0, y0, x1, y1 = box
    spots = []
    while len(spots) < count:
        x, y = rng.uniform(x0, x1), rng.uniform(y0, y1)
        if all(math.hypot(x - a, y - b) >= 6 for a, b in taken + spots):
            spots.append((round(x, 1), round(y, 1)))
    return spots


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--out", default="data/raw", help="folder to write into")
    parser.add_argument("--seed", type=int, default=7)
    args = parser.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    rows = ["x_km,y_km,elevation_m"]
    for y in range(0, SIZE + 1, 2):
        for x in range(-10, SIZE + 1, 2):
            rows.append(f"{x},{y},{-1 if x < 0 else round(elevation(x, y))}")
    (out / "terrain.csv").write_text("\n".join(rows) + "\n")

    (out / "alerts").mkdir(exist_ok=True)
    for alert, threshold in ALERTS.items():
        (out / "alerts" / f"{alert}.json").write_text(json.dumps(threshold) + "\n")

    fronts, gradient, clouds = weather(rng, REGIONS)
    taken = []
    for region, (box, names) in REGIONS.items():
        spots = place(rng, box, len(names), taken)
        inland = continentality((box[0] + box[2]) / 2)
        taken += spots
        for site, (x, y) in zip(names, spots):
            folder = out / region / site
            folder.mkdir(parents=True, exist_ok=True)
            metres = round(elevation(x, y) + rng.gauss(0, 15))
            (folder / "site.json").write_text(json.dumps({"x_km": x, "y_km": y, "elevation_m": metres}) + "\n")
            gain = round(rng.uniform(0.9, 1.1), 3)
            offset = round(rng.uniform(-2.5, 2.5), 2)
            (folder / "calibration.json").write_text(json.dumps({"gain": gain, "offset": offset}) + "\n")
            local = rng.gauss(0, 0.2)

            for day in range(0, DAYS, EVERY):
                if site == LATE[0] and day < LATE[1]:
                    continue
                if site == BATTERY[0] and day in BATTERY[1]:
                    continue
                rows = ["hour,temperature"]
                for hour in range(24):
                    t = temperature(site, inland, x, metres, local, day, hour, fronts[region], gradient, clouds[region])
                    t += rng.gauss(0, 0.3)
                    if site == DRIFTING:
                        t += max(0, day - 90) * 0.012  # the sensor starts to drift in April
                    raw = gain * t + offset
                    roll = rng.random()
                    if roll < 0.004:
                        raw = -999.0  # dropout
                    elif roll < 0.007:
                        raw += rng.choice([-1, 1]) * rng.uniform(25, 40)  # spike
                    rows.append(f"{hour},{raw:.2f}")
                date = datetime.date(YEAR, 1, 1) + datetime.timedelta(days=day)
                (folder / f"{date.isoformat()}.csv").write_text("\n".join(rows) + "\n")


if __name__ == "__main__":
    main()
