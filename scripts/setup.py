"""One-time (or re-run anytime) setup: collect natal data, geocode the location,
resolve the historical UTC offset, and write scripts/config.json + natal_chart.json.

Can be run interactively:
    python setup.py

Or non-interactively (used by the widget's setup form):
    python setup.py --date 2001-09-04 --time 18:40 --location "Belgrade, Serbia"
"""
import argparse
import json
import os
import sys
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from natal import compute_natal, OUT_PATH, CONFIG_PATH


def geocode(location_text):
    geolocator = Nominatim(user_agent="horoscope-widget-setup")
    loc = geolocator.geocode(location_text)
    if loc is None:
        raise ValueError(f"Could not find a location for '{location_text}'. Try 'City, Country'.")
    return loc.latitude, loc.longitude


def resolve_timezone(lat, lon):
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lat=lat, lng=lon)
    if tz_name is None:
        raise ValueError(f"Could not resolve a timezone for coordinates ({lat}, {lon}).")
    return tz_name


def build_config(date, time, location_text):
    lat, lon = geocode(location_text)
    tz_name = resolve_timezone(lat, lon)
    return {
        "date": date,
        "time": time,
        "location_text": location_text,
        "lat": lat,
        "lon": lon,
        "tz_name": tz_name,
    }


def run(date, time, location_text):
    config = build_config(date, time, location_text)
    with open(CONFIG_PATH, "w") as f:
        json.dump(config, f, indent=2)

    natal = compute_natal(config)
    with open(OUT_PATH, "w") as f:
        json.dump(natal, f, indent=2)

    return config, natal


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--date", help="YYYY-MM-DD")
    parser.add_argument("--time", help="HH:MM, 24-hour, local birth time")
    parser.add_argument("--location", help="City, Country")
    args = parser.parse_args()

    if args.date and args.time and args.location:
        date, time, location_text = args.date, args.time, args.location
    else:
        print("Let's set up your natal chart.")
        date = input("Birth date (YYYY-MM-DD): ").strip()
        time = input("Birth time, 24-hour (HH:MM): ").strip()
        location_text = input("Birth location (City, Country): ").strip()

    try:
        config, natal = run(date, time, location_text)
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(1)

    print(json.dumps({
        "ok": True,
        "resolved_location": f"{config['lat']:.4f}, {config['lon']:.4f} ({config['tz_name']})",
        "ascendant": natal["ascendant"]["sign"],
        "sun": natal["planets"]["Sun"]["sign"],
        "moon": natal["planets"]["Moon"]["sign"],
    }))


if __name__ == "__main__":
    main()
