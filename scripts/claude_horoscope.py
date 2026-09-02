"""Ask Claude to turn today's raw transit/aspect data into a few interpretive bullets.

Caches the result per calendar day (keyed also on the underlying data, so if the
sky picture shifts meaningfully within a day it will regenerate) to avoid calling
the API on every hourly widget refresh.
"""
import datetime
import hashlib
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ENV_PATH = os.path.join(HERE, ".env")
CACHE_PATH = os.path.join(HERE, "horoscope_cache.json")
MODEL = "claude-sonnet-5"


def _read_env_var(key):
    if os.environ.get(key):
        return os.environ[key]
    if os.path.exists(ENV_PATH):
        with open(ENV_PATH) as f:
            for line in f:
                line = line.strip()
                if line.startswith(f"{key}="):
                    return line.split("=", 1)[1].strip().strip('"').strip("'")
    return None


def load_api_key():
    return _read_env_var("ANTHROPIC_API_KEY")


def load_workspace_id():
    return _read_env_var("ANTHROPIC_WORKSPACE_ID")


def _signature(natal_summary, aspects, transit_houses):
    # Round orbs so tiny sub-degree drift between hourly refreshes doesn't
    # bust the cache; a new day or a real shift in the picture will.
    payload = {
        "natal": natal_summary,
        "aspects": [
            {"t": a["transiting"], "a": a["aspect"], "n": a["natal"], "o": round(a["orb"])}
            for a in aspects[:6]
        ],
        "houses": sorted(transit_houses),
    }
    blob = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(blob.encode()).hexdigest()


def _load_cache():
    if os.path.exists(CACHE_PATH):
        try:
            with open(CACHE_PATH) as f:
                return json.load(f)
        except (json.JSONDecodeError, OSError):
            return None
    return None


def _save_cache(entry):
    with open(CACHE_PATH, "w") as f:
        json.dump(entry, f, indent=2)


def build_prompt(natal_summary, aspects, transit_houses):
    lines = [
        f"My natal chart: Sun in {natal_summary['sun']}, Moon in {natal_summary['moon']}, "
        f"Ascendant in {natal_summary['ascendant']}.",
        "",
        "Current transiting planets and which of my natal houses they're passing through:",
    ]
    for planet, house in sorted(transit_houses, key=lambda x: x[1]):
        lines.append(f"- {planet} is transiting my {house}th house")

    lines.append("")
    lines.append("Active transit-to-natal aspects right now (tightest orb first):")
    for a in aspects[:8]:
        lines.append(
            f"- Transiting {a['transiting']} {a['aspect']} my natal {a['natal']} (orb {a['orb']}°)"
        )

    lines.append("")
    lines.append(
        "Write my horoscope for today as 3-5 short bullet points. Each bullet should name "
        "the specific transit or house placement it's about, in plain language (not jargon-only), "
        "and explain concretely how it might show up in my day. Prioritize the tightest-orb "
        "aspects and any personal-planet house transits. Be specific and grounded, not generic "
        "fortune-cookie language. No preamble, no closing summary — just the bullets, each ~1-2 sentences."
    )
    return "\n".join(lines)


def get_horoscope_bullets(natal_summary, aspects, transit_houses):
    sig = _signature(natal_summary, aspects, transit_houses)
    today = datetime.date.today().isoformat()

    cache = _load_cache()
    if cache and cache.get("date") == today and cache.get("signature") == sig:
        return cache["bullets"], True

    api_key = load_api_key()
    if not api_key:
        return ["(Set ANTHROPIC_API_KEY in scripts/.env to enable Claude-written horoscopes.)"], False

    import anthropic
    workspace_id = load_workspace_id()
    default_headers = {"anthropic-workspace-id": workspace_id} if workspace_id else None
    client = anthropic.Anthropic(api_key=api_key, default_headers=default_headers)
    prompt = build_prompt(natal_summary, aspects, transit_houses)

    message = client.messages.create(
        model=MODEL,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    text = "".join(block.text for block in message.content if block.type == "text")
    bullets = [line.strip("-• ").strip() for line in text.strip().splitlines() if line.strip()]

    _save_cache({"date": today, "signature": sig, "bullets": bullets})
    return bullets, False
