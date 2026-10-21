type BetSliderProps = { value: number; min: number; max: number; pot: number; onChange: (value: number) => void };

export function BetSlider({ value, min, max, pot, onChange }: BetSliderProps) {
  const clamp = (next: number) => onChange(Math.min(max, Math.max(min, next)));
  return (
    <div className="bet-control">
      <div className="bet-presets">
        {[["Min", min], ["½ pot", pot / 2], ["¾ pot", pot * .75], ["Pot", pot], ["All-in", max]].map(([label, amount]) => (
          <button type="button" key={label} onClick={() => clamp(Number(amount))}>{label}</button>
        ))}
      </div>
      <input aria-label="Bet amount" type="range" min={min} max={max} step=".5" value={Math.min(max, Math.max(min, value))} onChange={(event) => clamp(Number(event.target.value))} />
      <div className="bet-input-row"><span>Min {min.toFixed(1)} BB</span><input aria-label="Bet amount number" type="number" min={min} max={max} step=".5" value={value} onChange={(event) => clamp(Number(event.target.value))} /><span>Max {max.toFixed(1)} BB</span></div>
    </div>
  );
}
