import { run } from "uebersicht";

const PY = "/Users/tijanaminic/Documents/astro-widget/venv/bin/python";
const SCRIPT_DIR = "/Users/tijanaminic/Documents/astro-widget/scripts";

export const command = `cd "${SCRIPT_DIR}" && "${PY}" transits.py`;

export const refreshFrequency = 60 * 60 * 1000; // hourly

export const className = `
  top: 40px;
  right: 40px;
  width: 340px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 16px 18px;
  background: rgba(18, 14, 30, 0.86);
  color: #f1ecff;
  font-family: -apple-system, "SF Pro Text", sans-serif;
  border-radius: 14px;
  box-shadow: 0 8px 30px rgba(0,0,0,0.35);
  backdrop-filter: blur(10px);

  .title {
    font-size: 13px;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #b9a6ff;
    margin-bottom: 6px;
  }
  .subtitle {
    font-size: 12px;
    color: #cfc4ff;
    margin-bottom: 12px;
    line-height: 1.4;
  }
  .natal-row {
    display: flex;
    gap: 14px;
    font-size: 12px;
    color: #cfc4ff;
    margin-bottom: 10px;
    padding-bottom: 10px;
    border-bottom: 1px solid rgba(255,255,255,0.12);
  }
  .natal-row b { color: #fff; }
  .section-label {
    font-size: 11px;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #8f7fc7;
    margin: 10px 0 4px;
  }
  .transit-grid {
    display: grid;
    grid-template-columns: repeat(5, 1fr);
    gap: 6px;
    font-size: 15px;
    text-align: center;
    margin-bottom: 4px;
  }
  .transit-cell {
    background: rgba(255,255,255,0.06);
    border-radius: 8px;
    padding: 4px 2px;
  }
  .transit-cell .house {
    display: block;
    font-size: 9px;
    color: #a293d6;
    margin-top: 1px;
  }
  .retro { color: #ff8b8b; }
  .horoscope-line {
    font-size: 12.5px;
    line-height: 1.5;
    margin-bottom: 8px;
    color: #e6e0ff;
  }
  .error {
    font-size: 12px;
    color: #ff8b8b;
    margin-top: 6px;
  }
  .updated {
    font-size: 9px;
    color: #6f5f9e;
    margin-top: 8px;
  }
  .field {
    margin-bottom: 8px;
  }
  .field label {
    display: block;
    font-size: 10px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: #8f7fc7;
    margin-bottom: 3px;
  }
  .field input {
    width: 100%;
    box-sizing: border-box;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.15);
    border-radius: 6px;
    color: #fff;
    padding: 6px 8px;
    font-size: 12.5px;
  }
  .submit-btn {
    width: 100%;
    margin-top: 6px;
    padding: 7px;
    background: #7a5cff;
    border: none;
    border-radius: 6px;
    color: #fff;
    font-size: 12.5px;
    font-weight: 600;
    cursor: pointer;
  }
  .submit-btn:disabled {
    opacity: 0.5;
  }
`;

const escapeShellArg = (s) => `'${String(s).replace(/'/g, `'\\''`)}'`;

const SetupForm = ({ state, updateState }) => {
  const busy = state?.setupBusy;
  const setupError = state?.setupError;

  const submit = async () => {
    const date = document.getElementById("hw-date").value.trim();
    const time = document.getElementById("hw-time").value.trim();
    const location = document.getElementById("hw-location").value.trim();

    if (!date || !time || !location) {
      updateState({ ...state, setupError: "Please fill in all three fields." });
      return;
    }

    updateState({ ...state, setupBusy: true, setupError: null });

    const setupCmd =
      `cd "${SCRIPT_DIR}" && "${PY}" setup.py ` +
      `--date ${escapeShellArg(date)} --time ${escapeShellArg(time)} --location ${escapeShellArg(location)}`;

    try {
      const setupOut = await run(setupCmd);
      const setupResult = JSON.parse(setupOut);
      if (setupResult.error) {
        updateState({ ...state, setupBusy: false, setupError: setupResult.error });
        return;
      }
      const transitsOut = await run(command);
      const override = JSON.parse(transitsOut);
      updateState({ override, setupBusy: false, setupError: null });
    } catch (e) {
      updateState({ ...state, setupBusy: false, setupError: String(e) });
    }
  };

  return (
    <div>
      <div className="title">Set Up Your Chart</div>
      <div className="subtitle">
        Enter your birth details once. They're geocoded locally and saved only on this Mac —
        never committed to the repo.
      </div>
      <div className="field">
        <label>Birth date (YYYY-MM-DD)</label>
        <input id="hw-date" type="text" placeholder="2001-09-04" />
      </div>
      <div className="field">
        <label>Birth time, 24h (HH:MM)</label>
        <input id="hw-time" type="text" placeholder="18:40" />
      </div>
      <div className="field">
        <label>Birth location</label>
        <input id="hw-location" type="text" placeholder="Belgrade, Serbia" />
      </div>
      <button className="submit-btn" disabled={busy} onClick={submit}>
        {busy ? "Calculating chart…" : "Save & Calculate Chart"}
      </button>
      {setupError && <div className="error">{setupError}</div>}
    </div>
  );
};

const Horoscope = ({ data }) => {
  const { natal_summary, transits, horoscope, generated_at } = data;
  const order = ["Sun", "Moon", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Uranus", "Neptune", "Pluto"];

  return (
    <div>
      <div className="title">Daily Transits</div>
      <div className="natal-row">
        <span>☉ <b>{natal_summary.sun}</b></span>
        <span>☽ <b>{natal_summary.moon}</b></span>
        <span>ASC <b>{natal_summary.ascendant}</b></span>
      </div>

      <div className="section-label">Sky right now</div>
      <div className="transit-grid">
        {order.map((name) => {
          const t = transits[name];
          if (!t) return null;
          return (
            <div className="transit-cell" key={name}>
              <span className={t.retro ? "retro" : ""}>
                {t.glyph}{t.sign_glyph}
              </span>
              <span className="house">H{t.house}{t.retro ? " R" : ""}</span>
            </div>
          );
        })}
      </div>

      <div className="section-label">Today's Horoscope</div>
      {horoscope.length === 0 && (
        <div className="horoscope-line">No exact transits right now — a quiet, steady day.</div>
      )}
      {horoscope.slice(0, 6).map((line, i) => (
        <div className="horoscope-line" key={i}>{line}</div>
      ))}

      <div className="updated">Updated {new Date(generated_at).toLocaleString()}</div>
    </div>
  );
};

export const render = ({ output, error, state, updateState }) => {
  if (state?.override) {
    return <Horoscope data={state.override} />;
  }

  if (error) {
    return <div className="error">Widget error: {String(error)}</div>;
  }
  if (!output) {
    return <div className="title">Loading…</div>;
  }

  let data;
  try {
    data = JSON.parse(output);
  } catch (e) {
    return <div className="error">Parse error: {String(e)}</div>;
  }

  if (data.needs_setup) {
    return <SetupForm state={state} updateState={updateState} />;
  }

  if (data.error) {
    return <div className="error">Python error: {data.error}</div>;
  }

  return <Horoscope data={data} />;
};
