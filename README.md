# horoscope-widget

A macOS desktop widget (built on [Übersicht](https://tracesof.net/uebersicht/)) that computes your
natal chart, tracks current planetary transits against it, and shows a daily horoscope written by
Claude from the specific aspects and house placements active that day.

Your birth data never leaves your machine and is never committed to this repo — it's entered once
through the widget's setup form (or `setup.py`) and cached locally in gitignored files.

## How it works

- **`scripts/astro_common.py`** — shared ephemeris helpers (signs, houses, aspects) built on
  [pyswisseph](https://pypi.org/project/pyswisseph/) (Swiss Ephemeris).
- **`scripts/setup.py`** — takes a birth date, time, and location; geocodes the location and
  resolves its historical UTC offset (handles old DST rules correctly); writes `config.json` and
  computes `natal_chart.json` (Placidus houses).
- **`scripts/transits.py`** — run on every widget refresh. Computes today's planetary positions,
  which natal house each one currently occupies, and every transit-to-natal aspect within orb.
- **`scripts/claude_horoscope.py`** — sends that data to Claude and asks for a few concrete,
  specific horoscope bullets. Cached once per calendar day so it isn't calling the API hourly.
- **`widget/horoscope.widget/index.jsx`** — the Übersicht widget itself: shows a setup form until
  a chart exists, then renders the natal summary, today's transiting planets/houses, and the
  horoscope bullets. Refreshes hourly.

## Setup on a new machine

```bash
brew install --cask ubersicht
cd astro-widget
python3 -m venv venv
venv/bin/pip install pyswisseph geopy timezonefinder anthropic
```

Add your Anthropic key (and, if your key is workspace-scoped, its workspace ID) to a local,
gitignored env file:

```bash
cat > scripts/.env <<'EOF'
ANTHROPIC_API_KEY=sk-ant-...
ANTHROPIC_WORKSPACE_ID=wrkspc_...   # only needed for identity-linked keys
EOF
chmod 600 scripts/.env
```

Symlink the widget into Übersicht's widgets folder:

```bash
ln -s "$(pwd)/widget/horoscope.widget" \
  ~/Library/Application\ Support/Übersicht/widgets/horoscope.widget
```

Open Übersicht once — the widget will show a setup form asking for your birth date, time, and
location. Fill it in (or run `venv/bin/python scripts/setup.py` from `scripts/` interactively) and
the chart + transits take over from there.

## Removing it

| Goal | Command |
|---|---|
| Hide it right now | Quit Übersicht from its menu bar icon |
| Remove just this widget | `rm ~/Library/Application\ Support/Übersicht/widgets/horoscope.widget` |
| Stop auto-launch at login | System Settings → General → Login Items → remove Übersicht |
| Full uninstall | Quit Übersicht, remove the Login Item, `brew uninstall --cask ubersicht`, delete this folder |
