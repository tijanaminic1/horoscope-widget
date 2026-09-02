"""Compute a natal chart from scripts/config.json and cache it to natal_chart.json.

config.json (gitignored, created by setup.py) looks like:
{
  "date": "YYYY-MM-DD",
  "time": "HH:MM",
  "location_text": "City, Country",
  "lat": 44.8125,
  "lon": 20.4612,
  "tz_name": "Europe/Belgrade"
}
"""
import json
import os
import datetime
import swisseph as swe
from zoneinfo import ZoneInfo
from astro_common import get_bodies, get_houses, house_of, sign_name, sign_glyph, deg_in_sign

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG_PATH = os.path.join(HERE, "config.json")
OUT_PATH = os.path.join(HERE, "natal_chart.json")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return None
    with open(CONFIG_PATH) as f:
        return json.load(f)


def compute_natal(config):
    year, month, day = (int(x) for x in config["date"].split("-"))
    hour, minute = (int(x) for x in config["time"].split(":"))
    lat, lon = config["lat"], config["lon"]

    local_dt = datetime.datetime(year, month, day, hour, minute, tzinfo=ZoneInfo(config["tz_name"]))
    utc_dt = local_dt.astimezone(datetime.timezone.utc)

    jd_ut = swe.julday(utc_dt.year, utc_dt.month, utc_dt.day,
                        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0)

    bodies = get_bodies(jd_ut)
    houses = get_houses(jd_ut, lat, lon)
    cusps = houses["cusps"]

    planets_out = {}
    for name, data in bodies.items():
        planets_out[name] = {
            "glyph": data["glyph"],
            "lon": data["lon"],
            "sign": sign_name(data["lon"]),
            "sign_glyph": sign_glyph(data["lon"]),
            "deg_in_sign": round(deg_in_sign(data["lon"]), 2),
            "retro": data["retro"],
            "house": house_of(data["lon"], cusps),
        }

    asc = houses["asc"]
    mc = houses["mc"]

    return {
        "birth": {
            "date": config["date"],
            "time_local": config["time"],
            "location": config.get("location_text", ""),
            "lat": lat,
            "lon": lon,
            "tz_name": config["tz_name"],
            "jd_ut": jd_ut,
        },
        "ascendant": {
            "lon": asc,
            "sign": sign_name(asc),
            "sign_glyph": sign_glyph(asc),
            "deg_in_sign": round(deg_in_sign(asc), 2),
        },
        "midheaven": {
            "lon": mc,
            "sign": sign_name(mc),
            "sign_glyph": sign_glyph(mc),
            "deg_in_sign": round(deg_in_sign(mc), 2),
        },
        "houses": cusps,
        "planets": planets_out,
    }


def main():
    config = load_config()
    if config is None:
        print("No config.json found. Run setup.py first.")
        return

    natal = compute_natal(config)
    with open(OUT_PATH, "w") as f:
        json.dump(natal, f, indent=2)

    print(f"Wrote {OUT_PATH}")
    print(f"Ascendant: {natal['ascendant']['sign']} {natal['ascendant']['deg_in_sign']}°")
    for name, p in natal["planets"].items():
        r = " (R)" if p["retro"] else ""
        print(f"  {name:8s} {p['sign']:12s} {p['deg_in_sign']:5.2f}°  house {p['house']:2d}{r}")


if __name__ == "__main__":
    main()
