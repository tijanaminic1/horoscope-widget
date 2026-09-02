"""Compute today's transits against the cached natal chart and print JSON to stdout.
Meant to be invoked by the Übersicht widget on a refresh timer."""
import json
import os
import sys
import datetime
import swisseph as swe
from astro_common import ASPECTS, get_bodies, house_of, sign_name, sign_glyph, deg_in_sign, angle_diff
from interpret import build_horoscope
from claude_horoscope import get_horoscope_bullets

HERE = os.path.dirname(os.path.abspath(__file__))
NATAL_PATH = os.path.join(HERE, "natal_chart.json")


def main():
    if not os.path.exists(NATAL_PATH):
        print(json.dumps({"needs_setup": True}))
        return

    with open(NATAL_PATH) as f:
        natal = json.load(f)

    cusps = natal["houses"]
    natal_planets = natal["planets"]

    now = datetime.datetime.now(datetime.timezone.utc)
    jd_ut = swe.julday(now.year, now.month, now.day,
                        now.hour + now.minute / 60.0 + now.second / 3600.0)

    transiting = get_bodies(jd_ut)

    transit_out = {}
    transit_houses = []
    for name, data in transiting.items():
        h = house_of(data["lon"], cusps)
        transit_out[name] = {
            "glyph": data["glyph"],
            "sign": sign_name(data["lon"]),
            "sign_glyph": sign_glyph(data["lon"]),
            "deg_in_sign": round(deg_in_sign(data["lon"]), 2),
            "retro": data["retro"],
            "house": h,
        }
        transit_houses.append((name, h))

    # Aspects: every transiting body vs every natal body
    aspects = []
    for t_name, t_data in transiting.items():
        for n_name, n_data in natal_planets.items():
            diff = angle_diff(t_data["lon"], n_data["lon"])
            for aspect_name, exact_angle, orb_limit in ASPECTS:
                orb = abs(diff - exact_angle)
                if orb <= orb_limit:
                    aspects.append({
                        "transiting": t_name,
                        "natal": n_name,
                        "aspect": aspect_name,
                        "orb": round(orb, 2),
                    })
                    break  # only closest aspect type per pair

    aspects.sort(key=lambda a: a["orb"])

    natal_summary = {
        "sun": natal_planets["Sun"]["sign"],
        "moon": natal_planets["Moon"]["sign"],
        "ascendant": natal["ascendant"]["sign"],
    }

    try:
        bullets, from_cache = get_horoscope_bullets(natal_summary, aspects, transit_houses)
    except Exception as e:
        bullets = build_horoscope(transit_houses, aspects)  # fallback: template engine
        from_cache = False

    output = {
        "generated_at": now.isoformat(),
        "natal_summary": natal_summary,
        "natal_planets": natal_planets,
        "natal_ascendant": natal["ascendant"],
        "natal_midheaven": natal["midheaven"],
        "transits": transit_out,
        "aspects": aspects,
        "horoscope": bullets,
        "horoscope_from_cache": from_cache,
    }

    print(json.dumps(output))


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.exit(0)
