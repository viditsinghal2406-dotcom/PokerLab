import { ChipStack } from "./ChipStack";

export function PotDisplay({ amount }: { amount: number }) {
  return <div className="pot-display"><span className="pot-label">Main pot</span><ChipStack amount={amount} /></div>;
}
