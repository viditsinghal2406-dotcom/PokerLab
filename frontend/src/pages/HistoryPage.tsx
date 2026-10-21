import { useEffect, useState } from "react";

import { apiBaseUrl, type HistoryItem } from "../services/api";

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [error, setError] = useState<string | null>(null);

  const load = async () => {
    try {
      const response = await fetch(`${apiBaseUrl}/analytics/history`);
      if (!response.ok) throw new Error(`History failed (${response.status})`);
      setItems((await response.json()).items);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "History failed");
    }
  };

  useEffect(() => { void load(); }, []);

  const remove = async (id: number) => {
    const response = await fetch(`${apiBaseUrl}/analytics/history/${id}`, { method: "DELETE" });
    if (!response.ok) {
      setError(`Delete failed (${response.status})`);
      return;
    }
    setItems((current) => current.filter((item) => item.id !== id));
  };

  return (
    <section className="panel analytics-page" aria-labelledby="history-title">
      <div className="page-heading"><div><p className="eyebrow">Saved work</p><h2 id="history-title">Analytics history</h2><p className="page-subtitle">Review or remove saved ATSA and forecast runs.</p></div></div>
      {error && <p className="error">{error}</p>}
      {items.length === 0 ? <p className="m">No saved ATSA or forecast runs yet.</p> : (
        <ul>{items.map((item) => (
          <li key={item.id}>
            <span>{item.name} ({item.kind})</span>
            <button type="button" onClick={() => void remove(item.id)} aria-label={`Delete ${item.name}`}>Delete</button>
          </li>
        ))}</ul>
      )}
    </section>
  );
}
