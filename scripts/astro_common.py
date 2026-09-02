"""Shared constants and helpers for natal chart + transit calculations."""
import swisseph as swe

SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
         "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]

SIGN_GLYPHS = ["♈", "♉", "♊", "♋", "♌", "♍",
               "♎", "♏", "♐", "♑", "♒", "♓"]

# swisseph body id -> (name, glyph)
BODIES = [
    (swe.SUN, "Sun", "☉"),
    (swe.MOON, "Moon", "☽"),
    (swe.MERCURY, "Mercury", "☿"),
    (swe.VENUS, "Venus", "♀"),
    (swe.MARS, "Mars", "♂"),
    (swe.JUPITER, "Jupiter", "♃"),
    (swe.SATURN, "Saturn", "♄"),
    (swe.URANUS, "Uranus", "♅"),
    (swe.NEPTUNE, "Neptune", "♆"),
    (swe.PLUTO, "Pluto", "♇"),
]

ASPECTS = [
    ("Conjunction", 0, 8),
    ("Sextile", 60, 4),
    ("Square", 90, 6),
    ("Trine", 120, 6),
    ("Opposition", 180, 8),
]

HOUSE_SYSTEM = b'P'  # Placidus


def sign_index(longitude):
    return int(longitude // 30) % 12


def sign_name(longitude):
    return SIGNS[sign_index(longitude)]


def sign_glyph(longitude):
    return SIGN_GLYPHS[sign_index(longitude)]


def deg_in_sign(longitude):
    return longitude % 30


def angle_diff(a, b):
    """Smallest absolute angular distance between two longitudes, 0-180."""
    d = abs(a - b) % 360
    return d if d <= 180 else 360 - d


def house_of(longitude, cusps):
    """Given 12 house cusps (index 0 = house 1 start), return house number 1-12."""
    for i in range(12):
        start = cusps[i]
        end = cusps[(i + 1) % 12]
        if start < end:
            if start <= longitude < end:
                return i + 1
        else:  # wraps past 0 Aries
            if longitude >= start or longitude < end:
                return i + 1
    return 12


def get_bodies(jd_ut):
    """Return dict name -> {lon, speed, retro} for the 10 main bodies."""
    result = {}
    for body_id, name, glyph in BODIES:
        pos, _ = swe.calc_ut(jd_ut, body_id)
        lon, lat, dist, speed_lon = pos[0], pos[1], pos[2], pos[3]
        result[name] = {
            "glyph": glyph,
            "lon": lon,
            "speed": speed_lon,
            "retro": speed_lon < 0,
        }
    return result


def get_houses(jd_ut, lat, lon):
    cusps, ascmc = swe.houses(jd_ut, lat, lon, HOUSE_SYSTEM)
    return {
        "cusps": list(cusps),   # 12 values, index 0 = house 1 cusp
        "asc": ascmc[0],
        "mc": ascmc[1],
    }
