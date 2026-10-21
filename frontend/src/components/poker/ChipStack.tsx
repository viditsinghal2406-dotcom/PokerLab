export function ChipStack({ amount, label = "simulated chips" }: { amount: number; label?: string }) {
  const denominations = [25, 5, 1, 0.5];
  let remaining = Math.max(0, amount);
  const chips = denominations.flatMap((value) => {
    const count = Math.min(5, Math.floor(remaining / value + 1e-9));
    remaining -= count * value;
    return Array.from({ length: count }, () => value);
  });
  return <span className="chip-stack"><span className="chip-pile" aria-hidden="true">{(chips.length ? chips : [0.5]).map((value, index) => <i key={`${value}-${index}`} className={`chip chip-${String(value).replace(".", "-")}`} />)}</span><span>{amount.toFixed(1)} BB</span><small>{label}</small></span>;
}
