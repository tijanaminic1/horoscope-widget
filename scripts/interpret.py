"""Template-based interpretation of transiting planets: house placements and aspects."""

PLANET_THEME = {
    "Sun": "identity and vitality",
    "Moon": "emotions and instincts",
    "Mercury": "communication and thinking",
    "Venus": "love, values, and money",
    "Mars": "drive, action, and conflict",
    "Jupiter": "growth, luck, and expansion",
    "Saturn": "responsibility, limits, and discipline",
    "Uranus": "sudden change and disruption",
    "Neptune": "dreams, intuition, and confusion",
    "Pluto": "transformation and power",
}

HOUSE_THEME = {
    1: "your sense of self and how you show up",
    2: "money, resources, and self-worth",
    3: "communication, siblings, and everyday learning",
    4: "home, family, and emotional foundations",
    5: "creativity, romance, and self-expression",
    6: "work, routines, and health",
    7: "partnerships and one-on-one relationships",
    8: "shared resources, intimacy, and transformation",
    9: "travel, beliefs, and the big picture",
    10: "career, reputation, and public life",
    11: "friends, community, and future goals",
    12: "rest, solitude, and the subconscious",
}

HOUSE_ORDINAL = {
    1: "1st", 2: "2nd", 3: "3rd", 4: "4th", 5: "5th", 6: "6th",
    7: "7th", 8: "8th", 9: "9th", 10: "10th", 11: "11th", 12: "12th",
}

ASPECT_VERB = {
    "Conjunction": "merging with",
    "Sextile": "opening a gentle door to",
    "Square": "creating friction with",
    "Trine": "flowing easily with",
    "Opposition": "pulling against",
}

ASPECT_TONE = {
    "Conjunction": "an intense, all-in energy",
    "Sextile": "a low-key opportunity, if you take initiative",
    "Square": "real tension that asks you to adjust",
    "Trine": "an easy, supportive current",
    "Opposition": "a push-pull that wants balance, not a winner",
}


def house_line(planet, house):
    theme = PLANET_THEME[planet]
    hteme = HOUSE_THEME[house]
    ordinal = HOUSE_ORDINAL[house]
    return f"Transiting {planet} is moving through your {ordinal} house, stirring up {theme} around {hteme}."


def aspect_line(transiting_planet, aspect_name, natal_planet, orb):
    t_theme = PLANET_THEME[transiting_planet]
    n_theme = PLANET_THEME[natal_planet]
    verb = ASPECT_VERB[aspect_name]
    tone = ASPECT_TONE[aspect_name]
    return (
        f"Transiting {transiting_planet} is {verb} your natal {natal_planet} "
        f"({aspect_name.lower()}, orb {orb:.1f}°) — {t_theme} meets {n_theme}: {tone}."
    )


def build_horoscope(transit_houses, aspects):
    """transit_houses: list of (planet, house). aspects: list of dicts with
    transiting, aspect, natal, orb. Returns a list of sentences, most important first."""
    lines = []

    # Aspects sorted by tightness (smaller orb = more exact = more important today)
    for a in sorted(aspects, key=lambda x: x["orb"]):
        lines.append(aspect_line(a["transiting"], a["aspect"], a["natal"], a["orb"]))

    # Fast-moving personal-planet house transits worth flagging (Sun, Moon, Mercury, Venus, Mars)
    personal = {"Sun", "Moon", "Mercury", "Venus", "Mars"}
    for planet, house in transit_houses:
        if planet in personal:
            lines.append(house_line(planet, house))

    return lines
