export function ShowdownPanel({ winners, handNames = {}, payouts = [], wonUncontested = false }: { winners: number[]; handNames?: Record<string, string>; payouts?: number[]; wonUncontested?: boolean }) {
  if (!winners.length) return null;
  return <div className="showdown-panel" aria-label="Showdown result">
    <strong>{winners.length > 1 ? "Split pot" : `Seat ${winners[0] + 1} wins`}</strong>
    <span>{wonUncontested ? "Won uncontested" : winners.map((winner) => handNames[String(winner)] ?? "Winning hand").join(" · ")}</span>
    {payouts.length > 0 && <span>Pot share: {winners.map((winner) => `${payouts[winner]?.toFixed(1) ?? "0.0"} BB`).join(" / ")}</span>}
  </div>;
}
