export function DealerButton({ marker = "D" }: { marker?: string }) {
  return <span className="dealer-button" aria-label="Dealer button">{marker}</span>;
}
