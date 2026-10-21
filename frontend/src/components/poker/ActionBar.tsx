import { BetSlider } from "./BetSlider";

type ActionBarProps = { legal: string[]; callAmount: number; bet: number; min: number; max: number; pot: number; onBetChange: (value: number) => void; onAction: (action: string) => void };

export function ActionBar({ legal, callAmount, bet, min, max, pot, onBetChange, onAction }: ActionBarProps) {
  const enabled = (action: string) => legal.includes(action);
  return (
    <div className="action-bar" aria-label="Poker actions">
      <div className="action-buttons">
        <button className="action-fold" disabled={!enabled("fold")} onClick={() => onAction("fold")}>Fold <kbd>F</kbd></button>
        <button disabled={!enabled("check") && !enabled("call")} onClick={() => onAction(enabled("check") ? "check" : "call")}>{enabled("check") ? "Check" : `Call ${callAmount.toFixed(1)} BB`} <kbd>C</kbd></button>
        <button disabled={!enabled("raise")} onClick={() => onAction("raise")}>Bet / Raise <kbd>R</kbd></button>
        <button className="action-all-in" disabled={!enabled("all-in")} onClick={() => onAction("all-in")}>All-in</button>
      </div>
      <BetSlider value={bet} min={min} max={max} pot={pot} onChange={onBetChange} />
    </div>
  );
}
