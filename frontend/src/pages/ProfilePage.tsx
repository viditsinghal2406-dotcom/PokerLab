import { useEffect, useState } from "react";

const SETTINGS_KEY = "pokerlab.profile";

type ProfileSettings = { displayName: string; energyMode: boolean; personalization: boolean };

const defaults: ProfileSettings = { displayName: "Vidit", energyMode: false, personalization: true };

export function ProfilePage() {
  const [settings, setSettings] = useState<ProfileSettings>(defaults);
  useEffect(() => {
    const saved = localStorage.getItem(SETTINGS_KEY);
    if (saved) {
      try { setSettings({ ...defaults, ...JSON.parse(saved) }); } catch { /* ignore malformed local preference */ }
    }
  }, []);

  const update = (patch: Partial<ProfileSettings>) => {
    const next = { ...settings, ...patch };
    setSettings(next);
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(next));
  };

  return (
    <section className="panel analytics-page profile-page" aria-labelledby="profile-title">
      <div className="page-heading"><div><p className="eyebrow">Local preferences</p><h2 id="profile-title">Vidit Mode profile</h2><p className="page-subtitle">Personalization stays in this browser and never becomes telemetry.</p></div></div>
      {settings.personalization ? (
        <>
          <p>Vidit Mode balances aggressive decisions, controlled bluffing, and risk-aware sizing.</p>
          <label>Display name
            <input value={settings.displayName} onChange={(event) => update({ displayName: event.target.value })} />
          </label>
          <label>Energy Mode
            <input type="checkbox" checked={settings.energyMode} onChange={(event) => update({ energyMode: event.target.checked })} />
          </label>
          <p className="m">Achievements: First Deal · 100 Hands · Experimenter · Forecast Analyst · Showdown Specialist.</p>
          <button type="button" onClick={() => update({ displayName: "Vidit" })}>Reset display name</button>
          <button type="button" onClick={() => alert("PokerLab easter egg unlocked")}>Reveal easter egg</button>
        </>
      ) : <p className="m">Personalization is disabled. No profile settings are used.</p>}
      <label>Enable local personalization
        <input type="checkbox" checked={settings.personalization} onChange={(event) => update({ personalization: event.target.checked })} />
      </label>
      <p className="m">Settings are stored in this browser only. PokerLab does not send telemetry for personalization.</p>
    </section>
  );
}
