import { useEffect, useState } from "react";

import { createTable, submitTableAction, type TableState } from "../services/api";
import { ActionBar } from "../components/poker/ActionBar";
import { HandHistory } from "../components/poker/HandHistory";
import { ShowdownPanel } from "../components/poker/ShowdownPanel";
import { TableLayout } from "../components/poker/TableLayout";

export function PokerArenaPage() {
  const [players, setPlayers] = useState(3);
  const [table, setTable] = useState<TableState | null>(null);
  const [bet, setBet] = useState(2);
  const [thinking, setThinking] = useState(false);
  const [debug, setDebug] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const newHand = async () => {
    try {
      setError(null);
      setTable(await createTable(players));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Unable to deal hand");
    }
  };

  useEffect(() => { void newHand(); }, [players]);

  useEffect(() => {
    const handler = (event: KeyboardEvent) => {
      if (!table || table.finished || (event.target as HTMLElement)?.tagName === "INPUT") return;
      const action = event.key.toLowerCase() === "f" ? "fold" : event.key.toLowerCase() === "c" ? (table.legal_actions.includes("check") ? "check" : "call") : event.key.toLowerCase() === "r" ? "raise" : null;
      if (action && table.legal_actions.includes(action)) void act(action);
    };
    window.addEventListener("keydown", handler);
    return () => window.removeEventListener("keydown", handler);
  });

  const act = async (kind: string) => {
    if (!table) return;
    setThinking(true);
    try {
      const next = await submitTableAction(table.id, table.current_player, kind, kind === "raise" ? bet : 0);
      window.setTimeout(() => { setTable(next); setThinking(false); }, 300);
    } catch (reason) {
      setThinking(false);
      setError(reason instanceof Error ? reason.message : "Action failed");
    }
  };

  return (
    <section className="poker-arena" aria-labelledby="arena-title">
      <div className="arena-header">
        <div><p className="eyebrow">Virtual chips · backend-controlled</p><h2 id="arena-title">Poker Arena</h2></div>
        <div className="arena-settings"><label>Players <select value={players} onChange={(event) => setPlayers(Number(event.target.value))}>{Array.from({ length: 8 }, (_, index) => index + 2).map((value) => <option key={value}>{value}</option>)}</select></label><span className="variant-pill">No-limit Hold'em</span></div>
      </div>
      {error && <p className="error">{error}</p>}
      {table && <TableLayout board={table.board} street={table.street} pot={table.pot_total ?? table.pot} stacks={table.stacks} acting={table.current_player} hole={table.hole} finished={table.finished} winners={table.winners} seats={table.seats} usedCards={table.used_cards} />}
      {table && !table.finished && <p className="thinking" aria-live="polite">{thinking ? "Opponent is thinking…" : table.current_player === 0 ? "Your action" : "Waiting for opponent…"}</p>}
      {table && !table.finished && table.current_player === 0 && <ActionBar legal={table.legal_actions} callAmount={table.to_call ?? Math.max(0, table.minimum_raise_to - 1)} bet={Math.min(table.maximum_raise_to, Math.max(table.minimum_raise_to, bet))} min={table.minimum_raise_to} max={table.maximum_raise_to} pot={table.pot_total ?? table.pot} onBetChange={setBet} onAction={act} />}
      {table?.finished && <ShowdownPanel winners={table.winners} handNames={table.hand_names} payouts={table.payouts} wonUncontested={table.won_uncontested} />}
      {table?.finished && <button type="button" className="next-hand" onClick={() => void newHand()}>Next hand</button>}
      {table && <HandHistory entries={table.action_log} />}
      <details className="debug-panel" open={debug} onToggle={(event) => setDebug((event.currentTarget as HTMLDetailsElement).open)}><summary>Developer / debug</summary><pre>{JSON.stringify({ tableId: table?.id, legalActions: table?.legal_actions, actingPlayer: table?.current_player, stacks: table?.stacks }, null, 2)}</pre></details>
    </section>
  );
}
